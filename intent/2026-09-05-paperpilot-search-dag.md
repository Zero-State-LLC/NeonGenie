# Intent

## Problem

U8 never-generate-cites is live (Gate CITE). Evidence research still lacks a first-class **editable search DAG** (PaperPilot): keyword → cite-expand → filter → score → extract. Operators cannot inspect/replay research path structure.

## Proposed outcome

1. Shared schema `schemas/research-search-dag.schema.json` with ordered stages.
2. Optional `research_search_dag` on EvidenceIntelligence (warn-then-require 3.26.x) — **write DAG only when research runs**.
3. Prose + Gate PILOT: research ran but DAG missing/empty → CLEAR fail (warn-then-require); fabricated nodes still Gate CITE.
4. Out of scope: invent Brier; U4 reopen; Waykin; new bots; phenomenology.

## Author / date

- Author: GAP (Danny “All of it” via Boof)
- Status: **ACCEPTED** 2026-09-05 PT — execute as PR-B
- Keeper: arXiv:2607.00597 (PaperPilot); cite policy arXiv:2605.14306
