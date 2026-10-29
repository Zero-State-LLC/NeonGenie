# Intent

## Problem

Neon Genie v3.35.0 (main `430e42f`) still puts vaguer contradiction lines
on the main page where v3.29 (`7c06cfd`) used a specific sentence. Round 8
scored the v3.29 page plus the named money recomputes at 15.95, with
correctness 1.06, level with v3.29. That is the page this release keeps.

## Proposed outcome

1. The main-page contradiction set for the five bake-off ideas is v3.29's
   set plus the named money recomputes. All 16 reviewed lines are restored
   verbatim.
2. A later contradiction line is dropped when it concerns the same field
   or quantity as an earlier reviewed line.
3. The research sidecar, the idempotent page-budget dedupe, the one-action
   cheapest test, the build handoff, and the `NEON_GENIE_RESEARCH_PAID=1`
   gate stay as they are in v3.35.0.

Out of scope: merging, live Jev or Firecrawl calls, a schema `$id` bump.

## Affected users / systems

Hermes operators; `scripts/packet_compose.py`; eval fixtures; CHANGELOG;
VERSION 3.36.0. Artifact schema stays **1.3.0**.

## Constraints / non-goals

- Advisory only. `authority: advisory_only`, `grants_execution: false`.
- Labels stay OBSERVED / INFERRED / SPECULATIVE / NOT_COMPUTABLE.
- Do not invent buyers, revenue, prices, or URLs.
- Do not weaken the held-out 12/12 or the zero false-positive checks.
- The 450-word main-page cap stays.
- No secrets in the tree. Learning-ledger entries stay PROPOSED.

## Open questions

None blocking. The implement brief asked for this final bake-off page on
a draft PR against main at `430e42f`.

## Verified / assumed claims

| Claim | Label | Basis |
|---|---|---|
| main was v3.35.0 at `430e42f` before this branch | `OBSERVED` | `git rev-parse` on the fetched main |
| Round 8 scored v3.29 page + recomputes at 15.95, correctness 1.06, level with v3.29 | `OBSERVED` | implement brief |
| Live head-to-head score after this patch | `NOT_COMPUTABLE` | no outside judge was run in this change |

## Author / date

- Author: Cursor cloud agent
- Date: 2026-10-01
- Status: **ACCEPTED** 2026-10-01 by the implement brief for v3.36
