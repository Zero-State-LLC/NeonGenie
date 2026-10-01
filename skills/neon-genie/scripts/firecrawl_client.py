#!/usr/bin/env python3
"""Firecrawl /search client for the capped research step. Stdlib only.

The client does not open a socket when a transport is injected. CI tests
inject one. A missing key is handled by ``research_mode`` before this
client is built, so an unset key never reaches the network.

Credit model (docs.firecrawl.dev/billing, read 2026-10-01):

- Search costs 2 credits per 10 results, rounded up.
- Optional markdown scrape adds the scrape rate: 1 credit per result.
- ``DOLLARS_PER_CREDIT`` converts credits into the dollar caps. The
  default is the dearest published self-serve pay-as-you-go rate:
  Hobby, 1,000 credits per 5 USD = 0.005 USD per credit. Standard is
  2,000 per 5 USD, Growth 2,500, Scale 5,000. Using the Hobby rate
  overestimates cheaper plans, so a call that would exceed $0.20 per
  idea or $1.00 per run is skipped before it is sent.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any, Callable

import privacy_preflight

FIRECRAWL_KEY_ENV = "FIRECRAWL_API_KEY"
SCRAPE_FLAG_ENV = "NEON_GENIE_FIRECRAWL_SCRAPE"
DOLLARS_PER_CREDIT_ENV = "NEON_GENIE_FIRECRAWL_DOLLARS_PER_CREDIT"
DEFAULT_API_BASE = "https://api.firecrawl.dev/v2"
# Hobby pay-as-you-go: 1,000 credits / 5 USD. Config value, not a quote.
DOLLARS_PER_CREDIT = 0.005
SEARCH_CREDITS_PER_TEN = 2
SCRAPE_CREDITS_PER_PAGE = 1
DEFAULT_LIMIT = 5
DEFAULT_TIMEOUT_S = 20.0
RETRY_BACKOFF_S = 0.5
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
_ALLOWED_HOST = "api.firecrawl.dev"


class FirecrawlError(Exception):
    """A search that produced no citable source. ``reason`` is not a URL."""

    def __init__(self, reason: str, status: int | None = None) -> None:
        super().__init__(reason)
        self.reason = reason
        self.status = status


def estimated_credits(limit: int, scrape: bool) -> int:
    """Credits reserved before the call. Search rounds up per 10 results."""
    count = max(1, min(int(limit), 100))
    search = SEARCH_CREDITS_PER_TEN * ((count + 9) // 10)
    extra = count * SCRAPE_CREDITS_PER_PAGE if scrape else 0
    return search + extra


def estimated_dollars(
    limit: int,
    scrape: bool,
    dollars_per_credit: float = DOLLARS_PER_CREDIT,
) -> float:
    return estimated_credits(limit, scrape) * float(dollars_per_credit)


def _allowed_base(url: str) -> str:
    """Only the official Firecrawl host receives the API key."""
    parts = urllib.parse.urlsplit(url.strip())
    if parts.scheme != "https" or parts.hostname != _ALLOWED_HOST:
        raise FirecrawlError("bad_base_url")
    path = parts.path.rstrip("/")
    if path not in {"", "/v1", "/v2"}:
        raise FirecrawlError("bad_base_url")
    return f"https://{_ALLOWED_HOST}{path or '/v2'}"


def extract_hits(payload: Any) -> tuple[list[Any], int | None]:
    """Accept v2 ``data.web`` and v1 ``data`` lists. Invent no hits."""
    if not isinstance(payload, dict):
        raise FirecrawlError("bad_response")
    if payload.get("success") is False:
        raise FirecrawlError("search_failed")
    credits = payload.get("creditsUsed")
    if isinstance(credits, bool) or not isinstance(credits, int) or credits < 0:
        credits = None
    data = payload.get("data")
    if data is None:
        return [], credits
    if isinstance(data, list):
        return data, credits
    if isinstance(data, dict):
        web = data.get("web")
        if web is None:
            return [], credits
        if isinstance(web, list):
            return web, credits
    raise FirecrawlError("bad_response")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
        raise urllib.error.HTTPError(req.full_url, code, msg, headers, fp)


def _read_limited(source: Any) -> bytes:
    raw = source.read(MAX_RESPONSE_BYTES + 1)
    if not isinstance(raw, (bytes, bytearray)):
        return b""
    return bytes(raw)


def urllib_post(req: urllib.request.Request, timeout: float) -> tuple[int, bytes]:
    """One POST. Redirects are not followed, so the key stays on this host."""
    opener = urllib.request.build_opener(_NoRedirect)
    try:
        with opener.open(req, timeout=timeout) as resp:
            status = getattr(resp, "status", None) or getattr(resp, "code", 200)
            return int(status or 200), _read_limited(resp)
    except urllib.error.HTTPError as exc:
        raw = b""
        if exc.fp is not None:
            raw = _read_limited(exc.fp)
        return int(exc.code), raw


def _is_timeout(exc: BaseException) -> bool:
    if isinstance(exc, TimeoutError):
        return True
    reason = getattr(exc, "reason", None)
    if isinstance(reason, TimeoutError):
        return True
    return "timed out" in str(exc).lower()


class FirecrawlClient:
    """POST /search. ``name`` is the research adapter id."""

    name = "firecrawl"

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_API_BASE,
        scrape: bool = False,
        limit: int = DEFAULT_LIMIT,
        dollars_per_credit: float = DOLLARS_PER_CREDIT,
        transport: Callable[..., Any] | None = None,
        sleep: Callable[[float], None] | None = None,
        user_agent: str = "neon-genie-research",
        timeout: float = DEFAULT_TIMEOUT_S,
        backoff: float = RETRY_BACKOFF_S,
    ) -> None:
        self.api_key = api_key
        self.base_url = _allowed_base(base_url)
        self.scrape = bool(scrape)
        self.limit = max(1, min(int(limit), 100))
        rate = float(dollars_per_credit)
        self.dollars_per_credit = rate if rate > 0 else DOLLARS_PER_CREDIT
        self.transport = transport
        self.sleep = sleep or time.sleep
        self.user_agent = user_agent
        self.timeout = timeout
        self.backoff = backoff
        self.last_credits_used: int | None = None
        self.last_price = self.price_per_call

    def __repr__(self) -> str:
        return (
            f"FirecrawlClient(base_url={self.base_url!r}, limit={self.limit}, "
            f"scrape={self.scrape})"
        )

    @property
    def credits_per_call(self) -> int:
        return estimated_credits(self.limit, self.scrape)

    @property
    def price_per_call(self) -> float:
        return estimated_dollars(self.limit, self.scrape, self.dollars_per_credit)

    def search(self, query: str) -> list[dict[str, Any]]:
        """Return source rows. Raise ``FirecrawlError`` instead of inventing one."""
        self.last_credits_used = None
        self.last_price = self.price_per_call
        if not isinstance(query, str) or not query.strip():
            raise FirecrawlError("empty_query")
        if len(query) > 500:
            raise FirecrawlError("query_too_long")
        if not privacy_preflight.preflight(query)["safe_for_egress"]:
            raise FirecrawlError("secret_like_query")
        body: dict[str, Any] = {"query": query, "limit": self.limit}
        if self.scrape:
            formats: Any = (
                [{"type": "markdown"}] if self.base_url.endswith("/v2") else ["markdown"]
            )
            body["scrapeOptions"] = {"formats": formats, "onlyMainContent": True}
        status, raw = self._call(body)
        if status == 408:
            raise FirecrawlError("timeout", status)
        if status >= 400:
            raise FirecrawlError(f"http_{status}", status)
        if len(raw) > MAX_RESPONSE_BYTES:
            raise FirecrawlError("body_cap")
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise FirecrawlError("bad_response") from exc
        hits, credits = extract_hits(payload)
        if credits is not None:
            self.last_credits_used = credits
            actual = credits * self.dollars_per_credit
            if actual > self.last_price:
                self.last_price = actual
        return _rows_from_hits(hits, query)

    def _call(self, body: dict[str, Any]) -> tuple[int, bytes]:
        payload = json.dumps(body).encode("utf-8")
        url = self.base_url + "/search"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }
        attempts = 0
        while True:
            try:
                status, raw = self._once(url, headers, payload)
            except FirecrawlError:
                raise
            except urllib.error.HTTPError as exc:
                status = int(exc.code)
                raw = b""
                if exc.fp is not None:
                    raw = _read_limited(exc.fp)
            except (TimeoutError, urllib.error.URLError, OSError) as exc:
                if _is_timeout(exc):
                    raise FirecrawlError("timeout") from exc
                raise FirecrawlError("http_error") from exc
            if status == 408:
                raise FirecrawlError("timeout", status)
            if status == 429 or 500 <= status <= 599:
                if attempts < 1:
                    attempts += 1
                    self.sleep(self.backoff)
                    continue
                raise FirecrawlError(f"http_{status}", status)
            return status, raw

    def _once(self, url: str, headers: dict[str, str], payload: bytes) -> tuple[int, bytes]:
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        transport = self.transport or urllib_post
        result = transport(req, self.timeout)
        if isinstance(result, tuple) and len(result) == 2:
            status, raw = result
            if isinstance(raw, str):
                raw = raw.encode("utf-8")
            if not isinstance(raw, (bytes, bytearray)):
                raw = b""
            return int(status), bytes(raw)
        status = getattr(result, "status", None) or getattr(result, "code", 200)
        return int(status or 200), _read_limited(result)


def _rows_from_hits(hits: list[Any], query: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for hit in hits:
        if not isinstance(hit, dict):
            continue
        url = hit.get("url")
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            continue
        text = hit.get("markdown")
        if not isinstance(text, str) or not text.strip():
            text = hit.get("description")
        if not isinstance(text, str) or not text.strip():
            text = hit.get("snippet")
        if not isinstance(text, str) or not text.strip():
            continue
        text = text.strip()
        if len(text.encode("utf-8")) > MAX_RESPONSE_BYTES:
            continue
        if not privacy_preflight.preflight(text)["safe_for_egress"]:
            continue
        row: dict[str, Any] = {
            "url": url,
            "text": text,
            "complete": True,
            "query": query,
        }
        title = hit.get("title")
        if isinstance(title, str) and title.strip():
            row["title"] = title.strip()
        rows.append(row)
    return rows
