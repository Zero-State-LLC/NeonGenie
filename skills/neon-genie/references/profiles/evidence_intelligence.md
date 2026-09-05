# Evidence and Stakeholder Intelligence Profile

Proactive research and stakeholder intelligence for grants, boards, philanthropy, competitive landscape, and current external facts.

**Default:** auto-load when external facts would improve the result — not only when the operator names this profile.

## Triggers

grants, boards, philanthropy, competitive research, current external facts, market facts, standards, auto: material external gap.

## Runes

- `RUNE.NG.RESEARCH.GAP_DETECT`
- `RUNE.NG.RESEARCH.QUERY_PLAN`
- `RUNE.NG.RESEARCH.FETCH`
- `RUNE.NG.RESEARCH.CITE`
- `RUNE.NG.GRANT_DISCOVER`
- `RUNE.NG.GRANT_PROCESS`
- `RUNE.NG.BOARD_RESOLVE`
- `RUNE.NG.PHILANTHROPY_TRACE`
- `RUNE.NG.AFFINITY_MODEL`
- `RUNE.NG.PORTFOLIO_RANK`
- `RUNE.NG.OUTREACH_BUILD`
- `RUNE.NG.COMPETITIVE.SCAN`
- `RUNE.NG.MARKET.FACT_CHECK`

## Source classes (host-dependent)

Use whichever host tools exist; do not hard-require any single provider:

| Class | Examples (illustrative) |
|-------|-------------------------|
| Open web | search, official product/docs pages, news |
| Academic / preprints | arXiv, papers with code, conference sites |
| Standards & regs | RFCs, W3C, gov/regulatory portals |
| Market / company | public sites, filings, pricing pages |
| Grants & funders | foundation sites, grant databases, 990s where public |
| Boards & people | public bios, org pages (no private scraping) |
| Technical | package registries, API docs, GitHub public repos |
| Operator / workspace | files, repos, pasted corpora |

If a class is unavailable on the host, skip it and record `tooling_gap` (Gate O) — never invent results.

## Auto-research protocol

1. List decision-critical questions.
2. Map each to source class + query; classify sensitivity (`public` | `operator` | `private`).
3. **Find** public/likely-public gaps via host tools (usefulness order: primary → secondary).
4. **Request** operator/private gaps (or undeclared access) with a `DataRequest` (`schemas/data-request.schema.json`) — do not invent or scrape private systems.
5. Normalize into evidence items with URL/path, title, date, snippet, retrieval time.
6. Label claims; promote only what is supported. `NOT_COMPUTABLE` only after find and/or request as appropriate.
7. Stop when additional fetches would not change the recommendation or scorecard.

Open DataRequests with `blocks_promotion: true` block promotion until satisfied or waived (Gates P–R in `references/anti-overclaim-patterns.md`).

## Attribution boundaries

Separate person / company / foundation / model inference. Never fabricate familiarity, referrals, giving motives, or private knowledge. Private decision-critical facts require a `DataRequest` (Gate Q), not silent invent as `OBSERVED` (Gate R).

## Drafting ≠ outreach

Drafting applications, emails, or board lists does **not** authorize sending, applying, or contacting (Gate E).

## Outputs

- `EvidenceIntelligencePacket`
- `NeonGenieRunReceipt`

Schema: `schemas/evidence-intelligence-packet.schema.json`

## Offline

When `research.enabled=false` / offline: use operator + workspace only; model prior ≤ `SPECULATIVE` (Gate N).

## Citation policy (U8 · P2 lock-now)

**Never generate** arXiv IDs, DOIs, or paper titles. Only rank / cite IDs that were verified fetched or operator-supplied.

- Fabricated cite → Gate fail (Gate CITE / anti-overclaim A).
- PaperPilot search DAG (U7): keyword → cite-expand → filter → score → extract. Emit optional `research_search_dag` **only when research runs** (`schemas/research-search-dag.schema.json`). Gate PILOT. Keeper: arXiv:2607.00597.
- Keeper: arXiv:2605.14306 (never-generate-cites).


## Metric roles (P0-3)

When this profile scores or recommends metrics, label each as `success` | `guardrail` | `deterioration` | `quality`. Guardrail breach blocks promotion (Gate METRIC). Keepers: arXiv:2402.11609, arXiv:2210.17187.

## Claim → evidence → stance (P1-1 prose)

For material claims, prefer the spine **claim → evidence item → stance**. Stance values may still use `Support` | `Contradict` | `Invalidate` | `Unknown`. Keeper: arXiv:2506.16383.

## Claim graph as control plane (U4 · EviGraph prose · intent DRAFT)

The **claim graph / evidence ledger** is the CLEAR control plane, not a post-hoc appendix log. Schema/SKILL field lift waits on accepted intent (`intent/2026-09-05-evigraph-ledger.md`); until then emit ledger cites in narrative / `gate_results` notes.

| Rule | Hold |
|------|------|
| No material claim promotes without an **active ledger cite** (pointer to claim node + evidence edge) | Gate LEDGER |
| Typed relations | `Support` · `Depend-on` · `Contradict` · `Invalidate` · `Update` |
| Do not invent ledger IDs as `OBSERVED` | Gate R / CITE / LEDGER |
| Final-answer fluency ≠ provenance | Anti-overclaim; execution traces ≠ truth (arXiv:2606.04990, 2608.04738, 2607.28374) |
| Contradict / Invalidate without resolution | Block ≥TESTABLE until Update or explicit waive |
| Ready(G)-style closure | SPECULATIVE until schema + goldens; do not invent Brier / auto-settle |

Keepers: arXiv:2606.04990, 2608.04738, 2607.28374 (plus P1-1 2506.16383). No phenomenology / new bots.

## Proxy vs construct (P1-2)

When a metric is a **proxy** for a latent construct, say so. Do not treat proxy movement as construct proof. Keeper: arXiv:2507.02819.

## Offline-causal before live (P1-3)

Prefer an **offline / logged-data causal pass** before recommending live A/B, pricing, or other irreversible user-harming tests.

| Rule | Label / gate |
|------|----------------|
| Offline causal / logged analysis first | Keeper arXiv:2001.05699 |
| Decision thresholds = operator policy | `SPECULATIVE` / policy — not `OBSERVED` (arXiv:1710.03410) |
| `recommended_test_n` | Always `SPECULATIVE` advisory; AUTHORITY forbids auto-roll (arXiv:1811.00457) |
| `p<0.05` (or any significance) as OBSERVED truth without source | Fail CLEAR (Gate B / Gate LIVE) |

CLEAR: live pricing or A/B recommendation with **no offline pass** and **no human-yes** → blocked (Gate LIVE).

## Planner / worker / validator in research loop (P2-1)

- **Planner** (GAP run): gap list, query plan, which CLEAR gates apply.
- **Worker**: host-tool fetches; keep raw/noisy tool output in worker context — do not promote noise to OBSERVED (arXiv:2510.04678).
- **Validator**: independent check that claim→evidence→stance holds before promotion; no circular self-grade.
- Roles are operational only. No phenomenology (“agent feels/wants”). No new bot names for validator.

## PaperPilot search DAG (U7)

When research runs, write an editable `research_search_dag`:

1. `keyword` — seed queries  
2. `cite-expand` — expand from verified cites only  
3. `filter` — drop irrelevant / contradictory retrieval  
4. `score` — rank candidates (no invent Brier / auto-settle)  
5. `extract` — pull claims into evidence ledger cites  

CLEAR (Gate **PILOT**): `research_ran: true` but missing/empty DAG → fail (warn-then-require in 3.26.x). Fabricated citation IDs inside DAG nodes → Gate **CITE** (arXiv:2605.14306). Do not invent OBSERVED cites.
