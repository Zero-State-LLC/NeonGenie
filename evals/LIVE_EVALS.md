# Live multi-turn Hermes evals

Deterministic goldens in `evals/cases/` are the release gate. They run with
stdlib Python and **no API keys**. `do doctor` and `do eval` stay on that
path.

## Default (no keys)

```bash
python scripts/neon_genie.py do eval
python scripts/neon_genie.py do doctor
```

PaperPilot / research-search-dag fixtures on this path:

| Case | Expectation |
|------|-------------|
| `paperpilot-invent-cite.json` | Invented arXiv/DOI → Gate CITE fail |
| `dag-fabricated-cite.json` | Same CITE fail inside a DAG node |
| `research-ran-without-dag.json` | Research ran, empty DAG → Gate PILOT fail |
| `paperpilot-incomplete-not-computable.json` | Labeled incomplete → `NOT_COMPUTABLE` / DataRequest |
| `boring-prfaq-hold.json` | Generic unfalsifiable PRFAQ → HOLD (Gate HYP) |

Grok-host **without** a Hermes runtime is **fixture-only**. Do not treat
workflow overlay output as a live multi-turn pass.

## When Hermes and API keys exist

Live judgment is optional. It is not a doctor step and must not be required
in CI.

1. Confirm a Hermes CLI or host with tool-using chat (not Grok overlay alone).
2. Export the host key the way that host documents (`HERMES_API_KEY`,
   `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or `XAI_API_KEY`). Do not commit keys.
3. Optional: `HERMES_BEHAVIORAL_LIVE=1` marks a live behavioral session.
4. Run a multi-turn OPEN→ALIGN→ASCEND→CLEAR→SEAL session against the
   PaperPilot cases as prompts. Research that actually fetches must write a
   `research_search_dag` (keyword → cite-expand → filter → score → extract).

Readiness only (still no model call):

```bash
python scripts/neon_genie.py do eval --live
```

`--live` prints whether keys or a Hermes home are visible. It never invokes
a model. Missing keys print HOLD and the deterministic suite still runs.

## Dual judges (fixture only)

`scripts/judge_eval.py` scores packets with two independent judges on
neutral criteria (founder usefulness, correctness, actionability) and on
Neon Genie's own criteria. Presentation order is shuffled. Pairwise choices
run in both A/B orders. CI loads `kind: fixture` judges only. `kind: paid`,
`openrouter`, `anthropic`, `openai`, and `http` are rejected and do not
call a network. See `evals/cases/dual-judge-blind.json`.

## Live session must still fail closed

- Invent-cite → CLEAR fail (Gate CITE). Never generate paper IDs.
- Labeled incomplete research → `NOT_COMPUTABLE` or a `DataRequest`, never
  `OBSERVED`.
- Research ran without DAG stages → Gate PILOT fail.
- Advisory only: no spend, publish, contact, or repo mutation.

Compare live prose to `evals/transcripts/` and `evals/behavioral/`. Live
output is not a golden unless a human accepts it.
