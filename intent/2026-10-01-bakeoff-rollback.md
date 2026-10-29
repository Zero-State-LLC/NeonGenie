# Intent

## Problem

Neon Genie v3.33.0 (main `53a85e3`, schema 1.3.0) scored 0.79 on
correctness in the outside bake-off. v3.29.0 (`7c06cfd`) scored 1.13.
Every automatic main-page check added after v3.29.0 lowered correctness.
v3.33.0 also took the reviewed contradictions off the main page and
printed search hits and Jev reconcile lines there.

## Proposed outcome

1. The main page again shows the reviewed contradictions (a dual option
   lock, a monthly rate that is not the yearly band, and an action that
   is both required and excluded) and the verified money-table recomputes
   that name both quantities. A false double flag stays off the main page.
   A seat recompute stays singular.
2. Firecrawl hits, Jev reconcile lines, and the other scanner notes go to
   an appendix labeled `Research (unreviewed, needs a person's review)`.
   None of that is OBSERVED and none of it is on the main page.
3. Firecrawl and the Jev reconcile step stay off unless
   `NEON_GENIE_RESEARCH_PAID=1`. Existing caps stay.
4. The build handoff and the one-action cheapest test stay as they are.
   Schema stays 1.3.0. Held-out stays 12/12 with 0 false positives.

Out of scope: merging, live Firecrawl or Jev calls, a schema `$id` bump.

## Affected users / systems

Hermes operators; `SKILL.md`; `scripts/packet_compose.py`,
`scripts/research_mode.py`; eval fixtures under `evals/fixtures/v334/`;
CHANGELOG; VERSION 3.34.0. Artifact schema stays **1.3.0**.

## Constraints / non-goals

- Advisory only. `authority: advisory_only`, `grants_execution: false`.
- Labels stay OBSERVED / INFERRED / SPECULATIVE / NOT_COMPUTABLE.
- Do not invent buyers, revenue, prices, or URLs.
- Do not weaken the held-out 12/12 or the zero false-positive checks.
- No secrets in the tree. Learning-ledger entries stay PROPOSED.

## Open questions

None blocking. The implement brief asked for this rollback on a draft PR
against main at `53a85e3`.

## Verified / assumed claims

| Claim | Label | Basis |
|---|---|---|
| main was v3.33.0 at `53a85e3` before this branch | `OBSERVED` | `git rev-parse` on the fetched base |
| v3.29 correctness 1.13 versus v3.33 0.79 | `OBSERVED` | the implement brief |
| Live head-to-head score after this patch | `NOT_COMPUTABLE` | no outside judge was run in this change |

## Author / date

- Author: Cursor cloud agent
- Date: 2026-10-01
- Status: **ACCEPTED** 2026-10-01 by the implement brief for v3.34
