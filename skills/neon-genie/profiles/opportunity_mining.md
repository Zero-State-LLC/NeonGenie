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
| kill criteria | What evidence stops the path. On schema 1.2.0 this is a list of `{metric, threshold, comparison, check_date, data_source, claim_label}`. Prose-only kills fail (NG-KILL-001). Schema 1.3.0 recomputes `threshold` from `derivation` (NG-KILL-004 / NG-KILL-005). A cost threshold that ignores tiers or fees declared in the packet fails (NG-KILL-006). |

Missing map → fail CLEAR (Gate HYP). Do not promote on thesis prose alone. Keepers: arXiv:1808.05630, arXiv:2506.16334.

Schema 1.2.0 packets also carry `input_contradictions` (checked before writing; arithmetic, inconsistent quantities, period mismatches, count series, floors, and option locks), `build_handoff.first_commit` (touch, done-when, one test, owner role), and `page_budget` (450 words / 3200 characters of decision prose; evidence in `appendix`). Schema 1.3.0 recomputes each kill threshold from its inputs. A reviewed contradiction stays on the main page by its source, and a money-table mismatch says `notes say X, recomputed Y`. Unreviewed scanner notes and paid research go to a sidecar file next to the packet, not into the packet body. Money-table mismatches say `notes say X, recomputed Y`. Optional `cheapest_test` is one dated yes/no action (NG-TEST-001) and does not change the handoff. Research adapters may add OBSERVED claims only with a URL and a real retrieval date. Per idea, free `robots_http` fetch runs first (missing robots.txt HTTP 404 allows the page, bodies over 2 MiB are rejected whole, `retrieved_at` is the America/Los_Angeles date), then at most 5 calls and $0.20, with a $1.00 run cap. Over cap or no paid-search key, the query is `NOT_FETCHED`. Offline adds none. A cited quote that does not support the claim is not OBSERVED. Negation flips quote polarity, and a number counts only as a whole token.

Note: Gate HYP is distinct from Wayfinder **Gate H** (intent-rewrite handoff).

## Competitor set + recognition basis (P2-2)

- Competitive / share claims need `competitor_set_definition` + metric definition (Gate CSET; arXiv:2212.04810).
- Opportunity recognition must cite **knowledge_basis** and/or **network_basis** with epistemic labels (arXiv:2401.17448).
- Model-prior networks or access paths → Gate R / DataRequest — never silent `OBSERVED`.

