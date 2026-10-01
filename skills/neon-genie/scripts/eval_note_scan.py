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
    {"id": "1.1", "file": "1-hyperlex-plugin.md", "needles": ["1.2B", "UNVERIFIED", "OBSERVED"]},
    {"id": "1.2", "file": "1-hyperlex-plugin.md", "needles": ["not allowed", "upsell"]},
    {"id": "1.3", "file": "1-hyperlex-plugin.md", "needles": ["OpenAPI", "MCP"]},
    {"id": "2.1", "file": "2-x402-vernacular-api.md", "needles": ["all three", "Nebius"]},
    {"id": "2.2", "file": "2-x402-vernacular-api.md", "needles": ["open-source", "repo"]},
    {"id": "2.3", "file": "2-x402-vernacular-api.md", "needles": ["x402", "through the API"]},
    {"id": "3.1", "file": "3-autogive-tenant-sku.md", "needles": ["886", "559"]},
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
            cached[name] = packet_compose.scan_input_notes(text)
        blob = _blob(cached[name]["findings"] + cached[name].get("unverified_notes", []))
        needles = [str(item) for item in issue["needles"]]  # type: ignore[union-attr]
        hit = all(needle in blob for needle in needles)
        if hit:
            caught += 1
        rows.append(
            {
                "id": issue["id"],
                "caught": hit,
                "findings": len(cached[name]["findings"])
                + len(cached[name].get("unverified_notes") or []),
            }
        )
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


# Why the pre-extension general rules missed each issue. Measurement text, not scanner rules.
DIAGNOSIS = [
    ("1.1", "epistemic label clash", "mechanical", "UNVERIFIED and OBSERVED sit on the same magnitude in different sentences. The old check looked for the word verified, which this note does not use."),
    ("1.2", "policy vs proposed funnel", "NOT_COMPUTABLE", "A ban on upsells and a free-then-paid plan conflict only if those are the same offer. That needs judgment."),
    ("1.3", "mechanism mismatch", "NOT_COMPUTABLE", "OpenAPI versus Skills/MCP is world knowledge, not two values of one quantity."),
    ("2.1", "universal claim vs runtime constraint", "NOT_COMPUTABLE", "One build covering every surface versus a required runtime needs world knowledge."),
    ("2.2", "license vs later paid reuse", "NOT_COMPUTABLE", "An open-source requirement versus paid reuse is a legal judgment."),
    ("2.3", "channel mismatch", "NOT_COMPUTABLE", "Two route names for one buyer conflict only with outside knowledge of the rails."),
    ("3.1", "count series vs implied line", "mechanical", "The per-count totals are not the line implied by the larger counts. The old check needed the words 'not at N='."),
    ("3.2", "list price below floor", "mechanical", "A list price sits under the floor at the count the note says to use. The old check had no floor comparison."),
    ("3.3", "exclusion vs unnamed rate", "NOT_COMPUTABLE", "A seat exclusion and a later rate conflict only if the rate is the excluded thing. The note never says that."),
    ("3.4", "computed figure unused", "mechanical", "A stated double never appears in a later total. Absence is not an equality the old check could see."),
    ("4.1", "rationale polarity", "mechanical", "The rationale's high/low words match a different option row than the lock. The old check needed 'rationale for option X:'."),
    ("4.3", "credit versus monthly rates", "mechanical", "One credit divided by the stated monthly amounts covers inconsistent months. The missing single rate on the lock is NOT_COMPUTABLE."),
    ("5.1", "label scope", "mechanical", "A section labeled OBSERVED also says unverified, and a figure from it is reused as fact."),
    ("5.2", "required and excluded action", "mechanical", "The same action is forced and excluded. The old check did not compare directives."),
]


def held_out_report() -> dict:
    path = FIXTURE_DIR / "held-out-notes.json"
    rows = json.loads(path.read_text(encoding="utf-8"))["notes"]
    planted_hit = 0
    planted = 0
    clean_findings = 0
    detail = []
    for row in rows:
        scanned = packet_compose.scan_input_notes(row["text"])
        findings = scanned["findings"]
        unverified = scanned.get("unverified_notes") or []
        hit = bool(findings)
        if row["expect"] == "finding":
            planted += 1
            if hit:
                planted_hit += 1
        elif findings or unverified:
            clean_findings += len(findings) + len(unverified)
        detail.append(
            {
                "id": row["id"],
                "expect": row["expect"],
                "findings": len(findings),
                "ok": (row["expect"] == "finding" and hit) or (row["expect"] == "clean" and not hit),
            }
        )
    return {
        "planted_caught": planted_hit,
        "planted": planted,
        "clean_findings": clean_findings,
        "clean": len(rows) - planted,
        "notes": detail,
    }


def false_positive_report() -> dict:
    findings = []
    for path in _clean_paths():
        text = path.read_text(encoding="utf-8")
        scanned = packet_compose.scan_input_notes(text)
        for row in list(scanned["findings"]) + list(scanned.get("unverified_notes") or []):
            findings.append(
                {
                    "path": str(path.relative_to(ROOT)),
                    "kind": row.get("kind"),
                    "summary": row.get("summary"),
                }
            )
    synthetic_hits = []
    for index, note in enumerate(CLEAN_SYNTHETIC):
        scanned = packet_compose.scan_input_notes(note)
        rows = list(scanned["findings"]) + list(scanned.get("unverified_notes") or [])
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
    held = held_out_report()
    print(
        f"fix4 catch {caught['caught']}/{caught['total']} "
        f"false_positives docs={fps['doc_findings']} synthetic={fps['synthetic_findings']} "
        f"held_out {held['planted_caught']}/{held['planted']} "
        f"clean_findings={held['clean_findings']}"
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
    print("held-out:")
    for row in held["notes"]:
        mark = "ok" if row["ok"] else "BAD"
        print(f"  {row['id']} {mark} expect={row['expect']} findings={row['findings']}")
    print("diagnosis:")
    for issue_id, kind, status, why in DIAGNOSIS:
        print(f"  {issue_id} {kind} {status}: {why}")
    if "--json" in sys.argv:
        print(json.dumps({"catch": caught, "false_positives": fps, "held_out": held}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
