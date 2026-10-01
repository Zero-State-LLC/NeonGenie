# Intent

## Problem

Neon Genie v3.32.0 (main `d622079`, schema 1.3.0) scored 0.90 on
correctness in the 2026-10-01 round-5 bake-off, down from 0.93 (v3.30)
and 1.11 (v3.29). Automatic scanner lines reached the main page as
confirmed and sometimes conflicted (Autogive showed both "recomputed
336.4" and "implies 331.5"). Web search hits were listed and labeled
OBSERVED, including a Not found page and Instagram, and every link was
printed on the main page, which broke the 450-word cap. Nothing
reconciled a hit with the notes.

## Proposed outcome

1. The main page keeps only verified money-table recomputes, each naming
   what the two numbers are. A second line about the same quantity is
   dropped. Every other scanner flag is an unverified appendix note.
2. One Jev call per idea (at most two) compares each kept web fact with
   the notes and yields AGREES, CONTRADICTS, or NOT_APPLICABLE plus the
   quoted note line. CONTRADICTS is on the main page. The others are in
   the appendix. No key means NOT_COMPUTABLE. Tests mock Jev.
3. Only primary sources are OBSERVED. Social, forums, aggregators,
   other blogs, error pages, and fragments under about 20 words are
   unverified or dropped. The main page lists at most five primary links.

Out of scope: merging, live Jev or Firecrawl calls, schema `$id` bump,
Opus or other paid model calls in tests.

## Affected users / systems

Hermes operators; `SKILL.md`; `scripts/packet_compose.py`,
`scripts/research_mode.py`, `scripts/judge_eval.py`; eval fixtures under
`evals/fixtures/v333/`; CHANGELOG; VERSION 3.33.0. Artifact schema stays
**1.3.0**.

## Constraints / non-goals

- Advisory only. `authority: advisory_only`, `grants_execution: false`.
- Labels stay OBSERVED / INFERRED / SPECULATIVE / NOT_COMPUTABLE.
- Do not invent buyers, revenue, prices, or URLs.
- Do not weaken the held-out 12/12 or the zero false-positive checks.
- The build handoff and the one-action cheapest test stay as they are.
- No secrets in the tree. Learning-ledger entries stay PROPOSED.

## Open questions

None blocking. The implement brief asked for these three fixes on a
draft PR against main at `d622079`.

## Verified / assumed claims

| Claim | Label | Basis |
|---|---|---|
| main was v3.32.0 at `d622079` before this branch | `OBSERVED` | `git rev-parse HEAD` on the base checkout |
| correctness 1.11 → 0.93 → 0.90 across v3.29, v3.30, v3.32 | `OBSERVED` | uploaded REPORT-round5.md |
| Autogive printed both recomputed 336.4 and implies 331.5 | `OBSERVED` | same report |
| A Not found page and Instagram were labeled OBSERVED | `OBSERVED` | same report |
| Live head-to-head score after this patch | `NOT_COMPUTABLE` | no outside judge was run in this change |

## Author / date

- Author: Cursor cloud agent
- Date: 2026-10-01
- Status: **ACCEPTED** 2026-10-01 by the implement brief for v3.33
