#!/usr/bin/env python3
"""Unit tests for Hermes v0.21 SKILL.md frontmatter gates (stdlib only)."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import validate_hermes_skill as vhs  # noqa: E402

FOLDED = """---
name: neon-genie
description: >
  Evidence-bound product and opportunity intelligence — audits, zero-option
  loops, commercial models, agentic graphs, and Wayfinder handoffs with claim
  labels and fail-closed gates. Use for product intent, opportunity mining,
  and advisory packets — not cinematic work (use Kubrick) or code execution.
version: 3.26.0
author: Applied Alchemy Labs / Zero State
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags:
      - Product
    related_skills: []
---

# Body
"""


def test_folded_description_exceeds_limit() -> None:
    fields = vhs.parse_frontmatter(FOLDED)
    desc = str(fields.get("description", ""))
    if len(desc) <= vhs.SKILL_PROMPT_DESC_LIMIT:
        raise AssertionError(f"folded description should exceed 60, got {len(desc)}")
    errors = vhs.validate_description(desc)
    if not any("truncates" in e for e in errors):
        raise AssertionError(f"expected length error, got {errors}")


def test_short_description_passes() -> None:
    desc = "Audit products and opportunities with labeled evidence."
    if len(desc) > vhs.SKILL_PROMPT_DESC_LIMIT:
        raise AssertionError(f"hunch description is {len(desc)} chars")
    errors = vhs.validate_description(desc)
    if errors:
        raise AssertionError(errors)


def test_marketing_and_period() -> None:
    errors = vhs.validate_description("A powerful product auditor")
    joined = " ".join(errors)
    if "marketing" not in joined or "period" not in joined:
        raise AssertionError(f"expected marketing + period errors, got {errors}")


def test_live_skill_frontmatter() -> None:
    text = (vhs.SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise AssertionError("SKILL.md must start at byte 0 with ---")
    fields = vhs.parse_frontmatter(text)
    missing = vhs.REQUIRED_FRONTMATTER - set(fields)
    if missing:
        raise AssertionError(f"missing fields: {missing}")
    errors = vhs.validate_description(str(fields.get("description", "")))
    if errors:
        raise AssertionError(errors)
    hermes = fields.get("_hermes")
    if not isinstance(hermes, dict):
        raise AssertionError("metadata.hermes missing")
    missing_h = vhs.REQUIRED_HERMES_KEYS - set(hermes)
    if missing_h:
        raise AssertionError(f"missing hermes keys: {missing_h}")


def main() -> int:
    tests = (
        test_folded_description_exceeds_limit,
        test_short_description_passes,
        test_marketing_and_period,
        test_live_skill_frontmatter,
    )
    for fn in tests:
        fn()
    print("ALL PASS: test_hermes_frontmatter")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
