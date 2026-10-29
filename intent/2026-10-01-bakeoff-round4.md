# Intent

## Problem

Neon Genie v3.30.0 (main `62f51a2`, schema 1.3.0) scored worse than v3.29
on correctness in the 2026-10-01 outside bake-off (0.95 vs 1.11) and lost
head-to-head to Grok 4.7 (1/10) and GPT-5.6 Sol (2/10). The note scanner
printed unconfirmed arithmetic as fact. Stripping those lines restored
correctness to 1.06. Outside models also cited live pages. Neon Genie
still led build handoff (1.87 vs about 1.5).

## Proposed outcome

1. A numeric contradiction is on the main packet only when the cited
   operands recompute and the reading is unambiguous. Everything else is
   an unverified scanner appendix, not stated as fact. Money tables print
   `notes say X, recomputed Y` when they differ.
2. Optional capped research per idea. Free fetch first. Paid search off
   unless a key and flag are set. Over cap or no key: skip and mark
   `NOT_FETCHED`. No invented sources. Tests mock the provider.
3. Optional `cheapest_test`: one action with a dated numeric pass/fail.
   The build handoff stays as it is.

Out of scope: merging, calling Opus or any paid model in tests, bumping
schema `$id`, copying large example packets.

## Affected users / systems

Hermes operators; `SKILL.md`; `scripts/packet_compose.py`,
`scripts/research_mode.py`; eval fixtures under `evals/fixtures/v331/`;
CHANGELOG; VERSION 3.31.0. Artifact schema stays **1.3.0**.

## Constraints / non-goals

- Advisory only. `authority: advisory_only`, `grants_execution: false`.
- Labels stay OBSERVED / INFERRED / SPECULATIVE / NOT_COMPUTABLE.
- Do not invent buyers, revenue, prices, or URLs.
- Do not weaken the v3.30 held-out 12/12 or the zero false-positive checks.
- No secrets in the tree. Learning-ledger entries stay PROPOSED.

## Open questions

None blocking. The implement brief asked for these three fixes on a draft
PR against main at `62f51a2`.

## Verified / assumed claims

| Claim | Label | Basis |
|---|---|---|
| main was v3.30.0 at `62f51a2` before this branch | `OBSERVED` | `git log -1 origin/main` |
| v3.30 correctness 0.95 vs v3.29 1.11; head-to-head 1/10 and 2/10 | `OBSERVED` | uploaded REPORT-round4-outside.md |
| Stripping scanner lines restored correctness to 1.06 | `OBSERVED` | same report, ablation note |
| Live head-to-head score after this patch | `NOT_COMPUTABLE` | no outside judge was run in this change |

## Author / date

- Author: Cursor cloud agent
- Date: 2026-10-01
- Status: **ACCEPTED** 2026-10-01 by the implement brief for v3.31
