#!/usr/bin/env python3
"""Firecrawl paid search. Stdlib only. The transport is injected. No live calls."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

import firecrawl_client
import research_mode

_ENV_KEYS = (
    research_mode.PAID_KEY_ENV,
    research_mode.PAID_FLAG_ENV,
    research_mode.FIRECRAWL_KEY_ENV,
    firecrawl_client.SCRAPE_FLAG_ENV,
    firecrawl_client.DOLLARS_PER_CREDIT_ENV,
)
_KEY = "test-firecrawl-key"
_CITE = (
    "Vendor pricing documentation lists the published monthly price, "
    "the included quota, and the plan name on this official pricing page."
)


class _Transport:
    def __init__(self, responses: list[object]) -> None:
        self.responses = list(responses)
        self.calls: list[str] = []
        self.bodies: list[dict] = []
        self.headers: list[str] = []

    def __call__(self, req: urllib.request.Request, timeout: float) -> tuple[int, bytes]:
        self.calls.append(req.full_url)
        self.headers.append(str(req.get_header("Authorization")))
        raw = req.data.decode("utf-8") if isinstance(req.data, bytes) else "{}"
        self.bodies.append(json.loads(raw))
        if not self.responses:
            raise AssertionError("unexpected Firecrawl call")
        item = self.responses.pop(0)
        if isinstance(item, BaseException):
            raise item
        status, body = item  # type: ignore[misc]
        if isinstance(body, str):
            body = body.encode("utf-8")
        return int(status), body


class _Page:
    def __init__(self, body: bytes, url: str, status: int = 200) -> None:
        self._body = body
        self._url = url
        self.status = status

    def read(self, n: int = -1) -> bytes:
        if n < 0 or n >= len(self._body):
            return self._body
        return self._body[:n]

    def geturl(self) -> str:
        return self._url

    def __enter__(self) -> _Page:
        return self

    def __exit__(self, *_exc: object) -> bool:
        return False


def _forbid_live(req: urllib.request.Request, timeout: float) -> tuple[int, bytes]:
    raise AssertionError(f"live Firecrawl call: {req.full_url}")


def _quiet() -> dict[str, str | None]:
    saved = {key: os.environ.get(key) for key in _ENV_KEYS}
    for key in _ENV_KEYS:
        os.environ.pop(key, None)
    return saved


def _restore(saved: dict[str, str | None]) -> None:
    for key, value in saved.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


def _web(url: str, markdown: str | None, description: str = "snippet") -> dict:
    hit: dict = {"url": url, "title": "Pricing", "description": description}
    if markdown is not None:
        hit["markdown"] = markdown
    return hit


def _payload(hits: list[dict], *, credits: int = 2, v1: bool = False) -> tuple[int, bytes]:
    data: object = hits if v1 else {"web": hits}
    body = {"success": True, "creditsUsed": credits, "data": data}
    return 200, json.dumps(body).encode("utf-8")


def _policy(transport: _Transport, **extra: object) -> dict:
    os.environ[research_mode.FIRECRAWL_KEY_ENV] = _KEY
    policy: dict = {
        "enabled": True,
        "offline": False,
        "adapter": "null",
        "allow_paid": True,
        "firecrawl_transport": transport,
        "firecrawl_sleep": extra.pop("sleep", lambda _seconds: None),
    }
    policy.update(extra)
    return policy


def _run(transport: _Transport, queries: list[str], **extra: object) -> dict:
    return research_mode.run_idea_research(_policy(transport, **extra), queries)


def test_success_cites_markdown_and_pt_date() -> None:
    transport = _Transport([
        _payload([_web("https://example.test/pricing", _CITE)]),
    ])
    result = _run(transport, ["official pricing"])
    assert transport.calls == ["https://api.firecrawl.dev/v2/search"]
    assert transport.headers == [f"Bearer {_KEY}"]
    assert "scrapeOptions" not in transport.bodies[0]
    assert len(result["observed_claims"]) == 1
    claim = result["observed_claims"][0]
    assert claim["label"] == "OBSERVED"
    assert claim["url"] == "https://example.test/pricing"
    assert claim["text"] == _CITE
    assert claim["retrieved_at"] == research_mode._today()
    assert _KEY not in json.dumps(result)
    print("success cites the returned markdown with a PT date")


def test_description_when_markdown_absent() -> None:
    transport = _Transport([
        _payload([_web("https://example.test/docs", None, _CITE)]),
    ])
    result = _run(transport, ["floor price"])
    assert result["observed_claims"][0]["text"] == _CITE
    print("description is the citation when markdown is absent")


def test_empty_invents_nothing() -> None:
    transport = _Transport([_payload([])])
    result = _run(transport, ["missing topic"])
    assert transport.calls
    assert result["observed_claims"] == []
    assert result["not_fetched"][0]["status"] == "NOT_FETCHED"
    assert result["not_fetched"][0]["reason"] == "empty"
    assert "url" not in result["not_fetched"][0]
    print("empty search invents no URL")


def test_403_is_not_fetched_and_not_retried() -> None:
    sleeps: list[float] = []
    transport = _Transport([(403, b'{"error":"forbidden"}')])
    result = _run(transport, ["blocked page"], sleep=lambda seconds: sleeps.append(seconds))
    assert len(transport.calls) == 1
    assert sleeps == []
    assert result["observed_claims"] == []
    assert result["not_fetched"][0]["reason"] == "http_403"
    assert "url" not in result["not_fetched"][0]
    print("403 is NOT_FETCHED with no retry")


def test_429_retries_once_then_cites() -> None:
    sleeps: list[float] = []
    transport = _Transport([
        (429, b"{}"),
        _payload([_web("https://example.test/pricing/after-retry", _CITE)]),
    ])
    result = _run(transport, ["retry me"], sleep=lambda seconds: sleeps.append(seconds))
    assert len(transport.calls) == 2
    assert sleeps == [firecrawl_client.RETRY_BACKOFF_S]
    assert result["observed_claims"][0]["url"] == "https://example.test/pricing/after-retry"
    assert result["observed_claims"][0]["label"] == "OBSERVED"
    print("429 retries once")


def test_429_twice_stops() -> None:
    transport = _Transport([(429, b"{}"), (429, b"{}"), (200, b'{"success":true,"data":{"web":[]}}')])
    result = _run(transport, ["still limited"])
    assert len(transport.calls) == 2
    assert result["observed_claims"] == []
    assert result["not_fetched"][0]["reason"] == "http_429"
    print("a second 429 is NOT_FETCHED")


def test_5xx_retries_once_then_stops() -> None:
    transport = _Transport([(502, b"{}"), (503, b"{}")])
    result = _run(transport, ["down"])
    assert len(transport.calls) == 2
    assert result["not_fetched"][0]["reason"] == "http_503"
    print("5xx retries once")


def test_timeout_is_not_retried() -> None:
    transport = _Transport([TimeoutError("timed out"), _payload([])])
    result = _run(transport, ["slow host"])
    assert len(transport.calls) == 1
    assert result["not_fetched"][0]["reason"] == "timeout"
    assert result["observed_claims"] == []
    print("timeout is NOT_FETCHED with no retry")


def test_over_cap_does_not_call() -> None:
    transport = _Transport([_payload([_web("https://example.test/nope", "should not be fetched")])])
    result = _run(
        transport,
        ["too expensive", "also too expensive"],
        firecrawl_dollars_per_credit=1.0,
    )
    assert transport.calls == []
    assert result["observed_claims"] == []
    assert [row["reason"] for row in result["not_fetched"]] == ["over_cap", "over_cap"]
    assert result["caps"]["credits_per_call"] == 2
    assert result["caps"]["dollars_per_credit"] == 1.0
    assert result["caps"]["calls_used"] == 0
    print("over cap skips the call")


def test_actual_credits_fail_closed_for_the_next_query() -> None:
    transport = _Transport([
        _payload([_web("https://example.test/pricing/first", _CITE)], credits=80),
        _payload([_web("https://example.test/pricing/second", _CITE)]),
    ])
    result = _run(transport, ["one", "two"])
    assert len(transport.calls) == 1
    assert result["observed_claims"][0]["url"] == "https://example.test/pricing/first"
    assert result["not_fetched"][-1]["reason"] == "over_cap"
    assert not any(claim["url"].endswith("/second") for claim in result["observed_claims"])
    print("creditsUsed above the reservation blocks the next call")


def test_run_cap_blocks_the_next_idea() -> None:
    first = _Transport([_payload([_web("https://example.test/idea", "Idea one.")])])
    ledger = research_mode.ResearchLedger(0.01)
    os.environ[research_mode.FIRECRAWL_KEY_ENV] = _KEY
    research_mode.run_idea_research(
        {
            "enabled": True,
            "offline": False,
            "adapter": "null",
            "allow_paid": True,
            "firecrawl_transport": first,
            "dollar_cap_per_run": 0.01,
        },
        ["idea one"],
        ledger=ledger,
    )
    second = _Transport([_payload([_web("https://example.test/later", "nope")])])
    later = research_mode.run_idea_research(
        {
            "enabled": True,
            "offline": False,
            "adapter": "null",
            "allow_paid": True,
            "firecrawl_transport": second,
            "dollar_cap_per_idea": 0.20,
            "dollar_cap_per_run": 0.01,
        },
        ["idea two"],
        ledger=ledger,
    )
    assert len(first.calls) == 1
    assert second.calls == []
    assert later["not_fetched"][0]["reason"] == "over_cap"
    print("run cap blocks the next idea")


def test_flag_and_key_gate() -> None:
    transport = _Transport([_payload([_web("https://example.test/x", "body")])])
    os.environ[research_mode.FIRECRAWL_KEY_ENV] = _KEY
    off = research_mode.run_idea_research(
        {
            "enabled": True,
            "offline": False,
            "adapter": "null",
            "firecrawl_transport": transport,
        },
        ["needs a flag"],
    )
    assert transport.calls == []
    assert off["not_fetched"][0]["reason"] == "paid_off"

    os.environ.pop(research_mode.FIRECRAWL_KEY_ENV, None)
    os.environ[research_mode.PAID_KEY_ENV] = _KEY
    legacy = research_mode.run_idea_research(
        {"enabled": True, "offline": False, "adapter": "null", "allow_paid": True},
        ["legacy key"],
    )
    assert legacy["not_fetched"][0]["reason"] == "no_key"
    os.environ.pop(research_mode.PAID_KEY_ENV, None)

    missing = research_mode.run_idea_research(
        {"enabled": True, "offline": False, "adapter": "null", "allow_paid": True},
        ["no key"],
    )
    assert missing["not_fetched"][0]["reason"] == "no_key"

    os.environ[research_mode.FIRECRAWL_KEY_ENV] = _KEY
    offline = research_mode.run_idea_research(
        {
            "enabled": False,
            "offline": True,
            "allow_paid": True,
            "firecrawl_transport": transport,
        },
        ["offline"],
    )
    assert transport.calls == []
    assert offline["observed_claims"] == []
    assert offline["research_ran"] is False
    print("flag and Firecrawl key are both required")


def test_free_fetch_runs_before_search() -> None:
    seen: list[str] = []

    def opener(req: object, timeout: int = 10) -> _Page:
        url = req.full_url if hasattr(req, "full_url") else req.get_full_url()  # type: ignore[attr-defined]
        seen.append(str(url))
        if str(url).endswith("/robots.txt"):
            return _Page(b"User-agent: *\nAllow: /\n", str(url))
        return _Page(b"Published list price is 12.", str(url))

    transport = _Transport([
        _payload([_web("https://example.test/docs/search-hit", _CITE)]),
    ])
    result = _run(
        transport,
        ["https://example.test/pricing", "competitor pricing"],
        adapter="robots_http",
        adapter_options={"opener": opener},
    )
    assert any(url.endswith("/pricing") for url in seen)
    assert len(transport.calls) == 1
    urls = [claim["url"] for claim in result["observed_claims"]]
    assert "https://example.test/pricing" in urls
    assert "https://example.test/docs/search-hit" in urls
    assert all(claim["label"] == "OBSERVED" for claim in result["observed_claims"])
    assert all(claim["retrieved_at"] == research_mode._today() for claim in result["observed_claims"])
    print("free robots fetch runs first; search cites only returned URLs")


def test_scrape_option_and_v1_body() -> None:
    transport = _Transport([
        _payload([_web("https://example.test/pricing/v1", _CITE)], v1=True),
    ])
    result = _run(
        transport,
        ["v1 query"],
        firecrawl_scrape=True,
        firecrawl_base_url="https://api.firecrawl.dev/v1",
    )
    assert transport.calls == ["https://api.firecrawl.dev/v1/search"]
    assert transport.bodies[0]["scrapeOptions"]["formats"] == ["markdown"]
    assert result["observed_claims"][0]["text"] == _CITE
    v2 = _Transport([_payload([_web("https://example.test/docs/v2", _CITE)])])
    scraped = _run(
        v2,
        ["v2 query", "held for the cap"],
        firecrawl_scrape=True,
        max_calls_per_idea=1,
    )
    assert v2.bodies[0]["scrapeOptions"]["formats"] == [{"type": "markdown"}]
    assert scraped["not_fetched"][0]["reason"] == "over_cap"
    assert scraped["caps"]["credits_per_call"] == 2 + 5
    assert abs(scraped["caps"]["paid_price_per_call"] - 0.035) < 1e-9
    print("scrape is optional; v1 and v2 bodies both parse")


def test_secret_query_is_not_sent() -> None:
    transport = _Transport([_payload([_web("https://example.test/secret", "nope")])])
    result = _run(transport, ["api_key=" + ("a" * 20)])
    assert transport.calls == []
    assert result["observed_claims"] == []
    assert result["not_fetched"][0]["reason"] == "secret_like_query"
    print("secret-like query is not sent")


def test_bad_host_is_not_called() -> None:
    transport = _Transport([_payload([])])
    result = _run(transport, ["elsewhere"], firecrawl_base_url="https://example.test")
    assert transport.calls == []
    assert result["not_fetched"][0]["reason"] == "bad_base_url"
    print("API key is not sent to another host")


def test_url_error_timeout_shape() -> None:
    transport = _Transport([urllib.error.URLError(TimeoutError("timed out"))])
    result = _run(transport, ["urlerror"])
    assert len(transport.calls) == 1
    assert result["not_fetched"][0]["reason"] == "timeout"
    print("URLError timeout is NOT_FETCHED")


def main() -> None:
    firecrawl_client.urllib_post = _forbid_live  # type: ignore[assignment]
    saved = _quiet()
    try:
        test_success_cites_markdown_and_pt_date()
        test_description_when_markdown_absent()
        test_empty_invents_nothing()
        test_403_is_not_fetched_and_not_retried()
        test_429_retries_once_then_cites()
        test_429_twice_stops()
        test_5xx_retries_once_then_stops()
        test_timeout_is_not_retried()
        test_over_cap_does_not_call()
        test_actual_credits_fail_closed_for_the_next_query()
        test_run_cap_blocks_the_next_idea()
        test_flag_and_key_gate()
        test_free_fetch_runs_before_search()
        test_scrape_option_and_v1_body()
        test_secret_query_is_not_sent()
        test_bad_host_is_not_called()
        test_url_error_timeout_shape()
    finally:
        _restore(saved)
    print("PASS: firecrawl research")


if __name__ == "__main__":
    main()
