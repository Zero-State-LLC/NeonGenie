# Intent

## Problem

Opportunity and commercial packet schemas still use empty `{}` property
shapes. Profiles already require affected user, economic buyer (Gate C),
wedge, distribution, and failure modes, and commercial doctrine already
forbids invented CAC/LTV as `OBSERVED`. Packaging can accept fluent but
under-specified packets. PaperPilot / research-search-dag goldens cover
DAG-missing and fabricated cites, but not the labeled-incomplete
`NOT_COMPUTABLE` / DataRequest path, and live multi-turn Hermes evals
are undocumented. CHANGELOG / ROADMAP lag the shipped 3.27.0 line
(`#14`: ISO, PILOT, required `logic_label` / `stage` / `evidence_ledger`).

## Proposed outcome

1. Additive typing of `schemas/opportunity-packet.schema.json` and
   `schemas/commercial-simulation.schema.json` (Hermes-native names;
   PRISM CLEAR / engine-tag stay sidecar). Existing required keys
   unchanged. Optional mining fields typed, not newly required.
2. CHANGELOG `[3.27.0]` narrative completed; ROADMAP records 3.27 shipped
   and this schema thicken; `engine_tag` documented as PRISM-sidecar-only.
3. PaperPilot / research-search-dag eval fixtures (invent-cite fail;
   labeled incomplete → `NOT_COMPUTABLE` / DataRequest; optional
   `boring_prfaq_hold`) plus live-eval docs. `do doctor` stays green
   without API keys.
4. Hub mirrors via `distribution_spine.py write`. Advisory only.

Out of scope: `SKILL.md` rewrite; baking `engine_tag` into Hermes
packets; inventing buyers/TAM/revenue; public-mirror sync; Kubrick;
fifth growth bot; auto-canon.

## Affected users / systems

Hermes operators; `schemas/` + `references/schemas/`; commercial and
opportunity recipes/samples; `scripts/validate_packet.py`;
`scripts/run_hermes_evals.py`; `evals/cases/`; CHANGELOG; ROADMAP;
hub package after spine write.

## Constraints / non-goals

- Advisory only. `authority: advisory_only`, `grants_execution: false`.
- Do not invent `OBSERVED` buyers, CAC/LTV, or citations.
- Prefer additive typing over breaking renames.
- Do not require secrets for doctor smoke.
- Learning-ledger entries stay PROPOSED.

## Open questions

None blocking. Danny authorized this work 2026-09-17 PT.

## Verified / assumed claims

| Claim | Label | Basis |
|---|---|---|
| Org SoT VERSION is 3.27.0; `#14` shipped ISO/PILOT/required fields | `OBSERVED` | `VERSION`, `git log` `8292a1e` |
| Opportunity/commercial schemas still use empty `{}` required props | `OBSERVED` | current schema files vs uploads CURRENT |
| Danny yes 2026-09-17 PT | `OBSERVED` | implement brief: “Yes where a yes is needed.” |
| Engine taxonomy should stay PRISM sidecar | `INFERRED` | adapt `engine-tag.adaptation.schema.json`; hub MIT consumers |

## Author / date

- Author: GAP / Cursor cloud agent
- Date: 2026-09-17 PT
- Status: **ACCEPTED** 2026-09-17 PT by Danny (“Yes where a yes is needed.”)
