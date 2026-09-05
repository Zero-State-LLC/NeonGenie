---
name: neon-genie
description: Audit products and opportunities with labeled evidence.
version: 3.26.1
author: Daniel Meyer (scrimshawlife-ctrl), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags:
      - Product
      - OpportunityIntelligence
      - ProductArchitecture
      - ZeroOption
      - Commercial
      - EvidenceBound
      - WayfinderHandoff
      - AdvisoryOnly
      - AgenticServices
    category: product
    related_skills: []
---

# Neon Genie Skill

Neon Genie is a standalone Hermes skill for evidence-bound product and opportunity intelligence. It drafts audits, opportunity packets, commercial models, agentic graphs, and Wayfinder handoffs with claim labels and fail-closed gates. It does not execute code, spend, publish, contact, or mutate repositories, and it is not cinematic work (use Kubrick). Credit: Applied Alchemy Labs / Zero State.

See `references/hermes-runtime-contract.md` for path, artifact, authority, and dependency policy. Profile contracts, packet schemas, and golden tests ship as hub mirrors and as root `profiles/`, `schemas/`, `evals/` on full install.

## When to Use

- Product intent, product audit, app/game/system design, or feature coherence.
- Opportunity mining, blocked transitions, roadmaps, or first-cash / zero-option work.
- Fragmentation, commercial simulation, agentic/x402 graphs, or evidence intelligence.
- Wayfinder execution-packet handoff, audit delivery, or capital-sprint planning.
- The operator needs labeled claims (`OBSERVED` / `INFERRED` / `SPECULATIVE` / `NOT_COMPUTABLE`) and fail-closed gates.

Do not use for:

- Cinematic or motif work (use Kubrick).
- Code execution, repo mutation, spend, publish, contact, or canon promotion.
- Treating packaging envelopes as execution authority.

## Prerequisites

- Hermes Agent that can load this directory and invoke `terminal`.
- Python 3 on PATH for the packaging CLI (stdlib only). No package install, API key, or secret is required to load.
- Optional companions: host research tools, Wayfinder (handoff consumer). Their absence never blocks local advisory work.
- Path, artifact, and authority rules: `references/hermes-runtime-contract.md`.
- Privacy contract: root `PRIVACY.md` and hub mirror `references/PRIVACY.md`; always-on profile `profiles/privacy.md`.

## How to Run

Frame every packaging command through Hermes `terminal`. Substitute `${HERMES_SKILL_DIR}` (Hermes replaces it with the installed skill root):

```text
terminal(command="python ${HERMES_SKILL_DIR}/scripts/neon_genie.py do <job> [options]")
```

When the operator is new, unsure which packaging job to run, or says “wizard” / “guide me” / “walk me through”:

1. Prefer `do wizard` over freestyling `do run` flags. Completion: a resolve plan is printed or a named recipe is queued.
2. Chat-driven Q&A (Desktop-safe): merge answers JSON → `do wizard --answers answers.json --print-only --json` → confirm → `--run`. Completion: plan JSON matches the answers file.
3. New install: `do wizard --path quick --auto` (doctor + sample product-audit). Completion: doctor exits 0 and a demo envelope exists.
4. After packaging, resume product judgment in chat (OPEN→SEAL). The envelope is not execution authority.

Load [references/wizard.md](references/wizard.md) while guiding. Packaging only — no invented opportunities, no ledger writes, no repo mutation.

See `README.md` (How to use) and `QUICKSTART.md`. Golden prose: `examples/evals/transcripts/README.md`. Post-SEAL: `references/post-seal-verification.md`. Gate ontology: `references/gates.yaml`.

## Quick Reference

```text
terminal(command="python ${HERMES_SKILL_DIR}/scripts/neon_genie.py help")
terminal(command="python ${HERMES_SKILL_DIR}/scripts/neon_genie.py do doctor")
terminal(command="python ${HERMES_SKILL_DIR}/scripts/neon_genie.py do check")
terminal(command="python ${HERMES_SKILL_DIR}/scripts/neon_genie.py do wizard --preset product-audit --print-only --json")
terminal(command="python ${HERMES_SKILL_DIR}/scripts/neon_genie.py do wizard --path quick --auto")
terminal(command="python ${HERMES_SKILL_DIR}/scripts/neon_genie.py do run --recipe product-audit --out out/neon-genie/demo")
terminal(command="python ${HERMES_SKILL_DIR}/scripts/neon_genie.py do privacy --json")
terminal(command="python ${HERMES_SKILL_DIR}/scripts/neon_genie.py do eval")
```

Jobs: `doctor` (full smoke), `wizard` (guided packaging), `privacy` (resolved boundary), `check` (skill integrity), `run` (brief/recipe → envelope), `capabilities` (JSON surface), `dist` (hub mirrors), `recipe` (named example), `route` / `validate` / `receipt` / `envelope`, `eval` / `transcripts`, `behavioral` / `runtime`, `learn` / `reconcile` (PROPOSED ledger only), `release-check`.

## Procedure

1. **Load as a standalone skill.** Hermes uses this `SKILL.md` as the operating contract. No Python package install, Kubrick skill, Wayfinder runtime, or external knowledge base is required to load. Completion: skill index shows `neon-genie` with an intact description.

2. **State the mission.** Convert weak signals, blocked state transitions, fragmented systems, raw ideas, and incomplete products into evidence-bound, externally testable, buildable opportunity systems. Neon Genie owns product and opportunity intelligence. It does not grant execution, forecast, governance, spending, publication, or canon-promotion authority. Completion: the operator can name the blocked transition and the desired state.

3. **Default operator job (transitional builders).** When the operator is developing an idea under constraint (solo, transitional, limited money/time/skills) and has not named a specialized recipe, still stay advisory only:
   1. Name the stuck point — who is blocked, current state, what “done” looks like.
   2. Capture constraints — time, money, skills, access. Never invent resources.
   3. Find → request → refuse — research public facts; emit `DataRequest` for private facts; label claims `OBSERVED` / `INFERRED` / `SPECULATIVE` / `NOT_COMPUTABLE`.
   4. Shape the plan — roadmap and/or approach options with `completion_proof` (externally checkable). Prefer profiles `opportunity_mining` and, when resources are scarce, `zero_option` (plus `product_architecture` only if a product/system boundary is in scope).
   5. Seal as drafts — packets + receipt; no spend, publish, contact, or repo mutation.

   Example Hermes prompt:

   ```text
   Use Neon Genie. I'm between jobs with limited money and an app idea.
   I need a realistic roadmap and first approaches I can actually run.
   Do not invent buyers, capital, or skills I did not declare.
   Research public facts if you can; request private facts with DataRequest.
   Label every important claim. Advisory only — do not modify any repo.
   ```

   Completion: every material claim has a label; missing private facts have a `DataRequest`.

4. **Research doctrine (default: proactive).** Automatically perform any research the host can run when it improves usefulness. Do not wait for the operator to name every source. Prefer a researched, labeled answer over a thin `NOT_COMPUTABLE` wall when facts are fetchable.

   Source stack (priority order):

   1. Operator-supplied — pasted evidence, attached files, declared URLs, explicit `canonical_sources`
   2. Workspace / host context — open repo, local files, prior run artifacts Hermes can read
   3. Live host research — web search, page fetch, academic indexes, docs, registries, market/public filings, standards, news, competitor sites, grant/board databases — *whatever tools the host exposes*
   4. Model prior — only as `SPECULATIVE` or scaffolding; never as `OBSERVED`

   No external knowledge base is required to *load* the skill. Research uses host-available tools at run time. If a tool class is unavailable, record the gap and continue with the best remaining stack.

   Run research during `ALIGN` and again in `ASCEND` whenever any of these hold:

   - a material claim would otherwise be `NOT_COMPUTABLE` or weak `SPECULATIVE` and is fetchable;
   - buyer, market, competitor, pricing, regulation, or technical feasibility is decision-critical;
   - grants, boards, philanthropy, standards, or current external facts affect the scorecard;
   - product/system claims depend on public APIs, licenses, or third-party capabilities;
   - the operator asked for an audit, opportunity, commercial model, or handoff packet.

   Research loop:

   ```text
   GAP_DETECT → QUERY_PLAN → PRIVACY_EGRESS_CHECK → FETCH (host tools) → NORMALIZE → CITE
     → LABEL (OBSERVED | INFERRED | SPECULATIVE | NOT_COMPUTABLE)
     → RE-SCORE → (repeat until usefulness plateaus or budget/tooling ends)
   ```

   Before every host research/tool send: classify → minimize → `RUNE.PRIVACY_EGRESS_CHECK` → only then FETCH. Outcomes: `ALLOW` | `REDACT_THEN_ALLOW` | `REQUEST_CONSENT` | `BLOCK`. Log attempts in receipt `external_actions`. See `profiles/privacy.md` and `references/PRIVACY.md`.

   Research rules:

   - Proactive by default — research is on unless the operator sets `research: false` or `offline: true`.
   - Smallest sufficient fetch — enough evidence for the decision, not infinite crawl.
   - Cite or drop — every `OBSERVED` claim needs a source pointer (URL, path, title+date, or tool result id).
   - Find → request private → `NOT_COMPUTABLE` — for public/fetchable gaps, attempt research first; for operator/private gaps, emit a `DataRequest` before (or instead of) `NOT_COMPUTABLE`; never invent.
   - Never fabricate — if fetch fails or tools are absent, mark `NOT_COMPUTABLE` with the attempted query (after find was attempted or correctly skipped offline, and after request when private).
   - Freshness — prefer primary/current sources; note retrieval time for volatile facts.
   - Attribution boundaries — separate person / company / foundation / model inference.
   - Authority unchanged — research may draft; it may not submit, contact, spend, publish, or mutate repos.
   - Privacy — do not probe private systems without declared access; public + operator-granted only; request private facts via `DataRequest`. Run egress check before host tools; credentials never leave; private/operator egress needs consent.

   Completion: every fetch is cited or dropped; egress decisions are logged.

5. **Evidence Request Protocol.** Priority when a material fact is missing:
   1. Find — if sensitivity is public (or unknown-but-likely-public) and host tools can run, attempt research; cite or drop.
   2. Request — if sensitivity is operator/private or access is undeclared, emit a `DataRequest` (`references/schemas/data-request.schema.json`) instead of inventing.
   3. `NOT_COMPUTABLE` — only after find was attempted (or correctly skipped offline) and/or a DataRequest is open or unanswered.
   4. Never mark model prior as `OBSERVED`.

   DataRequest required fields: `field`, `why_decision_critical`, `sensitivity` (`public`|`operator`|`private`), `suggested_source`, `blocks_promotion` (bool), `status` (`open`|`satisfied`|`waived`).

   CLEAR rules:

   - Public gap + tools available + no research attempt → fail (Gate P)
   - Private decision-critical gap + no DataRequest → fail (Gate Q)
   - Private/unknown fact labeled OBSERVED from model prior without source → fail (Gate R)
   - Open DataRequests with `blocks_promotion: true` cap promotion until satisfied or waived
   - Dual-logic / stage / means / cites (warn-then-require in 3.26.x; schemas optional):
     - Missing or mismatched `logic_label` (`effectual`|`causal`|`mixed`) when opportunity/product/zero-option CLEAR expects it → fail (Gate LOGIC)
     - Opportunity/agentic run missing `stage` (`shape`|`test`|`scale`), or `scale` without test evidence → fail (Gate STAGE)
     - Effectual / zero-option with empty means inventory and no DataRequest / NOT_COMPUTABLE → fail (Gate BRIC)
     - arXiv/DOI/paper claim without verified fetch or operator source → fail (Gate CITE); never fabricate citations
   - Claim graph / EviGraph ledger (warn-then-require in 3.26.x; optional `evidence_ledger` on EvidenceIntelligence + optional peer attach):
     - Material claim promotes without an **active ledger cite** (claim node + typed relation) → fail (Gate LEDGER)
     - Unresolved `Contradict` / `Invalidate` at ≥TESTABLE → fail (Gate LEDGER)
     - Invent-OBSERVED from model prior without ledger cite → fail (Gate LEDGER); fabricated paper IDs still Gate CITE
     - Final-answer fluency ≠ provenance; no invent Brier / auto-settle
   - Also apply (registry `references/gates.yaml`): HYP, METRIC, LIVE, CSET, LEDGER
   - CLEAR order: authority → evidence P–R → LOGIC/STAGE/BRIC/CITE/LEDGER → HYP/METRIC/LIVE/CSET → privacy S–Y → remaining anti-overclaim

   SEAL: run receipt must list `data_requests`, `open_blocking_requests`, and `research_attempts` (may be empty arrays). See `references/schemas/run-receipt.schema.json`.

   Privacy provenance (Gate Y / `RUNE.PRIVACY_SEAL_PROVENANCE`) is also required: `privacy_mode`, `privacy_contract_version`, `data_sources_used`, `external_actions`, `artifact_paths`, `telemetry_status` (`disabled`), `retention_statement`, `privacy_warnings`, `deletion_instructions`, `redaction`, `research_policy`. Contract: `PRIVACY.md` / `references/PRIVACY.md`.

   Opportunity, product, and zero-option packets at `TESTABLE` or higher require `completion_proof` (externally checkable) and should include a `proof_path`. After SEAL, follow `references/post-seal-verification.md`. Record real outcomes with:

   ```text
   terminal(command="python ${HERMES_SKILL_DIR}/scripts/neon_genie.py do learn --class proof_obtained --summary \"...\" --envelope out/neon-genie/demo/run-envelope.json --ledger out/neon-genie/learning-ledger.jsonl")
   terminal(command="python ${HERMES_SKILL_DIR}/scripts/neon_genie.py do reconcile --ledger out/neon-genie/learning-ledger.jsonl --runs-root out/neon-genie")
   ```

   Learning ledger entries are `PROPOSED` / `OBSERVATION` only — never auto-canon. Prefer linking via `--envelope` / `run_id`. Completion: receipt lists requests and research attempts; TESTABLE+ packets have `completion_proof`.

6. **Default operating sequence.** Always execute `OPEN` → `ALIGN` (gap-driven research plan + first fetch) → `ASCEND` (continue research when new gaps appear) → `CLEAR` → `SEAL` (source manifest lists every fetch). Every material claim must be labeled `OBSERVED`, `INFERRED`, `SPECULATIVE`, or `NOT_COMPUTABLE`. SHADOW detects drift and anomalies only. FORECAST performs evidence-based inference only. Completion: all five modes ran; unlabeled material claims are absent.

7. **Router.** Determine the smallest sufficient profile set. Additionally auto-load `evidence_intelligence` whenever external facts would change the recommendation, scorecard, or handoff quality — even if the operator did not name that profile.

   Load `references/profile-routing.md` when selecting specialized profiles; it preserves the full trigger registry. Core/privacy always apply, and evidence intelligence loads whenever external facts change the result.

   Do not activate a specialized product/commercial profile merely because it exists. Do activate research when usefulness requires it. Completion: selected profiles match triggers; unused specialized profiles stay unloaded.

8. **Core pipeline.**

   ```text
   SIGNAL
   → BLOCKED TRANSITION
   → OUTCOME MODEL
   → EVIDENCE GAPS
   → RESEARCH LOOP (PRIVACY_EGRESS_CHECK → host tools)
   → SYSTEM TOPOLOGY
   → OPPORTUNITY THESIS
   → INTERVENTION
   → PRODUCT / SERVICE GRAPH
   → VALIDATION LOOP
   → SCORECARD
   → ROUTING
   → VERIFIED OUTCOME
   → LEARNING MEMORY
   ```

   Core runes: `RUNE.NG.INTAKE`, `RUNE.NG.EVIDENCE.NORMALIZE`, `RUNE.NG.RESEARCH.GAP_DETECT`, `RUNE.NG.RESEARCH.QUERY_PLAN`, `RUNE.NG.RESEARCH.FETCH`, `RUNE.NG.RESEARCH.CITE`, `RUNE.NG.BLOCKED_TRANSITION`, `RUNE.NG.OUTCOME.MODEL`, `RUNE.NG.TOPOLOGY`, `RUNE.NG.DISCOVER`, `RUNE.NG.RECOMBINE`, `RUNE.NG.DIFFERENTIATE`, `RUNE.NG.SHAPE`, `RUNE.NG.SCORE`, `RUNE.NG.VALIDATE_PATH`, `RUNE.NG.ROUTE`, `RUNE.NG.CLEAR_CHECK`, `RUNE.NG.SEAL`, `RUNE.PRIVACY_CLASSIFY`, `RUNE.PRIVACY_MINIMIZE`, `RUNE.PRIVACY_EGRESS_CHECK`, `RUNE.PRIVACY_SEAL_PROVENANCE`.

   Completion: pipeline stages that ran are named in the receipt; skipped stages have a reason.

9. **Authority boundaries.** Neon Genie may research (proactively, via host tools), infer, generate, compare, score, model, audit, specify, route, draft, and recommend. Neon Genie may not, without explicit downstream authorization: spend or transfer money; submit applications; contact targets; publish content; modify repositories; execute irreversible workflows; promote artifacts to canon; represent forecasts as facts; mutate runtime state. Completion: no output claims execution authority.

10. **Output selection.** A run emits one or more of:

    Load `references/output-selection.md` for packet-to-schema mapping. Every run still emits a receipt and validates each emitted packet against its schema.

    Anti-overclaim gates: `references/anti-overclaim-patterns.md`. Privacy: `PRIVACY.md`, `references/PRIVACY.md`, `profiles/privacy.md`. Completion: emitted packets validate against the named schema.

11. **Promotion ladder.** `RAW_SIGNAL` → `MAPPED` → `CONCEPTUAL` → `TESTABLE` → `SERVICE_FIRST` → `SERVICE_PROVEN` → `SPEC_COMPLETE` → `WAYFINDER_READY` → `BUILD_READY` → `CANON_CANDIDATE` → `ARCHIVED` / `NOT_COMPUTABLE`. A composite score may never override a mandatory gate failure. Completion: promotion state matches the weakest mandatory gate.

12. **Mandatory gates.** Fail closed when:

    - the desired state is ambiguous;
    - the affected user is absent;
    - buyer and beneficiary are conflated;
    - completion proof is undefined;
    - critical integration access is unknown;
    - claims lack provenance;
    - a proposed action exceeds authority;
    - x402 is ornamental rather than economically useful;
    - Zero State benefit reduces portability or user control;
    - a concept duplicates an existing subsystem without wrapper classification;
    - the implementation handoff changes product intent;
    - missing data is fabricated instead of marked `NOT_COMPUTABLE` after research was attempted (or correctly skipped under offline mode);
    - public fetchable facts are skipped without a research attempt (Gate P);
    - private decision-critical facts lack a `DataRequest` (Gate Q);
    - private facts are silently invented as `OBSERVED` without source or request (Gate R);
    - external action sent with unknown/empty destination (Gate S);
    - offline / `LOCAL_ONLY` / research disabled but external send recorded (Gate T);
    - credential or secret-like payload would be or was sent (Gate U);
    - private/operator egress without consent reference (Gate V);
    - absolute privacy claim without matching mode and evidence (Gate W);
    - telemetry status is not `disabled` (Gate X);
    - SEAL without required privacy provenance fields (Gate Y);
    - opportunity/product/zero-option CLEAR without a coherent `logic_label` when dual-logic applies (Gate LOGIC);
    - opportunity/agentic run missing `stage`, or recommending `scale` without test evidence (Gate STAGE);
    - effectual / zero-option spend-buy-build without means inventory, or empty means without NOT_COMPUTABLE + DataRequest (Gate BRIC);
    - fabricated or unverified paper/DOI/arXiv citation (Gate CITE);
    - ≥TESTABLE without hypothesis↔MVP map (Gate HYP; distinct from Gate H Wayfinder);
    - decision-critical metric without role, or guardrail breached (Gate METRIC);
    - live A/B or pricing rec without offline causal pass and without human-yes (Gate LIVE);
    - market-share / competitive OBSERVED without competitor_set_definition + metric (Gate CSET);
    - material claim without active ledger cite, invent-OBSERVED without ledger, or unresolved Contradict/Invalidate at ≥TESTABLE (Gate LEDGER).

    Also apply anti-overclaim gates A–R and privacy gates S–Y in `references/anti-overclaim-patterns.md` during CLEAR. Registry: `references/gates.yaml` (includes LOGIC, STAGE, BRIC, CITE, HYP, METRIC, LIVE, CSET, LEDGER). Completion: CLEAR lists every failed gate or records none.

13. **Profile loading.** Load the relevant profile markdown contracts (hub mirror files listed below, or root profiles on full install) and follow their local contracts. Profile-specific runes must remain namespaced and must not silently change core outputs. Completion: each loaded profile file exists.

14. **Wayfinder contract.** Neon Genie determines what should be built, why it should exist, target user and blocked transition, product boundary, system behavior, success criteria, and proof requirements. Wayfinder determines work decomposition, dependency sequence, milestones, engineering validation, and implementation status. Any proposed change to product intent returns to Neon Genie as a change request. Completion: handoff packets do not rewrite product intent.

15. **Registry and memory.** Every run should record: source manifest (operator + workspace + live fetches, with tool and timestamp); research queries attempted and outcomes; input hash; selected profiles; assumptions; scores; promotion state; rejected alternatives; failure reasons; output hash; human review status.

    Neon Genie must become harder to impress over time by learning from failed opportunities, brittle integrations, buyer failures, distribution failures, and anti-capture failures. Capture those as append-only learning ledger observations (`references/schemas/learning-ledger-entry.schema.json`, `do learn`) with `canon_status: PROPOSED` only — never auto-apply to the skill corpus.

16. **Hermes Hub support files.** Hub installs copy only the generated list below.

### Hermes Hub support files


Hermes Hub installs only `SKILL.md` plus **explicitly path-referenced** files under allowlisted dirs (`references/`, `templates/`, `scripts/`, `assets/`, `examples/`). The list below is **generated** from `distribution.yaml` — run `python scripts/distribution_spine.py write` after adding packaging files:

<!-- BEGIN HUB_SUPPORT_FILES (generated; do not edit) -->
- `examples/README.md`
- `examples/agentic.brief.yaml`
- `examples/audit.brief.yaml`
- `examples/capital-sprint.brief.yaml`
- `examples/commercial.brief.yaml`
- `examples/evals/behavioral/README.md`
- `examples/evals/behavioral/cases/memetic-weak-proof.json`
- `examples/evals/behavioral/cases/privacy-api-key-block.json`
- `examples/evals/behavioral/cases/privacy-local-only-blocks-egress.json`
- `examples/evals/behavioral/cases/privacy-offline-no-send.json`
- `examples/evals/behavioral/cases/privacy-private-list-consent.json`
- `examples/evals/behavioral/cases/privacy-private-list-requires-consent.json`
- `examples/evals/behavioral/cases/privacy-unknown-retention-claim.json`
- `examples/evals/behavioral/cases/private-buyer-datarequest.json`
- `examples/evals/behavioral/cases/public-market-research.json`
- `examples/evals/behavioral/cases/repo-mutation-advisory-only.json`
- `examples/evals/behavioral/cases/wayfinder-change-control.json`
- `examples/evals/behavioral/cases/zero-resources-not-computable.json`
- `examples/evals/behavioral/transcripts/01-private-buyer-datarequest.md`
- `examples/evals/behavioral/transcripts/02-public-market-research.md`
- `examples/evals/behavioral/transcripts/03-zero-resources-not-computable.md`
- `examples/evals/behavioral/transcripts/04-repo-mutation-advisory-only.md`
- `examples/evals/behavioral/transcripts/05-memetic-weak-proof.md`
- `examples/evals/behavioral/transcripts/06-wayfinder-change-control.md`
- `examples/evals/behavioral/transcripts/07-privacy-local-only-blocks-egress.md`
- `examples/evals/behavioral/transcripts/07-privacy-offline-no-send.md`
- `examples/evals/behavioral/transcripts/08-privacy-api-key-block.md`
- `examples/evals/behavioral/transcripts/08-privacy-private-list-requires-consent.md`
- `examples/evals/behavioral/transcripts/09-privacy-private-list-consent.md`
- `examples/evals/behavioral/transcripts/10-privacy-unknown-retention-claim.md`
- `examples/evals/cases/authority-leakage.json`
- `examples/evals/cases/buyer-beneficiary-conflation.json`
- `examples/evals/cases/completion-proof-present.json`
- `examples/evals/cases/completion-proof-required.json`
- `examples/evals/cases/contradict-unresolved-testable.json`
- `examples/evals/cases/effectual-missing-means.json`
- `examples/evals/cases/fabricated-cite.json`
- `examples/evals/cases/fictional-resource.json`
- `examples/evals/cases/memetic-cannot-promote.json`
- `examples/evals/cases/offline-no-fabricated-observed.json`
- `examples/evals/cases/privacy-consent-purpose-bound.json`
- `examples/evals/cases/privacy-egress-local-only.json`
- `examples/evals/cases/privacy-secret-blocks-egress.json`
- `examples/evals/cases/private-gap-must-request.json`
- `examples/evals/cases/private-gap-request-open.json`
- `examples/evals/cases/private-gap-silent-invent.json`
- `examples/evals/cases/public-gap-must-attempt-research.json`
- `examples/evals/cases/public-gap-research-attempted.json`
- `examples/evals/cases/scale-without-test.json`
- `examples/evals/cases/scorecard-cannot-override-gate.json`
- `examples/evals/cases/uncited-claim.json`
- `examples/evals/cases/wayfinder-change-control.json`
- `examples/evals/cases/x402-misfit.json`
- `examples/evals/cases/zero-option.json`
- `examples/evals/rubric.md`
- `examples/evals/transcripts/01-zero-option-empty.md`
- `examples/evals/transcripts/02-product-audit.md`
- `examples/evals/transcripts/03-fragmentation.md`
- `examples/evals/transcripts/04-commercial-missing-buyer.md`
- `examples/evals/transcripts/05-offline-audit.md`
- `examples/evals/transcripts/06-agentic-x402-misfit.md`
- `examples/evals/transcripts/07-memetic-cannot-promote.md`
- `examples/evals/transcripts/08-evidence-intelligence.md`
- `examples/evals/transcripts/09-opportunity-mining.md`
- `examples/evals/transcripts/README.md`
- `examples/evals/transcripts/rubric.md`
- `examples/evidence.brief.yaml`
- `examples/fragmentation.brief.yaml`
- `examples/memetic.brief.yaml`
- `examples/opportunity.brief.yaml`
- `examples/packets/sample-capital-sprint.packet.json`
- `examples/packets/sample-data-request.json`
- `examples/packets/sample-external-action.json`
- `examples/packets/sample-opportunity.packet.json`
- `examples/packets/sample-privacy-context.json`
- `examples/packets/sample-purpose-bound-consent.json`
- `examples/packets/sample-receipt-with-requests.json`
- `examples/packets/sample-receipt.packet.json`
- `examples/packets/sample-run-envelope.json`
- `examples/privacy-external-research.brief.yaml`
- `examples/product-audit.brief.yaml`
- `examples/zero-option-with-skills.brief.yaml`
- `examples/zero-option.brief.yaml`
- `references/CAPABILITY_MAP.md`
- `references/GOLDEN_TESTS.md`
- `references/PRIVACY.md`
- `references/VERSION`
- `references/anti-overclaim-patterns.md`
- `references/gates.yaml`
- `references/hermes-runtime-contract.md`
- `references/manifest.json`
- `references/output-selection.md`
- `references/post-seal-verification.md`
- `references/privacy-contract.md`
- `references/profile-routing.md`
- `references/profiles/agentic_services.md`
- `references/profiles/audit_delivery.md`
- `references/profiles/capital_sprint.md`
- `references/profiles/commercial.md`
- `references/profiles/core.md`
- `references/profiles/evidence_intelligence.md`
- `references/profiles/fragmentation.md`
- `references/profiles/memetic.md`
- `references/profiles/opportunity_mining.md`
- `references/profiles/privacy.md`
- `references/profiles/product_architecture.md`
- `references/profiles/wayfinder_handoff.md`
- `references/profiles/zero_option.md`
- `references/schema-versioning.md`
- `references/schemas/agentic-service-graph.schema.json`
- `references/schemas/audit-delivery-packet.schema.json`
- `references/schemas/capital-sprint-packet.schema.json`
- `references/schemas/commercial-simulation.schema.json`
- `references/schemas/data-request.schema.json`
- `references/schemas/evidence-intelligence-packet.schema.json`
- `references/schemas/evidence-ledger.schema.json`
- `references/schemas/fragmentation-packet.schema.json`
- `references/schemas/learning-ledger-entry.schema.json`
- `references/schemas/memetic-pressure-packet.schema.json`
- `references/schemas/opportunity-packet.schema.json`
- `references/schemas/privacy-context.schema.json`
- `references/schemas/product-packet.schema.json`
- `references/schemas/run-envelope.schema.json`
- `references/schemas/run-receipt.schema.json`
- `references/schemas/wayfinder-execution-packet.schema.json`
- `references/schemas/wizard-answers.v1.schema.json`
- `references/schemas/zero-option-packet.schema.json`
- `references/wizard.md`
- `scripts/audit_release_version.py`
- `scripts/build_envelope.py`
- `scripts/build_receipt.py`
- `scripts/capabilities.py`
- `scripts/check_behavioral_invariants.py`
- `scripts/check_transcripts.py`
- `scripts/distribution_spine.py`
- `scripts/doctor.py`
- `scripts/hermes_runtime_smoke.py`
- `scripts/lineage.py`
- `scripts/neon_genie.py`
- `scripts/paths.py`
- `scripts/privacy_diagnostics.py`
- `scripts/privacy_preflight.py`
- `scripts/privacy_report.py`
- `scripts/privacy_runtime.py`
- `scripts/recipe_common.py`
- `scripts/recipe_product_audit.py`
- `scripts/recipe_run.py`
- `scripts/reconcile_learning.py`
- `scripts/record_learning.py`
- `scripts/release_check.py`
- `scripts/route_profiles.py`
- `scripts/run_fixture_invariants.py`
- `scripts/run_hermes_evals.py`
- `scripts/run_job.py`
- `scripts/validate_hermes_skill.py`
- `scripts/validate_packet.py`
- `scripts/wizard.py`
- `templates/request.yaml`
<!-- END HUB_SUPPORT_FILES -->

Full tree also keeps root schemas, profiles, evals, VERSION, and manifest for clone/`./install.sh` installs (scripts resolve either layout via `scripts/paths.py`).

## Pitfalls

- A folded or multi-sentence `description` loses routing signal: Hermes indexes 60 characters and truncates at 57 + `...`.
- Leading blank lines or a BOM before `---` fail frontmatter parse.
- Treating `do run` / `run-envelope.json` as execution authority. Packaging is not product judgment.
- Inventing buyers, capital, skills, or `OBSERVED` facts. Use Find → `DataRequest` → `NOT_COMPUTABLE`.
- Skipping host research on public fetchable gaps (Gate P) or skipping `DataRequest` on private gaps (Gate Q).
- Sending credentials or private/operator data without consent (Gates U/V). Offline / `LOCAL_ONLY` still recorded as an external send (Gate T).
- Letting a scorecard override a failed mandatory gate.
- Changing product intent inside a Wayfinder handoff. Return a change request to Neon Genie.
- Loading Kubrick, Wayfinder, or an external knowledge base as a load-time dependency.
- Pointing `related_skills` at other-org repos. Keep `related_skills: []`.
- Machine-local home paths in skill docs. Use `${HERMES_SKILL_DIR}` and repo-relative paths.

## Verification

Prove the skill loaded and the packaging CLI still works:

```text
terminal(command="python ${HERMES_SKILL_DIR}/scripts/neon_genie.py do check")
terminal(command="python ${HERMES_SKILL_DIR}/scripts/neon_genie.py do eval")
terminal(command="python ${HERMES_SKILL_DIR}/scripts/neon_genie.py do doctor")
```

Pass when:

- `SKILL.md` starts at byte 0 with `---`; `name` is `neon-genie`.
- `description` is one sentence, ≤60 characters, ends with a period, and has no marketing words.
- `version`, `author`, `license`, `platforms`, `metadata.hermes.tags`, and `metadata.hermes.related_skills` are present.
- VERSION matches frontmatter and `manifest.json`.
- `do check`, `do eval`, and `do doctor` exit 0.
- Advisory authority is unchanged: no spend, publish, contact, or repo mutation.

Source, profile, and migration rules: `references/source-and-upgrades.md`.
