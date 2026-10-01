# Intent

## Problem

Neon Genie v3.34.0 (main `df3958d`) scored last on correctness in the
2026-10-01 bake-off (0.87 versus 1.11 for v3.29.0). Removing the research
appendix from the packet raised that score to 1.04. The page-budget step
appends another copy of each research row every time it runs, and a
reviewed contradiction survives only when its summary matches one of five
fixed phrases, so most of v3.29's lines never reach the main page.

## Proposed outcome

1. Paid and automatic research is a sidecar file next to the packet, not
   part of the packet. The packet may carry one line pointing at the file.
   Nothing in that file is OBSERVED. Firecrawl and Jev reconcile stay
   opt-in behind `NEON_GENIE_RESEARCH_PAID=1`.
2. The page-budget step is idempotent. Running it twice yields the same
   rows. Repeated main-page lines collapse, including Jev `ask_human`.
3. A contradiction stays on the main page when its source is the reviewed
   or v3.29-style pass. The phrase list is gone. Unreviewed scanner output
   stays off the main page.

Out of scope: merging, live Jev or Firecrawl calls, a schema `$id` bump,
and any change to the build handoff or the one-action cheapest test.

## Affected users / systems

Hermes operators; `SKILL.md`; `scripts/packet_compose.py`; eval fixtures;
CHANGELOG; VERSION 3.35.0. Artifact schema stays **1.3.0**.

## Constraints / non-goals

- Advisory only. `authority: advisory_only`, `grants_execution: false`.
- Labels stay OBSERVED / INFERRED / SPECULATIVE / NOT_COMPUTABLE.
- Do not invent buyers, revenue, prices, or URLs.
- Do not weaken the held-out 12/12 or the zero false-positive checks.
- The 450-word main-page cap stays.
- No secrets in the tree. Learning-ledger entries stay PROPOSED.

## Open questions

None blocking. The implement brief asked for these three fixes on a draft
PR against main at `df3958d`.

## Verified / assumed claims

| Claim | Label | Basis |
|---|---|---|
| main was v3.34.0 at `df3958d` before this branch | `OBSERVED` | `git rev-parse HEAD` on the base checkout |
| v3.34 correctness 0.87 versus v3.29 1.11; dropping the appendix scored 1.04 | `OBSERVED` | implement brief |
| Live head-to-head score after this patch | `NOT_COMPUTABLE` | no outside judge was run in this change |

## Author / date

- Author: Cursor cloud agent
- Date: 2026-10-01
- Status: **ACCEPTED** 2026-10-01 by the implement brief for v3.35
