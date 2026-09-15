# Job Getter Bot — Autonomous Job Acquisition Engine

**A fully autonomous, model-agnostic job hunting agent that runs 24/7 on Hermes Agent.**
Built for [YOUR_NAME] ([YOUR_CITY] [STATE], [DEGREE] [MAJOR] [UNIVERSITY] [YEAR], [X]+ years [PREVIOUS FIELD] + [TRANSITION CONTEXT]). Target roles: **Customer Success Engineer (CSE), Account Manager (AM), Implementation Consultant (IC), Client Partner (CP), Strategic Account Executive (SAE)**. [YOUR_METRO_AREA] + Remote. Flexible comp.

---

## What This Bot Does

| Phase | Capability | Skills Used |
|-------|------------|-------------|
| **🔍 Scan** | Discovers new jobs from Greenhouse, Ashby, Lever, LinkedIn, company career pages. Deduplicates against history. | `career-ops-scan` |
| **🧠 Evaluate** | Scores every job on **Soul (mission)**, **Pocket (comp)**, **Path (trajectory)** using 3D model. Generates A-G evaluation reports. | `career-ops-evaluate`, `career-ops-shared` |
| **✍️ Tailor** | Creates ATS-optimized résumés & cover letters with keyword injection, humanized voice, JD-tailored bullets. | `career-ops-pdf`, `job-hunt-cheat-code`, `humanizer` (7-layer) |
| **📤 Apply** | Auto-fills application forms, uploads tailored PDFs, submits. Safety: only applies to jobs scoring ≥ 4.0. | `career-ops-apply` |
| **🤝 Outreach** | Finds hiring managers, recruiters, peers on LinkedIn. Generates personalized connection messages. | `career-ops-contact`, `linkedin-network-scan` |
| **📬 Follow-up** | Tracks every application. Flags overdue (>5 business days) and urgent follow-ups. Drafts tailored emails. | `career-ops-followup` |
| **🎯 Interview Prep** | Company-specific intelligence: Glassdoor, Blind, Levels.fyi. Audience maps, STAR stories, technical checklists. | `career-ops-interview-prep`, `behavioral-interview`, `career-ops-deep` |
| **💰 Negotiate** | Turns offer letters into negotiation playbooks with leverage maps, scripts, counter-simulations. | `salary-negotiation` |
| **👤 Onboard** | **NEW** — First-run wizard: ingests your résumés/cover letters, extracts voice & experience, asks 7 targeted questions, runs gap analysis. | `career-ops-onboard` |
| **🤖 Model-Agnostic LLM** | **NEW** — All LLM calls route through a wrapper that reads the active model from env/config. Works with Ollama Cloud, OpenRouter, local Ollama, LMStudio, any OpenAI-compatible endpoint. | `career-ops-llm` |

---

## Architecture

```
job-getter/
├── start.bat                  ← one-click launcher (Windows)
├── Procfile                   ← Render/Heroku deployment
├── config/
│   └── profile.yml            ← Your contact info, target roles, geography, comp
├── modes/
│   └── _profile.md            ← Archetypes, narrative, writing style, deployment table
├── data/
│   ├── pipeline.md            ← Kanban: Pending → Evaluated → Applied → Interview → Offer
│   ├── applications.md        ← Application tracker (TSV)
│   ├── scan-history.tsv       ← Every URL ever scanned (dedup)
│   ├── follow-ups.md          ← Follow-up cadence log
│   └── profile_onboard.md     ← **NEW** Synthesized user profile from onboarding
├── onboard/                   ← **NEW** Onboarding workflow
│   ├── processing/
│   │   ├── resumes/           ← Drop your résumés here (PDF/DOCX/TXT)
│   │   ├── cover_letters/     ← Drop cover letters here
│   │   └── parsed/            ← Parsed JSON (auto-generated)
│   ├── template_questions.md  ← 7 targeted questions
│   ├── wait_for_ready.sh      ← Helper script
│   └── gap_analysis.md        ← Gap analysis output
├── reference/
│   └── 2026_RESUME_AND_COVER_LETTER_DISSERTATION.md  ← 1162 lines, 18 tier-1 sources
├── references/                ← Interview guide template, prompts
├── reports/                   ← Per-job A-G evaluation reports
├── jds/                       ← Extracted job descriptions
├── interview-prep/            ← Company-specific interview intelligence
├── writing-samples/           ← Your past cover letters for voice calibration
├── output/                    ← Generated PDFs (tailored résumés)
├── scripts/                   ← Automation scripts (merge_onboard.py, etc.)
├── skills/                    ← Hermes skills (career-ops-* + job-getter-bot)
│   ├── career-ops-llm/        ← **NEW** Model-agnostic LLM wrapper
│   ├── career-ops-onboard/    ← **NEW** Onboarding skill
│   └── career-ops-hermes/     ← 17 career-ops skills + 6 standalone
├── backend/                   ← Flask API + SQLite (dashboard)
│   ├── server.py
│   ├── jobs.db
│   └── requirements.txt
└── frontend/                  ← React + Three.js dashboard (alabaster/sage/rust theme)
```

---

## Quick Start (for your friend)

### 1. Clone & Configure

```bash
git clone https://github.com/YOUR_USERNAME/job-getter-bot-sanitized.git
cd job-getter-bot-sanitized
```

### 2. Set Your Model (pick one)

**Option A: Environment variables (recommended)**

```bash
# Ollama Cloud (DeepSeek, Nemotron, etc.)
export HERMES_LLM_ENDPOINT="https://ollama.com/v1"
export HERMES_LLM_API_KEY="sk-..."
export HERMES_LLM_MODEL="deepseek-v4-pro"   # optional

# OR OpenRouter free tier
export HERMES_LLM_ENDPOINT="https://openrouter.ai/api/v1"
export HERMES_LLM_API_KEY="sk-or-..."
export HERMES_LLM_MODEL="nvidia/nemotron-3-super-120b-a12b:free"

# OR Local Ollama
export HERMES_LLM_ENDPOINT="http://127.0.0.1:11434/v1"
export HERMES_LLM_API_KEY=""   # usually not needed
export HERMES_LLM_MODEL="nemotron-3-ultra"
```

**Option B: Hermes config file** (`~/.hermes/config.yaml`)

```yaml
llm:
  endpoint: "https://ollama.com/v1"
  api_key: "sk-..."
  model: "deepseek-v4-pro"
```

### 3. First Run — Onboarding

```bash
# Start Hermes with the jobgetter profile
hermes run jobgetter
```

On first run, the bot will:
1. **Greet you** and ask you to drop files in:
   - `~/Documents/job-getter/onboard/processing/resumes/`
   - `~/Documents/job-getter/onboard/processing/cover_letters/`
2. **Wait for you to type `ready`**
3. **Parse your documents** (extracts experience, skills, writing voice)
4. **Ask 7 targeted questions** about goals, preferences, constraints
5. **Generate**:
   - `data/profile_onboard.md` — your synthesized profile
   - `onboard/gap_analysis.md` — readiness gaps vs. CSE/AM/IC/CP/SAE
6. **Start scanning** for jobs automatically

### 4. Ongoing Operation

The bot runs on a **4-hour cron** (scan → evaluate → alert). You'll get Telegram alerts via your configured bot (or whatever gateway you configure) with:
- Top 3 new high-score jobs (≥ 4.0)
- Follow-ups needed
- Urgent items

Dashboard: `http://127.0.0.1:5000` (after `start.bat` or `gunicorn`)

---

## Key Configuration Files

| File | Purpose | Edit? |
|------|---------|-------|
| `config/profile.yml` | Your contact, target roles, geography, comp floor | **YES** — fill in your details |
| `portals.yml` | Tracked companies, search queries, title/location filters | **YES** — add your target companies |
| `cv.md` | Fallback résumé (used if onboarding not done) | **YES** — keep current |
| `modes/_profile.md` | Archetypes, narrative, writing style cache | Auto-updated |
| `data/profile_onboard.md` | **NEW** Your synthesized profile from onboarding | Auto-generated |
| `reference/2026_RESUME_AND_COVER_LETTER_DISSERTATION.md` | ATS/keyword/bullet rules (18 sources) | **Reference only** |

---

## Skills Inventory (24 total)

### Core Pipeline (17 career-ops)
1. `career-ops-shared` — System context, scoring, writing style, ethics
2. `career-ops-scan` — 4-level portal discovery (parsers, APIs, browser, web search)
3. `career-ops-evaluate` — Full A-G evaluation (match, comp, legitimacy)
4. `career-ops-pdf` — ATS-optimized PDF generation + verification
5. `career-ops-apply` — Live form filling & submission
6. `career-ops-pipeline` — URL inbox → JD extract → evaluate → report → PDF → tracker
7. `career-ops-batch` — Mass parallel processing (10+ jobs)
8. `career-ops-contact` — LinkedIn outreach (recruiter/HM/peer templates)
9. `career-ops-followup` — Cadence tracker + tailored drafts
10. `career-ops-deep` — 6-axis company research
11. `career-ops-interview-prep` — Company-specific interview intelligence
12. `career-ops-tracker` — Application viewer + stats dashboard
13. `career-ops-compare` — Multi-offer comparison (10 dimensions)
14. `career-ops-patterns` — Rejection pattern detector
15. `career-ops-project` — Portfolio project evaluation (6 dimensions)
16. `career-ops-training` — Course/cert evaluation (6 dimensions)
17. `career-ops-llm` — **NEW** Model-agnostic LLM wrapper

### Standalone Job-Hunt Skills (7)
18. `job-getter-bot` — Orchestrates full lifecycle (cron + on-demand)
19. `job-hunt-cheat-code` — One-job deep attack: tailored résumé + outreach plan
20. `job-match` — Score fit + generate cover letter from JD + CV
21. `jd-decoder` — Decode any JD into actionable offer strategy
22. `salary-negotiation` — Turn offer letter into negotiation playbook
23. `linkedin-network-scan` — Scan connections for warm intros
24. `behavioral-interview` — Reusable STAR story bank
25. `resume-builder` — 13 print-ready templates
26. `career-ops-onboard` — **NEW** First-run profiling wizard

---

## Model-Agnostic Design (NEW)

**No hard-coded model names anywhere.** All LLM calls go through `career-ops-llm` which reads:

1. `HERMES_LLM_ENDPOINT` (env) → 2. `HERMES_LLM_API_KEY` (env) → 3. `HERMES_LLM_MODEL` (env, optional) → 4. `~/.hermes/config.yaml` → 5. Local defaults

**Switch providers in seconds** — just change env vars or config file. No code changes.

---

## Humanization & AI Detection

- **Writing Style Calibration**: Reads `writing-samples/` → extracts 7 style descriptors → caches in `_profile.md`
- **7-Layer Humanizer** (`humanization-seven-layer`): Tone, sentence length, openings, punctuation, vocabulary, structure, voice + "avoid" list
- **Dissertation Compliance**: Every résumé/cover letter follows `2026_RESUME_AND_COVER_LETTER_DISSERTATION.md` (ATS architecture, keyword strategy, bullet formula, layoff narrative, AI-evasion)
- **Typical AI-detector scores**: < 15% (youscan.io) — "primarily human-written"

---

## Deployment

### Local (Windows)

```bash
# Double-click start.bat
# Opens http://127.0.0.1:5000
```

### Render / Heroku / Any Container

```bash
# Build command:
pip install -r backend/requirements.txt && cd frontend && npm install --legacy-peer-deps && npm run build

# Start command:
gunicorn -w 2 -b 0.0.0.0:$PORT backend.server:app
```

### Cron (Autonomous 4-hour cycles)

Configured in Hermes cron for profile `jobgetter`:

```
Schedule: every 4 hours
Prompt: "Run the job-getter bot: scan for new CSE/AM/IC/CP/SAE roles in YOUR_METRO_AREA + Remote, evaluate any new finds, auto-apply to anything scoring 4.0+, check follow-ups, alert me on anything needing attention."
```

---

## Updating the Bot

To pull latest changes from upstream:

```bash
cd job-getter-bot-sanitized
git remote add upstream https://github.com/BBridgeers/job-getter.git   # replace with your upstream if different
git fetch upstream
git merge upstream/main   # resolve any conflicts
git push origin main      # push to your public repo
```

---

## License

MIT — Free to use, modify, share. Built on [santifer/career-ops](https://github.com/santifer/career-ops) (MIT).

---

## Support

- **Issues**: GitHub Issues on your fork
- **Documentation**: This README + inline skill docs (`skills/*/SKILL.md`)
- **Hermes Agent Docs**: https://hermes-agent.nousresearch.com/docs

---

**Built with Hermes Agent** — Autonomous AI agent framework by Nous Research.