#!/usr/bin/env python3
"""v3.31 bake-off fixes. Stdlib only. No network and no paid model calls.

Confirmed numeric mismatches stay on the main packet. Unconfirmed scanner
flags go to an unverified appendix. Research is capped and mocked. The
cheapest test is one dated yes/no action. The build handoff is unchanged.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import packet_compose
import research_mode

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "evals" / "fixtures" / "v331" / "regressions.json"
RAW = ROOT / "evals" / "bakeoff-v330" / "raw-notes"
FALSE_FLAG = "Double of 64 is 128, not 512"


def _notes(name: str) -> str:
    return (RAW / name).read_text(encoding="utf-8")


def _main_text(scanned: dict) -> str:
    packet = {"input_contradictions": {"checked": True, "findings": scanned["findings"]}}
    return packet_compose.prose_main(packet) + "\n" + "\n".join(
        row["summary"] for row in scanned["findings"]
    )


def test_false_double_stays_off_the_main_page() -> None:
    rows = json.loads(FIX.read_text(encoding="utf-8"))
    for text in (rows["false_double"], _notes("3-autogive-tenant-sku.md")):
        scanned = packet_compose.scan_input_notes(text)
        blob = _main_text(scanned)
        assert FALSE_FLAG not in blob
        unverified = "\n".join(row["summary"] for row in scanned["unverified_notes"])
        assert FALSE_FLAG not in unverified
        for row in scanned["findings"]:
            if row.get("source") == "v329":
                assert row["claim_label"] in {"OBSERVED", "INFERRED"}
            else:
                assert row["claim_label"] == "OBSERVED"
    print("false double 64/128/512 absent from main")


def test_alta_burn_and_autogive_heavy_recompute() -> None:
    rows = json.loads(FIX.read_text(encoding="utf-8"))
    for text in (rows["alta_burn_rent"], _notes("4-alta-commons-founding100.md")):
        scanned = packet_compose.scan_input_notes(text)
        summaries = [row["summary"] for row in scanned["findings"]]
        assert any(
            summary == "notes say monthly burn 35000, recomputed monthly rent 55000"
            for summary in summaries
        ), summaries
        prose = _main_text(scanned)
        assert "notes say monthly burn 35000, recomputed monthly rent 55000" in prose
        assert "8.57143" not in prose
    for text in (rows["autogive_heavy"], _notes("3-autogive-tenant-sku.md")):
        scanned = packet_compose.scan_input_notes(text)
        summaries = [row["summary"] for row in scanned["findings"]]
        assert "notes say Heavy per tenant 636, recomputed Shared Heavy 336.4" in summaries, summaries
        assert not any("331.5" in summary for summary in summaries)
        prose = _main_text(scanned)
        assert "notes say Heavy per tenant 636, recomputed Shared Heavy 336.4" in prose
        assert "331.5" not in prose
        assert "below the count-1 floor 886" not in prose
        wrapped = packet_compose.apply_page_budget(
            {
                "input_contradictions": scanned,
                "research": {"observed_claims": []},
            }
        )
        parked = packet_compose.unreviewed_research(wrapped)
        assert parked is not None
        assert parked["label"] == "Research (unreviewed, needs a person's review)"
        assert "research_unreviewed" not in wrapped.get("appendix", {})
        assert "unverified_notes" not in wrapped["input_contradictions"]
        for note in parked["scanner_notes"]:
            assert note["claim_label"] == "NOT_COMPUTABLE"
            assert note["claim_label"] != "OBSERVED"
            assert note["summary"].startswith("Unverified scanner note: not stated as fact.")
    print("alta burn 35000→55000 and autogive 636→336.4 on the main page")


def test_held_out_still_clean() -> None:
    import eval_note_scan

    held = eval_note_scan.held_out_report()
    fps = eval_note_scan.false_positive_report()
    assert held["planted_caught"] == held["planted"] == 12, held
    assert held["clean_findings"] == 0, held
    assert fps["doc_findings"] == 0, fps["docs"]
    assert fps["synthetic_findings"] == 0, fps["synthetic"]
    print("held-out 12/12 and 0 false positives")


def _valid_test() -> dict:
    return {
        "action": "one prepaid pilot at the floor price",
        "metric": "prepaid_pilots",
        "threshold": 1,
        "comparison": "lt",
        "check_date": "2026-11-01",
        "kill_if": "kill if no one pays by 2026-11-01",
    }


def test_cheapest_test_is_one_action() -> None:
    ok = packet_compose.packaging_errors(
        {"schema_version": "1.1.0", "cheapest_test": _valid_test()},
        "opportunity",
    )
    assert not any(line.startswith("NG-TEST") for line in ok), ok

    missing = packet_compose.packaging_errors(
        {
            "schema_version": "1.1.0",
            "cheapest_test": {
                "action": "one prepaid pilot at the floor price",
                "comparison": "lt",
                "check_date": "2026-11-01",
            },
        },
        "opportunity",
    )
    assert any("numeric pass/fail threshold" in line for line in missing)

    listed = packet_compose.packaging_errors(
        {
            "schema_version": "1.1.0",
            "cheapest_test": {
                "action": "1. email five buyers\n2. then wait for a wire",
                "threshold": 1,
                "comparison": "gte",
                "check_date": "2026-11-01",
            },
        },
        "opportunity",
    )
    assert any("multi-step" in line for line in listed), listed

    as_list = packet_compose.packaging_errors(
        {"schema_version": "1.1.0", "cheapest_test": ["call", "invoice"]},
        "opportunity",
    )
    assert any("not a list" in line for line in as_list)

    handoff = {
        "summary": "Ship the notes check.",
        "first_commit": {
            "touch": ["pricing notes"],
            "done_when": "One seat rule is declared.",
            "test_to_write": "Re-run the input pass.",
            "owner_role": "operator",
        },
    }
    both = packet_compose.packaging_errors(
        {
            "schema_version": "1.2.0",
            "build_handoff": handoff,
            "cheapest_test": {
                "action": "first call the buyer then send a contract",
                "threshold": 1,
                "comparison": "gte",
                "check_date": "2026-11-01",
            },
        },
        "opportunity",
    )
    assert any(line.startswith("NG-TEST-001") for line in both)
    assert not any(line.startswith("NG-HANDOFF") for line in both)
    broken = packet_compose.packaging_errors(
        {"schema_version": "1.2.0", "cheapest_test": _valid_test()},
        "opportunity",
    )
    assert any(line.startswith("NG-HANDOFF-001") for line in broken)
    print("cheapest test is one dated yes/no; handoff unchanged")


class _Page:
    def __init__(self, body: bytes, url: str, status: int = 200) -> None:
        self._body = body
        self.status = status
        self._url = url

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


class _Provider:
    name = "paid_search"

    def __init__(self, rows: list[dict] | None = None) -> None:
        self.calls = 0
        self.rows = rows

    def search(self, query: str) -> list[dict]:
        self.calls += 1
        if self.rows is not None:
            return self.rows
        return [
            {
                "url": f"https://example.test/pricing/p/{self.calls}",
                "text": (
                    "Vendor pricing documentation lists the published monthly price, "
                    "the included quota, and the plan name on this official pricing page."
                ),
                "complete": True,
                "kind": "web_page",
                "retrieved_at": "2026-10-01",
            }
        ]


def _quiet_env() -> None:
    os.environ.pop(research_mode.PAID_KEY_ENV, None)
    os.environ.pop(research_mode.PAID_FLAG_ENV, None)
    os.environ.pop(research_mode.FIRECRAWL_KEY_ENV, None)


def test_capped_research_is_offline_safe() -> None:
    _quiet_env()
    provider = _Provider()
    offline = research_mode.run_idea_research(
        {"enabled": False, "offline": True, "allow_paid": True, "search_provider": provider},
        ["stripe pricing"],
    )
    assert provider.calls == 0
    assert offline["observed_claims"] == []
    assert offline["research_ran"] is False

    blocked = research_mode.run_idea_research(
        {"enabled": True, "offline": False, "adapter": "null", "allow_paid": True},
        ["stripe pricing", "competitor page"],
    )
    assert blocked["observed_claims"] == []
    assert blocked["not_fetched"]
    assert all(row["status"] == "NOT_FETCHED" for row in blocked["not_fetched"])
    assert all(row["reason"] == "no_key" for row in blocked["not_fetched"])
    assert not any(row.get("url") for row in blocked["not_fetched"])

    off = research_mode.run_idea_research(
        {"enabled": True, "offline": False, "adapter": "null"},
        ["official docs"],
    )
    assert off["not_fetched"][0]["reason"] == "paid_off"
    assert off["observed_claims"] == []

    priced = _Provider()
    capped = research_mode.run_idea_research(
        {
            "enabled": True,
            "offline": False,
            "adapter": "null",
            "allow_paid": True,
            "search_provider": priced,
            "paid_price_per_call": 0.08,
            "dollar_cap_per_idea": 0.20,
            "max_calls_per_idea": 5,
        },
        ["live pricing", "competitor", "official docs"],
    )
    assert priced.calls == 2
    assert capped["observed_claims"] == []
    assert len(capped["unverified_hits"]) == 2
    assert capped["not_fetched"][0]["reason"] == "over_cap"
    for claim in capped["unverified_hits"]:
        assert claim["claim_label"] == "NOT_COMPUTABLE"
        assert claim.get("label") != "OBSERVED"
        assert str(claim["url"]).startswith("https://")
        assert claim["retrieved_at"] == "2026-10-01"

    empty = _Provider(rows=[{"text": "a price with no source", "complete": True}])
    invented = research_mode.run_idea_research(
        {
            "enabled": True,
            "offline": False,
            "adapter": "null",
            "allow_paid": True,
            "search_provider": empty,
            "paid_price_per_call": 0.08,
        },
        ["mystery price"],
    )
    assert invented["observed_claims"] == []
    assert invented["rejected"][0]["reason"] == "missing_url"

    calls: list[str] = []

    def opener(req: object, timeout: int = 10) -> _Page:
        url = req.full_url if hasattr(req, "full_url") else req.get_full_url()  # type: ignore[attr-defined]
        calls.append(str(url))
        if str(url).endswith("/robots.txt"):
            return _Page(b"User-agent: *\nAllow: /\n", str(url))
        return _Page(b"Published list price is 12.", str(url))

    fetched = research_mode.run_idea_research(
        {
            "enabled": True,
            "offline": False,
            "adapter": "robots_http",
            "adapter_options": {"opener": opener},
            "max_calls_per_idea": 1,
        },
        [
            "https://example.test/pricing",
            "https://example.test/competitors",
        ],
    )
    assert len(fetched["observed_claims"]) == 1
    claim = fetched["observed_claims"][0]
    assert claim["url"] == "https://example.test/pricing"
    assert claim["retrieved_at"] == research_mode._today()
    assert claim["label"] == "OBSERVED"
    assert fetched["not_fetched"][0]["status"] == "NOT_FETCHED"
    assert fetched["not_fetched"][0]["reason"] == "over_cap"
    assert not any(url.startswith("https://example.test/competitors") for url in calls)

    ledger = research_mode.ResearchLedger(0.20)
    first = _Provider()
    research_mode.run_idea_research(
        {
            "enabled": True,
            "offline": False,
            "adapter": "null",
            "allow_paid": True,
            "search_provider": first,
            "paid_price_per_call": 0.08,
            "dollar_cap_per_idea": 0.20,
            "dollar_cap_per_run": 0.20,
        },
        ["one", "two"],
        ledger=ledger,
    )
    assert first.calls == 2
    second = _Provider()
    later = research_mode.run_idea_research(
        {
            "enabled": True,
            "offline": False,
            "adapter": "null",
            "allow_paid": True,
            "search_provider": second,
            "paid_price_per_call": 0.08,
            "dollar_cap_per_idea": 0.20,
            "dollar_cap_per_run": 0.20,
        },
        ["three"],
        ledger=ledger,
    )
    assert second.calls == 0
    assert later["observed_claims"] == []
    assert later["not_fetched"][0]["reason"] == "over_cap"
    print("capped research fail-closed; free fetch cited; no invented URL")


def main() -> None:
    test_false_double_stays_off_the_main_page()
    test_alta_burn_and_autogive_heavy_recompute()
    test_held_out_still_clean()
    test_cheapest_test_is_one_action()
    test_capped_research_is_offline_safe()
    print("PASS: bake-off v3.31")


if __name__ == "__main__":
    main()
