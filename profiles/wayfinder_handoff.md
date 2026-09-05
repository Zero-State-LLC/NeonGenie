# Wayfinder Handoff Profile

Produce an execution packet only after product intent is stable enough.

## Triggers

build plan, engineering readiness, execution packet, wayfinder handoff, implementation packet.

## Ownership split

| Neon Genie owns | Wayfinder owns |
|-----------------|----------------|
| What should be built and why | Work decomposition |
| Target user and blocked transition | Dependency sequence |
| Product boundary and system behavior | Milestones and eng validation |
| Success criteria and proof requirements | Implementation status |

## Required fields

product authority, version, objective, non-goals, target outcome, acceptance criteria, workstreams, dependencies, constraints, canonical interfaces, artifacts, validation gates, regression risks, deferred scope, and change control.

## Change control (Gate H)

```yaml
product_intent_changes_require_neon_genie_review: true
```

Any proposed change to product intent returns to Neon Genie as a change request. The handoff packet **must not** rewrite intent — see `evals/cases/wayfinder-change-control.json`.

## Outputs

- `WayfinderExecutionPacket`
- `NeonGenieRunReceipt`

Schema: `schemas/wayfinder-execution-packet.schema.json`

## Authority

Handoff is still **advisory**. It does not authorize spend, deploy, or repo mutation. Wayfinder runtime is optional; absence never blocks emitting a local packet.

## Validation isolation (P2-1 · PROMETHEUS consumes)

Schema: `schemas/wayfinder-execution-packet.schema.json` (`validation_isolation`, optional until a later require-bump).

**Irreversible conjunction (PROMETHEUS gap close):** when work can irreversibly affect users/spend/egress, CLEAR needs:

`independent` ∧ versioned log pointer

i.e. `validation_isolation.independent_of_planner: true` **and** both `validation_log_pointer` + `validation_log_version` (or graph aliases below). Schema if-then remains optional; doctrine is fail-closed in CLEAR.

### Alias table (packet ↔ graph ↔ eval)

| Concept | Wayfinder packet | Agentic graph | Eval fixture keys |
|---------|------------------|---------------|-------------------|
| Validation present | `validation_isolation.enabled` | `validation_step.present` | `validation_step_present` / `validation_isolation_enabled` |
| Independence (boolean attestation; SHADOW — no proof protocol) | `validation_isolation.independent_of_planner` | `validation_step.independent` | `validation_independent` / `independent_of_planner` |
| Versioned log pointer | `validation_isolation.validation_log_pointer` | `validation_step.log_pointer` | `validation_log_pointer` |
| Log version / content-hash | `validation_isolation.validation_log_version` | `validation_step.validation_log_version` | `validation_log_version` |

PROMETHEUS consumes these fields — **no Wayfinder bot**, no fifth growth bot. Gate H (intent rewrite) still binds. Gate **ISO** when irreversible work lacks the conjunction above. Keepers: arXiv:2503.11951, 2511.03094.
