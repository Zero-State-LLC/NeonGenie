# Commercial Modeling Profile

## Triggers

pricing, buyer, revenue, costs, market pressure, business model, first customer.

## Runes

- `RUNE.NG.COMMERCIAL.BUYER_MAP`
- `RUNE.NG.COMMERCIAL.MODEL`
- `RUNE.NG.COMMERCIAL.SIMULATE`
- `RUNE.NG.COMMERCIAL.PRESSURE_SCAN`
- `RUNE.NG.COMMERCIAL.PORTFOLIO`

## Role map (required separation — Gate C)

Separate **beneficiary**, **user**, **buyer**, **authorizer**, **payer**, and **risk bearer**. Conflation fails commercial CLEAR.

## Generate

- startup and operating cost ranges (with provenance);
- pricing model and packaging;
- conservative, balanced, and aggressive scenarios;
- first-customer profile;
- acquisition channels;
- integration economics;
- data moat (only if evidenced);
- network effect (only if evidenced);
- regulatory and platform pressure;
- first 90-day validation plan.

## Number discipline

| Situation | Label |
|-----------|--------|
| Cited public price / filing | `OBSERVED` |
| Model from cited inputs | `INFERRED` |
| Unanchored projection | `SPECULATIVE` |
| No basis after research | `NOT_COMPUTABLE` |

Unsupported numerical projections remain `SPECULATIVE` or `NOT_COMPUTABLE` — never `OBSERVED` (Gate B).

## Outputs

- `CommercialSimulationPacket`
- `NeonGenieRunReceipt`

Schema: `schemas/commercial-simulation.schema.json`

## Metric roles (P0-3)

Every scored metric in commercial / validation plans must declare a **role**:

| Role | Meaning |
|------|---------|
| `success` | Primary outcome we want to move |
| `guardrail` | Must not breach; **breach blocks promotion** |
| `deterioration` | Early-warning decline signal |
| `quality` | Evidence / sample / measurement integrity |

- Guardrail breach or missing role on a decision-critical metric → fail CLEAR (Gate METRIC).
- Never invent conversion rates or volumes (Gate B).
- Keepers: arXiv:2402.11609, arXiv:2210.17187.

## Offline-causal before live (P1-3)

Do not recommend live pricing tests or user-facing A/B that can irreversibly hurt users until an offline/logged causal pass is noted (or operator human-yes waives). Thresholds are policy, not OBSERVED. `recommended_test_n` stays SPECULATIVE. Gate LIVE. Keepers: arXiv:2001.05699, 1710.03410, 1811.00457.

## Competitor set before share claims (P2-2)

Market-share or competitive claims require:

1. Explicit `competitor_set_definition` (who is in/out).
2. Explicit metric definition (numerator/denominator/time window).

Missing set when the claim `blocks_promotion` → emit DataRequest `competitor_set_definition` (Gate Q / Gate CSET). “10% share” labeled `OBSERVED` without competitor_set → Gate B/Q/CSET. Keeper: arXiv:2212.04810.

