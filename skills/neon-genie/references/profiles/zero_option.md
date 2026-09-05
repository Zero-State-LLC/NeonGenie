# Zero Option Profile

Convert a zero-capital or severe-constraint state into externally testable action loops.

## Triggers

zero capital, first cash, immediate executable opportunity, constrained launch, no budget.

## Conversion

```text
ZERO_STATE → OPTIONALITY → MICRO_EXECUTION → FEEDBACK → LEVERAGE
```

## Runes

- `RUNE.NG.ZERO.NORMALIZE`
- `RUNE.NG.ZERO.EXTRACT_CAPABILITIES`
- `RUNE.NG.ZERO.GENERATE`
- `RUNE.NG.ZERO.SCORE_OPTIONALITY`
- `RUNE.NG.ZERO.BUILD_MICRO_LOOP`
- `RUNE.NG.ZERO.HYPERSTITION_BIND`

## Required inputs

- declared skills / capabilities (explicit list; empty → fail);
- declared access (accounts, audiences, tools, inventory);
- time window;
- capital constraint (often zero);
- proof definition for “done / cash / signal.”

## Hard filters

- cost equals zero when explicitly operating in zero-capital mode;
- executable within the declared time window;
- direct proof path;
- **no fictional credentials, access, tools, or relationships** (Gate G).

## Detectors

`DRIFT`, `STAGNATION`, `NON_EXECUTION`, `FICTIONAL_RESOURCE`.

Narrative must bind to observable action:

```text
Narrative → Action → Result → Reinforcement
```

## Outputs

- `ZeroOptionPacket`
- `NeonGenieRunReceipt`

Schema: `schemas/zero-option-packet.schema.json`

## Fail closed

If skills and access are empty or unusable under constraints → `NOT_COMPUTABLE` with reason (see `evals/cases/zero-option.json`).

## Dual-logic + bricolage (U1 · U3 · P0)

Default Zero-Option posture is **effectual** (means → optional loops). Emit `logic_label`.

**Bricolage checklist (before buy/build):**
1. Inventory declared repertoire: skills, access, tools, inventory, relationships (operator-supplied only).
2. Prefer recombine existing means over purchase or invent.
3. Affordable-loss framing when any spend is proposed — still advisory; human-yes on spend.
4. Forbid inventing missing resources (Gate G / Gate BRIC).

Keepers: arXiv:2108.09943, arXiv:2507.02819 (cite Sarasvathy / Baker&Nelson via these; NOT_COMPUTABLE as direct arXiv).

## Means inventory empty (P0-1)

Tighten U3 / effectual CLEAR:

- **Means** = declared skills + access + tools + inventory + relationships (operator-supplied only).
- If means inventory is **empty or unusable** under constraints → `NOT_COMPUTABLE` **and** emit a `DataRequest` for the missing means (Gate Q / Gate BRIC). Do not invent means. Do not promote.
- Keepers: arXiv:2312.00916, arXiv:2311.14340, arXiv:2108.09943.

