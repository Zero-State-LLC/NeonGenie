# Intent

## Problem

The 2026-09-30 bake-off (Neon Genie v3.27.0 @ 86def00 versus a one-prompt
baseline on five ideas) showed Neon Genie winning on claim labels and on
not inventing buyers or prices, and losing or tying on outside context,
build handoff, kill criteria, catching input errors, and length. The
judge rubric was also Neon Genie's own criteria, with one judge.

## Proposed outcome

1. Optional research mode with pluggable adapters. Gathered items are
   OBSERVED only with URL and retrieval date. Offline still works.
2. Every schema 1.2.0 opportunity and commercial packet ends its build
   handoff with a first commit: touch, done-when, one test, owner role.
3. Kill criteria are structured (metric, threshold, comparison, check
   date, data source). Prose fails validation.
4. A mandatory input-contradiction pass is a packet section.
5. Decision prose fits one page. Long evidence moves to an appendix
   without truncation.
6. Evals can score packets with two fixture judges, neutral criteria,
   shuffled order, and an A/B swap. No paid API calls in CI.

Out of scope: ChatGPT plugin/MCP packaging, hosting, the autorag classify
path, the personal scrimshawlife-ctrl mirror, merging the PR.

## Affected users / systems

Hermes operators; `SKILL.md`; opportunity and commercial schemas;
`scripts/research_mode.py`, `packet_compose.py`, `judge_eval.py`,
`validate_packet.py`, `recipe_run.py`, `run_hermes_evals.py`; eval
fixtures; CHANGELOG; VERSION 3.28.0.

## Constraints / non-goals

- Advisory only. `authority: advisory_only`, `grants_execution: false`.
- Epistemic labels stay OBSERVED / INFERRED / SPECULATIVE / NOT_COMPUTABLE.
- Do not invent buyers, revenue, or prices.
- 1.1.0 packets remain valid. 1.2.0 is the opt-in contract.
- No secrets in fixtures. License stays MIT.
- Learning-ledger entries stay PROPOSED.

## Open questions

None blocking. Danny approved all six changes in the 2026-10-01 implement brief.

## Verified / assumed claims

| Claim | Label | Basis |
|---|---|---|
| Main is v3.27.0 @ 86def00; opportunity and commercial schemas are 1.1.0 | `OBSERVED` | `VERSION`, `git rev-parse`, schema `$id` |
| Bake-off: NG mean handoff 1.40/2; honesty higher than the baseline | `OBSERVED` | uploaded bake-off report, 2026-09-30 PT |
| Danny approved the six changes | `OBSERVED` | implement brief: "Owner Danny approved all six changes below." |
| One page is 450 words and 3200 characters of decision prose | `INFERRED` | chosen budget; evidence moves to appendix instead of being sliced |

## Author / date

- Author: Cursor cloud agent
- Date: 2026-10-01
- Status: **ACCEPTED** 2026-10-01 by Danny (implement brief: approved all six changes)
