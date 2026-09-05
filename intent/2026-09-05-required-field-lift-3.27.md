# Intent

## Problem

logic_label, run-envelope stage, and evidence_ledger were optional (warn-then-require) in 3.26.x. Goldens are green; time to fail closed.

## Proposed outcome

- VERSION 3.27.0
- Required: `logic_label` on opportunity/product/zero-option packets; `stage` on run-envelope; `evidence_ledger` on EvidenceIntelligence packet
- Recipes/stubs emit the fields; doctor + goldens green
- Out of scope: invent Brier; reopen U4; Waykin; new bots; phenomenology

## Author / date

- Author: GAP (Danny “All of it” via Boof)
- Status: **ACCEPTED** 2026-09-05 PT — execute as PR-C

## Also in this ship (PROMETHEUS PR-A gaps)

1. Irreversible ⇒ `independent` ∧ versioned log pointer (CLEAR doctrine; schema if-then still optional).
2. Alias table: packet `validation_isolation.*` vs graph `validation_step.*` vs eval keys.
3. `validation_log_version` on graph `validation_step`.
4. Independence stays boolean attestation at SHADOW — no proof protocol.
