# Intent

## Problem

The 2026-10-01 round-2 rerun of Neon Genie 3.28.0 (main `2b41169`) still
missed most input defects, accepted a kill threshold that ignored fees and
tiers, accepted placeholder OBSERVED dates and unsupported quotes, could not
fetch for free, and had no tie-breaker when two judges disagreed.

## Proposed outcome

Schema 1.3.0 packets recompute kill thresholds, the note scan does the
arithmetic and option-rationale check named in the round-2 report, OBSERVED
claims fail on placeholder dates and unsupported quotes, a free robots.txt
fetch adapter exists, and the eval harness can call a third fixture judge
only on disagreement. Offline packets and 1.2.0 packets stay valid.

Out of scope: the unpublished list of 14 host findings (the report gives the
count, not the items), Crawl4AI as a dependency, paid research, merging.

## Affected users / systems

Hermes operators, `SKILL.md`, packaging CLI, opportunity and commercial
schemas, hub package, evals, CI.

## Constraints / non-goals

Advisory only. Labels stay OBSERVED / INFERRED / SPECULATIVE /
NOT_COMPUTABLE. No invented buyers, revenue, or prices. No secrets in
fixtures. No paid calls in CI. MIT license. Hub mirrors stay generated.

## Open questions

None. Danny approved the five changes on 2026-10-01.

## Verified / assumed claims

| Claim | Label | Basis |
|---|---|---|
| main was v3.28.0 at 2b41169 before this branch | OBSERVED | `git log -1 origin/main` |
| The round-2 report says the host review found 14 issues and does not list them | OBSERVED | uploads/REPORT-round2 |
| Named defects in the two reports are the ones the new fixtures cover | OBSERVED | both bake-off reports |

## Author / date

- Author: Cursor agent, accepted by Danny
- Date: 2026-10-01
- Status: ACCEPTED
