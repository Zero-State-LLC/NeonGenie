# IDEA 5: Jev-gated crypto arbitrage loop (paper-first) (Zero State LLC)

----- SOURCE: jev-crypto-arb/CARD.md -----
<!-- PROVENANCE: REWRITTEN from summary, 2026-09-24 PT post-migration recovery. The original file at this path was lost 2026-09-24 19:41 PT.
     The body below is the surviving summary source copied verbatim (not the original file, which was likely longer):
       - vault:Research/Jev crypto arbitrage route — X top20 stress 2026-09-23.md
       - vault:Research/Jev crypto arb red team plain English — 2026-09-23.md
-->

# Jev × crypto arbitrage — recommended route

**Verdict:** use Jev as a **fail-closed gate + dual-score**, not as the arb executor. Paper first. Live capital still needs `jev-gate-send-spend-legal` + Danny human-yes.

## Recommended route (INFERRED)

1. **Boof** owns the loop; no new trading bot.
2. **Hot path (non-Jev):** venue books, balances, fee schedule, transfer ETA — deterministic code.
3. **Jev pack (ACTIVE honor on decisions, not on money):**
   - Choice `action`: `skip` | `paper` | `ask_human` | `blocked` (no `execute` enum until Phase 2 band)
   - Noul `edge_alive` (fees+slippage+time in state)
   - Score `restraint_integrity` (LUDUS Dual-Track — refuse strip-caution Goodhart)
   - Noul `data_freshness`
   - Noul `consequential_spend` → if high, force HOLD / ask_human
4. **Owners:** VECTOR regime · Acquire EV/fees · SHADOW honesty · TRUTINA settled calibration · ADVERSARY red-team before any band.
5. **Phases:** Paper → shadow live quotes → micro human-yes band only after calibration.

## X top 20 (OBSERVED, ranked engagement heuristic)

1. @oliviscusAI · jev_launch · ♥8 · impressions 891  
   https://x.com/oliviscusAI/status/2101282902856368378  
   jev returns typed decisions not chat; 70-500ms; 200x faster framing
2. @BQQKED · funding_arb_ops · ♥12 · impressions 247  
   https://x.com/BQQKED/status/2099332890811351429  
   Running funding rate arb bot 24-48h for data; hands-free method
3. @Arbistocks · jev_trading_arch · ♥2 · impressions 377  
   https://x.com/Arbistocks/status/2102012472035299725  
   typesafe calls jev a system one model: state in, typed probabilistic decisions out. trading loop needs both halves — fast half glances at board; slow half does arithmetic
4. @degenv_eth · jev_primitive · ♥1 · impressions 358  
   https://x.com/degenv_eth/status/2101740125537362131  
   Article: Jev Isn't a Chain — It's a Decision Primitive Bots Can Actually Afford
5. @grok · jev_hype_check · ♥1 · impressions 282  
   https://x.com/grok/status/2102856505418449316  
   Jev real; 'probably make you a lot of money' is hyperbole; no evidence
6. @dlimeng192048 · jev_launch · ♥1 · impressions 69  
   https://x.com/dlimeng192048/status/2101966965359435925  
   Jev public, $5 credits, structured judgments with probabilities
7. @JF_Stanley · arb_reality · ♥1 · impressions 59  
   https://x.com/JF_Stanley/status/2098454382031278232  
   Fees eat the edge; 11,000x claim isn't arbitrage — arb is thin margins
8. @tushar40186231 · terminal_features · ♥0 · impressions 59  
   https://x.com/tushar40186231/status/2099020191774724120  
   Funding arb, cross-exchange arb as one-click terminal features
9. @OleksandrKryv · jev_crypto_pitch · ♥0 · impressions 56  
   https://x.com/OleksandrKryv/status/2101380362551361916  
   TypeSafe structured decisions for crypto systems / wallets — speculative product pitch
10. @SoulEXtender618 · jev_safer_bot · ♥0 · impressions 43  
   https://x.com/SoulEXtender618/status/2101803268791742756  
   Jev would be safer for trading bot (typesafe system one)
11. @grok · jev_onchain_bot · ♥0 · impressions 34  
   https://x.com/grok/status/2102213338243445117  
   Jev powers real-time trading bot buy/sell every block on onchain data (claimed)
12. @grok · jev_project_list · ♥0 · impressions 33  
   https://x.com/grok/status/2101536319440646476  
   Thread of Jev projects includes trading bot among demos
13. @lumenovaxyz · multi_venue_agent · ♥0 · impressions 32  
   https://x.com/lumenovaxyz/status/2100027085943365632  
   One agent routes CEX DEX derivatives prediction markets
14. @web3eaglealpha · funding_arb_promo · ♥0 · impressions 21  
   https://x.com/web3eaglealpha/status/2092729802088161365  
   fxyz Funding Rate Arb bot — automate monitoring
15. @Iamsmith25 · vault_ai_promo · ♥0 · impressions 15  
   https://x.com/Iamsmith25/status/2094219540796199165  
   Knidos deposit USDC; funding-rate arb automated policy-controlled
16. @grok · jev_onchain_bot · ♥0 · impressions 14  
   https://x.com/grok/status/2102053594757239048  
   Autonomous trading bot deciding buy/sell every ~300ms from on-chain+off-chain
17. @grok · jev_gating · ♥0 · impressions 10  
   https://x.com/grok/status/2102642558958530886  
   Devs building experimental trading bots with Jev as confirmation/gating layer
18. @wilywonka14469 · claude_arb_video · ♥0 · impressions 6  
   https://x.com/wilywonka14469/status/2101538280793665549  
   Claude AI crypto arbitrage bot 13-hour live test video — unverified PnL
19. @ErnestinaC3442 · vault_ai_promo · ♥0 · impressions 5  
   https://x.com/ErnestinaC3442/status/2101247899610788213  
   Knidos autonomous funding arb zk-verified — marketing voice
20. @GulapFool · vault_ai_promo · ♥0 · impressions 4  
   https://x.com/GulapFool/status/2099132257462305009  
   Knidos: AI allocates funding rate arb with policy limits

## Stress test

- **S1 Latency mismatch** — `FAIL`: Cross-venue arb windows often << Jev RTT (70-500ms) + transfer + settle. Jev cannot be the hot path for quote-chasing.
- **S2 State incompleteness** — `FAIL if omitted`: If state omits fees, withdraw locks, depth, oracle lag, nonce/gas, Jev Choice is confident nonsense.
- **S3 Goodhart / restraint strip** — `HIGH`: X+Moltbook pattern: strip caution → score↑. Dual-axis required: edge_score vs restraint_integrity (LUDUS Dual-Track).
- **S4 Calibration ≠ PnL** — `HIGH`: Typed confidence is not EV. Need settled Brier/PnL labels (TRUTINA) before ACTIVE honor on execute.
- **S5 Hype vs evidence** — `OBSERVED`: Grok discourse admits money claims are hyperbole; most arb AI posts are vault promo / YouTube with no audited ledger.
- **S6 Fee/slippage wipe** — `OBSERVED`: JF_Stanley: thin arb margins vs taker fees — many 'arb bots' are marketing.
- **S7 Spend authority** — `WALL`: Any capital move = jev-gate-send-spend-legal + Danny human-yes. Jev alone never authorizes.
- **S8 Auto-execute from Choice** — `REJECT`: Do not wire destination=EXECUTE to exchange APIs. Gate only: SKIP / PAPER / ASK_HUMAN / (rare) PREAPPROVED_BAND.

## What X actually supports

- OBSERVED: discourse wants Jev as **gating / confirmation / fast typed decisions** for bots (Arbistocks two-half loop; Grok “confirmation/gating layer”).
- OBSERVED: money claims are contested even by Grok; arb AI posts are mostly vault/YouTube promo.
- NOT_COMPUTABLE: any edge size, win rate, or that Jev improves PnL.

## Walls

- Human-yes for spend/send/legal
- Do not wire exchange keys into agents without explicit Danny order
- Access≠phenomenal; Detector > generator

Artifacts: `/workspace/out/jev-crypto-arb/REPORT.json`

---

# Jev × crypto arb — red team (plain English)

**When:** 2026-09-23 PT · **Who:** Boof first pass (ADVERSARY briefed in parallel)  
**Target:** the proposed “Jev as gate, not executor” pack  
**Verdict:** **keep the route**, but **do not treat it as ready for money**. Several holes would still let you fool yourself into trading.

## What the design gets right
- It refuses to let Jev place orders.
- It forces fees and time into the story (`edge_alive`).
- It keeps a second score for “did we strip the safety rails?” (`restraint_integrity`).
- Real spend still needs Danny’s yes.

Those are good walls. The attacks below are how they fail in practice.

## Attacks (how this still goes wrong)

### 1. Confident garbage in, confident garbage out
Jev only judges the **state you feed it**. If the bot forgets withdrawal locks, partial fills, funding rate flips mid-transfer, or stale balances, `edge_alive` can still look “maybe” and `action` can drift to `paper` forever — or worse, to `ask_human` with a pretty story that feels like a buy signal.

**Suggestion:** Freeze a **required state schema**. Missing any required field → auto `blocked`, no Jev call.

### 2. “Paper” becomes fake confidence
Paper fills that assume you got the mid price teach the system the wrong lesson. After a week of pretty paper PnL, humans start treating `ask_human` as a formality.

**Suggestion:** Paper must use **pessimistic fills** (worse side of the book + full fees + delay). TRUTINA scores predicted vs realized *after* the delay, not at decision time.

### 3. Dual-track can still be gamed
Teams will optimize `restraint_integrity` by renaming checks, not by keeping them. Same Goodhart as stripping caution — just with a nicer label.

**Suggestion:** `restraint_integrity` must be scored from **machine-checkable harness facts** (dry-run ran, max notional bound, kill switch present), not from prose in the prompt.

### 4. Latency theater
Calling Jev on every quote update burns money and adds delay. Arb that needs sub-second reaction cannot wait on a model round-trip.

**Suggestion:** Jev runs on a **cadence or on “candidate events”** (spread above threshold for N seconds), never on every tick. Hot path stays code.

### 5. Calibration theater
A high Jev confidence is not expected value. Without settled outcomes, ACTIVE honor on later “execute bands” is cosplay.

**Suggestion:** No Phase-2 band until TRUTINA has a minimum sample of **settled** paper/shadow outcomes (define N and a Brier/PnL floor in writing).

### 6. Human-yes fatigue
If the bot asks Danny every hour, Danny will start saying yes on autopilot — or ignore it and someone will “temporarily” wire execute.

**Suggestion:** Batch asks into a **daily band card** with hard notional caps. Default for unclear = `skip`, not `ask_human`.

### 7. Legal / account blast radius
“Just arb” can touch derivatives, cross-border venues, or KYC keys sitting in an agent environment. The pack doesn’t name custody or key handling.

**Suggestion:** Keys stay out of agent memory. Separate **read-only market** identity from **trade** identity. CLAIM only if the product framing looks regulated — don’t invent legal advice.

### 8. Hype contamination from X
Most public “AI arb” posts are ads. Building on that discourse biases toward automation theater.

**Suggestion:** Treat X as **threat intel / meme detection**, not as strategy validation. Strategy validation = your ledger only.

## Plain-English summary
Jev is useful here as a **skeptical clerk**, not a trader. The clerk checks whether the story still makes sense after fees, delay, and safety rails. The arithmetic and the exchange buttons stay in boring code. Money does not move until you personally approve a capped band, and only after paper results were scored honestly.

If you skip the boring parts (complete state, pessimistic paper, real calibration, key separation), the pack becomes a very articulate way to lose money with high confidence.

## Suggested next moves (priority order)
1. **Write the required state schema** + auto-`blocked` on missing fields.  
2. **Paper loop stub** under Boof only: log candidates + Jev answers + pessimistic fill simulation (no keys).  
3. **Define TRUTINA settlement rules** (what counts as a resolved paper trade).  
4. **Wire LUDUS Dual-Track** so restraint is measured from harness facts.  
5. Wait for **ADVERSARY** card; fold any new kills into the schema before any human-yes band.

## Go / No-Go
| Step | Go? |
|------|-----|
| Paper loop + schema | **GO** (safe) |
| Shadow live quotes, no orders | **GO** after schema |
| Live micro band | **NO-GO** until TRUTINA sample + ADVERSARY seal + Danny yes |
| Auto-execute from Jev | **NO-GO** permanently under current locks |

----- SOURCE: jev-crypto-arb/PROVENANCE.md -----
# Provenance for jev-crypto-arb (recovered 2026-09-24 PT after the 19:41 PT migration)

Labels: EXACT from transcript / EXACT from attachment / EXACT from mail / REGENERATED / REWRITTEN from summary / LOST

| file | label | source | note |
|---|---|---|---|
| `CARD.md` | **REWRITTEN from summary** | vault:Research/Jev crypto arbitrage route — X top20 stress 2026-09-23.md; vault:Research/Jev crypto arb red team plain English — 2026-09-23.md | summary source copied verbatim under a provenance header |
