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
import urllib.request
from datetime import datetime, timezone
from typing import Any, Callable, Protocol

import privacy_preflight

MAX_BODY_BYTES = 65536
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_KINDS = frozenset({"web_page", "paper", "social_post"})


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


def _today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


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
            headers={"User-Agent": "neon-genie-research/3.28"},
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
    raise KeyError(f"unknown research adapter: {name}")


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
    if adapter is None:
        options = policy.get("adapter_options")
        if not isinstance(options, dict):
            options = {}
        adapter = get_adapter(str(policy.get("adapter") or "null"), **options)
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
