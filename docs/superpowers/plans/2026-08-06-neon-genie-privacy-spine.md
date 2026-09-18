# Neon Genie Privacy-by-Construction Spine (W1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship Neon Genie **3.24.0** privacy-by-construction spine (issue #15 P0–P2): contract docs, receipt/envelope privacy provenance, always-on privacy profile, egress gates S–Y, secret preflight, `do privacy` + doctor, behavioral evals, hub parity.

**Architecture:** Doctrine + deterministic packaging (not a Python research proxy). Hermes prose enforces egress via `profiles/privacy.md` + SKILL runes/gates. Stdlib CLI builds/validates privacy fields, runs preflight, and proves offline packaging paths. Wayfinder remains optional handoff only.

**Tech Stack:** Markdown skill contracts, JSON Schema, YAML gates, Python 3 standard library only (no new third-party deps). Hermes Hub distribution via `distribution.yaml` + `distribution_spine.py`.

**Spec:** `docs/superpowers/specs/2026-08-06-neon-genie-privacy-spine-design.md`

## Global Constraints

- Version target: **3.24.0** across `VERSION`, `SKILL.md` frontmatter, `manifest.json`, `references/VERSION`, CHANGELOG
- Envelope `schema_version`: **1.1.0** (additive `privacy` summary); `schema_id` remains `neon-genie/run-envelope`
- Privacy contract version: **1.0.0** (`privacy_contract_version` field)
- `telemetry_status` const: **`disabled`** in W1
- Authority: **`advisory_only`**, `grants_execution: false`
- Wayfinder: **optional handoff consumer only** — never required for doctor/privacy/recipes
- Stdlib only for new Python
- Hub allowlist: ship contract as **`references/PRIVACY.md`** (mirror of root `PRIVACY.md`)
- Always co-load profile **`privacy`** with **`core`**
- Gates **S–Y** registered in `references/gates.yaml` + anti-overclaim patterns
- Do not claim absolute “never leaves your device”
- W2/W3 not implemented in this plan — only freeze interfaces from spec §6.4

---

## File map

| Path | Action | Responsibility |
|------|--------|----------------|
| `scripts/privacy_preflight.py` | Create | Deterministic secret/PII preflight |
| `scripts/test_privacy_preflight.py` | Create | Unit tests for preflight |
| `scripts/privacy_report.py` | Create | `do privacy` report implementation |
| `scripts/test_privacy_surface.py` | Create | Integration tests for privacy CLI + receipt/envelope fields |
| `schemas/run-receipt.schema.json` | Modify | Privacy provenance properties |
| `schemas/run-envelope.schema.json` | Modify | `1.1.0` + required `privacy` object |
| `references/schemas/*` | Mirror | Via distribution spine write |
| `scripts/build_receipt.py` | Modify | Emit privacy defaults; ensure `privacy` in profiles |
| `scripts/build_envelope.py` | Modify | `ENVELOPE_SCHEMA_VERSION = "1.1.0"` + `privacy` summary |
| `scripts/validate_packet.py` | Modify | Privacy validation rules for receipt/envelope |
| `scripts/route_profiles.py` | Modify | Always include `privacy` with `core` |
| `scripts/neon_genie.py` | Modify | Register `privacy` job |
| `scripts/doctor.py` | Modify | Run privacy report + preflight self-test |
| `scripts/test_run_envelope.py` | Modify | Expect `1.1.0` + privacy block |
| `scripts/recipe_common.py` | Modify | Ensure privacy on finish path if needed |
| `profiles/privacy.md` | Create | Always-on privacy profile contract |
| `profiles/core.md` | Modify | CLEAR/SEAL privacy gates + co-load note |
| `SKILL.md` | Modify | Router, research loop, runes, version, hub list (generated) |
| `references/gates.yaml` | Modify | Gates S–Y |
| `references/anti-overclaim-patterns.md` | Modify | Gates S–Y prose |
| `references/schema-versioning.md` | Modify | Envelope 1.1.0 |
| `references/CAPABILITY_MAP.md` | Modify | Privacy capability line |
| `PRIVACY.md` | Create | Root human contract |
| `references/PRIVACY.md` | Create | Hub-safe copy (keep byte-equal via spine or explicit sync) |
| `docs/adr/0006-privacy-by-construction.md` | Create | ADR |
| `docs/adr/README.md` | Modify | Index entry |
| `examples/packets/sample-run-envelope.json` | Modify | 1.1.0 + privacy |
| `examples/packets/sample-receipt*.json` | Modify | Privacy provenance |
| `evals/behavioral/cases/privacy-*.json` | Create | Cases 1–10 (subset may share files) |
| `evals/behavioral/transcripts/0N-privacy-*.md` | Create | Matching transcripts |
| `scripts/check_behavioral_invariants.py` | Modify | Privacy invariant checks |
| `distribution.yaml` | Modify | Globs for privacy files |
| `README.md`, `QUICKSTART.md`, `docs/DEMO.md` | Modify | Trust surfaces |
| `VERSION`, `manifest.json`, `CHANGELOG.md`, `docs/ROADMAP.md` | Modify | 3.24.0 release notes |

**Distribution note:** Add mirror entry so root `PRIVACY.md` → `references/PRIVACY.md` (file mirror) in `distribution.yaml`, same pattern as VERSION/manifest.

---

### Task 1: Branch + privacy preflight (TDD)

**Files:**
- Create: `scripts/privacy_preflight.py`
- Create: `scripts/test_privacy_preflight.py`

**Interfaces:**
- Produces:
  - `Finding` dict: `{"category": str, "span_hint": str, "severity": "block"|"warn"}`
  - `preflight(text: str) -> dict` with keys: `findings`, `blocked_categories`, `safe_for_egress: bool`, `redacted_text: str`
  - Categories used: `credentials`, `secrets`, `passwords_connection`, `financial`, `contact_lists`
  - `safe_for_egress` is `False` if any finding has `severity == "block"`

- [ ] **Step 1: Create branch**

```bash
cd /home/scrimshawlife/Neon-Genie-Hermes
git checkout main
git pull --ff-only 2>/dev/null || true
git checkout -b feat/privacy-spine-w1
```

- [ ] **Step 2: Write failing unit tests**

Create `scripts/test_privacy_preflight.py`:

```python
#!/usr/bin/env python3
"""Unit tests for privacy_preflight (stdlib only)."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import privacy_preflight as pp  # noqa: E402


def test_api_key_blocks_egress() -> None:
    text = "deploy with sk-abc123DEF456ghi789jkl012mno345pqr678stu901vwx"
    r = pp.preflight(text)
    assert r["safe_for_egress"] is False
    assert "credentials" in r["blocked_categories"]
    assert "sk-abc123" not in r["redacted_text"] or "[REDACTED" in r["redacted_text"]
    print("PASS: api key blocks egress")


def test_pem_private_key_blocks() -> None:
    # Built at runtime so secret scanners do not match a contiguous PEM block in source.
    text = (
        "-----BEGIN "
        + "RSA PRIVATE KEY-----\n"
        + "TESTONLY_NOT_A_REAL_KEY_MATERIAL\n"
        + "-----END "
        + "RSA PRIVATE KEY-----"
    )
    r = pp.preflight(text)
    assert r["safe_for_egress"] is False
    assert "secrets" in r["blocked_categories"]
    print("PASS: pem blocks egress")


def test_bearer_token_blocks() -> None:
    # Opaque non-JWT token: still matches Bearer detector, not GitHub JWT/bearer secret rules.
    text = "Authorization: Bearer " + "test_opaque_token_" + "abcdefghijklmnopqrstuvwxyz0123456789"
    r = pp.preflight(text)
    assert r["safe_for_egress"] is False
    print("PASS: bearer blocks egress")


def test_benign_product_copy_safe() -> None:
    text = (
        "We sell an audio continuity tool for podcast editors. "
        "Pricing is unknown. Buyer is missing. Research public competitors."
    )
    r = pp.preflight(text)
    assert r["safe_for_egress"] is True
    assert r["blocked_categories"] == []
    print("PASS: benign product copy safe")


def test_password_in_url_blocks() -> None:
    text = "postgres://admin:SuperSecret99@db.example.com:5432/app"
    r = pp.preflight(text)
    assert r["safe_for_egress"] is False
    assert "passwords_connection" in r["blocked_categories"] or "credentials" in r["blocked_categories"]
    print("PASS: connection string blocks")


def main() -> int:
    test_api_key_blocks_egress()
    test_pem_private_key_blocks()
    test_bearer_token_blocks()
    test_benign_product_copy_safe()
    test_password_in_url_blocks()
    print("PASS: all privacy_preflight tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 3: Run tests — expect FAIL (module missing)**

```bash
python scripts/test_privacy_preflight.py
```

Expected: `ModuleNotFoundError: No module named 'privacy_preflight'` or import error.

- [ ] **Step 4: Implement `scripts/privacy_preflight.py`**

```python
#!/usr/bin/env python3
"""Deterministic secret/PII preflight before external egress (stdlib only).

High-precision on credentials/secrets; fail closed on API keys and private keys.
Does not claim complete PII detection.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

_PATTERNS: list[tuple[str, re.Pattern[str], str]] = [
    (
        "secrets",
        re.compile(
            r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----[\s\S]*?"
            r"-----END (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
            re.I,
        ),
        "block",
    ),
    ("credentials", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"), "block"),
    (
        "credentials",
        re.compile(r"\b(?:api[_-]?key|apikey)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}", re.I),
        "block",
    ),
    ("credentials", re.compile(r"\bBearer\s+[A-Za-z0-9\-._~+/]+=*", re.I), "block"),
    ("credentials", re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "block"),
    (
        "passwords_connection",
        re.compile(r"(?:postgres|mysql|mongodb|redis|amqp)://[^\s:]+:[^\s@]+@", re.I),
        "block",
    ),
    ("passwords_connection", re.compile(r"\bpassword\s*[:=]\s*\S+", re.I), "block"),
    (
        "financial",
        re.compile(r"\b(?:4\d{12}(?:\d{3})?|5[1-5]\d{14}|3[47]\d{13})\b"),
        "block",
    ),
]


def preflight(text: str) -> dict[str, Any]:
    if not text:
        return {
            "findings": [],
            "blocked_categories": [],
            "safe_for_egress": True,
            "redacted_text": text or "",
        }
    findings: list[dict[str, str]] = []
    blocked: set[str] = set()
    redacted = text
    for category, pattern, severity in _PATTERNS:
        for m in pattern.finditer(text):
            span = m.group(0)
            findings.append(
                {
                    "category": category,
                    "span_hint": span[:48] + ("…" if len(span) > 48 else ""),
                    "severity": severity,
                }
            )
            if severity == "block":
                blocked.add(category)
        if severity == "block":
            redacted = pattern.sub(f"[REDACTED:{category}]", redacted)
    return {
        "findings": findings,
        "blocked_categories": sorted(blocked),
        "safe_for_egress": len(blocked) == 0,
        "redacted_text": redacted,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Neon Genie privacy preflight")
    parser.add_argument("--text", default="")
    parser.add_argument("--file", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    text = args.text
    if args.file is not None:
        text = args.file.read_text(encoding="utf-8")
    result = preflight(text)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("safe_for_egress:", result["safe_for_egress"])
        print("blocked_categories:", ",".join(result["blocked_categories"]) or "(none)")
        for f in result["findings"]:
            print(f"  [{f['severity']}] {f['category']}: {f['span_hint']}")
    return 0 if result["safe_for_egress"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Run tests — expect PASS**

```bash
python scripts/test_privacy_preflight.py
```

Expected: `PASS: all privacy_preflight tests`

- [ ] **Step 6: Commit**

```bash
git add scripts/privacy_preflight.py scripts/test_privacy_preflight.py
git commit -m "feat: privacy preflight for secret/credential egress blocking"
```

---

### Task 2: Receipt privacy provenance

**Files:**
- Modify: `schemas/run-receipt.schema.json`
- Modify: `scripts/build_receipt.py`
- Create: assertions in `scripts/test_privacy_surface.py` (start file)

**Interfaces:**
- Produces receipt fields (always on packaging receipts):
  - `privacy_mode`: `"LOCAL_ONLY"` default for packaging CLI
  - `privacy_contract_version`: `"1.0.0"`
  - `data_sources_used`: `["operator_input"]` default when packets/brief implied; else `["operator_input"]` for packaging
  - `external_actions`: `[]`
  - `artifact_paths`: `[]` (envelope builder may enrich later) or list of packet paths if provided
  - `telemetry_status`: `"disabled"`
  - `retention_statement`: fixed string from spec
  - `privacy_warnings`: `[]`
  - `deletion_instructions`: string mentioning operator-selected output paths
  - `redaction`: `{"enabled": true, "blocked_categories": [], "events": []}`
  - `research_policy`: `{"enabled": false, "offline": true}`
  - `profiles_loaded` always includes `"privacy"` after `"core"`

**Retention statement (exact default):**

```text
Neon-Genie-owned artifacts live only under operator-selected paths listed in artifact_paths; delete those paths to remove them. Host/provider retention is outside this skill.
```

**Deletion instructions (exact default):**

```text
Remove the directories/files listed in artifact_paths (and any explicit learning-ledger path). Uninstalling the skill does not delete prior run outputs.
```

FULL_CONTENT_CONTINUES_IN_/tmp/neon-plan.md_BYTES_FROM_HERE