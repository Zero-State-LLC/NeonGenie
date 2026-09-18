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

PLACEHOLDER_TRUNCATED_WILL_REPLACE