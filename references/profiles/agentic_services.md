# Agentic Services and x402 Profile

Decompose opportunities into bounded actions, authority requirements, exception paths, and machine-purchasable capabilities.

## Triggers

agent workflow, delegated outcome, automation, x402, machine services, capability market.

## Runes

- `RUNE.NG.AGENT.ACTION_DECOMPOSE`
- `RUNE.NG.AGENT.AUTHORITY_GATE`
- `RUNE.NG.AGENT.OUTCOME_CONTRACT`
- `RUNE.NG.X402.SCAN`
- `RUNE.NG.X402.CAPABILITY_GRAPH`
- `RUNE.NG.X402.MISFIT_CHECK`

## Action decomposition

For each action: actor (human/agent), input, output, authority class, failure mode, exception path, verification, cost/price surface.

## Autonomy gates

| Gate | Meaning |
|------|---------|
| `AUTO_ALLOWED` | Safe to automate within declared policy |
| `POLICY_ALLOWED` | Allowed if policy engine confirms |
| `USER_CONFIRMATION_REQUIRED` | Human must confirm each run |
| `QUALIFIED_HUMAN_REQUIRED` | Specialist human required |
| `PROHIBITED` | Never automate / never execute here |

Default for Neon Genie drafts: no packet elevates above drafting; execution remains downstream.

## x402 positive test

Machine-addressable, bounded, explicitly priced, verifiable, frequent/dynamic, substitutable, policy-bounded, privacy-safe.

## x402 reject (Gate F)

Reject x402 when subscription, account billing, or a persistent relationship is superior — see `evals/cases/x402-misfit.json`.

## Outputs

- `AgenticServiceGraph`
- `NeonGenieRunReceipt`

Schema: `schemas/agentic-service-graph.schema.json`

## Stage vocab (U2 · P0)

Bind agent/service graphs to envelope stage `shape` | `test` | `scale`.

- Do not recommend scale automation without test evidence.
- Autonomy gates remain advisory in Neon Genie drafts (no packet elevates execution).

## Planner / worker / validator roles (P2-1 · no new bots)

Operational roles **inside** an existing Neon Genie run or PROMETHEUS consume — never a fifth growth bot.

| Role | Owns | Does not |
|------|------|----------|
| Planner | Goal decomposition, tool plan, CLEAR gate list | Mute tool noise; invent OBSERVED |
| Worker | Tool fetch / transform; noisy output stays in worker context | Bypass privacy S–Y egress checks |
| Validator | Independent non-circular check before irreversible action | Rewrite product intent; grant execution |

- Multi-step `AgenticServiceGraph` with irreversible action and **no** validation step → autonomy gate fail (CLEAR). Keepers: arXiv:2510.04678, 2503.11951, 2511.03094.
- GenAI empowerment-entrapment checklist (arXiv:2604.02567): hallucinations / overconfidence → anti-overclaim, not phenomenology.
- Privacy S–Y still bind tool workers (egress known, offline no-send, secrets, consent).

CLEAR (Gate **ISO**): `has_irreversible_action: true` requires conjunction **`validation_step.independent: true` ∧ versioned log pointer** (`log_pointer` + `validation_log_version`). Missing either → GATE_FAIL. Independence is a boolean attestation at SHADOW — no proof protocol. See alias table in `profiles/wayfinder_handoff.md`. Do not invent a fifth bot for the validator role.
