# Intent

## Problem

P2-1 prose already describes `validation_isolation` + versioned validation log pointer on Wayfinder handoffs, but `schemas/wayfinder-execution-packet.schema.json` lacks the fields. Irreversible agentic graphs without an independent validation step are only prose-gated.

## Proposed outcome

- Optional (warn-then-require style) `validation_isolation` object on WayfinderExecutionPacket, including versioned validation log pointer.
- CLEAR golden: irreversible agentic graph without validation step → GATE_FAIL.
- PROMETHEUS consumes isolation — no Wayfinder bot / no fifth growth bot.
- Out of scope: U7 DAG, required-field minor bump (separate PR-C), phenomenology, invent Brier.

## Affected users / systems

`schemas/wayfinder-execution-packet.schema.json`, `profiles/wayfinder_handoff.md`, `profiles/agentic_services.md`, evals, gates registry.

## Constraints / non-goals

Advisory only. No Waykin. Intent lives at repo-root `intent/` only (never under hub `skills/neon-genie/`).

## Author / date

- Author: GAP (Danny “All of it” via Boof, 2026-09-05 PT)
- Status: **ACCEPTED** 2026-09-05 PT — execute as PR-A
