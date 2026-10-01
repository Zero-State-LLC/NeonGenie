#!/usr/bin/env python3
"""v3.34 main-page rollback. Stdlib only. No network and no paid calls.

Reviewed contradictions and named money recomputes stay on the main page.
Scanner notes, search hits, and Jev lines go to the unreviewed appendix.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import packet_compose
import research_mode

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "evals" / "fixtures" / "v334" / "main-page.json"
RAW = ROOT / "evals" / "bakeoff-v330" / "raw-notes"


def _rows() -> dict:
    return json.loads(FIX.read_text(encoding="utf-8"))


def _page(name: str) -> tuple[dict, str]:
    notes = (RAW / name).read_text(encoding="utf-8")
    scanned = packet_compose.scan_input_notes(notes)
    packet = packet_compose.apply_page_budget(
        {
            "opportunity_thesis": "Short thesis.",
            "input_contradictions": scanned,
            "research": {"observed_claims": []},
            "build_handoff": {
                "summary": "Ship the notes check.",
                "first_commit": {
                    "touch": ["notes"],
                    "done_when": "One rule is declared.",
                    "test_to_write": "Re-run the input pass.",
                    "owner_role": "operator",
                },
            },
            "cheapest_test": {
                "action": "one prepaid pilot at the floor price",
                "metric": "prepaid_pilots",
                "threshold": 1,
                "comparison": "lt",
                "check_date": "2026-11-01",
            },
        }
    )
    return packet, packet_compose.prose_main(packet)


def test_reviewed_lines_and_named_recomputes_stay() -> None:
    rows = _rows()
    alta, alta_prose = _page("4-alta-commons-founding100.md")
    jev, jev_prose = _page("5-jev-crypto-arb.md")
    auto, auto_prose = _page("3-autogive-tenant-sku.md")
    for line in rows["alta_main"]:
        assert line in alta_prose, line
        assert any(row["summary"] == line for row in alta["input_contradictions"]["findings"])
    for line in rows["jev_main"]:
        assert line in jev_prose, line
    for line in rows["autogive_main"]:
        assert line in auto_prose, line
        assert auto_prose.count(line) == 1
    for prose in (alta_prose, jev_prose, auto_prose):
        for banned in rows["off_main"]:
            assert banned not in prose, banned
        assert "one prepaid pilot at the floor price" in prose
        assert "Ship the notes check." in prose
        assert len(prose.split()) <= packet_compose.WORD_BUDGET
    appendix = alta["appendix"]["research_unreviewed"]
    assert appendix["label"] == rows["appendix_label"]
    parked = appendix["scanner_notes"] + appendix["search_hits"] + appendix["reconcile"]
    assert parked
    assert all(row.get("claim_label") != "OBSERVED" for row in parked)
    assert all(row.get("label") != "OBSERVED" for row in parked)
    blob = json.dumps(parked)
    assert "The rationale for locked Option A agrees with Option B." in blob
    print("reviewed contradictions and named recomputes stay; other scanner lines do not")


def test_paid_research_is_off_without_the_flag() -> None:
    os.environ.pop(research_mode.PAID_FLAG_ENV, None)
    os.environ.pop(research_mode.FIRECRAWL_KEY_ENV, None)

    class _Provider:
        name = "paid_search"
        calls = 0

        def search(self, query: str) -> list[dict]:
            self.calls += 1
            return []

    provider = _Provider()
    result = research_mode.run_idea_research(
        {"enabled": True, "offline": False, "adapter": "null", "search_provider": provider},
        ["vendor pricing"],
    )
    assert provider.calls == 0
    assert result["observed_claims"] == []
    assert result["not_fetched"][0]["reason"] == "paid_off"
    print("Firecrawl stays off unless NEON_GENIE_RESEARCH_PAID=1")


def main() -> None:
    test_reviewed_lines_and_named_recomputes_stay()
    test_paid_research_is_off_without_the_flag()
    print("PASS: bake-off v3.34")


if __name__ == "__main__":
    main()
