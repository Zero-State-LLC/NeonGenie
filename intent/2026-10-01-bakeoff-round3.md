# Intent

## Problem

Neon Genie v3.29.0 (main `7c06cfd`, schema 1.3.0) still accepts an OBSERVED
quote whose polarity is the opposite of the claim, treats the digits inside
`x402` as the number 402, ignores a placeholder word that sits only in an
OBSERVED `note`, accepts an identity kill of $170 that drops tiers and card
fees stated elsewhere in the packet, scans notes with phrases fitted to
round 1–2 packet wording, refuses a missing robots.txt, drops normal HTML
pages at 64 KB, and stamps retrieval dates in UTC. The correctness judge
returns a score and no line it thinks is wrong.

## Proposed outcome

1. Quote support flips polarity on not/no/never/without/n't and matches
   numbers only as whole tokens.
2. Placeholder dates and placeholder words are checked on every string field
   of any object labeled OBSERVED, including `note`.
3. A kill derivation that ignores price tiers or fees declared elsewhere in
   the same packet fails. An identity derivation ("taken as-is") needs a
   written `justification` when it does that.
4. The note scan drops the round 1–2 phrase rules and keeps general checks:
   the same quantity stated twice, monthly versus yearly (including per-sf),
   and mutually exclusive options both locked.
5. `robots_http` allows HTTP 404 (including urllib `HTTPError`), raises the
   body cap to a stated bound, and stamps `retrieved_at` in America/Los_Angeles.
6. An optional Jev correctness pass, off by default, quotes the document line
   and the SOURCE_NOTES line it selected. Tests use a mock client. No network
   in doctor or eval.

Out of scope: a bake-off round, other gates, paid adapters, merging.

## Affected users / systems

Hermes operators; `SKILL.md`; `scripts/packet_compose.py`,
`scripts/research_mode.py`, `scripts/judge_eval.py`; eval fixtures;
CHANGELOG; VERSION 3.30.0. Artifact schema stays **1.3.0**.
`derivation.justification` is an optional string the 1.3.0 packaging check
reads. It is not a new required schema field, so `$id` does not move.

## Constraints / non-goals

- Advisory only. `authority: advisory_only`, `grants_execution: false`.
- Labels stay OBSERVED / INFERRED / SPECULATIVE / NOT_COMPUTABLE.
- Do not invent buyers, revenue, or prices. Do not tune scan rules to the
  16 raw-note issue texts.
- No OpenRouter or Opus calls. Jev only, and only when the diagnostic is on.
- No secrets in the tree. Never log `TYPESAFE_AI_API_KEY`.
- Learning-ledger entries stay PROPOSED.

## Open questions

None blocking. Danny approved this implementation on 2026-09-30 at 22:35 PT.

## Verified / assumed claims

| Claim | Label | Basis |
|---|---|---|
| Checkout is v3.29.0 at `7c06cfd`; schema `$id` is 1.3.0 | `OBSERVED` | `VERSION`, `git rev-parse`, `schemas/opportunity-packet.schema.json` |
| v3.29 `quote_support` returns supports for "allowed" against "not allowed", and for the x402 opposite claim | `OBSERVED` | `evals/bakeoff-v330/fixtures-v330.json` `v329` notes |
| The yard-pass r2 kill states the placeholder only in `note` | `OBSERVED` | `r2-packets/4-willow-yard-pass.opportunity.packet.json` |
| Jev System One returns choice, score, and noul answers, not prose | `OBSERVED` | TypeSafe API reference, `docs.typesafe.ai/api.md` |
| A 2 MiB body cap is enough for the probed HTML pages that failed at 64 KB | `INFERRED` | probe file shows `body_cap` at 65536; cap choice is local |

## Author / date

- Author: Cursor cloud agent
- Date: 2026-10-01
- Status: **ACCEPTED** 2026-09-30 by Danny (implement brief: approved at 22:35 PT)
