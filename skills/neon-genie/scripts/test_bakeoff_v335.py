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
    desk, desk_prose = _page("1-lumen-desk-widget.md")
    meter, meter_prose = _page("2-brook-meter-api.md")
    seat, seat_prose = _page("3-harbor-seat-plan.md")
    yard, yard_prose = _page("4-willow-yard-pass.md")
    route, route_prose = _page("5-cinder-route-desk.md")

    assert "4.4 million monthly readers" in desk_prose
    assert "paid meter funnel" in desk_prose
    assert "4.4 million" in json.dumps(desk["appendix"]["contradiction_evidence"])
    assert "upsell" in json.dumps(desk["appendix"]["contradiction_evidence"]).lower()
    assert desk["input_contradictions"]["findings"]
    assert "none found" not in desk_prose.lower()
    assert "The same quantity is marked both UNVERIFIED and OBSERVED." not in desk_prose

    assert meter["input_contradictions"]["findings"]
    assert "none found" not in meter_prose.lower()
    assert "all three surfaces" in meter_prose
    assert "shared-code repo" in meter_prose
    assert "through the meter" in meter_prose
    assert "serves every listed surface" not in meter_prose

    assert "refund load" in yard_prose
    assert "Input notes lock both Option A and B." in yard_prose
    assert "$4/sf/mo implies $48/sf/yr, not $40/sf/yr." in yard_prose
    assert "notes say monthly burn 18000, recomputed monthly rent 32000" in yard_prose
    assert "The rationale for locked Option A agrees with Option B." not in yard_prose
    option_notes = packet_compose.scan_input_notes(packet_compose.SEAT_OPTION_NOTES)
    assert any(
        row["summary"] == "The rationale for locked A describes B."
        for row in option_notes["findings"]
    )

    assert "no floor row" in seat_prose
    assert "Computed 160 does not appear in a later total." not in seat_prose
    assert seat_prose.count("notes say Cove per tenant 425, recomputed Pooled cove 225") == 1
    assert "Double of 40 is 80, not 160" not in seat_prose

    assert "40-90" in json.dumps(route["appendix"]["contradiction_evidence"])
    assert "default to skip, not hold_review" in route_prose
    assert "The action hold_review is both required and excluded." not in route_prose
    assert len([line for line in route_prose.splitlines() if "hold_review" in line]) == 1

    for prose in (desk_prose, meter_prose, seat_prose, yard_prose, route_prose):
        assert len(prose.split()) <= packet_compose.WORD_BUDGET
    for packet in (desk, meter, seat, yard, route):
        for row in packet["input_contradictions"]["findings"]:
            assert row.get("source") in {"reviewed", "v329"}
    print("reviewed lines are on the main page; desk and meter are not empty")


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
    notes = (RAW / "5-cinder-route-desk.md").read_text(encoding="utf-8")
    scanned = packet_compose.scan_input_notes(notes)
    scanned["findings"].append(
        {
            "finding_id": "in-v329",
            "kind": "contradiction",
            "summary": (
                "The route sends high spend to hold_review; "
                "the review note says unclear cases default to skip, not hold_review."
            ),
            "claim_label": "OBSERVED",
            "source": "v329",
            "evidence": "skip, not hold_review",
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
    assert len([line for line in prose.splitlines() if "hold_review" in line]) == 1
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
