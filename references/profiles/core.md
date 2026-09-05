# Core Kernel

Always loaded. Owns OPEN → ALIGN → ASCEND → CLEAR → SEAL and claim-label discipline.

## Modes

### OPEN
Resolve request, outcome, actor, current state, evidence, constraints, authority, and requested artifact.
Detect decision-critical unknowns that research could close.
Record non-goals and authority ceiling (`advisory_only` unless operator raises).

### ALIGN
1. Merge operator-supplied canonical sources with workspace context (no external KB required to load).
2. Build evidence hierarchy and non-goals.
3. **Gap-detect** material claims that would be weak without external facts.
4. Load `privacy` with core. Research is local-only by default; before any host-tool action apply `RUNE.PRIVACY_EGRESS_CHECK`. Private gaps remain DataRequests.
5. Normalize and cite; set novelty, buildability, and success criteria on the refreshed evidence base.
6. Auto-load `evidence_intelligence` when external facts would change the recommendation.

### ASCEND
Run state-transition, topology, intervention, validation, scoring, and routing functions.
Re-enter the research loop when new gaps appear mid-ascent and host tools can close them.
Select specialized profiles only when triggers match (smallest sufficient set).

### CLEAR
Flag unsupported claims, authority leakage, duplicate concepts, hidden dependencies, scope expansion, and uncited “facts.”
Apply `references/anti-overclaim-patterns.md` gates A–R as relevant (including Evidence Request Protocol gates P–R):
- **P** — public gap with tools available and no research attempt;
- **Q** — private/operator decision-critical gap with no `DataRequest`;
- **R** — private/unknown fact labeled `OBSERVED` from model prior without source.
Confirm research attempts were logged for remaining `NOT_COMPUTABLE` fields.
Open DataRequests with `blocks_promotion: true` cap promotion until satisfied or waived.

### SEAL
Emit selected packets plus run receipt, including full source manifest, research log, and evidence spine fields: `data_requests`, `open_blocking_requests`, and `research_attempts` (may be empty arrays). See `schemas/run-receipt.schema.json` and `schemas/data-request.schema.json`.
Never grant execution, spending, or publishing authority in sealed packets.

## Claim labels (mandatory on material claims)

| Label | Rule |
|-------|------|
| `OBSERVED` | Direct support from cited operator, workspace, or live source |
| `INFERRED` | Valid inference from evidence (FORECAST-class) |
| `SPECULATIVE` | Plausible but unproven; not fact |
| `NOT_COMPUTABLE` | Missing data after research attempt or correct offline skip — never fabricate |

## Core score axes

- evidence density
- outcome clarity
- affected-user clarity
- completion-proof quality
- integration feasibility
- reversibility
- auditability
- scope boundedness

Composite score never overrides a mandatory gate failure.

## Core runes

- `RUNE.NG.INTAKE`
- `RUNE.NG.EVIDENCE.NORMALIZE`
- `RUNE.NG.RESEARCH.GAP_DETECT`
- `RUNE.NG.RESEARCH.QUERY_PLAN`
- `RUNE.NG.RESEARCH.FETCH`
- `RUNE.NG.RESEARCH.CITE`
- `RUNE.NG.BLOCKED_TRANSITION`
- `RUNE.NG.OUTCOME.MODEL`
- `RUNE.NG.TOPOLOGY`
- `RUNE.NG.DISCOVER`
- `RUNE.NG.RECOMBINE`
- `RUNE.NG.DIFFERENTIATE`
- `RUNE.NG.SHAPE`
- `RUNE.NG.SCORE`
- `RUNE.NG.VALIDATE_PATH`
- `RUNE.NG.ROUTE`
- `RUNE.NG.CLEAR_CHECK`
- `RUNE.NG.SEAL`
- `RUNE.PRIVACY_EGRESS_CHECK`

## Outputs

Always consider `NeonGenieRunReceipt`. Other packets by profile selection.

## Dual-logic + stage + cite (doctrine 2026-09-05)

On opportunity/product/zero-option runs, CLEAR also checks:

- **logic_label** present (`effectual` | `causal` | `mixed`) — Gate LOGIC.
- **stage** on envelope when opportunity/agentic profiles resolve (`shape` | `test` | `scale`) — Gate STAGE; `scale` needs test evidence.
- **Citation integrity** — never invent arXiv/DOI; Gate CITE.
- **Bricolage** — no proposed spend/buy/build without repertoire inventory — Gate BRIC.

`logic_label` and envelope `stage` are **required** as of 3.27.0 (Gate LOGIC / STAGE).

## Reconcile 2026-09-05 (prose-only)

Schema/SKILL field lift **HOLD** (Danny skipped intent). Additional CLEAR prose:

- Empty means → `NOT_COMPUTABLE` + DataRequest (P0-1).
- Hypothesis↔MVP map before ≥TESTABLE — Gate HYP (P0-2; not Wayfinder Gate H).
- Metric roles; guardrail blocks promotion — Gate METRIC (P0-3).

## Continue 2026-09-05 (LIVE + CSET)

- Gate LIVE: offline/logged causal pass before live A/B or pricing recs that can hurt users; human-yes required; no auto-roll.
- Gate CSET: competitor_set_definition + metric before share/competitive OBSERVED claims.

## Claim graph / Gate LEDGER (U4 · required evidence_ledger on EvidenceIntelligence as of 3.27.0)

When `evidence_intelligence` resolves (or any material external claim is promoted):

- Treat the claim graph as CLEAR **control plane**: every promoting claim needs an active ledger cite.
- Relations: `Support` | `Depend-on` | `Contradict` | `Invalidate` | `Update`.
- Gate **LEDGER**: uncited material claim, or invent-OBSERVED from model prior without ledger cite → fail CLEAR.
- Fluency of the final answer is **not** provenance. Do not invent Brier scores or auto-settle.
- `evidence_ledger` required on EvidenceIntelligence packets (3.27.0).
