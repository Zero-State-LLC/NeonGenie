# Opportunity Mining Profile

Find valuable state transitions that users cannot complete efficiently.

## Triggers

new venture, unmet need, market opportunity, blocked transition, weak signal, portfolio idea.

## Signal classes

- human friction;
- institutional friction;
- economic friction;
- technology frontier;
- repeated workarounds;
- exception patterns;
- unused rights, benefits, capacity, or capability.

## Runes

- `RUNE.NG.SENSE`
- `RUNE.NG.TRANSITION_MARKET`
- `RUNE.NG.INTERVENTION.SHAPE`
- `RUNE.NG.PORTFOLIO.ROUTE`

## Required fields

| Field | Rule |
|-------|------|
| affected user | Must be concrete; absence fails closed |
| economic buyer | Separate from beneficiary (Gate C) |
| authority holders | Who can approve / block |
| transition market | Current → desired state gap |
| coordination gap | Why the market has not cleared |
| service-first wedge | Smallest testable intervention |
| distribution | How the wedge reaches the user |
| completion proof | Externally checkable success |
| failure modes | How the opportunity dies |

## Pipeline bind

```text
SIGNAL → BLOCKED TRANSITION → OUTCOME MODEL → OPPORTUNITY THESIS
  → INTERVENTION → VALIDATION → SCORECARD → ROUTING
```

## Outputs

- `NeonGenieOpportunityPacket`
- optional commercial / agentic packets when co-triggered
- `NeonGenieRunReceipt`

Schema: `schemas/opportunity-packet.schema.json`

## CLEAR rules

- High monetization cannot override missing user, proof, or authority.
- Weak signals stay `SPECULATIVE` until evidence density rises.

## Dual-logic label (U1 · P0)

Every Opportunity / Product / Zero-Option run must emit `logic_label`: `effectual` | `causal` | `mixed`.

| Label | When | CLEAR |
|-------|------|-------|
| `effectual` | Means-driven explore; affordable loss; partner co-creation | Requires means inventory (declared skills/access/partners). Missing means → fail CLEAR. |
| `causal` | Goal-driven verify; predicted market → build → test | Requires `completion_proof` + test evidence path. Missing proof → Gate G. |
| `mixed` | Explicit split of explore vs verify legs | Each leg must satisfy its own CLEAR rules. |

Cite keepers: arXiv:2103.07999, arXiv:1711.07045 (OBSERVED). Do not invent OBSERVED citations.

## Stage vocab (U2 · P0)

Envelope / opportunity stage: `shape` → `test` (nano-MVP) → `scale`.

- `shape`: intervention still forming; promotion capped below TESTABLE without proof.
- `test`: nano-MVP / external check running; needs completion_proof definition.
- `scale`: blocked without test evidence (Gate STAGE).

Keeper: arXiv:2511.09533.

## Hypothesis↔MVP map (P0-2)

Before promotion ≥ `TESTABLE`, require an explicit **hypothesis ↔ MVP** map:

| Field | Rule |
|-------|------|
| falsifiable hypothesis | What must be true for the opportunity to work |
| MVP / nano-test | Smallest external check that could falsify it |
| kill criteria | What evidence stops the path |

Missing map → fail CLEAR (Gate HYP). Do not promote on thesis prose alone. Keepers: arXiv:1808.05630, arXiv:2506.16334.

Note: Gate HYP is distinct from Wayfinder **Gate H** (intent-rewrite handoff).

## Competitor set + recognition basis (P2-2)

- Competitive / share claims need `competitor_set_definition` + metric definition (Gate CSET; arXiv:2212.04810).
- Opportunity recognition must cite **knowledge_basis** and/or **network_basis** with epistemic labels (arXiv:2401.17448).
- Model-prior networks or access paths → Gate R / DataRequest — never silent `OBSERVED`.

