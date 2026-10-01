#!/usr/bin/env python3
"""v3.36 final bake-off page. Stdlib only. No network and no paid calls.

The main-page contradiction set for the five bake-off ideas is v3.29's
set plus the named money recomputes.
"""

from __future__ import annotations

import json
from pathlib import Path

import packet_compose

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "evals" / "bakeoff-v330" / "raw-notes"
R2 = ROOT / "evals" / "bakeoff-v330" / "r2-packets"
REVIEWED = ROOT / "evals" / "fixtures" / "v329" / "reviewed-lines.json"
IDEAS = (
    "1-hyperlex-plugin.md",
    "2-x402-vernacular-api.md",
    "3-autogive-tenant-sku.md",
    "4-alta-commons-founding100.md",
    "5-jev-crypto-arb.md",
)
MONEY = {
    "3-autogive-tenant-sku.md": "notes say Heavy per tenant 636, recomputed Shared Heavy 336.4",
    "4-alta-commons-founding100.md": "notes say monthly burn 35000, recomputed monthly rent 55000",
}
FALSE_FLAG = "Double of 64 is 128, not 512"


def _v329(name: str) -> set[str]:
    packet = R2 / (Path(name).stem + ".opportunity.packet.json")
    data = json.loads(packet.read_text(encoding="utf-8"))
    lines: set[str] = set()
    for row in data["input_contradictions"]["findings"]:
        note = str(row.get("host_review") or "")
        if note.startswith("FALSE_POSITIVE"):
            continue
        lines.add(row["summary"])
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
        packet, prose = _page(name)
        got = {row["summary"] for row in packet["input_contradictions"]["findings"]}
        want = set(_v329(name))
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
    _, auto = _page("3-autogive-tenant-sku.md")
    assert auto.count(MONEY["3-autogive-tenant-sku.md"]) == 1
    assert "331.5" not in auto
    _, jev = _page("5-jev-crypto-arb.md")
    assert jev.count("red team says unclear cases default to skip, not ask_human") == 1
    assert "The action ask_human is both required and excluded." not in jev
    print("main page is the v3.29 set plus the money recomputes")


def main() -> None:
    test_main_page_is_v329_plus_recomputes()
    print("PASS: bake-off v3.36")


if __name__ == "__main__":
    main()
