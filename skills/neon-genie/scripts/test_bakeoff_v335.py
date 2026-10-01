#!/usr/bin/env python3
"""v3.35 sidecar, idempotent page budget, provenance. Stdlib only. No paid calls.

Reviewed contradictions stay by source. Research leaves the packet.
Running the page-budget step twice does not duplicate a row.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import packet_compose

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "evals" / "bakeoff-v330" / "raw-notes"
R2 = ROOT / "evals" / "bakeoff-v330" / "r2-packets"
LABEL = "Research (unreviewed, needs a person's review)"


def _page(name: str) -> tuple[dict, str]:
    notes = (RAW / name).read_text(encoding="utf-8")
    packet = packet_compose.apply_page_budget(
        {
            "opportunity_thesis": "Short thesis.",
            "input_contradictions": packet_compose.scan_input_notes(notes),
            "research": {"observed_claims": []},
        }
    )
    return packet, packet_compose.prose_main(packet)


def test_expected_lines_and_no_empty_pass() -> None:
    hyper, hyper_prose = _page("1-hyperlex-plugin.md")
    x402, x402_prose = _page("2-x402-vernacular-api.md")
    auto, auto_prose = _page("3-autogive-tenant-sku.md")
    alta, alta_prose = _page("4-alta-commons-founding100.md")
    jev, jev_prose = _page("5-jev-crypto-arb.md")

    assert "1.2B weekly users UNVERIFIED" in hyper_prose
    assert "paid API funnel" in hyper_prose
    assert "1.2B" in json.dumps(hyper["appendix"]["contradiction_evidence"])
    assert "upsell" in json.dumps(hyper["appendix"]["contradiction_evidence"]).lower()
    assert hyper["input_contradictions"]["findings"]
    assert "none found" not in hyper_prose.lower()
    assert "The same quantity is marked both UNVERIFIED and OBSERVED." not in hyper_prose

    assert x402["input_contradictions"]["findings"]
    assert "none found" not in x402_prose.lower()
    assert "One build serves all three" in x402_prose
    assert "open-source repo" in x402_prose
    assert "through the API" in x402_prose
    assert "serves every listed surface" not in x402_prose

    assert "maximizes conversion" in alta_prose
    assert "Input notes lock both Option A and B." in alta_prose
    assert "$5.5/sf/mo implies $66/sf/yr, not $60/sf/yr." in alta_prose
    assert "notes say monthly burn 35000, recomputed monthly rent 55000" in alta_prose
    assert "The rationale for locked Option A agrees with Option B." not in alta_prose
    seat = packet_compose.scan_input_notes(packet_compose.SEAT_OPTION_NOTES)
    assert any(
        row["summary"] == "The rationale for locked A describes B."
        for row in seat["findings"]
    )

    assert "no floor row" in auto_prose
    assert "Computed 512 does not appear in a later total." not in auto_prose
    assert auto_prose.count("notes say Heavy per tenant 636, recomputed Shared Heavy 336.4") == 1
    assert "331.5" not in auto_prose
    assert "Double of 64 is 128, not 512" not in auto_prose

    assert "70-500" in json.dumps(jev["appendix"]["contradiction_evidence"])
    assert "red team says unclear cases default to skip, not ask_human" in jev_prose
    assert "The action ask_human is both required and excluded." not in jev_prose
    assert len([line for line in jev_prose.splitlines() if "ask_human" in line]) == 1

    for prose in (hyper_prose, x402_prose, auto_prose, alta_prose, jev_prose):
        assert len(prose.split()) <= packet_compose.WORD_BUDGET
    for packet in (hyper, x402, auto, alta, jev):
        for row in packet["input_contradictions"]["findings"]:
            assert row.get("source") in {"reviewed", "v329"}
    print("reviewed lines are on the main page; hyperlex and x402 are not empty")


def test_v329_packet_lines_pass_by_provenance() -> None:
    kept = 0
    total = 0
    for path in sorted(R2.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        findings = data["input_contradictions"]["findings"]
        packet = packet_compose.apply_page_budget(
            {
                "opportunity_thesis": "Short thesis.",
                "input_contradictions": data["input_contradictions"],
                "research": {"observed_claims": []},
            }
        )
        out = [row["summary"] for row in packet["input_contradictions"]["findings"]]
        for row in findings:
            total += 1
            assert row["summary"] in out, (path.name, row["summary"])
            kept += 1
        prose = packet_compose.prose_main(packet)
        assert "none found" not in prose.lower()
        assert packet["page_budget"]["main_word_count"] <= packet_compose.WORD_BUDGET
    assert total == 18 and kept == 18
    print("v3.29 packet lines stay without a phrase list")


def test_page_budget_twice_and_sidecar() -> None:
    notes = (RAW / "5-jev-crypto-arb.md").read_text(encoding="utf-8")
    scanned = packet_compose.scan_input_notes(notes)
    scanned["findings"].append(
        {
            "finding_id": "in-v329",
            "kind": "contradiction",
            "summary": (
                "The route sends high consequential_spend to ask_human; "
                "the red team says unclear cases default to skip, not ask_human."
            ),
            "claim_label": "OBSERVED",
            "source": "v329",
            "evidence": "skip, not ask_human",
        }
    )
    base = {
        "opportunity_thesis": "Short thesis.",
        "input_contradictions": scanned,
        "research": {
            "observed_claims": [],
            "unverified_hits": [
                {
                    "url": "https://example.test/pricing/unreviewed",
                    "text": "A search hit that is not a primary source and is not reviewed.",
                    "claim_label": "OBSERVED",
                }
            ],
            "reconcile": {
                "items": [
                    {
                        "verdict": "AGREES",
                        "sentence": "AGREES: quoted note",
                        "claim_label": "OBSERVED",
                    }
                ]
            },
        },
    }
    once = packet_compose.apply_page_budget(base)
    twice = packet_compose.apply_page_budget(once)
    assert packet_compose.unreviewed_research(once) == packet_compose.unreviewed_research(twice)
    assert [row["summary"] for row in once["input_contradictions"]["findings"]] == [
        row["summary"] for row in twice["input_contradictions"]["findings"]
    ]
    prose = packet_compose.prose_main(twice)
    assert len([line for line in prose.splitlines() if "ask_human" in line]) == 1
    doc = packet_compose.unreviewed_research(twice)
    assert doc is not None
    assert doc["label"] == LABEL
    assert len(doc["search_hits"]) == 1
    assert len(doc["reconcile"]) == 1
    rows = doc["scanner_notes"] + doc["search_hits"] + doc["reconcile"]
    assert rows
    assert all(row.get("claim_label") != "OBSERVED" for row in rows)
    assert all(row.get("label") != "OBSERVED" for row in rows)
    body = {key: value for key, value in twice.items() if key != "_research_unreviewed"}
    blob = json.dumps(body)
    assert "https://example.test/pricing/unreviewed" not in blob
    assert "AGREES:" not in blob
    assert "research_unreviewed" not in blob

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "idea.packet.json"
        written = packet_compose.write_packet(path, twice)
        side = Path(str(path) + ".research.md")
        text = side.read_text(encoding="utf-8")
        assert text.startswith(f"# {LABEL}")
        assert "https://example.test/pricing/unreviewed" in text
        assert "AGREES: quoted note" in text
        saved = json.loads(path.read_text(encoding="utf-8"))
        assert "_research_unreviewed" not in saved
        assert "research_unreviewed" not in json.dumps(saved.get("appendix") or {})
        assert saved["research_sidecar"] == side.name
        assert "\n" not in saved["research_sidecar"]
        again = packet_compose.write_packet(path, written)
        assert again == written
        assert side.read_text(encoding="utf-8") == text
    print("page budget twice matches; research is the sidecar")


def main() -> None:
    test_expected_lines_and_no_empty_pass()
    test_v329_packet_lines_pass_by_provenance()
    test_page_budget_twice_and_sidecar()
    print("PASS: bake-off v3.35")


if __name__ == "__main__":
    main()
