#!/usr/bin/env python3
"""v3.36 final bake-off page. Stdlib only. No network and no paid calls.

The main-page contradiction set for the five bake-off ideas is the
reviewed-line fixture plus the named money recomputes.
"""

from __future__ import annotations

import json
from pathlib import Path

import packet_compose

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "evals" / "bakeoff-v330" / "raw-notes"
REVIEWED = ROOT / "evals" / "fixtures" / "v329" / "reviewed-lines.json"
IDEAS = (
    "1-lumen-desk-widget.md",
    "2-brook-meter-api.md",
    "3-harbor-seat-plan.md",
    "4-willow-yard-pass.md",
    "5-cinder-route-desk.md",
)
MONEY = {
    "3-harbor-seat-plan.md": "notes say Cove per tenant 425, recomputed Pooled cove 225",
    "4-willow-yard-pass.md": "notes say monthly burn 18000, recomputed monthly rent 32000",
}
FALSE_FLAG = "Double of 40 is 80, not 160"
ROUTE_LINE = (
    "The route sends high spend to hold_review; "
    "the review note says unclear cases default to skip, not hold_review."
)


def _reviewed(name: str, notes: str) -> set[str]:
    prefix = name.split("-", 1)[0] + "."
    payload = json.loads(REVIEWED.read_text(encoding="utf-8"))
    lines: set[str] = set()
    for row in payload["lines"]:
        if not str(row["id"]).startswith(prefix):
            continue
        needles = [str(item) for item in row["needles"]]
        if needles and all(needle in notes for needle in needles):
            lines.add(str(row["summary"]))
    return lines


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


def test_main_page_is_v329_plus_recomputes() -> None:
    reviewed = json.loads(REVIEWED.read_text(encoding="utf-8"))["lines"]
    assert len(reviewed) == 16
    seen: set[str] = set()
    for name in IDEAS:
        notes = (RAW / name).read_text(encoding="utf-8")
        packet, prose = _page(name)
        got = {row["summary"] for row in packet["input_contradictions"]["findings"]}
        want = _reviewed(name, notes)
        extra = MONEY.get(name)
        if extra:
            want.add(extra)
        assert got == want, (name, got - want, want - got)
        for row in packet["input_contradictions"]["findings"]:
            assert row.get("source") in {"reviewed", "v329"}
        assert len(prose.split()) <= packet_compose.WORD_BUDGET
        assert FALSE_FLAG not in prose
        seen.update(got)
    for row in reviewed:
        assert row["summary"] in seen, row["id"]
    _, seat = _page("3-harbor-seat-plan.md")
    assert seat.count(MONEY["3-harbor-seat-plan.md"]) == 1
    assert "below the count-1 floor" not in seat
    _, route = _page("5-cinder-route-desk.md")
    assert route.count(ROUTE_LINE) == 1
    assert "The action hold_review is both required and excluded." not in route
    print("main page is the reviewed set plus the money recomputes")


def main() -> None:
    test_main_page_is_v329_plus_recomputes()
    print("PASS: bake-off v3.36")


if __name__ == "__main__":
    main()
