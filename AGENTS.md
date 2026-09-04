# Agent contract — Neon Genie

You are working in the **Neon Genie Hermes skill** (`Zero-State-LLC/NeonGenie`).
This file is the canonical contract for Cursor, Claude, Codex, Grok, and
OpenClaw. Harness adapters (`CLAUDE.md`) only point here.

Advisory product and opportunity intelligence only. No spend, publish,
contact, or repo mutation. Cinematic work belongs in Kubrick.

## Intent

Read the active `intent.md` under [`intent/`](intent/) before editing.
Next stage is a spec or plan in this repo's existing docs — do not skip
to code.

If the change is non-trivial and no intent exists, draft one from
[`intent/_TEMPLATE.md`](intent/_TEMPLATE.md) and wait for a human to
accept it. Trivial docs and chore fixes do not need an intent file.
See [`intent/README.md`](intent/README.md).

## Commands

Fill only from this repo's scripts. Do not invent commands.

| Task | Command |
|---|---|
| Full smoke | `python scripts/neon_genie.py do doctor` |
| Skill / version check | `python scripts/neon_genie.py do check` |
| Golden + behavioral evals | `python scripts/neon_genie.py do eval` |
| Hub mirrors (after packaging change) | `python scripts/distribution_spine.py write` then `verify` |
| Pre-tag | `python scripts/release_check.py` |

Stdlib Python 3 only. No package install or secret is required to doctor.

## Invariants

- **Advisory only** ([ADR 0001](docs/adr/0001-advisory-only-authority.md)):
  `authority: advisory_only`, `grants_execution: false`.
- **`SKILL.md` is the product brain** ([ADR 0002](docs/adr/0002-skill-contract-is-product-brain.md)).
  Python is packaging. Do not rewrite `SKILL.md` unless an accepted intent
  is a skill-contract change.
- **Hub mirrors are generated** ([ADR 0003](docs/adr/0003-hub-mirror-strategy.md)).
  Edit root sources; run `distribution_spine.py write`.
- **Wayfinder boundary** ([ADR 0004](docs/adr/0004-neon-genie-wayfinder-boundary.md)):
  Neon owns what/why; Wayfinder owns execution planning.
- **Claim labels** ([ADR 0005](docs/adr/0005-claim-label-ontology.md)):
  `OBSERVED` / `INFERRED` / `SPECULATIVE` / `NOT_COMPUTABLE`. Never invent
  `OBSERVED`.
- **Privacy by construction** ([ADR 0006](docs/adr/0006-privacy-by-construction.md),
  [PRIVACY.md](PRIVACY.md)).
- Do not put secrets in the tree. Do not invent buyers, capital, or proof.
- Do not copy Noema Worker deploy, pin, or world-id dumps into this repo.
- Human yes on tag/release, spend, publish, and legal.

## Docs

No `graft/` here. Start at `README.md`, then
[CONTRIBUTING.md](CONTRIBUTING.md), [docs/adr/](docs/adr/),
[references/hermes-runtime-contract.md](references/hermes-runtime-contract.md).

## Escalation

If CI, evals, doctor, or validators look wrong — missing coverage, silent
skips, green-but-inert checks, or a suite that contradicts the skill
contract:

1. Open a bounded defect issue labeled `bug`. Do not expand this task to
   paper over it.
2. Do **not** weaken, skip, or rewrite assertions, goldens, or transcripts
   to obtain a passing result.
3. Do **not** rewrite `SKILL.md` to force evals green.
4. Reward-hacking is forbidden: no silent skips, no fixture forgery, no
   green-at-any-cost edits.

Escalate instead of guessing on skill-contract, schema, gate, privacy,
license, or hub-release changes. Learning-ledger entries stay
**PROPOSED**; never auto-apply. A red honest check is better than a
green lie.

## Team context

Org and partner status is not this repo. When a task needs cross-repo
or partner state, load [Zero-State-LLC/agent-context](https://github.com/Zero-State-LLC/agent-context):

1. `HANDOFF.md`
2. `STATUS.md`
3. `DECISIONS.md` only if a prior choice affects this task

Clone: `gh repo clone Zero-State-LLC/agent-context ~/agent-context`.
Pull `--ff-only` before trusting a local copy.
