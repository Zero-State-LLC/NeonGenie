# Neon Genie Roadmap

Sibling skill to Kubrick: **shared architecture patterns**, separate domain (opportunity / product intelligence, not cinematic engineering).

## Wave 1 — Ops shell

Installable skill root, Hermes runtime contract, `install.sh`, VERSION/CHANGELOG/QUICKSTART, smoke validator, examples + evals skeleton, flatten nested package.

**Status:** shipped as **v3.2.0**.

## Wave 2 — Domain depth

- Thicken profile contracts
- Fill missing packet schemas (`EvidenceIntelligencePacket`, `MemeticPressurePacket`, `AuditDeliveryPacket`)
- Richer golden/eval cases and anti-overclaim references

**Status:** shipped as **v3.3.0**.

## Wave 3 — Thin operator surface

Optional packaging CLI only (no product brain in Python):

```text
python scripts/neon_genie.py do check | validate | route | receipt
```

**Status:** shipped as **v3.4.0**.

## Wave 4 — Release maturity

CI evals workflow, release checklist, version audit, fixture invariants.

**Status:** shipped as **v3.5.0**.

## Wave 5 — Executable evals + recipes

- Deterministic golden gate runner (`do eval`) comparing case `expected` to gate logic
- Product-audit packaging recipe (`do recipe`) for first operator path
- CI artifacts from recipe output

**Status:** shipped as **v3.6.0**.

## Wave 6 — Recipe family + deeper validation

- Multi-recipe dispatcher (product-audit, zero-option variants, fragmentation)
- Typed packet validation subset + strict authority checks
- Expanded golden gates (fictional resource, scorecard override ban)
- Sample packets for offline validation demos

**Status:** shipped as **v3.7.0**.

## Premiere program (post packaging waves)

See `docs/superpowers/specs/2026-07-30-neon-genie-premiere-program-design.md`.

| Wave | Status |
|------|--------|
| P0 Evidence spine | shipped **3.8.0** |
| P1 Prose excellence | shipped **3.9.0** (golden transcripts + `do transcripts`) |
| P2 Outcome density | shipped **3.10.0** (completion_proof, learn ledger, post-SEAL) |
| P3 Category ownership | shipped **3.11.0** (`docs/PREMIERE.md`, `docs/DEMO.md`, gallery) |

## Premiere program complete (P0–P3)

Public entry points:

- [PREMIERE.md](./PREMIERE.md) — thesis & comparison  
- [DEMO.md](./DEMO.md) — 10-minute path  
- [examples/gallery/](../examples/gallery/) — sanitized exemplars  

## Maintenance / corpus depth

| Release | Focus |
|---------|--------|
| **3.12.0** | Commercial + audit recipes; `do doctor` full-suite smoke |
| **3.13.0** | Agentic/memetic recipes; transcripts 06–07 (x402 / Gate D) |
| **3.14.0** | Evidence + opportunity recipes; transcripts 08–09 (10 recipes, 9 goldens) |
| **3.15.0** | README How to use; simplified `do <job>` help for agents & users |
| **3.16.0** | Hermes Skills Hub tap package (`skills/neon-genie/`) + distribution docs |
| **3.17.0** | Hub-hardened package: allowlisted mirrors + dual-path resolver so hub install runs `do doctor` |
| **3.18.0** | Distribution spine: single-source mirrors, generated hub contract, negative packaging tests, OS smoke matrix |
| **3.19.0** | Live Hermes behavioral verification: semantic invariants + isolated hub runtime smoke |
| **3.20.0** | Canonical run-envelope.json, lineage IDs, schema versioning policy |
| **3.21.0** | Operator surface: do run, do capabilities, worked example, tighter README |
| **3.22.0** | Feedback loop: issue templates, learn↔run_id reconcile, ADRs |
| **3.23.0** | Release automation, branch protection, gates.yaml registry, CONTRIBUTING |
| **3.24.0** | Privacy-by-construction spine + runtime (issues #15 + #17); tagged `v3.24.0` |
| **3.25.0** | Founder cold-start: founder-language routing, capital_sprint recipe, default transitional-builder job shape, hub list after doctrine, judgment honesty |
| **3.26.0** | Hermes packaging wizard (`do wizard`), presets, `references/wizard.md` |
| **3.27.0** | Gate ISO; PaperPilot PILOT; required `logic_label` / envelope `stage` / `evidence_ledger`; CLEAR BRIC / CITE / LEDGER / LOGIC / STAGE (`#14`) |
| **3.28.0** | Bake-off follow-up: research adapters, input-contradiction pass, numeric kill criteria, first-commit handoff, one-page prose plus appendix, dual fixture judges. Opportunity/commercial schema **1.2.0** (1.1.0 packets still validate). |
| **3.29.0** | Round-2 follow-up: stronger note arithmetic, kill recomputation, OBSERVED date and quote checks, free robots.txt fetch, tie-breaker judge. Opportunity/commercial schema **1.3.0** (older packets still validate). |
| **3.30.0** | Round-3 fixes: quote negation and whole-token numbers, OBSERVED placeholder words on every labeled field, kill derivations that ignore declared tiers or fees, general note-scan checks, robots.txt 404 and a 2 MiB body cap, Los Angeles retrieval dates, optional Jev line-id correctness diagnostic. Schema stays **1.3.0**. |
| **3.31.0** | Round-4 fixes: numeric note flags stay on the main page only when they recompute, money-table mismatches print `notes say X, recomputed Y`, unconfirmed flags go to an unverified appendix, capped per-idea research (free fetch first; paid search off unless keyed), optional one-action cheapest test. Schema stays **1.3.0**. |
| **3.32.0** | Firecrawl `POST /search` fills the capped paid-search slot. On only when `NEON_GENIE_RESEARCH_PAID=1` and `FIRECRAWL_API_KEY` are set. Credit cost uses `DOLLARS_PER_CREDIT` (default 0.005). Schema stays **1.3.0**. |

Also on main around this line: **capital_sprint** profile/protocol and **external-signals** corpus (labeled references).

**Schema thicken (this PR, unreleased):** opportunity-packet and
commercial-simulation move from empty `{}` shapes to Hermes-native typed
properties (artifact schema **1.1.0**). Optional mining fields stay
optional. CAC/LTV cannot be `OBSERVED` without `evidence_refs`. Andrey
`engine_tag` (`labor`|`capital`|`arbitrage`|`insurance`) plus
`arbitrage_expires` remain a **PRISM adaptation sidecar** — not part of
the Hermes hub packet, so MIT package consumers are not forced onto PRISM
engine taxonomy.

## Production maturity (3.18–3.23) — complete

| Theme | Shipped |
|-------|---------|
| Distribution spine | `distribution.yaml`, mirrors, generated Hub support list |
| Runtime proof | Behavioral suite + hub-layout smoke (no LLM keys required) |
| Artifact protocol | Mandatory `run-envelope.json`, lineage IDs, schema versioning |
| Operator surface | `do run`, `do capabilities`, worked README example |
| Feedback loop | Issue templates, learn↔run_id reconcile, ADRs |
| Governance | Tag-driven Release workflow, branch protection, CONTRIBUTING |

## Privacy spine (3.24.0) — shipped

| Theme | Shipped |
|-------|---------|
| Human + hub contract | `PRIVACY.md`, `references/PRIVACY.md`, ADR 0006, `references/privacy-contract.md` |
| Doctrine | Always-on `privacy` profile, gates S–Y, egress rune in research loop |
| Runtime engine | `scripts/privacy_runtime.py` — `local_only` default, purpose-bound consents, `REDACT_THEN_ALLOW` |
| Packaging surface | Receipt/envelope privacy provenance, `do privacy --json`, doctor diagnostics, NG-PRIV-* validation |
| Helpers & tests | `privacy_preflight.py`, runtime/integration unit tests, 12 behavioral cases (incl. privacy) |
| Hub parity | Distribution spine mirrors + package under `skills/neon-genie/` |

**Program next (optional waves):** W2 Outcomes ∥ W3 Judgment in parallel, then W4 distribution/announce polish. Interfaces: privacy fields on receipt/envelope, `do privacy`, Wayfinder remains optional handoff only. This schema thicken does not change that order.

Design/plan: `docs/superpowers/specs/2026-08-06-neon-genie-privacy-spine-design.md` · `docs/superpowers/plans/2026-08-06-neon-genie-privacy-spine.md` (full clone)

Public entry: [README](../README.md) · [DEMO](./DEMO.md) · [PRIVACY](../PRIVACY.md) · [HERMES_DISTRIBUTION](./HERMES_DISTRIBUTION.md) · [GOVERNANCE](./GOVERNANCE.md)

### Optional later (not blocking)

- Live multi-turn Hermes LLM evals when host keys exist (see `evals/LIVE_EVALS.md`; doctor/CI stay fixture-only)
- Official Nous `optional-skills/` merge ([PR #75028](https://github.com/NousResearch/hermes-agent/pull/75028) — leaf refreshed for 3.25.0 authoring standards)
- Discord/social announce with install one-liner
- Shorter community install path (repo rename / skills monorepo)
- Profile capability-contract router (beyond keyword routing)
- Required PR reviews when collaborators join

## Non-goals (all waves)

- Merging Neon Genie and Kubrick domains
- Auto-execution, spending, or canon promotion
- Shared monorepo runtime library (revisit only after Wave 2 if a third skill needs a scaffold)
