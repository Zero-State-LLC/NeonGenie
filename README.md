<div align="center">

# Neon Genie

### Product & opportunity intelligence for Hermes

[![Version](https://img.shields.io/badge/version-3.27.0-7c3aed?style=for-the-badge)](./manifest.json)
[![Hermes Skill Evals](https://img.shields.io/github/actions/workflow/status/scrimshawlife-ctrl/NeonGenie/hermes-evals.yml?branch=main&label=hermes-evals&style=for-the-badge)](./.github/workflows/hermes-evals.yml)
[![Authority](https://img.shields.io/badge/authority-advisory%20only-0ea5e9?style=for-the-badge)](#what-it-will-not-do)
[![Privacy](https://img.shields.io/badge/privacy-by%20construction-a855f7?style=for-the-badge)](./PRIVACY.md)
[![License](https://img.shields.io/badge/license-MIT-22c55e?style=for-the-badge)](./LICENSE)

<img src="docs/assets/hero.jpg" alt="Neon Genie — luminous lamp on a dark network grid" width="920" />

**You have an idea. You need a real plan — not invented buyers, fake capital, or “just ship it.”**

Neon Genie is a Hermes skill for people turning ideas into roadmaps and approaches under real constraints (solo, between jobs, limited money). It labels what is known vs guessed, asks for missing private facts, and **refuses to invent** what it cannot know.

[Website](https://scrimshawlife-ctrl.github.io/NeonGenie/) · [Install](#install) · [Use it](#use-it-in-hermes) · [Privacy](./PRIVACY.md) · [Demo](./docs/DEMO.md)

</div>

---

## What you get

| You bring | Neon Genie helps with |
|-----------|------------------------|
| An idea, product, or stuck project | A clearer plan: who it’s for, what “done” looks like, what to try next |
| Constraints (time, money, skills) | Honest limits — no invented resources |
| Questions about buyers, markets, proof | Labeled claims, research when public facts help, questions when private facts are missing |

**It is advice only.** It will not spend money, email people, publish posts, or change your git repo.

---

## Install

```bash
# Prefer org path (Zero State)
hermes skills install Zero-State-LLC/NeonGenie/skills/neon-genie
# Mirror (personal): scrimshawlife-ctrl/NeonGenie/skills/neon-genie
```

Then reload or restart Hermes.

**Or clone this repo:**

```bash
git clone https://github.com/Zero-State-LLC/NeonGenie.git
# mirror: https://github.com/scrimshawlife-ctrl/NeonGenie.git
cd NeonGenie
./install.sh
python scripts/neon_genie.py do wizard --path quick --auto
# or: python scripts/neon_genie.py do doctor
```

You want doctor smoke to pass and a sample package under `out/neon-genie/wizard-quick/`.

More detail: [docs/HERMES_DISTRIBUTION.md](./docs/HERMES_DISTRIBUTION.md)

---

## Use it in Hermes

1. Start Hermes with Neon Genie installed.  
2. Say **“Use Neon Genie”** (or describe a product/opportunity problem).  
3. Explain in plain language: who is stuck, what “done” looks like, what you already know, and what you refuse to invent.  
4. Read the answer as a **draft**. Check that claims are labeled and missing private facts are asked for, not filled in.

### Packaging wizard (CLI)

When you are new to the skill or unsure which packaging job to run:

```bash
python scripts/neon_genie.py do wizard --preset product-audit --print-only --json
python scripts/neon_genie.py do wizard --path quick --auto
python scripts/neon_genie.py do wizard --answers answers.json --run
```

Resolve path defaults to **print-only** (exact `do …` argv). Quick path runs
doctor + a sample product-audit package. Product judgment stays in Hermes chat
(OPEN→SEAL). See [references/wizard.md](./references/wizard.md).

### Guided dashboard wizard

Hermes installations that include the Neon Genie dashboard integration also
show a **Neon Genie** page in the sidebar at `/neon-genie`.

```bash
hermes dashboard
```

Use the dashboard wizard when you want help shaping the **chat prompt** before
entering Chat (mission, outcome, constraints, research toggles). It does not
replace the packaging CLI wizard above and does not grant execution rights.

### Example prompts

```text
Use Neon Genie. I'm between jobs with limited money and an app idea.
I need a realistic roadmap and first approaches I can actually run.
Do not invent buyers, capital, or skills I did not declare.
Research public facts if you can; ask me for private facts instead of inventing.
Label every important claim. Do not modify any repo.
```

```text
Use Neon Genie. We have a tool but no clear who-pays.
What should we charge? Research public competitors if you can.
If you need private facts (budget owner), ask me. Do not invent a buyer.
```

```text
Use Neon Genie. First cash in 7 days, no new capital.
Only use skills and access I list. If you cannot answer honestly, say so.
```

```text
Use Neon Genie. Stay offline: research.enabled=false
Only use what I paste and what is already in this workspace.
```

### What a good answer looks like

- Important claims marked as **observed** (with a source), **inferred**, **speculative**, or **not computable**  
- Missing private facts asked as questions (not invented)  
- A concrete next step or draft packet you can act on  
- Still **advice only** — no “I’ll charge the card” or “I’ll merge the PR”

Shorter guide: [QUICKSTART.md](./QUICKSTART.md) · Walkthrough: [docs/DEMO.md](./docs/DEMO.md)

---

## Simple rules

| Rule | Meaning |
|------|---------|
| **Don’t invent** | No fake buyers, budgets, credentials, or capital |
| **Label claims** | Separate facts, inferences, guesses, and unknowns |
| **Ask for private facts** | Don’t scrape secrets or guess what only you know |
| **Advice only** | Recommend; never spend, publish, contact, or edit the repo |
| **Privacy-first packaging** | Sample CLI runs stay local by default; see [PRIVACY.md](./PRIVACY.md) |

---

## Privacy (short)

This skill does **not** run ads, silent telemetry, or train models on your content. Files it writes go where **you** choose.

Hermes, model APIs, and search tools have **their own** policies — Neon Genie cannot rewrite those. When research is allowed, external actions are recorded on the run receipt.

Full contract: [PRIVACY.md](./PRIVACY.md)

---

## Optional: check install from a terminal

Most people only need Hermes chat. Use the CLI if you want to **verify install** or run a **sample package** on disk.

From a clone of this repo:

```bash
# 1. Is the skill healthy?
python scripts/neon_genie.py do doctor

# 2. Write one sample run (then open run-envelope.json in that folder)
python scripts/neon_genie.py do run --recipe product-audit --out out/neon-genie/demo
```

That’s enough for almost everyone.

**A few more samples** (same pattern):

```bash
python scripts/neon_genie.py do run --brief examples/zero-option.brief.yaml --out out/neon-genie/zero
python scripts/neon_genie.py do run --brief examples/capital-sprint.brief.yaml --out out/neon-genie/sprint
```

After any sample run, open **`run-envelope.json`** first — it points at the rest.

**For maintainers / CI** (not everyday use): full command list in [QUICKSTART.md](./QUICKSTART.md) · release notes in [CHANGELOG.md](./CHANGELOG.md)

Green `do doctor` / CI means the **install and fixtures** work. It does **not** prove every chat answer is perfect — that still depends on Hermes and the model.

---

## Example: missing buyer

**You say:** “We have an audio tool but no defined buyer. What should we charge?”

**Expect something like:**

- Product idea clarified as a draft  
- **Price stays unknown** until who pays is known  
- A clear **ask for private facts** (who buys, who controls budget)  
- **No** invented market size, **no** repo changes, **no** spend  

Try the same idea in Hermes with the prompts above, or run:

```bash
python scripts/neon_genie.py do run --recipe commercial --out out/neon-genie/audio-buyer
```

---

## More docs

| Link | What it is |
|------|------------|
| [Website](https://scrimshawlife-ctrl.github.io/NeonGenie/) | Short landing page |
| [QUICKSTART.md](./QUICKSTART.md) | Install + prompts |
| [docs/DEMO.md](./docs/DEMO.md) | 10-minute walkthrough |
| [docs/PREMIERE.md](./docs/PREMIERE.md) | Why this vs free-form idea chat |
| [PRIVACY.md](./PRIVACY.md) | Privacy contract |
| [docs/CATALOG.md](./docs/CATALOG.md) | Hub / catalog status |
| [CHANGELOG.md](./CHANGELOG.md) | What’s new |
| [CONTRIBUTING.md](./CONTRIBUTING.md) | Development |

**Version:** 3.27.0 · **License:** MIT · **Maintainers:** [Applied Alchemy Labs / @scrimshawlife-ctrl](https://github.com/scrimshawlife-ctrl) · [Zero-State-LLC](https://github.com/Zero-State-LLC)

---

<div align="center">
<sub>Neon Genie v3.27.0 · advice only · evidence before invention</sub>
</div>


## License

This repository now uses the MIT License for original Zero State materials going forward. See [LICENSE](LICENSE). Earlier grants in repository history are not rewritten.

Third-party components remain subject to their respective licenses.

Source, profile, and migration rules: `references/source-and-upgrades.md`.
