#!/usr/bin/env python3
"""Optional evidence gathering before a packet is written.

Adapters are pluggable. The core stays on the standard library and can run
with no network. Offline and research-disabled runs do not call adapters and
do not emit OBSERVED claims.

A gathered item is OBSERVED only when it has an http(s) URL, a retrieval
date, and a complete source body. No source means no OBSERVED label.
"""

from __future__ import annotations

import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any, Callable, Protocol
from zoneinfo import ZoneInfo

import privacy_preflight

# Normal HTML pricing and docs pages exceeded 64 KiB in the round-3 probe
# (10 of 14). 2 MiB is still a hard cap: a larger body is rejected whole.
MAX_BODY_BYTES = 2 * 1024 * 1024
RESEARCH_UA = "neon-genie-research/3.30"
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
