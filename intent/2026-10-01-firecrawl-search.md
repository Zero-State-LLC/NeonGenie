# Intent

## Problem

Neon Genie v3.31.0 (main `32378f7`) added capped per-idea research and a
pluggable paid-search slot. The slot stays off: a set
`NEON_GENIE_SEARCH_API_KEY` still returns `NOT_FETCHED` / `no_key` because
no provider is bundled. Operators who want a paid search have nowhere to
plug Firecrawl in without a live call in CI.

## Proposed outcome

Wire Firecrawl `POST /search` (v2 default, v1 responses accepted) as that
provider.

- Enabled only when `NEON_GENIE_RESEARCH_PAID=1` (or `allow_paid`) and
  `FIRECRAWL_API_KEY` are both set. Otherwise the pass is unchanged: free
  robots-aware fetch first, other queries `NOT_FETCHED`.
- Keep the caps: 5 calls and $0.20 per idea, $1.00 per run. Price a call
  as Firecrawl credits times `DOLLARS_PER_CREDIT` (documented config).
  Skip the call when the cap would be exceeded.
- Cite a hit as `OBSERVED` only with the returned URL and an
  America/Los_Angeles retrieval date. Do not invent sources.
- HTTP errors, timeouts, and 403s are `NOT_FETCHED`. At most one retry, and
  only for 429 or 5xx.
- Tests inject a transport. CI does not call Firecrawl.
- VERSION 3.32.0. Artifact schema stays **1.3.0**.

Out of scope: merging, live Firecrawl calls, schema `$id` bump, other paid
adapters (Serper, Tavily, model APIs).

## Affected users / systems

Hermes operators enabling paid research; `SKILL.md`; `scripts/research_mode.py`;
`scripts/firecrawl_client.py`; `scripts/test_firecrawl_research.py`; CHANGELOG;
VERSION 3.32.0.

## Constraints / non-goals

- Advisory only. `authority: advisory_only`, `grants_execution: false`.
- Labels stay OBSERVED / INFERRED / SPECULATIVE / NOT_COMPUTABLE.
- Do not invent buyers, revenue, prices, or URLs.
- Do not weaken v3.31 research caps or the offline path.
- No secrets in the tree. The API key stays in the environment.
- Learning-ledger entries stay PROPOSED.

## Open questions

None blocking. The implement brief specified Firecrawl, the env key, the
existing caps, and a draft PR against main at `32378f7`.

## Verified / assumed claims

| Claim | Label | Basis |
|---|---|---|
| main was v3.31.0 at `32378f7` before this branch | `OBSERVED` | `git rev-parse origin/main` |
| Search is 2 credits per 10 results; scrape adds 1 credit per page | `OBSERVED` | docs.firecrawl.dev/billing, read 2026-10-01 |
| Hobby pay-as-you-go is 1,000 credits per 5 USD | `OBSERVED` | same billing page |
| Using 0.005 USD/credit fails closed against cheaper plans | `INFERRED` | Standard, Growth, and Scale list more credits per 5 USD |
| A live Firecrawl account was not used in this change | `OBSERVED` | tests inject the transport |

## Author / date

- Author: Cursor cloud agent
- Date: 2026-10-01
- Status: **ACCEPTED** 2026-10-01 by the implement brief for v3.32
