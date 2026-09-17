#!/usr/bin/env python3
"""Packaging checks for thickened commercial / opportunity schemas."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
PY = sys.executable
VALIDATE = SCRIPT_DIR / "validate_packet.py"


def _run(packet: Path, packet_type: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [PY, str(VALIDATE), "--packet", str(packet), "--type", packet_type],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def test_sample_packets_pass() -> None:
    for rel, ptype in (
        ("examples/packets/sample-opportunity.packet.json", "opportunity"),
        ("examples/packets/sample-commercial.packet.json", "commercial"),
    ):
        r = _run(ROOT / rel, ptype)
        assert r.returncode == 0, r.stderr or r.stdout


def test_observed_cac_without_refs_fails() -> None:
    packet = {
        "buyer_map": {
            "economic_buyer": "NOT_COMPUTABLE_until_declared",
            "beneficiary": "NOT_COMPUTABLE_until_declared",
            "evidence_refs": [],
        },
        "pricing_model": {
            "model_type": "fixed_fee",
            "claim_label": "OBSERVED",
            "cac": 120,
            "evidence_refs": [],
        },
        "cost_scenarios": {"conservative": "NOT_COMPUTABLE"},
        "revenue_scenarios": {"conservative": "NOT_COMPUTABLE"},
        "distribution": "unknown",
        "risks": ["invented CAC"],
    }
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "bad-commercial.json"
        path.write_text(json.dumps(packet), encoding="utf-8")
        r = _run(path, "commercial")
    assert r.returncode != 0, "OBSERVED CAC without evidence_refs must fail"
    assert "NG-COMM-001" in (r.stderr or "")


def main() -> int:
    test_sample_packets_pass()
    test_observed_cac_without_refs_fails()
    print("PASS: commercial/opportunity schema packaging checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
