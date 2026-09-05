# Product Architecture Profile

Use for apps, games, tools, workflows, platforms, and creative systems.

## Triggers

product audit, app design, game design, system design, feature coherence, product boundary, experience surface.

## Runes

- `RUNE.NG.PRODUCT.BOUNDARY`
- `RUNE.NG.PRODUCT.SYSTEM_INVENTORY`
- `RUNE.NG.PRODUCT.LOOP_MAP`
- `RUNE.NG.PRODUCT.CONFLICT_SCAN`
- `RUNE.NG.PRODUCT.EXPERIENCE`
- `RUNE.NG.PRODUCT.COST_SURFACE`
- `RUNE.NG.PRODUCT.REGRESSION_SCAN`
- `RUNE.NG.WAYFINDER_HANDOFF`

## Required analysis

- target user and job-to-be-done;
- blocked transition the product completes;
- core mechanism (what must be true for value to exist);
- product boundary (in / out / deferred);
- primary and secondary loops;
- feature interaction and orphan features;
- information architecture;
- emotional and sensory pacing where applicable;
- technical and production burden;
- validation path and acceptance criteria;
- canon-versus-implementation drift risks;
- integration surface and unknown access.

## Conflict scan (fail or flag)

- competing primary loops;
- features that undermine the core mechanism;
- scope that requires undeclared authority or access;
- success metrics that cannot be observed externally.

## Outputs

- `NeonGenieProductPacket` (primary)
- optionally `WayfinderExecutionPacket` when handoff is requested and intent is stable
- `NeonGenieRunReceipt`

Schema: `schemas/product-packet.schema.json`

## CLEAR rules

- Do not invent technical feasibility; mark `NOT_COMPUTABLE` when critical access is unknown.
- Do not silently expand product intent in handoff packets (Gate H).

## Dual-logic label (U1 · P0)

Emit `logic_label`: `effectual` | `causal` | `mixed` on product packets.

- Effectual PD ≠ standard waterfall SE (arXiv:1711.07045). Do not force causal SE process onto means-driven builds.
- Causal verify paths still need completion_proof + acceptance criteria.
- Never invent technical feasibility (Gate K / NOT_COMPUTABLE).

## Hypothesis↔MVP map (P0-2)

Product packets promoting ≥ `TESTABLE` need the same hypothesis ↔ MVP map as opportunity_mining (Gate HYP). Validation path must name the falsifier, not only the happy path. Keepers: arXiv:1808.05630, arXiv:2506.16334.

