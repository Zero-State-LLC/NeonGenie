#!/usr/bin/env python3
"""Measure the note scan. This file is the ruler, not the rules.

Catch rate is how many of the 16 known raw-note issues show up in a finding.
The needles live here so the scanner does not learn the issue sentences.
False positives are findings on repo docs, examples, and consistent notes.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import packet_compose

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "evals" / "bakeoff-v330"

# Measurement only. A hit means a finding quotes these fragments.
ISSUE_NEEDLES: list[dict[str, object]] = [
    {"id": "1.1", "file": "1-hyperlex-plugin.md", "needles": ["1.2B", "UNVERIFIED", "verified"]},
    {"id": "1.2", "file": "1-hyperlex-plugin.md", "needles": ["not allowed", "upsell"]},
    {"id": "1.3", "file": "1-hyperlex-plugin.md", "needles": ["OpenAPI", "MCP"]},
    {"id": "2.1", "file": "2-x402-vernacular-api.md", "needles": ["all three", "Nebius"]},
    {"id": "2.2", "file": "2-x402-vernacular-api.md", "needles": ["open-source", "repo"]},
    {"id": "2.3", "file": "2-x402-vernacular-api.md", "needles": ["x402", "through the API"]},
    {"id": "3.1", "file": "3-autogive-tenant-sku.md", "needles": ["N=1", "N=10"]},
    {"id": "3.2", "file": "3-autogive-tenant-sku.md", "needles": ["800", "886"]},
    {"id": "3.3", "file": "3-autogive-tenant-sku.md", "needles": ["Does not include API", "API"]},
    {"id": "3.4", "file": "3-autogive-tenant-sku.md", "needles": ["512"]},
    {"id": "4.1", "file": "4-alta-commons-founding100.md", "needles": ["rationale", "Option B"]},
    {"id": "4.2", "file": "4-alta-commons-founding100.md", "needles": ["Option A", "Option B"]},
    {"id": "4.3", "file": "4-alta-commons-founding100.md", "needles": ["months", "3,000"]},
    {"id": "4.4", "file": "4-alta-commons-founding100.md", "needles": ["5.5", "60"]},
    {"id": "5.1", "file": "5-jev-crypto-arb.md", "needles": ["70-500", "unverified"]},
    {"id": "5.2", "file": "5-jev-crypto-arb.md", "needles": ["ask_human", "skip"]},
]

CLEAN_SYNTHETIC = [
    "Option A is locked. Option B is archived and is not the plan.",
    "Asking rent is $5.50/sf/mo, which is $66/sf/yr.",
    "token floor: $170\ntoken floor: $170",
    "The fee is $10 monthly. The yearly fee is $120 yearly.",
    "N=1 counts one seat. N=10 counts one seat.",
    "10 × 5 = 50.",
    "The operator has not declared a buyer.",
]


def _blob(findings: list[dict]) -> str:
    parts: list[str] = []
    for row in findings:
        parts.append(str(row.get("summary") or ""))
        parts.append(str(row.get("evidence") or ""))
    return "\n".join(parts)


def catch_report(notes_dir: Path | None = None) -> dict:
    folder = notes_dir or (FIXTURE_DIR / "raw-notes")
    cached: dict[str, list[dict]] = {}
    rows = []
    caught = 0
    for issue in ISSUE_NEEDLES:
        name = str(issue["file"])
        if name not in cached:
            text = (folder / name).read_text(encoding="utf-8")
            cached[name] = packet_compose.scan_input_notes(text)["findings"]
        blob = _blob(cached[name])
        needles = [str(item) for item in issue["needles"]]  # type: ignore[union-attr]
        hit = all(needle in blob for needle in needles)
        if hit:
            caught += 1
        rows.append({"id": issue["id"], "caught": hit, "findings": len(cached[name])})
    return {"caught": caught, "total": len(ISSUE_NEEDLES), "issues": rows}


def _clean_paths() -> list[Path]:
    paths = [
        ROOT / "README.md",
        ROOT / "CONTRIBUTING.md",
        ROOT / "docs" / "ROADMAP.md",
        ROOT / "examples" / "README.md",
    ]
    paths.extend(sorted((ROOT / "docs" / "adr").glob("*.md")))
    paths.extend(sorted((ROOT / "examples").glob("*.brief.yaml")))
    return [path for path in paths if path.is_file()]


def false_positive_report() -> dict:
    findings = []
    for path in _clean_paths():
        text = path.read_text(encoding="utf-8")
        for row in packet_compose.scan_input_notes(text)["findings"]:
            findings.append(
                {
                    "path": str(path.relative_to(ROOT)),
                    "kind": row.get("kind"),
                    "summary": row.get("summary"),
                }
            )
    synthetic_hits = []
    for index, note in enumerate(CLEAN_SYNTHETIC):
        rows = packet_compose.scan_input_notes(note)["findings"]
        if rows:
            synthetic_hits.append({"index": index, "summaries": [row["summary"] for row in rows]})
    return {
        "doc_findings": len(findings),
        "docs": findings,
        "synthetic_findings": len(synthetic_hits),
        "synthetic": synthetic_hits,
    }


def main() -> int:
    caught = catch_report()
    fps = false_positive_report()
    print(
        f"fix4 catch {caught['caught']}/{caught['total']} "
        f"false_positives docs={fps['doc_findings']} synthetic={fps['synthetic_findings']}"
    )
    for row in caught["issues"]:
        mark = "hit" if row["caught"] else "miss"
        print(f"  {row['id']} {mark} findings_in_file={row['findings']}")
    if fps["docs"]:
        print("doc findings:")
        for row in fps["docs"]:
            print(f"  {row['path']}: {row['summary']}")
    if fps["synthetic"]:
        print("synthetic findings:")
        for row in fps["synthetic"]:
            print(f"  note {row['index']}: {row['summaries']}")
    if "--json" in sys.argv:
        print(json.dumps({"catch": caught, "false_positives": fps}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
