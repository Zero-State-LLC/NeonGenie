# Intent files

Non-trivial **Hermes skill / packaging** work starts here. Copy
[`_TEMPLATE.md`](_TEMPLATE.md) to a dated, scoped file (for example
`intent/2026-09-04-short-slug.md`) and fill every section before writing
a spec, plan, or code.

This repository is the Neon Genie skill (`SKILL.md` + packaging CLI).
Do not invent product opportunities, buyers, capital, or execution
authority here. Do not import Noema Worker deploy or pin runbooks.

Do not invent a parallel process. After the intent is written, continue
with the flow this repo already uses:

1. `intent.md` — problem, proposed outcome, constraints, verified vs assumed
2. Spec / plan — accepted [ADRs](../docs/adr/) for authority or schema
   changes; otherwise [CONTRIBUTING.md](../CONTRIBUTING.md),
   [docs/GOVERNANCE.md](../docs/GOVERNANCE.md), and any dated spec under
   `docs/superpowers/`
3. Implementation of packaging, docs, evals, or (only when the accepted
   intent is a skill-contract change) `SKILL.md`
4. PR with honest `OBSERVED` / `INFERRED` / `SPECULATIVE` /
   `NOT_COMPUTABLE` evidence

Trivial docs, chore, and single-line fixes do not need an intent file.
`_TEMPLATE.md` is the blank form; do not fill it in place.

An intent is not a spec, not a plan, and not implementation authority.
It does not authorize a `SKILL.md` rewrite, extra bots, spend, publish,
or a hub release.

Team-level handoff (cross-repo / partner state) lives in
[Zero-State-LLC/agent-context](https://github.com/Zero-State-LLC/agent-context)
(`HANDOFF.md`, then `STATUS.md`). Do not duplicate that diary here.
