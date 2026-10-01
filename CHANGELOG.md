# Changelog

All notable changes to Neon Genie are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses semantic versioning.

## [3.31.0] — 2026-10-01

Round-4 bake-off fixes on v3.30.0. Honesty stays: no invented buyers,
revenue, prices, or sources. Artifact schema stays **1.3.0**. New fields
are optional. Older packets still validate. The build handoff is unchanged.

### Fixed

- A numeric note-scan flag reaches the main packet only when its operands
  are re-parsed from the cited lines and the recomputed value still
  disagrees. The false flag `Double of 64 is 128, not 512` (the notes mean
  $256 × 2 = $512) is not stated as fact.
- Other unconfirmed flags, including a credit compared across two price
  tiers and a list price compared to a different series' floor, move to
  `appendix.unverified_scanner_notes`. Each note is labeled not confirmed
  and `NOT_COMPUTABLE`.
- Money-table rows recompute. A mismatch is `notes say X, recomputed Y`.
  The Alta notes say burn 35000 per month; rent at 10k sf × $5.50/sf/mo
  recomputes to 55000. The Autogive Heavy per-tenant row says 636; the
  seat, infra, and low token band recompute to 336.4.

### Added

- Optional capped research per idea (`scripts/research_mode.py`
  `run_idea_research`). Free robots-aware fetch runs first. A paid search
  provider is pluggable and off unless `NEON_GENIE_RESEARCH_PAID=1` and
  `NEON_GENIE_SEARCH_API_KEY` is set, or a test injects the provider.
  Defaults: 5 calls and $0.20 per idea, $1.00 per run. Over cap, or no
  key, the query is skipped and marked `NOT_FETCHED`. OBSERVED claims
  still require a URL and an America/Los_Angeles retrieval date. Tests
  mock the provider. No source is invented.
- Optional `cheapest_test`: one action, a numeric threshold, a binary
  comparison, and a `check_date`. A multi-step list or a test without
  that dated pass/fail fails (NG-TEST-001). Model: one prepaid pilot at
  the floor price; kill if no one pays by the date.

### Changed

- VERSION **3.31.0**. Research user agent `neon-genie-research/3.31`.
- What the round-4 judge could not score from these fixtures is marked
  `NOT_COMPUTABLE` in the unverified appendix, not promoted to OBSERVED.

## [3.30.0] — 2026-10-01

Round-3 bake-off fixes on v3.29.0. Honesty stays: no invented buyers,
revenue, or prices. Artifact schema stays **1.3.0**. `derivation.justification`
is an optional string the packaging check reads when an identity kill would
otherwise ignore price tiers or card fees declared elsewhere in the packet.
Older packets still validate.

### Fixed

- Quote support flips polarity on not, no, never, without, and n't, and
  matches numbers only as whole tokens. `402` inside `x402` is not the
  number 402. An "allowed" claim cited to "not allowed" fails (NG-LABEL-002).
- Placeholder dates and placeholder words are checked on every string field
  of any object labeled OBSERVED, including `note` (NG-LABEL-001).
- A cost kill whose derivation leaves out price tiers or card fees stated
  elsewhere in the same packet fails (NG-KILL-006). An identity derivation
  ("taken as-is") passes that check only with a written `justification`.
  The recomputed net `485.2` still passes.
- The note scan no longer uses phrase rules fitted to round 1–2 packet
  wording. It flags the same quantity stated twice, a monthly figure that
  does not match the yearly figure (including per-sf), mutually exclusive
  options both locked or one locked while another stays the recommendation,
  a count series that is not the line implied by its larger counts, a list
  price under the floor at the count the note says to use, sums and
  percent-of and per-unit totals that do not equal the stated result, a
  date interval that ends before it starts, a rationale whose high/low
  words match a different option, one credit that covers inconsistent
  months, a computed double missing from later totals, the same magnitude
  marked both UNVERIFIED and OBSERVED, an OBSERVED section that also says
  unverified and whose figure is reused as fact, and an action that is
  both required and excluded. Classes that need world knowledge or
  judgment stay NOT_COMPUTABLE for the scanner.
- `robots_http` treats a missing robots.txt as allowed, including urllib
  `HTTPError` 404. Page bodies use a 2 MiB cap (`MAX_BODY_BYTES`); a larger
  body is still rejected whole. `retrieved_at` is the America/Los_Angeles
  calendar date.

### Added

- Optional Jev correctness diagnostic in `scripts/judge_eval.py`
  (`judge_correctness`, off by default). Jev System One returns Choice,
  Score, and Noul answers, not prose, so the diagnostic asks for a document
  line id and a SOURCE_NOTES line id and quotes those lines. The key is
  `TYPESAFE_AI_API_KEY` and is never logged. Golden evals leave the
  diagnostic off. Tests inject a mock client.
- `scripts/eval_note_scan.py` reports catch rate on the 16 raw-note issues
  and false positives on clean docs and synthetic notes.
- `scripts/jev_client.py`, a stdlib client for `POST /v1/systemone`.

### Changed

- VERSION **3.30.0**. Research user agent `neon-genie-research/3.30`.

## [3.29.0] — 2026-10-01

Round-2 bake-off follow-up on v3.28.0. Honesty stays: no invented buyers,
revenue, or prices. Schema **1.3.0** is additive. Packets below 1.3.0 still
validate. See `schemas/migrations/1.2.0-to-1.3.0.md`.

### Added

- Note scan arithmetic for price × seats, fee-inclusive totals, flat per-unit
  floors, and same per-seat rates, plus option-rationale overlap, verification
  clashes, banned-upsell vs paid-funnel, scope clashes, and buyer-rail clashes.
  `$300k` is 300000, not 300.
- Kill recomputation (`derivation`) for schema 1.3.0. `min_tier_net_of_fee`
  requires every tier, the percent fee, and the fixed fee (NG-KILL-004,
  NG-KILL-005).
- OBSERVED placeholder dates fail (NG-LABEL-001). A cited quote that does not
  support the claim fails (NG-LABEL-002). Inconclusive quotes fail closed
  unless a pluggable quote judge returns `supports` (NG-LABEL-003).
- Free `robots_http` adapter. It honors robots.txt and does not fetch when
  robots cannot be read. Paid adapters stay opt-in and are not bundled. CI
  uses fixtures.
- Tie-breaker judge in `scripts/judge_eval.py`. It runs only when the first
  two judges disagree on the pairwise winner.

### Changed

- Opportunity packet and commercial simulation document `$id` **1.3.0**.
- Packaging recipes emit schema 1.3.0 packets. Their kill thresholds are
  identity derivations of the stated test count, not observed prices.
- VERSION **3.29.0**.

## [3.28.0] — 2026-10-01

Bake-off follow-up (2026-09-30, five ideas). Honesty stays: no invented
buyers, revenue, or prices. Schema **1.2.0** is additive. Packets below
1.2.0 still validate. See `schemas/migrations/1.1.0-to-1.2.0.md`.

### Added

- Research mode (`scripts/research_mode.py`): pluggable `null`, `fixture`,
  and opt-in `stdlib_http` adapters. A gathered item is `OBSERVED` only
  with an http(s) URL, a retrieval date, and a complete body. Offline and
  `research.enabled=false` do not call an adapter and add no OBSERVED claims.
- Input-contradiction pass (`input_contradictions`) before the packet is
  written: contradictions, arithmetic errors, inconsistent figures.
- Structured `kill_criteria` (metric, numeric threshold, comparison,
  check date, data source). Prose fails validation (NG-KILL-001).
- `build_handoff.first_commit`: areas to touch, done-when, one test, owner role.
- One-page decision prose (450 words, 3200 characters). Long evidence moves
  intact into `appendix`. The writer does not truncate.
- Dual-judge eval harness (`scripts/judge_eval.py`): two fixture judges,
  neutral criteria (founder usefulness, correctness, actionability) plus
  the skill criteria, shuffled order, A/B swap. No paid API calls.
- Golden cases for each of the six changes. `scripts/test_bakeoff_six.py`
  runs from `do doctor`.

### Changed

- Opportunity packet and commercial simulation document `$id` **1.2.0**.
- Opportunity and commercial packaging recipes emit schema 1.2.0 packets
  on the offline path.
- VERSION **3.28.0**.

## [Unreleased]

### Added

- Org multi-agent SDLC pack: short `AGENTS.md` (with Escalation), thin
  `CLAUDE.md` pointer, and `intent/` README + `_TEMPLATE.md`. Docs-only;
  no `SKILL.md` rewrite and no Noema deploy dumps.
- PaperPilot / research-search-dag goldens: `paperpilot-invent-cite`,
  `paperpilot-incomplete-not-computable`, optional `boring-prfaq-hold`.
- `evals/LIVE_EVALS.md` — how to run live multi-turn Hermes LLM evals when
  host keys exist; Grok-host without Hermes is fixture-only. `do eval --live`
  reports readiness only and never calls a model. Doctor smoke stays key-free.
- Typed sample `examples/packets/sample-commercial.packet.json`.

### Changed

- SkillEvaluator `metadata.author` in frontmatter (`Name <email>` shape)
- Root license and SPDX guidance are MIT going forward (Copyright 2026 Zero State LLC)
- Hermes Skill Evals stay ubuntu-only (`skill` job); hosted `macos-latest` smoke runners are not used
- Hub-safe doc links: ADR and superpowers paths are path text on a full clone; curated hub docs include `GOVERNANCE.md`
- Opportunity packet schema **1.1.0**: typed required shapes plus optional
  Hermes-native mining fields (`affected_user`, `economic_buyer`,
  `transition_market`, `coordination_gap`, `service_first_wedge`,
  `distribution`, `failure_modes`, `jtbd`). Existing required keys unchanged.
- Commercial simulation schema **1.1.0**: typed `buyer_map` (economic_buyer,
  beneficiary, evidence_refs), `pricing_model` (`model_type` + labeled
  assumptions), optional `scenarios[]` with `claim_label`. Packaging rejects
  CAC/LTV labeled `OBSERVED` without `evidence_refs` (NG-COMM-001 / Gate B).
- `engine_tag` / `arbitrage_expires` stay **PRISM-sidecar-only** — not baked
  into the Hermes MIT packet schemas.

## [3.27.0] — 2026-09-05

Shipped on org SoT as `#14` (`8292a1e`). Fail-closed after the 3.26.x
warn-then-require window.

### Changed

- **Required fields:** `logic_label` (`effectual`|`causal`|`mixed`) on
  opportunity / product / zero-option packets (Gate LOGIC); `stage`
  (`shape`|`test`|`scale`) on run-envelope (Gate STAGE); `evidence_ledger`
  on EvidenceIntelligence packets (Gate LEDGER).
- Gate ISO: irreversible work requires conjunction `independent` ∧ versioned
  log pointer; alias table packet `validation_isolation.*` ↔ graph
  `validation_step.*`; `validation_log_version` on graph `validation_step`.
- CLEAR also enforces BRIC (means inventory before buy/build), CITE (never
  generate paper/DOI/arXiv ids), LEDGER (active cite; unresolved
  Contradict/Invalidate blocks ≥TESTABLE), LOGIC, and STAGE.
- Public install/docs paths updated for repo rename **NeonGenie**
  (`scrimshawlife-ctrl/NeonGenie`, Pages `…/NeonGenie/`)

### Added

- PR-A: optional `validation_isolation` on WayfinderExecutionPacket; Gate ISO.
- PR-B: PaperPilot `research-search-dag` schema + Gate PILOT (write the DAG
  when research runs; fabricated DAG cites still Gate CITE).

## [3.26.1] — 2026-09-01

### Fixed

- `SKILL.md` frontmatter now matches Hermes Agent v0.21.0 (tag v2026.8.31):
  one-sentence `description` ≤60 characters, required author/license/platforms
  and `metadata.hermes.{tags, related_skills}`, frontmatter at byte 0.
- `do check` rejects folded or over-long descriptions so the skill index
  no longer truncates routing text at 57 characters.

### Changed

- Skill body uses the v0.21 section order (When to Use, Prerequisites, How to
  Run, Quick Reference, Procedure, Pitfalls, Verification).
- Packaging examples use `${HERMES_SKILL_DIR}` and Hermes `terminal`.
- Author credit is `Daniel Meyer (scrimshawlife-ctrl), Hermes Agent`. Applied
  Alchemy Labs / Zero State credit remains in the skill body.

## [3.26.0] — 2026-08-08

### Added

- **Hermes packaging wizard** (`do wizard`) — resolve-path plan resolver (default
  print-only) plus `--path quick` onboarding (doctor → sample product-audit)
- Presets: `doctor`, `check`, `privacy`, `product-audit`, `zero-option`,
  `opportunity`, `audit`, `route-sample`, `offline-scaffold`, `quick`
- Alias `wizard-quick` → `do wizard --path quick --auto`
- `references/wizard.md`, `schemas/wizard-answers.v1.schema.json`,
  `scripts/wizard.py`, `scripts/test_wizard.py`
- Design + plan:
  `docs/superpowers/specs/2026-08-08-neon-genie-hermes-wizard-design.md`,
  `docs/superpowers/plans/2026-08-08-neon-genie-hermes-wizard.md`

### Changed

- Everyday CLI help lists `wizard`; capabilities `cli_jobs` includes `wizard`
- SKILL.md / QUICKSTART document prefer-wizard agent protocol

### Added (prior unreleased)

- Schema-valid `examples/packets/sample-capital-sprint.packet.json`
- `CapitalSprintPacket` in SKILL output selection; `validate` / `capabilities` types

### Changed (prior unreleased)

- `do run --brief` auto-recipe prefers `capital-sprint` over commercial when both match
- Hub package no longer ships Pages assets, hallmark, or monorepo ADR/checklist bulk
- Public docs/README aligned to **3.25.0** (site link, founder prompts, capital-sprint CLI)
- Public install/docs paths updated for repo rename **NeonGenie**
  (`scrimshawlife-ctrl/NeonGenie`, Pages `…/NeonGenie/`)

## [3.25.0] — 2026-08-06

### Added

- **Founder cold-start** — language that maps solo/roadmap/limited-resource intent into
  opportunity + zero-option profile routes without VC false positives
- **`capital_sprint`** router triggers + packaging recipe for capital-constrained sprints
- Default transitional-builder job shape in SKILL.md (plain operator example)
- GitHub Pages landing under `docs/` (install-first for transitional builders)

### Changed

- Hub support file list moved below operating doctrine in SKILL.md
- Docs: packaging checks vs Hermes judgment (honesty boundary)

## [3.24.0] — 2026-08-06

### Added

- **Privacy-by-construction spine + runtime** (issue #15 + #17)
  - `PRIVACY.md` + `references/PRIVACY.md`, ADR 0006, gates S–Y doctrine
  - Always-on `privacy` profile; egress rune doctrine
  - Runtime engine `scripts/privacy_runtime.py` (contract 1.0.0): fail-closed
    `local_only` defaults, purpose-bound consents, `REDACT_THEN_ALLOW` safe queries
  - Receipt/envelope privacy provenance; packaging validation NG-PRIV-*
  - Deterministic preflight helpers; `do privacy --json` diagnostics
  - Behavioral privacy cases + golden evals; sample privacy-context packets

### Changed

- Profile router always co-loads `privacy` with `core`
- Brief/recipe `privacy:` config flows into receipt, envelope, and learning ledger

## [3.23.0] — 2026-07-30

### Added

- **Release automation** (`.github/workflows/release.yml`)
  - Tag `vX.Y.Z` → release check, full smoke, hub tarball + sha256, GitHub release notes from CHANGELOG
- **`do release-check`** / `scripts/release_check.py` — version + changelog + dist gate
- **`references/gates.yaml`** — canonical gate ontology
- **CONTRIBUTING.md** + **docs/GOVERNANCE.md**
- Main branch protection: required status check `eval`, no force-push/delete; delete head branch on merge

## [3.22.0] — 2026-07-30

### Added

- **Feedback loop**
  - GitHub issue templates: behavior, hub install, operator outcome, schema proposal
  - `do learn --run-id` / `--envelope` + routing/gate quality fields
  - `do reconcile` — link learning ledger entries to `run_id` envelopes
  - Classes: `false_route`, `false_gate`
  - ADRs under `docs/adr/` (authority, skill brain, hub mirrors, Wayfinder, claims)
- Learning reconcile tests; policy: never auto-apply to canon

## [3.21.0] — 2026-07-30

### Added

- **`do run`** — operator packaging path (`scripts/run_job.py`)
  - `--recipe` / `--brief` / `--text` → workspace + receipt + envelope
  - Auto-recipe from brief profiles; `--no-auto-recipe` for scaffold-only
  - Writes `HERMES_NEXT.md` (judgment stays in SKILL.md)
- **`do capabilities --json`** — machine-readable surface for orchestrators
- Operator surface tests (`scripts/test_operator_surface.py`)
- README worked example (audio tool / missing buyer) + compressed operator docs

### Changed

- CLI help lists `run` and `capabilities` in everyday jobs

## [3.20.0] — 2026-07-30

### Added

- **Canonical run envelope** (`run-envelope.json`) for every packaging recipe
  - `schema_id` / `schema_version` (`neon-genie/run-envelope` @ `1.0.0`)
  - `run_id`, artifact lineage IDs, `content_hash`
  - `primary_artifact`, `mode_status`, `promotion`, `wayfinder` ingest hints
  - `do envelope` / `scripts/build_envelope.py` + `scripts/lineage.py`
- Schema versioning policy: `references/schema-versioning.md`
- Envelope tests (`scripts/test_run_envelope.py`); doctor validates envelope
- Validator support for JSON Schema `const` and `pattern`

### Changed

- Expanded `schemas/run-envelope.schema.json` (required entry point for consumers)
- `recipe_common.finish` always writes and checks the envelope

## [3.19.0] — 2026-07-30

### Added

- **Behavioral verification suite** (`evals/behavioral/`, `do behavioral`)
  - Six semantic cases: DataRequest, research attempt, NOT_COMPUTABLE, advisory-only mutation refusal, Gate D, Wayfinder change-control
  - `scripts/check_behavioral_invariants.py` (`NG-RUNTIME-*` diagnostics)
- **Isolated runtime smoke** (`do runtime` / `scripts/hermes_runtime_smoke.py`)
  - Hub-layout install + check + behavioral + doctor without LLM keys
  - Optional `--hermes` path with isolated `HERMES_HOME`
- CI steps for behavioral suite and runtime smoke; doctor runs behavioral
- Dual-path `evals_dir()` prefers layouts that include `cases/`

## [3.18.0] — 2026-07-30

### Added

- **Distribution spine** (`distribution.yaml` + `scripts/distribution_spine.py`)
  - Single-source Hub mirrors, package parity, generated SKILL.md support list
  - `do dist verify|write|report` with stable `NG-PKG-*` diagnostics
  - Negative packaging tests (`scripts/test_distribution_spine.py`)
- CI: distribution verify + negative tests; hub-layout doctor smoke; OS/Python smoke matrix
- Doctor runs distribution verify on full tree; skips on Hub installs

### Changed

- `sync_skill_package.sh` delegates to `distribution_spine.py write`
- SKILL.md hub support file list is generated (markers `BEGIN/END HUB_SUPPORT_FILES`)

## [3.17.0] — 2026-07-30

### Added

- Hub-hardened layout: mirrors under allowlisted dirs
  - `references/schemas/`, `references/profiles/`
  - `examples/evals/` (cases + transcripts)
  - `references/VERSION`, `references/manifest.json`
- `scripts/paths.py` dual-path resolver (full tree or hub mirrors)
- Explicit **Hermes Hub support files** index in `SKILL.md` so hub install pulls scripts, schemas, profiles, recipes, and golden tests
- `sync_skill_package.sh` refreshes hub mirrors before packaging

### Changed

- Packaging scripts resolve schemas/profiles/evals/manifest/VERSION via dual paths
- `validate_hermes_skill.py` accepts hub layout (skips full-tree-only docs/CI paths)
- Schema/profile path docs prefer `references/…` for hub portability

## [3.16.0] — 2026-07-30

### Added

- Hermes Skills Hub packaging: `skills/neon-genie/` tap package
- `skills.sh.json` Product Intelligence grouping
- `scripts/sync_skill_package.sh` to refresh the tap package
- `docs/HERMES_DISTRIBUTION.md` — install/tap/catalog submission paths
- SKILL frontmatter `metadata.hermes` (category, tags) for hub discovery

### Changed

- README/QUICKSTART install one-liners for `hermes skills install …`

## [3.15.0] — 2026-07-30

### Changed

- README: plain-English **How to use** (Hermes chat vs CLI), command cheat sheet, agent rules
- Simplified CLI help: jobs grouped (everyday / verify / outcomes)
- QUICKSTART aligned with the same command shape
- SKILL packaging section shortened to the `do <job>` table

## [3.14.0] — 2026-07-30

### Added

- Recipes: `evidence` (find/request scaffold) and `opportunity` (blocked transition + completion_proof)
- Briefs: `examples/evidence.brief.yaml`, `examples/opportunity.brief.yaml`
- Transcripts 08–09 (9 total goldens)
- Doctor/CI cover evidence + opportunity

### Changed

- Full profile-adjacent recipe surface (10 recipes)

## [3.13.0] — 2026-07-30

### Added

- Recipes: `agentic` (x402 REJECT scaffold) and `memetic` (Gate D promotion cap)
- Briefs: `examples/agentic.brief.yaml`, `examples/memetic.brief.yaml`
- Transcripts: `06-agentic-x402-misfit.md`, `07-memetic-cannot-promote.md` (7 total)
- Doctor suite smokes agentic + memetic recipes

### Changed

- Gallery/examples indexes; ROADMAP maintenance 3.13.0

## [3.12.0] — 2026-07-30

### Added

- Corpus depth: `commercial` and `audit` packaging recipes + briefs
- `do doctor` full-suite operator smoke (`scripts/doctor.py`)
- Gallery/examples index updates for new recipes

### Changed

- CI runs commercial/audit recipes and doctor suite
- ROADMAP maintenance section documents 3.12.0

## [3.11.0] — 2026-07-30

### Added

- Category ownership (Wave P3): `docs/PREMIERE.md` thesis & comparison vs idea agents
- `docs/DEMO.md` — 10-minute install → check → eval → recipe → learn path
- `examples/gallery/README.md` — sanitized briefs, packets, transcripts index
- README short comparison table + premiere/demo nav links
- RELEASE-CHECKLIST-v3.11

### Changed

- Premiere program P0–P3 marked complete on ROADMAP and design spec
- Skill validator requires PREMIERE.md, DEMO.md, gallery README

## [3.10.0] — 2026-07-30

### Added

- Outcome density (Wave P2): `completion_proof` required on opportunity/product/zero-option schemas
- `proof_path` property on those packets; recipes emit proof paths
- Learning ledger: `schemas/learning-ledger-entry.schema.json`, `do learn` / `record_learning.py` (PROPOSED only)
- `references/post-seal-verification.md` checklist
- Golden evals: completion-proof required/present (16 total)

### Changed

- SKILL SEAL/memory doctrine ties packets to proof + ledger
- Docs/ROADMAP premiere P2 marked shipping

## [3.9.0] — 2026-07-30

### Added

- Golden prose transcripts (`evals/transcripts/`) for five premiere scenarios
- Transcript rubric + structural checker: `do transcripts` / `scripts/check_transcripts.py`
- CI step for transcript checks
- Docs: premiere positioning in README, RELEASE-CHECKLIST-v3.8/v3.9, docs index

### Changed

- ROADMAP: P0 shipped, P1 shipped as 3.9.0
- Premiere design spec: P0 success criteria checked off

## [3.8.0] — 2026-07-30

### Added

- Evidence Request Protocol: find public → request private → only then `NOT_COMPUTABLE`
- `schemas/data-request.schema.json` and `examples/packets/sample-data-request.json`
- Anti-overclaim gates **P–R** (skip-find, skip-request, silent private invent)
- Receipt evidence fields: `data_requests`, `open_blocking_requests`, `research_attempts`, `evidence_protocol`
- `build_receipt.py --data-requests`; product-audit recipe surfaces open DataRequests
- Golden evals: public-gap find (P), private-gap request (Q), silent invent (R) — 14 total cases
- Premiere program roadmap section (P0–P3)

### Changed

- Skill doctrine, Hermes runtime contract, and CAPABILITY_MAP gates **A–R**
- Skill validator requires `schemas/data-request.schema.json`

## [3.7.0] — 2026-07-30

### Added

- Multi-recipe runner: `do recipe --name product-audit|zero-option|zero-option-executable|fragmentation`
- `scripts/recipe_common.py`, `scripts/recipe_run.py`
- Briefs: `fragmentation.brief.yaml`, `zero-option-with-skills.brief.yaml`
- Sample packets under `examples/packets/`
- Deeper packet validator (typed JSON Schema subset + `--strict-authority`)
- Eval cases: `fictional-resource`, `scorecard-cannot-override-gate`

### Changed

- `do recipe` defaults to multi-recipe dispatcher (product-audit still default name)
- CI runs all packaging recipes + sample packet validation

## [3.6.0] — 2026-07-30

### Added

- Golden gate eval runner: `python scripts/neon_genie.py do eval` (`scripts/run_hermes_evals.py`)
- Product-audit packaging recipe: `python scripts/neon_genie.py do recipe`
- CLI intents `eval` and `recipe`; aliases `run-evals`, `product-audit`
- CI runs golden evals + recipe; uploads `out/neon-genie/` artifacts
- `.gitignore` for generated `out/`

### Notes

- Eval runner enforces packaging-level gate logic against `evals/cases/*` expected fields
- Recipe emits route + receipt + Wayfinder handoff stub (no product invention)

## [3.5.0] — 2026-07-30

### Added

- GitHub Actions: `.github/workflows/hermes-evals.yml` (check, CLI tests, fixtures, version audit)
- `scripts/run_fixture_invariants.py`
- `scripts/audit_release_version.py`
- `docs/RELEASE-CHECKLIST-v3.5.md`

### Changed

- Roadmap Wave 4 marked shipped

## [3.4.0] — 2026-07-30

### Added

- Thin packaging CLI: `python scripts/neon_genie.py do <check|validate|route|receipt>`
- `scripts/validate_packet.py`, `route_profiles.py`, `build_receipt.py`
- `scripts/test_wave3_cli.py` regression harness

### Notes

- CLI is packaging-only (no product brain, no research, no execution authority)

## [3.3.0] — 2026-07-30

### Added

- Packet schemas: `evidence-intelligence`, `memetic-pressure`, `audit-delivery`
- `references/anti-overclaim-patterns.md` (gates A–O)
- Eval cases: memetic promote block, offline fabrication, buyer conflation, authority leakage
- Thickened profile contracts (triggers, required fields, CLEAR rules, schema pointers)

### Changed

- Profiles expanded for operational clarity without changing mission or authority
- SKILL output selection links all packet schemas

## [3.2.0] — 2026-07-30

### Added

- Root-level Hermes skill packaging (installable skill root)
- `install.sh` → `~/.hermes/skills/neon-genie`
- `references/hermes-runtime-contract.md`
- `scripts/validate_hermes_skill.py` smoke validator
- `VERSION`, `QUICKSTART.md`, `docs/ROADMAP.md`, `docs/README.md`
- `examples/` operator briefs
- `evals/` fixture home + rubric skeleton

### Changed

- Flattened nested `neon-genie/` package to repository root
- Version alignment across `VERSION`, `SKILL.md`, and `manifest.json`

### Migration

- Replace `cp -R neon-genie …` with `./install.sh` or copy the **repository root** into Hermes skills

## [3.1.0] — prior

- Proactive research by default
- MIT license
- Packaging README polish and social assets
