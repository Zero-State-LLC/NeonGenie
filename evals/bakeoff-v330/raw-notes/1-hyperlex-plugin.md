# IDEA 1: Hyperlex ChatGPT plugin (Zero State LLC)

----- SOURCE: gap-packets/hyperlex-chatgpt-plugin-2026-09-30.md -----
# GAP packet: Hyperlex ChatGPT plugin (2026-09-30 PT). Advisory only.
Engine: arbitrage (selling public verdicts into a distribution surface). Stage: idea, not validated.
Platform claims (1.2B weekly users, mid-conversation plugin recommendations): UNVERIFIED until LIMINAL reports.

PAIN: Someone asks ChatGPT what a slang term means, where it came from, or whether it's rising or dated. Base models answer with stale or blended dictionary meanings, without evidence or a date. INFERRED; there's no user research yet.

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

CoS checklist: owner GAP (packet), PROMETHEUS (endpoint architecture), Acquire (price/economics), SIGNAL (copy after evidence). Open: LIMINAL platform facts, coverage-vs-query test.

----- SOURCE: chatgpt-plugins-verify/CARD-2026-09-30.md -----
# CARD 2026-09-30 — "ChatGPT recommends plugins mid-conversation" (Isenberg / @skirano)

**SIGNAL**
- Greg Isenberg (X, posted 2026-09-30 17:26 PT, https://x.com/gregisenberg/status/2105454208040206773) quotes @skirano (Pietro Schirano, CEO MagicPath; posted 2026-09-30 10:45 PT, https://x.com/skirano/status/2105353473118404648). OBSERVED via public fxtwitter API mirror; the `user-X` connector needed auth (NOT_COMPUTABLE through that path).
  - Isenberg, exact: "…building a ChatGPT plugin and getting in front of their 1.2 billion weekly users. As of yesterday, ChatGPT recommends plugins in the middle of conversations. Millions of questions get asked every day with no plugin to recommend. Each one is an empty slot." Playbook: "Write the description using the exact phrases people type into ChatGPT… Ship 5 of them…"
  - Schirano, exact: "Stop what you're doing and build a plugin extension for ChatGPT. We've grown over 2000% since the announcement!" Attached image: a daily bar chart from 2026-09-20 to 09-30 with no y-axis label or values. It is flat until 09-27 and then steps up on 09-28, 09-29 and 09-30.
- Verdict: mostly TRUE, but the framing is off. 1.2B weekly users is OBSERVED in an OpenAI primary source. In-conversation suggestions are not new: they launched 2025-10-06. What DevDay 2026 (09-29) announced was "improved ranking and recommendations… in the directory and in conversations." The 2000% figure is SPECULATIVE.

**EVIDENCE**

*Terminology.* "Plugins" is now OpenAI's own word (OBSERVED). developers.openai.com/apps-sdk redirects to /plugins. Help center: "An app connects ChatGPT to an external service… A plugin packages capabilities into a workflow and can include one or more apps, skills, or both" (https://help.openai.com/en/articles/11487775). Since 2026-07-09 the release notes say "We're also replacing the App Directory with the Plugin Directory" (https://help.openai.com/en/articles/6825453-chatgpt-release-notes). "Plugin extensions" is the DevDay 2026 name for sidebar/panel/file-viewer UI. This is not the retired 2023 plugin system (INFERRED).

**Q1 — Mid-conversation recommendations**
- OBSERVED, original launch 2025-10-06 ("Introducing apps in ChatGPT and the new Apps SDK"): "You can discover them when ChatGPT suggests one at the right time… ChatGPT can also suggest apps when they're relevant to the conversation… [e.g.] the Zillow app." Also: "those that meet higher design and functionality standards may be featured more prominently—both in the directory and in conversations." https://openai.com/index/introducing-apps-in-chatgpt/
- OBSERVED, 2026-09-29 DevDay 2026 Recap, section "Improved plugin creation, submission, and discovery": "Improved ranking and recommendations help people find relevant plugins in the directory and in conversations. Users choose which plugins to use and approve the access each one receives. Available to all plans." https://openai.com/index/devday-2026-recap/
- OBSERVED, 2026-08-21 release note "Improved plugin discovery on web and mobile": "Rankings now prioritize plugins people keep using after installation… Plugin availability depends on your plan, region, and workspace settings. Desktop is not included in this update." (release-notes URL above)
- OBSERVED, help center: "review a plugin suggested during a conversation. The options you see depend on your account and where you use ChatGPT." https://help.openai.com/articles/20001256
- OBSERVED, how selection works (developer docs): "ChatGPT and Codex decide when to call your tool based on the metadata you provide. Well-crafted names, descriptions, and parameter docs increase recall…" Tool descriptions should start with "Use this when…" and list disallowed cases. https://developers.openai.com/plugins/guides/optimize-metadata
- OBSERVED, ranking signals and eligibility: "Plugins that demonstrate strong real-world utility and high user satisfaction may be eligible for enhanced distribution opportunities, such as directory placement or proactive suggestions." https://developers.openai.com/plugins/plugin-guidelines
- OBSERVED, limits on influencing discovery (Fair play): no model-readable fields "that manipulate how the model selects or uses other plugins… or interfere with fair discovery"; descriptions "must not recommend overly broad triggering beyond the explicit user intent." (guidelines URL above)
- INFERRED: Isenberg's tip to stuff descriptions with "the exact phrases people type" is allowed only up to the accuracy and no-overbroad-triggering rules.
- INFERRED: suggestions appear to be limited to published Directory plugins. Proactive suggestion is earned (utility, satisfaction, retention), not guaranteed at listing.
- NOT_COMPUTABLE: I found no user opt-out switch for suggestions, no published ranking formula, and nothing on whether uninstalled plugins can be suggested to every user.

**Q2 — What it is technically, and how it gets listed**
- OBSERVED: a plugin = Skills (SKILL.md) and/or an MCP server ("tools… input and output schemas… authentication… optional UI resources"). One universal directory is shared by ChatGPT and Codex. UI uses the open MCP Apps standard plus optional ChatGPT extensions. https://developers.openai.com/plugins/concepts/plugins
- OBSERVED, server: a public HTTPS endpoint with streamable HTTP, typically /mcp. Secure MCP Tunnel or forwarding is for testing only. https://developers.openai.com/plugins/deploy/connect-chatgpt
- OBSERVED, auth: "you are expected to implement an OAuth 2.1 flow that conforms to the MCP authorization spec". Covers protected-resource metadata, PKCE, CIMD/DCR/predefined clients. https://developers.openai.com/plugins/build/auth
- OBSERVED, developer mode: Settings → Security and login → Developer mode. "Availability can depend on account and workspace policy." Use it for private or workspace-only plugins. (connect-chatgpt URL above)
- OBSERVED, submission: upload a ZIP to the Dashboard, pass automated checks, submit for review, then publish when you choose. Also required: verified individual/business identity, domain verification at /.well-known/openai-apps-challenge, a demo account with sample data, and test cases. "Only submit the plugin if you intend for it to be publicly available in the countries you define during submission." "For now, projects with EU data residency cannot submit plugins with MCP servers for review." Rejection emails can be appealed. After publication, MCP server changes go live automatically once they pass checks. https://developers.openai.com/plugins/deploy/submission · https://developers.openai.com/plugins/deploy/app-review
- OBSERVED, plans: "Select plugins are available in all plans, including ChatGPT Free, Plus, Pro, Business, Enterprise, Edu, and ChatGPT for Teachers. Some plugins require a paid plan." Business: on by default. Enterprise/Edu: off by default, admin-enabled. https://chatgpt.com/features/plugins/ · https://help.openai.com/en/articles/11509118
- OBSERVED: "Plugin extensions on the web are coming soon to ChatGPT Free and Go users." https://developers.openai.com/plugins/build/extensions
- OBSERVED, regions (historical): at the 2025-10-06 launch, apps were available "outside of the European Economic Area, Switzerland, and the United Kingdom," and OpenAI said "we expect to bring apps to EU users soon."
- NOT_COMPUTABLE, regions (current): current docs only say availability depends on "plan, region, and workspace." I found no current country list or EEA/UK status.

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

**Q4 — Data, privacy and content rules (for a slang-lookup database)**
- OBSERVED, privacy policy required, covering "categories of personal data collected, the purposes of use, the categories of recipients, data retention timelines, and any controls."
- OBSERVED, minimization: "Gather only the minimum data required." "Do not request the full conversation history, raw chat transcripts… Do not request accumulated conversation context or prior-turn arrays." The MCP server "must not pull, reconstruct, or infer the full chat log." Responses must not carry session/trace IDs or timestamps unless needed.
- OBSERVED, Restricted Data ban: PCI data, PHI, government IDs, credentials.
- OBSERVED: no profiling of "timestamps, IP addresses, or query patterns" unless disclosed, narrowly scoped and user-controllable.
- OBSERVED, content: "Plugins must be suitable for general audiences, including users aged 13–17. Plugins may not explicitly target children under 13. Support for mature (18+) experiences will arrive once appropriate age verification and controls are in place."
- OBSERVED, sourcing: "Do not scrape external websites, relay queries, or integrate with third-party APIs without proper authorization." Avoid "single-word dictionary terms" as plugin names.
- Source for all of the above: https://developers.openai.com/plugins/plugin-guidelines
- OBSERVED, what ChatGPT shares: apps "may access and use relevant context from your ChatGPT conversations" and Memory. They may also see "IP address, device or browser type, language and region settings, and approximate location." Shared data follows the app's own terms/privacy policy. Tool calls include `_meta["openai/session"]`, an anonymized conversation id (changelog 2026-01-15). https://help.openai.com/en/articles/11487775 · https://developers.openai.com/plugins/changelog
- OBSERVED, retention guidance: "Decide how long you keep user data and publish a retention policy. Respect deletion requests… avoid storing raw prompt text unless necessary." https://developers.openai.com/plugins/guides/security-privacy
- OBSERVED, usage policies (effective 2025-10-29): bans "exposing minors to age-inappropriate content, such as graphic self-harm, sexual, or violent content," plus harassment and hate. https://openai.com/policies/usage-policies/
- NOT_COMPUTABLE: I found no rule that specifically covers dictionary or reference definitions of offensive, sexual or drug terms. The exact retention period OpenAI applies to app-call data was not checked.

**Q5 — The numbers**
- 1.2B weekly users: OBSERVED in OpenAI's own words, 2026-09-29: "developers can directly launch new native experiences to our collective 1.2B weekly users." https://openai.com/index/devday-2026-recap/ (TechCrunch 2026-09-29 repeats it; lead only). For context, earlier official figures were 700M+ WAU (2025-09-29 release note) and "over 800 million ChatGPT users" (2025-10-06 post). Caveat: "collective" may cover ChatGPT plus Codex surfaces (INFERRED). It is the latest official figure I found.
- "2000% growth": SPECULATIVE. The only source is Schirano's tweet. The chart has no metric name, units or y-values, and "the announcement" is undefined. No OpenAI source exists for any per-plugin growth. INFERRED: by pixel-measuring the bars, the 09-30 bar is roughly 15–23× the 09-20…09-27 baseline, which is roughly consistent with ~2000% if the y-axis is linear from zero. Also note the step-up starts 09-28, one day before DevDay. Treat it as an anecdote from one builder of a design-tool plugin.

**IMPLICATION for a Hyperlex slang-lookup ChatGPT plugin (all INFERRED)**
- **Build path:**
  - A remote MCP server (streamable HTTP at /mcp) with 2–3 read-only tools. Example: `lookup_slang_term(term)` and `search_slang(query, region?)`, each with `readOnlyHint:true`, `destructiveHint:false`, `openWorldHint:false`, and an outputSchema.
  - Optionally add a Skill for usage/etymology workflows.
  - No auth means no OAuth burden and no demo account.
  - Optional UI card. Test in developer mode, then ZIP → automated checks → review → publish.
  - Publisher verification and a domain challenge are needed. Use a global-residency (not EU-residency) project.
- **Discoverability:**
  - Real, but earned. Tool descriptions should match real phrasing ("Use this when the user asks what a slang term means…"). Exclusions keep precision high ("Do not use for standard dictionary words").
  - Build a golden prompt set (direct, indirect and negative prompts).
  - Biggest risk: ChatGPT already answers "what does X mean" natively. The guidelines require functionality "not natively supported," so the value must be the curated database itself (freshness, regional variants, citations, lineage).
  - Proactive suggestions depend on retention and satisfaction.
  - Name it "Hyperlex," not "Slang" (generic-name rule).
- **Monetization:**
  - Effectively none inside ChatGPT. No paid lookups, credits, subscriptions, upsells or ads.
  - Only allowed paths: (a) users sign in to an existing paid Hyperlex account to unlock features they already pay for; (b) link to an informational plans page, not checkout.
  - So treat the plugin as a brand/distribution and data-flywheel channel, with revenue earned off-platform (API, B2B licensing).
- **Content and privacy risks:**
  - Must be suitable for 13–17. Sexual, drug and slur entries need a teen-safe mode: neutral, clinical definitions, no explicit examples, possibly suppressing the most explicit entries until 18+ support exists. This is the top review-rejection risk.
  - Data provenance: entries scraped from Wiktionary, Urban Dictionary and similar sources need license/ToS compliance (attribution, share-alike) under the "Authorized access" rule. Crawl4AI harvests are not authorization.
  - Privacy: accept only the term or a short query, never conversation context. Don't log raw prompts linked to IP or session. Publish a privacy policy with retention timelines.
  - Query-pattern analytics must be disclosed and user-controllable.

**CONFIDENCE**
- High that the feature exists and on the official terms, build/review and monetization rules: these were read directly in OpenAI docs on 2026-09-30.
- High on 1.2B WAU (stated by OpenAI on 2026-09-29).
- Medium on what exactly changed on 09-29: the recap says "improved ranking and recommendations." Suggestions themselves date to 2025-10.
- Low or none on 2000% (SPECULATIVE).
- NOT_COMPUTABLE: current EEA/UK/CH availability, a suggestion opt-out, ranking internals, and OpenAI-side retention of app calls.

_Raw captures: /workspace/deliverables/chatgpt-plugins-verify/src/ (HTML + extracted text), greg.json, skirano.png._
