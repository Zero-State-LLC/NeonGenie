# IDEA 2: x402 pay-per-lookup Vernacular API (Zero State LLC)

----- SOURCE: gap-packets/hyperlex-chatgpt-plugin-2026-09-30.md (API/buyer/x402 lines) -----
# GAP packet: Hyperlex ChatGPT plugin (2026-09-30 PT). Advisory only.
Engine: arbitrage (selling public verdicts into a distribution surface). Stage: idea, not validated.
Platform claims (1.2B weekly users, mid-conversation plugin recommendations): UNVERIFIED until LIMINAL reports.
BUYER:
- End users (curious people, parents): highest volume, lowest willingness to pay. They're distribution, not revenue. WTP = NOT_COMPUTABLE.
- Trust and safety teams and moderation vendors: the clearest paying buyer for coded or emerging terms. They're reached through the API, not through ChatGPT. WTP unknown.
- Brands, marketers, social teams: they ask "is this term rising or cringe before we post it?" Mid willingness to pay. Freshness is what they're paying for.
- Recommendation: ChatGPT plugin = free top-of-funnel. Paid = the same backend sold through the x402 pay-per-lookup API and later a B2B key.

EXISTING ASSET: Vernacular public verdict export (84 attested terms per Boof, target +10–20 a day). Fields: meaning from context, lineage family, adoption evidence, OBSERVE/PASS. Shared backend with the x402 Vernacular API candidate and the Nebius x NVIDIA hackathon entry (due Oct 30). No new invention.

PRICE UNIT (PROPOSED, not live):
- Plugin: free to the ChatGPT user.
- API: one x402 micro-charge per verdict lookup. Freshness or adoption evidence could be a higher tier.
- No price number is set. Live pricing needs Danny's yes.

SMALLEST BUILD: One read-only endpoint, `GET /term/{slug}`, returns the public verdict JSON, plus a `search` endpoint for fuzzy match and miss logging. Serve it from a static snapshot of the public export only. Add an OpenAPI or MCP manifest for the ChatGPT apps surface and an x402 wrapper on the same route. One build serves all three (plugin, API, hackathon).

DISTRIBUTION: ChatGPT in-conversation discovery (UNVERIFIED), the hackathon demo, and SIGNAL drafts after evidence exists. Miss logs (terms people asked about that we lack) feed the Vernacular ingest queue, so the plugin also acts as a demand sensor.

KILL CRITERIA (proposed, Danny to set numbers):
- LIMINAL finds that plugin discovery doesn't reach third parties, or that listing needs terms we can't meet.
- Coverage is too thin: most real queries miss our corpus after N weeks even with +10–20 terms a day.
- No paid lookups on the x402 route within an agreed window after listing.
- Any leak path to private or held-out Hyperlex rows or raw source text means we stop at once.

WALLS: Public attested verdicts only. Never private, corpus or held-out rows. No raw Reddit/X/UD resale (paraphrased verdict plus evidence pointers only). Listing, pricing, terms, wallet and publish all gated on Danny's yes.


----- SOURCE: chatgpt-plugins-verify/CARD-2026-09-30.md (Q3 Monetization + implication) -----
**Q3 — Monetization**
- OBSERVED: "Currently, plugins may conduct commerce only for physical goods. Selling digital products or services—including subscriptions, digital content, tokens, or credits—is not allowed, whether offered directly or indirectly (for example, through freemium upsells)."
- OBSERVED: "Users may sign in to an existing paid account and access features already included in their subscription. Plugins must not display subscription plans, initiate new subscriptions, or promote upgrades." Plugins may link to an informational plans page but not to "a checkout or other transactional page."
- OBSERVED: no ChatGPT-specific fees or surcharges, and no worse version than on your own site.
- OBSERVED: names/descriptions must not advertise pricing, trials or promotions.
- OBSERVED: "Plugins must not serve advertisements and must not exist primarily as an advertising vehicle."
- OBSERVED: "Instant Checkout, which is currently in beta, is currently available only to select marketplace partners… standard external checkout is the required approach."
- Source for all of the above: https://developers.openai.com/plugins/plugin-guidelines
- OBSERVED, checkout docs: external checkout is recommended. "Current approval is limited to plugins for physical goods purchases". The ChatGPT payment sheet (private beta, select marketplaces) and an ACP Delegate Payment option exist for PCI DSS Level 1 merchants. https://developers.openai.com/plugins/build/monetization
- OBSERVED: ACP/Instant Checkout launched 2025-09-29 (release notes).
- OBSERVED: Sign in with ChatGPT lets users spend their own ChatGPT allowance in 16 partner tools; "A partner may still charge for its own product or services." (DevDay recap; 2026-09-29 release notes)
- INFERRED: there is no per-use charging for a digital service inside ChatGPT today, and no developer revenue share.
- **Monetization:**
  - Effectively none inside ChatGPT. No paid lookups, credits, subscriptions, upsells or ads.
  - Only allowed paths: (a) users sign in to an existing paid Hyperlex account to unlock features they already pay for; (b) link to an informational plans page, not checkout.
  - So treat the plugin as a brand/distribution and data-flywheel channel, with revenue earned off-platform (API, B2B licensing).

----- SOURCE: hackathons-2026-10/nebius-nvidia-plan.md (excerpt) -----
# Nebius x NVIDIA Global AI Hackathon: entry plan for Zero State LLC
Researched Sep 29, 2026 (PT). Sources: [Overview](https://nebiusglobalaihackathon.devpost.com/) · [Official Rules](https://nebiusglobalaihackathon.devpost.com/rules) · [Resources](https://nebiusglobalaihackathon.devpost.com/resources). The LinkedIn link https://lnkd.in/dsdEkmWw points to the overview page (OBSERVED).
Labels: **O** = OBSERVED (seen in a source) · **I** = INFERRED · **S** = SPECULATIVE · **NC** = NOT_COMPUTABLE

## Verdict: ENTER
Main reason: an LLC can enter, US entrants are allowed, entry is free, and the only platform requirement is a runtime call to Nebius Token Factory using an NVIDIA open model. A Hyperlex/Vernacular agent is a real, non-obvious product for the "Best Apps and Agents" track. The only real cost is open-sourcing the repo. **O** (Rules §3, §4)

## Key facts
- **Organizer:** Nebius B.V. (Netherlands) is the sponsor. Devpost is the administrator. **O**
- **Eligibility:** Individuals of legal age, Teams, and Organizations, including LLCs, "that exist and have been organized or incorporated at the time of entry." Excluded places include Brazil, Quebec, Russia, Crimea, Cuba, Iran, North Korea, and other OFAC-sanctioned places. Zero State (Wyoming, formed Aug 3, 2026) qualifies. **O** An organization must appoint one Representative, who would be Danny. **O**
- **Tech requirement:** The project must run on Nebius Token Factory (a runtime inference API call) or Nebius AI Cloud (Serverless Jobs, Endpoints, or DevPods), and it must use at least one NVIDIA open-source model, such as Nemotron. **O** The DGX Spark/Qwen boxes do **not** satisfy the requirement on their own. They can be used for dev or offline batch work only. **I**
- **What to submit:** a working demo URL, a text description, a public YouTube video under 3 minutes, and a public GitHub/GitLab/Bitbucket repo. The repo needs an **open-source license** (Apache-2.0, MIT, or MPL-2.0) visible in its About section, plus a README. You also pick a track and give feedback on Nebius/NVIDIA tools. If the project existed before Aug 26, you must explain what was "significantly updated." **O**
- **Judging:** Stage 1 is pass/fail on theme fit and API use ("not a superficial rebrand"). Stage 2 weighs four criteria equally: Technological Implementation, Design, Potential Impact, and Quality of the Idea. **O**
- **Prizes:** Grand $20K, 2nd $10K, 3rd $6K. Each of the 4 track winners gets a Jetson Orin Nano. Best Use of Tavily is $3K. City Winner is $500 × 20, and San Francisco and LA are among the cities. Most Valuable Feedback is $100 × 10. A project can win one Overall **or** one Track award, **plus** one Bonus award. **O** Competition is large: about 14,467 registered participants. **O**
- **Dates:** Submissions run Aug 26 to **Oct 30, 2026, 10:00 AM PT**. Judging runs Dec 1–15. Winners are announced around Jan 11, 2027. **O**
- **IP:** "All Submissions remain the intellectual property" of the entrant. The sponsor gets a non-exclusive license for judging only. The sponsor and Devpost can use the entry and contributors' names and likenesses for promotion for 3 years. **O** ⚠️ **Concern:** the public open-source license requirement means anything in the repo becomes freely reusable by anyone, not just Nebius. **I** Winners must provide a W-9, and disputes go to AAA arbitration under NY law. **O**
- **Costs:** entry is free. **O** Credits: $25 of Token Factory credit through a form (code NEBIUS-DEVPOST-GLOBAL26), plus another $25 for joining the free Nebius Builders Program, which also includes Tavily credit. **O** Whether $50 covers the build: **NC**. Nemotron Nano/Super pricing was not checked.

## Recommended pitch (track: Best Apps and Agents, plus the Tavily bonus)
**"Vernacular: a live slang-intelligence agent."** Nemotron on Token Factory reads any text (support tickets, comments, DMs), flags internet slang and memes, and explains them. It checks unknown terms live with Tavily search and saves confirmed terms to a growing term database. A Jev-style gate filters out false positives. The pitch is aimed at trust-and-safety and customer-support teams that can't keep up with how fast internet language changes. **S** (fit and win odds)
*Alternate:* use PatchHive in the Coding and Agentic Engineering track, as a coding agent that repairs code and is scored against the PatchHive benchmark inside Token Factory. **S**

## Smallest build that meets the rules
1. A new public repo (MIT or Apache-2.0) with a thin agent layer. It calls Token Factory, using Nemotron Nano for the fast "is this slang?" check and Super/Ultra for explanations, and calls Tavily for unknown terms.
2. A small web demo: paste text, get highlighted terms with definitions and confidence. Host it on Nebius Serverless Endpoints (encouraged) or anywhere else.
3. A **seed term sample** made only from data Zero State owns or is licensed to publish. Do not dump scraped Urban Dictionary, Know Your Meme, Reddit, or X data into the repo.
4. A README with a "What's new since Aug 26" section, a video under 3 minutes, and the feedback form.

## Timeline (Sep 30 to Oct 30)
- **Sep 30–Oct 2:** Danny registers and claims both $25 credits. Check Nemotron model IDs and pricing on Token Factory. Decide what code and data stay closed.

----- SOURCE: hackathons-2026-10/other-active.md (x402 line) -----
Search scope: Devpost (the public listing API for open and upcoming events, 78 events checked), lablab.ai event list, MLH, DoraHacks, Kaggle, and sponsor searches (NVIDIA, Google, Anthropic, OpenAI, Meta, Mistral, HF, Cerebras, Groq, Together, Tavily, x402/Coinbase). Free web sources only. Already excluded: Nebius x NVIDIA, AWS CDS, Amazon Build Ship Shape, OpenCV, Google Cloud AI Builder Cup, World Bank, AMD ACT III.
- **No open x402 or agent-payments hackathon found.** The SKALE/Coinbase SF x402 event (DoraHacks) ran Feb 11–13, 2026, and the other DoraHacks agent events found (Stellar, CROO, KeeperHub) had closed. **O** The DoraHacks listing page didn't render for me, so a smaller open event could have been missed.

----- SOURCE: vernacular-discovery/RUNBOOK.md (goal) -----
# Vernacular discovery lane (vernacular-discovery-v1)

Goal: add 10–20 genuinely new slang terms per day to `/workspace/vernacular-ingest/data/vernacular.sqlite3`.
Free sources handle broad discovery. Paid X is used only as a small, targeted live-evidence pull for high-signal fresh hits.

All lane files live in `/workspace/deliverables/vernacular-discovery/`. The lane never edits INGEST code or config, the
