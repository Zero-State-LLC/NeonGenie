#!/usr/bin/env python3
"""Optional evidence gathering before a packet is written.

Adapters are pluggable. The core stays on the standard library and can run
with no network. Offline and research-disabled runs do not call adapters and
do not emit OBSERVED claims.

A gathered item is OBSERVED only when it has an http(s) URL, a retrieval
date, and a complete source body. No source means no OBSERVED label.
A paid search hit is OBSERVED only when it is also a primary source
(vendor pricing or docs, an official blog, government or registry, or a
paper) and the snippet is longer than a fragment. Social posts, forums,
aggregators, other blogs, error pages, and short fragments are unverified.
"""

from __future__ import annotations

import os
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any, Callable, Protocol
from zoneinfo import ZoneInfo

import firecrawl_client
import privacy_preflight

# Normal HTML pricing and docs pages exceeded 64 KiB in the round-3 probe
# (10 of 14). 2 MiB is still a hard cap: a larger body is rejected whole.
MAX_BODY_BYTES = 2 * 1024 * 1024
RESEARCH_UA = "neon-genie-research/3.34"
MIN_SEARCH_WORDS = 20
DEFAULT_MAX_CALLS_PER_IDEA = 5
DEFAULT_DOLLAR_CAP_PER_IDEA = 0.20
DEFAULT_DOLLAR_CAP_PER_RUN = 1.00
DEFAULT_PAID_PRICE = 0.08
PAID_KEY_ENV = "NEON_GENIE_SEARCH_API_KEY"
PAID_FLAG_ENV = "NEON_GENIE_RESEARCH_PAID"
FIRECRAWL_KEY_ENV = firecrawl_client.FIRECRAWL_KEY_ENV
_LA = ZoneInfo("America/Los_Angeles")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_KINDS = frozenset({"web_page", "paper", "social_post"})
_PAID_ADAPTERS = frozenset(
    {"paid", "openrouter", "anthropic", "openai", "serper", "tavily"}
)
_PLACEHOLDER_DATES = frozenset(
    {"0000-00-00", "0001-01-01", "1900-01-01", "1970-01-01", "9999-12-31"}
)
_PLACEHOLDER_WORD = re.compile(
    r"\b(placeholder|tbd|todo|unspecified|unknown)\b",
    re.IGNORECASE,
)


class ResearchAdapter(Protocol):
    name: str

    def gather(self, queries: list[str]) -> list[dict[str, Any]]:
        """Return source records. Do not invent buyers, revenue, or prices."""


class NullAdapter:
    """Offline adapter. Returns nothing and never labels a claim."""

    name = "null"

    def gather(self, queries: list[str]) -> list[dict[str, Any]]:
        return []


class FixtureAdapter:
    """In-memory sources for tests and CI. No network."""

    name = "fixture"

    def __init__(self, items: list[dict[str, Any]] | None = None) -> None:
        self.items = list(items or [])

    def gather(self, queries: list[str]) -> list[dict[str, Any]]:
        if not queries:
            return list(self.items)
        matched: list[dict[str, Any]] = []
        for item in self.items:
            blob = " ".join(
                str(item.get(key) or "")
                for key in ("query", "title", "text", "excerpt", "url")
            ).lower()
            if any(q.lower() in blob for q in queries if q):
                matched.append(item)
        return matched


_SOCIAL_HOSTS = (
    "instagram.com",
    "facebook.com",
    "fb.com",
    "twitter.com",
    "x.com",
    "linkedin.com",
    "tiktok.com",
    "youtube.com",
    "youtu.be",
    "reddit.com",
    "threads.net",
    "bsky.app",
    "pinterest.com",
    "mastodon.social",
    "snapchat.com",
)
_FORUM_HOSTS = (
    "news.ycombinator.com",
    "stackoverflow.com",
    "stackexchange.com",
    "quora.com",
    "lobste.rs",
    "discourse.org",
)
_AGGREGATOR_HOSTS = (
    "yelp.com",
    "crunchbase.com",
    "g2.com",
    "capterra.com",
    "producthunt.com",
    "wikipedia.org",
    "wikimedia.org",
    "trustpilot.com",
    "glassdoor.com",
)
_BLOG_HOSTS = (
    "medium.com",
    "substack.com",
    "wordpress.com",
    "blogspot.com",
    "blogger.com",
    "dev.to",
    "hashnode.dev",
    "tumblr.com",
)
_PAPER_HOSTS = (
    "arxiv.org",
    "doi.org",
    "sciencedirect.com",
    "nature.com",
    "acm.org",
    "ieee.org",
    "springer.com",
    "pubmed.ncbi.nlm.nih.gov",
    "ncbi.nlm.nih.gov",
    "ssrn.com",
    "plos.org",
    "jstor.org",
)
_ERROR_PAGE = re.compile(
    r"\b(?:page not found|not found|404 not found)\b|\b404\b",
    re.IGNORECASE,
)
_PRIMARY_PATHS = (
    "/pricing",
    "/price",
    "/billing",
    "/docs",
    "/documentation",
    "/developers",
    "/developer",
    "/fees",
    "/api-docs",
    "/api/",
    "/blog",
    "/news/",
    "/index/",
    "/announcements",
    "/changelog",
    "/release-notes",
)


def _hostname(url: str) -> str:
    host = (urllib.parse.urlsplit(url).hostname or "").lower()
    if host.startswith("www."):
        return host[4:]
    return host


def _host_matches(host: str, names: tuple[str, ...]) -> bool:
    return any(host == name or host.endswith("." + name) for name in names)


def primary_source(url: str) -> bool:
    """Vendor docs/pricing, official blogs, government/registry, or a paper."""
    host = _hostname(url)
    path = urllib.parse.urlsplit(url).path.lower()
    if host.endswith(".gov") or host.endswith(".mil") or host.endswith(".gov.uk"):
        return True
    if _host_matches(host, _PAPER_HOSTS) or "/doi/" in path:
        return True
    if host.startswith(("docs.", "developer.", "developers.", "help.")):
        return True
    return any(bit in path for bit in _PRIMARY_PATHS)


def search_hit_block(url: str, text: str) -> str | None:
    """Why a search hit is not OBSERVED. None means it may be cited.

    Direct fetches the operator named are not passed through this filter.
    """
    if not isinstance(url, str) or not isinstance(text, str):
        return "not_primary"
    if _ERROR_PAGE.search(text):
        return "error_page"
    host = _hostname(url)
    if _host_matches(host, _SOCIAL_HOSTS):
        return "social"
    if _host_matches(host, _FORUM_HOSTS):
        return "forum"
    if _host_matches(host, _AGGREGATOR_HOSTS):
        return "aggregator"
    if _host_matches(host, _BLOG_HOSTS):
        return "blog"
    if len(text.split()) < MIN_SEARCH_WORDS:
        return "fragment"
    if not primary_source(url):
        return "not_primary"
    return None


def classify_url(url: str) -> str:
    lowered = url.lower()
    if any(token in lowered for token in ("arxiv.org", "doi.org", "/doi/", ".pdf")):
        return "paper"
    if any(
        token in lowered
        for token in ("twitter.com", "x.com/", "bsky.app", "mastodon")
    ):
        return "social_post"
    return "web_page"


def _today(moment: datetime | None = None) -> str:
    """Calendar date in America/Los_Angeles. UTC would stamp the next day after 5pm PT."""
    if moment is None:
        moment = datetime.now(_LA)
    elif moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(_LA).date().isoformat()


def fetch_url(url: str, opener: Callable[..., Any] | None = None) -> dict[str, Any]:
    """Fetch one URL with urllib. Incomplete or failed fetches are not OBSERVED.

    ``opener`` is injectable so tests do not touch the network. A body over
    ``MAX_BODY_BYTES`` is rejected whole — the partial bytes are not kept.
    """
    if not isinstance(url, str) or not url.startswith(("http://", "https://")):
        return {"url": url, "complete": False, "reason": "unsupported_scheme"}
    open_fn = opener or urllib.request.urlopen
    try:
        req = urllib.request.Request(
            url,
            method="GET",
            headers={"User-Agent": RESEARCH_UA},
        )
        with open_fn(req, timeout=10) as resp:
            raw = resp.read(MAX_BODY_BYTES + 1)
            final = resp.geturl() if hasattr(resp, "geturl") else url
    except Exception as exc:  # noqa: BLE001 — fail closed, keep no body
        return {
            "url": url,
            "complete": False,
            "reason": "fetch_failed",
            "error_type": type(exc).__name__,
        }
    final_url = str(final)
    if not final_url.startswith(("http://", "https://")):
        return {"url": url, "complete": False, "reason": "unsupported_scheme"}
    if len(raw) > MAX_BODY_BYTES:
        return {
            "url": final_url,
            "retrieved_at": _today(),
            "complete": False,
            "reason": "body_cap",
        }
    return {
        "url": final_url,
        "retrieved_at": _today(),
        "complete": True,
        "text": raw.decode("utf-8", errors="replace"),
        "kind": classify_url(final_url),
    }


class StdlibHttpAdapter:
    """Opt-in HTTP adapter. URLs only — non-URL queries are not searched."""

    name = "stdlib_http"

    def __init__(self, opener: Callable[..., Any] | None = None) -> None:
        self.opener = opener

    def gather(self, queries: list[str]) -> list[dict[str, Any]]:
        found: list[dict[str, Any]] = []
        for query in queries:
            if isinstance(query, str) and query.startswith(("http://", "https://")):
                found.append(fetch_url(query, opener=self.opener))
            else:
                found.append(
                    {
                        "query": query,
                        "complete": False,
                        "reason": "not_a_url",
                    }
                )
        return found


def get_adapter(name: str, **opts: Any) -> ResearchAdapter:
    key = (name or "null").strip().lower()
    if key in {"null", "offline", "none"}:
        return NullAdapter()
    if key == "fixture":
        items = opts.get("items") or []
        return FixtureAdapter(items if isinstance(items, list) else [])
    if key == "stdlib_http":
        return StdlibHttpAdapter(opener=opts.get("opener"))
    if key in {"robots_http", "robots", "free_http"}:
        return RobotsHttpAdapter(
            opener=opts.get("opener"),
            user_agent=str(opts.get("user_agent") or RESEARCH_UA),
        )
    if key in _PAID_ADAPTERS:
        raise KeyError("paid research adapter is opt-in and not bundled")
    raise KeyError(f"unknown research adapter: {name}")


def robots_allows(body: str, user_agent: str, path: str) -> bool:
    """Honor Allow/Disallow. An empty body allows. The longest matching rule wins."""
    if body == "":
        return True
    groups: list[tuple[list[str], list[tuple[str, str]]]] = []
    agents: list[str] = []
    rules: list[tuple[str, str]] = []

    def flush() -> None:
        nonlocal agents, rules
        if agents:
            groups.append((agents, rules))
        agents, rules = [], []

    for raw in body.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip()
        if key == "user-agent":
            if rules:
                flush()
            agents.append(value.lower())
        elif key in {"allow", "disallow"}:
            rules.append((key, value))
    flush()
    ua = user_agent.lower()
    specific = [
        group_rules
        for group_agents, group_rules in groups
        if any(agent != "*" and ua.startswith(agent) for agent in group_agents)
    ]
    chosen = specific[0] if specific else None
    if chosen is None:
        starred = [group_rules for group_agents, group_rules in groups if "*" in group_agents]
        chosen = starred[0] if starred else []
    best: tuple[int, bool] | None = None
    target = path or "/"
    for directive, rule_path in chosen:
        if rule_path == "":
            continue
        if target.startswith(rule_path):
            allow = directive == "allow"
            length = len(rule_path)
            if best is None or length > best[0] or (length == best[0] and allow):
                best = (length, allow)
    if best is None:
        return True
    return best[1]


def _origin(url: str) -> str:
    parts = urllib.parse.urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}"


def _path(url: str) -> str:
    path = urllib.parse.urlsplit(url).path or "/"
    return path


def _read_limited(resp: Any) -> tuple[int, bytes]:
    status = getattr(resp, "status", None)
    if status is None:
        status = getattr(resp, "code", 200)
    raw = resp.read(MAX_BODY_BYTES + 1)
    return int(status or 200), raw


class RobotsHttpAdapter:
    """Free stdlib fetch that honors robots.txt. No third-party crawler and no paid API.

    Crawl4AI is not a dependency. Tests inject ``opener``. A missing robots.txt
    (HTTP 404, including ``urllib.error.HTTPError``) allows the fetch. Any other
    robots failure fails closed and does not fetch the page. Page bodies over
    ``MAX_BODY_BYTES`` (2 MiB) are rejected whole. ``retrieved_at`` is the
    America/Los_Angeles calendar date.
    """

    name = "robots_http"

    def __init__(
        self,
        opener: Callable[..., Any] | None = None,
        user_agent: str = RESEARCH_UA,
    ) -> None:
        self.opener = opener
        self.user_agent = user_agent

    def gather(self, queries: list[str]) -> list[dict[str, Any]]:
        found: list[dict[str, Any]] = []
        for query in queries:
            if not isinstance(query, str) or not query.startswith(("http://", "https://")):
                found.append({"query": query, "complete": False, "reason": "not_a_url"})
                continue
            allowed, reason = self._allowed(query)
            if not allowed:
                found.append(
                    {
                        "url": query,
                        "complete": False,
                        "reason": reason,
                        "query": query,
                    }
                )
                continue
            found.append(fetch_url(query, opener=self.opener))
        return found

    def _allowed(self, url: str) -> tuple[bool, str]:
        robots_url = _origin(url) + "/robots.txt"
        open_fn = self.opener or urllib.request.urlopen
        try:
            req = urllib.request.Request(
                robots_url,
                method="GET",
                headers={"User-Agent": self.user_agent},
            )
            with open_fn(req, timeout=10) as resp:
                status, raw = _read_limited(resp)
        except urllib.error.HTTPError as exc:
            if getattr(exc, "code", None) == 404:
                return True, ""
            return False, "robots_unavailable"
        except Exception:
            return False, "robots_unavailable"
        if status == 404:
            return True, ""
        if status >= 400:
            return False, "robots_unavailable"
        if len(raw) > MAX_BODY_BYTES:
            return False, "robots_unavailable"
        body = raw.decode("utf-8", errors="replace")
        if robots_allows(body, self.user_agent, _path(url)):
            return True, ""
        return False, "robots_disallow"


def label_item(item: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    """Return an OBSERVED claim, or (None, reason). Never invents a label."""
    if item.get("complete") is False:
        return None, str(item.get("reason") or "incomplete_source")
    url = item.get("url")
    if not isinstance(url, str) or not url.startswith(("http://", "https://")):
        return None, "missing_url"
    retrieved = item.get("retrieved_at")
    if not isinstance(retrieved, str) or not _DATE.fullmatch(retrieved):
        return None, "missing_retrieved_at"
    if retrieved.strip().lower() in _PLACEHOLDER_DATES or _PLACEHOLDER_WORD.search(retrieved):
        return None, "placeholder_date"
    text = item.get("text")
    if text is None:
        text = item.get("excerpt")
    if not isinstance(text, str) or not text.strip():
        return None, "empty_text"
    source = item.get("source_text")
    if isinstance(source, str) and text not in source:
        return None, "text_not_in_source"
    if not privacy_preflight.preflight(text)["safe_for_egress"]:
        return None, "secret_like_body"
    kind = item.get("kind")
    if kind not in _KINDS:
        kind = classify_url(url)
    return {
        "text": text,
        "label": "OBSERVED",
        "url": url,
        "retrieved_at": retrieved,
        "kind": kind,
    }, None


def _empty_research() -> dict[str, Any]:
    return {
        "enabled": False,
        "offline": True,
        "adapter": "null",
        "research_ran": False,
        "items": [],
        "observed_claims": [],
        "rejected": [],
    }


def _index_item(item: dict[str, Any]) -> dict[str, Any]:
    kept: dict[str, Any] = {}
    for key in ("url", "retrieved_at", "kind", "complete", "reason", "title", "query"):
        if key in item:
            kept[key] = item[key]
    return kept


def run_research(
    policy: dict[str, Any] | None,
    queries: list[str] | None = None,
    adapter: ResearchAdapter | None = None,
) -> dict[str, Any]:
    """Gather sources. Offline / disabled skips the adapter entirely."""
    policy = policy or {}
    queries = [q for q in (queries or []) if isinstance(q, str)]
    enabled = policy.get("enabled") is True
    offline = policy.get("offline") is True or not enabled
    if offline:
        return _empty_research()
    requested = str(policy.get("adapter") or "null").strip().lower()
    if requested in _PAID_ADAPTERS:
        rejected_reason = (
            "paid_adapter_not_bundled"
            if policy.get("allow_paid") is True
            else "paid_adapter_opt_in"
        )
        empty = _empty_research()
        empty["enabled"] = True
        empty["offline"] = False
        empty["adapter"] = requested
        empty["rejected"] = [{"reason": rejected_reason, "url": None}]
        return empty
    if adapter is None:
        options = policy.get("adapter_options")
        if not isinstance(options, dict):
            options = {}
        adapter = get_adapter(requested, **options)
    raw = adapter.gather(queries)
    observed: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    items: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            rejected.append({"reason": "not_an_object", "url": None})
            continue
        items.append(_index_item(item))
        claim, reason = label_item(item)
        if claim is None:
            rejected.append({"reason": reason, "url": item.get("url")})
            continue
        claim["claim_id"] = f"obs-{len(observed) + 1}"
        observed.append(claim)
    return {
        "enabled": True,
        "offline": False,
        "adapter": str(getattr(adapter, "name", "custom")),
        "research_ran": True,
        "items": items,
        "observed_claims": observed,
        "rejected": rejected,
    }


class ResearchLedger:
    """Run-level dollar cap shared across ideas. Fail closed before a call."""

    def __init__(self, run_cap: float = DEFAULT_DOLLAR_CAP_PER_RUN) -> None:
        self.run_cap = float(run_cap)
        self.spent = 0.0

    def allows(self, price: float) -> bool:
        return self.spent + float(price) <= self.run_cap + 1e-9

    def commit(self, price: float) -> None:
        self.spent += float(price)

    def release(self, price: float) -> None:
        self.spent = max(0.0, self.spent - float(price))


def _firecrawl_key() -> str:
    return os.environ.get(FIRECRAWL_KEY_ENV, "").strip()


def _paid_ready(policy: dict[str, Any]) -> tuple[bool, str]:
    """Paid search stays off unless the flag is on and Firecrawl or a test provider is set.

    ``NEON_GENIE_SEARCH_API_KEY`` alone does not enable a provider. Firecrawl
    runs only when ``FIRECRAWL_API_KEY`` is set as well as the flag.
    """
    flagged = policy.get("allow_paid") is True or os.environ.get(PAID_FLAG_ENV) == "1"
    if not flagged:
        return False, "paid_off"
    if policy.get("search_provider") is not None:
        return True, ""
    if _firecrawl_key():
        return True, ""
    return False, "no_key"


def _positive_float(value: Any, default: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    if number <= 0:
        return default
    return number


def build_firecrawl_provider(policy: dict[str, Any]) -> firecrawl_client.FirecrawlClient:
    """Build the bundled client from the env key. Tests pass ``firecrawl_transport``."""
    scrape = policy.get("firecrawl_scrape")
    if scrape is None:
        scrape = os.environ.get(firecrawl_client.SCRAPE_FLAG_ENV) == "1"
    if "firecrawl_dollars_per_credit" in policy:
        rate = policy.get("firecrawl_dollars_per_credit")
    else:
        rate = os.environ.get(firecrawl_client.DOLLARS_PER_CREDIT_ENV, "").strip() or None
    if rate in (None, ""):
        dollars = firecrawl_client.DOLLARS_PER_CREDIT
    else:
        dollars = _positive_float(rate, firecrawl_client.DOLLARS_PER_CREDIT)
    try:
        limit = int(policy.get("firecrawl_limit", firecrawl_client.DEFAULT_LIMIT))
    except (TypeError, ValueError):
        limit = firecrawl_client.DEFAULT_LIMIT
    sleep = policy.get("firecrawl_sleep")
    return firecrawl_client.FirecrawlClient(
        api_key=_firecrawl_key(),
        base_url=str(policy.get("firecrawl_base_url") or firecrawl_client.DEFAULT_API_BASE),
        scrape=bool(scrape),
        limit=int(limit),
        dollars_per_credit=dollars,
        transport=policy.get("firecrawl_transport"),
        sleep=sleep if callable(sleep) else None,
        user_agent=RESEARCH_UA,
        timeout=_positive_float(
            policy.get("firecrawl_timeout"), firecrawl_client.DEFAULT_TIMEOUT_S
        ),
    )


def _can_search(adapter: ResearchAdapter) -> bool:
    return getattr(adapter, "name", "") not in {"robots_http", "stdlib_http", "null"}


def _not_fetched(query: str, reason: str) -> dict[str, Any]:
    return {"query": query, "status": "NOT_FETCHED", "reason": reason}


def run_idea_research(
    policy: dict[str, Any] | None,
    queries: list[str] | None = None,
    adapter: ResearchAdapter | None = None,
    ledger: ResearchLedger | None = None,
) -> dict[str, Any]:
    """Capped research for one idea.

    Free fetches run first and can be OBSERVED. Firecrawl search runs only when
    ``NEON_GENIE_RESEARCH_PAID=1`` (or ``allow_paid``) and ``FIRECRAWL_API_KEY``
    are both set, or a test injects ``search_provider``. Search hits are
    ``NOT_COMPUTABLE`` and are not OBSERVED. Over the call cap, the per-idea
    dollar cap, or the run cap, the query is ``NOT_FETCHED`` and the provider
    is not called. No URL is invented. Offline and disabled runs do not call
    an adapter.
    """
    policy = dict(policy or {})
    queries = [q for q in (queries or []) if isinstance(q, str)]
    enabled = policy.get("enabled") is True
    offline = policy.get("offline") is True or not enabled
    if offline:
        return _empty_research()

    max_calls = int(policy.get("max_calls_per_idea") or DEFAULT_MAX_CALLS_PER_IDEA)
    dollar_cap = float(policy.get("dollar_cap_per_idea") or DEFAULT_DOLLAR_CAP_PER_IDEA)
    run_cap = float(policy.get("dollar_cap_per_run") or DEFAULT_DOLLAR_CAP_PER_RUN)
    if ledger is None:
        ledger = ResearchLedger(run_cap)

    requested = str(policy.get("adapter") or "null").strip().lower()
    options = policy.get("adapter_options")
    if not isinstance(options, dict):
        options = {}
    free_adapter = adapter
    if free_adapter is None and requested not in _PAID_ADAPTERS and requested != "paid_search":
        try:
            free_adapter = get_adapter(requested, **options)
        except KeyError:
            free_adapter = None
    url_queries = [query for query in queries if query.startswith(("http://", "https://"))]
    if url_queries and (free_adapter is None or not _can_search(free_adapter)):
        if free_adapter is None or getattr(free_adapter, "name", "") in _PAID_ADAPTERS:
            free_adapter = RobotsHttpAdapter(opener=options.get("opener"))

    allowed: list[str] = []
    skipped: list[dict[str, Any]] = []
    calls = 0
    spent = 0.0
    paid_ok, paid_reason = _paid_ready(policy)
    provider = policy.get("search_provider") if paid_ok else None
    if provider is None and paid_ok and _firecrawl_key():
        try:
            provider = build_firecrawl_provider(policy)
        except firecrawl_client.FirecrawlError as exc:
            provider = None
            paid_reason = exc.reason
    if "paid_price_per_call" in policy:
        paid_price = float(policy["paid_price_per_call"])
    else:
        quoted = getattr(provider, "price_per_call", None) if provider is not None else None
        paid_price = float(quoted) if isinstance(quoted, (int, float)) and float(quoted) > 0 else DEFAULT_PAID_PRICE

    def room(price: float) -> bool:
        if calls >= max_calls:
            return False
        if spent + price > dollar_cap + 1e-9:
            return False
        return ledger.allows(price)

    for query in queries:
        is_url = query.startswith(("http://", "https://"))
        use_free = free_adapter is not None and (is_url or _can_search(free_adapter))
        price = 0.0 if use_free else paid_price
        if use_free or provider is not None:
            if not room(price):
                skipped.append(_not_fetched(query, "over_cap"))
                continue
            allowed.append(query)
            calls += 1
            spent += price
            ledger.commit(price)
            continue
        reason = paid_reason or "no_key"
        if not is_url:
            skipped.append(_not_fetched(query, reason))
            continue
        skipped.append(_not_fetched(query, "over_cap" if calls >= max_calls else reason))

    if free_adapter is not None and allowed:
        free_queries = [
            query
            for query in allowed
            if query.startswith(("http://", "https://")) or _can_search(free_adapter)
        ]
        paid_queries = [query for query in allowed if query not in free_queries]
        result = run_research(policy, free_queries, adapter=free_adapter)
    else:
        paid_queries = list(allowed)
        result = _empty_research()
        result["enabled"] = True
        result["offline"] = False
        result["adapter"] = requested or "null"
        result["research_ran"] = False

    if provider is not None and paid_queries:
        search = getattr(provider, "search", None)
        observed = list(result.get("observed_claims") or [])
        rejected = list(result.get("rejected") or [])
        items = list(result.get("items") or [])
        unverified_hits = [
            row
            for row in (result.get("unverified_hits") or [])
            if isinstance(row, dict)
        ]
        if callable(search):
            for query in paid_queries:
                if spent > dollar_cap + 1e-9 or ledger.spent > ledger.run_cap + 1e-9:
                    spent -= paid_price
                    ledger.release(paid_price)
                    calls -= 1
                    skipped.append(_not_fetched(query, "over_cap"))
                    continue
                try:
                    rows = search(query)
                except firecrawl_client.FirecrawlError as exc:
                    skipped.append(_not_fetched(query, exc.reason))
                    continue
                except Exception:  # noqa: BLE001 — fail closed, invent nothing
                    rejected.append({"reason": "search_failed", "url": None, "query": query})
                    continue
                if not isinstance(rows, list):
                    rejected.append({"reason": "search_failed", "url": None, "query": query})
                    continue
                actual = getattr(provider, "last_price", None)
                if isinstance(actual, (int, float)) and float(actual) > paid_price:
                    extra = float(actual) - paid_price
                    spent += extra
                    ledger.commit(extra)
                if not rows and getattr(provider, "name", "") == "firecrawl":
                    skipped.append(_not_fetched(query, "empty"))
                    continue
                for row in rows:
                    if not isinstance(row, dict):
                        rejected.append({"reason": "not_an_object", "url": None})
                        continue
                    item = dict(row)
                    item.setdefault("query", query)
                    if "retrieved_at" not in item:
                        item["retrieved_at"] = _today()
                    items.append(_index_item(item))
                    claim, reason = label_item(item)
                    if claim is None:
                        rejected.append({"reason": reason, "url": item.get("url"), "query": query})
                        continue
                    blocked = search_hit_block(
                        str(claim.get("url") or ""), str(claim.get("text") or "")
                    )
                    unverified_hits.append(
                        {
                            "url": claim.get("url"),
                            "text": claim.get("text"),
                            "retrieved_at": claim.get("retrieved_at"),
                            "kind": claim.get("kind"),
                            "reason": blocked or "unreviewed",
                            "status": "unreviewed",
                            "claim_label": "NOT_COMPUTABLE",
                            "query": query,
                        }
                    )
                    continue
            result["observed_claims"] = observed
            result["rejected"] = rejected
            result["items"] = items
            if unverified_hits:
                result["unverified_hits"] = unverified_hits
            result["research_ran"] = True
            result["adapter"] = str(getattr(provider, "name", "paid_search"))
            result["enabled"] = True
            result["offline"] = False

    if skipped:
        result["not_fetched"] = skipped
        caps: dict[str, Any] = {
            "max_calls_per_idea": max_calls,
            "dollar_cap_per_idea": dollar_cap,
            "dollar_cap_per_run": ledger.run_cap,
            "calls_used": calls,
            "dollars_used": round(spent, 4),
        }
        credits = getattr(provider, "credits_per_call", None) if provider is not None else None
        rate = getattr(provider, "dollars_per_credit", None) if provider is not None else None
        if isinstance(credits, int) and isinstance(rate, (int, float)):
            caps["credits_per_call"] = credits
            caps["dollars_per_credit"] = rate
            caps["paid_price_per_call"] = round(paid_price, 6)
        result["caps"] = caps
    return result


def research_search_dag(
    queries: list[str], claims: list[dict[str, Any]]
) -> dict[str, Any]:
    """PaperPilot DAG for a run that actually gathered. Cites only fetched URLs."""
    kinds = ("keyword", "cite-expand", "filter", "score", "extract")
    stages: list[dict[str, Any]] = []
    for index, kind in enumerate(kinds, start=1):
        stage: dict[str, Any] = {"stage_id": f"s{index}", "kind": kind}
        if kind == "keyword":
            stage["queries"] = list(queries)
        else:
            stage["inputs"] = [f"s{index - 1}"]
        if kind == "extract":
            stage["citations"] = [
                {
                    "id": claim["url"],
                    "verified_fetch": True,
                    "operator_supplied": False,
                }
                for claim in claims
                if isinstance(claim, dict) and isinstance(claim.get("url"), str)
            ]
        stages.append(stage)
    return {
        "schema_id": "neon-genie/research-search-dag",
        "schema_version": "1.0.0",
        "research_ran": True,
        "stages": stages,
        "edges": [
            {"from_stage": f"s{index}", "to_stage": f"s{index + 1}"}
            for index in range(1, 5)
        ],
        "notes": "Citations are fetched URLs only. No generated paper ids.",
    }
