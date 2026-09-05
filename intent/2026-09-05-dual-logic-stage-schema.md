# Intent

## Problem

arXiv doctrine (LIMINAL keepers + Boof P0, 2026-09-05) requires `logic_label` and envelope `stage` on opportunity/product/zero-option runs, plus CLEAR gates LOGIC / STAGE / BRIC / CITE. Profiles and `references/gates.yaml` can carry doctrine now, but packet schemas and `SKILL.md` do not yet name these fields/gates — so validators cannot enforce them as first-class JSON.

## Proposed outcome

- Schemas gain optional-then-required fields:
  - Opportunity / Product / Zero-Option packets: `logic_label` enum `effectual` | `causal` | `mixed`
  - Run envelope: `stage` enum `shape` | `test` | `scale`
- `SKILL.md` CLEAR section lists Gates LOGIC, STAGE, BRIC, CITE (after human accepts this intent).
- Eval goldens: missing means on effectual fails; scale without test fails; fabricated cite fails.
- Out of scope: P1 EviGraph ledger (U4), P2 PaperPilot DAG (U7) beyond citation policy already locked in profiles; Waykin; new bots; phenomenology.

## Affected users / systems

Hermes/Grok NeonGenie operators; `schemas/*-packet.schema.json`; `schemas/run-envelope.schema.json`; `SKILL.md`; evals/goldens; PROMETHEUS if code-bind needed after GAP seals intent.

## Constraints / non-goals

- Advisory only. No spend/publish/contact/repo-mutation authority.
- Do not rewrite `SKILL.md` until this intent is accepted.
- Never invent OBSERVED citations (U8).
- Cite keepers only: 2103.07999, 1711.07045, 2511.09533, 2108.09943, 2507.02819, 2605.14306.

## Open questions

- Make `logic_label` / `stage` required immediately vs warn-then-require for one minor version? (GAP recommends warn in 3.26.x, required in next minor after goldens.)
- Who accepts intent: Danny / Boof?

## Verified / assumed claims

| Claim | Label | Basis |
|---|---|---|
| Boof P0 = dual-logic first, then P1 ledger, P2 DAG | `OBSERVED` | `/workspace/neon-genie-adapt/arxiv/UPGRADE-BRIEF.md` |
| Profiles + gates.yaml updated with U1/U2/U3/U8 doctrine | `OBSERVED` | this apply run |
| Schemas currently lack logic_label and stage | `OBSERVED` | schema property dump 2026-09-05 |
| Schema/SKILL code-bind needs PROMETHEUS after accept | `INFERRED` | UPGRADE-BRIEF apply path |

## Author / date

- Author: GAP
- Date: 2026-09-05 PT
- Status: **ACCEPTED** 2026-09-05 ~08:28 PT by Danny (“Accept and continue”). Decision: warn-then-require in 3.26.x (optional fields + CLEAR doctrine in SKILL); required in next minor after goldens green.


## Decision

- **Accepted by:** Danny (via Boof), 2026-09-05 PT
- **Required vs optional:** warn-then-require for 3.26.x — add optional `logic_label` / `stage` to schemas + name Gates LOGIC/STAGE/BRIC/CITE (and note HYP/METRIC/LIVE/CSET) in `SKILL.md` CLEAR; make required in next minor after goldens.
- **Out of scope unchanged:** U4 ledger, U7 DAG beyond cite policy, Waykin, new bots, phenomenology.
