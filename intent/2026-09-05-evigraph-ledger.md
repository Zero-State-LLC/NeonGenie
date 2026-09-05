# Intent

## Problem

NeonGenie CLEAR now labels claims and forbids fabricated cites (Gate CITE / U8), and evidence_intelligence carries claim→evidence→stance prose. There is still no first-class **evidence ledger / claim graph** as operational state: claims can float without typed Support/Contradict/Invalidate links, and final-answer fluency can outrun provenance (arXiv:2606.04990, 2608.04738, 2607.28374).

## Proposed outcome

1. **Doctrine (prose first):** EvidenceIntelligence + core CLEAR treat the claim graph as control plane, not post-hoc log. No claim promotes without an active ledger cite.
2. **Schema (after accept):** optional-then-required `evidence_ledger` / claim-graph fields on EvidenceIntelligence packet (and optional attach on Opportunity/Product when evidence_intelligence profile resolves). Relation enum includes Support, Depend-on, Contradict, Invalidate, Update.
3. **Gate LEDGER:** uncited claim or invent-OBSERVED from model prior → fail CLEAR.
4. **Goldens:** uncited claim fails; contradict-without-resolution blocks ≥TESTABLE; fabricated cite still CITE.
5. **Out of scope:** U7 PaperPilot search DAG; invent Brier/auto-settle (VECTOR); Waykin; new bots; phenomenology / consciousness-module language.

## Affected users / systems

GAP (doctrine), schemas/evidence-intelligence-packet.schema.json (+ optional peer packets), references/gates.yaml, SKILL.md CLEAR, evals; PROMETHEUS if code-bind after accept.

## Constraints / non-goals

- Advisory only. Execution provenance ≠ final-answer accuracy.
- Warn-then-require in current minor if accepted mid-cycle; required next minor with goldens.
- Access≠phenomenal holds.
- Do not rewrite SKILL.md until this intent is **ACCEPTED**.

## Verified / assumed claims

| Claim | Label | Basis |
|---|---|---|
| #12 dual-logic/stage land on main | OBSERVED | Zero-State-LLC/NeonGenie#12 → 331394fb |
| Claim→evidence→stance prose already in evidence_intelligence | OBSERVED | GAP reconcile apply |
| EviGraph / Agent Traces / LedgerMind keepers | OBSERVED | LIMINAL arXiv feed + papers.json |
| Schema lacks ledger graph | OBSERVED | schema dump |

## Open questions

- Embed ledger inside EvidenceIntelligence only vs shared `evidence-ledger.schema.json` referenced by multiple packets?
- GAP recommends: shared schema file + EvidenceIntelligence required-when-profile; peers optional attach.

## Author / date

- Author: Boof (from LIMINAL/GAP upgrade path)
- Date: 2026-09-05 PT
- Status: **ACCEPTED** 2026-09-05 ~09:04 PT by Danny (“Continue as recommended” after U4 intent prompt). Decision: warn-then-require in 3.26.x — optional evidence_ledger fields + Gate LEDGER in SKILL CLEAR; required next minor after goldens.


## Decision

- **Accepted by:** Danny (via Boof), 2026-09-05 PT
- **Required vs optional:** warn-then-require for 3.26.x; shared `evidence-ledger.schema.json` + EvidenceIntelligence required-when-profile; peers optional attach (GAP open-question pick).
- **Out of scope unchanged:** U7 DAG, invent Brier, Waykin, new bots, phenomenology.
