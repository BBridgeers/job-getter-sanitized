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

---

## Detailed Configuration Walkthrough

### 1. Profile Configuration (`config/profile.yml`)

This is the **single most important file** to customize. Every job search parameter derives from here.

```yaml
# REQUIRED: Your identity
name: "Your Full Name"
email: "you@domain.com"
phone: "(XXX) XXX-XXXX"
location: "Your City, State (Metro Area)"
linkedin_url: "https://linkedin.com/in/yourhandle"
linkedin_display: "linkedin.com/in/yourhandle"
portfolio_url: "https://github.com/yourhandle"
portfolio_display: "github.com/yourhandle"

# REQUIRED: Target roles (edit titles to match your goals)
target_roles:
  - "Customer Success Executive"
  - "Account Manager"
  - "Implementation Consultant"
  - "Client Partner"
  - "Strategic Account Executive"

# REQUIRED: Geography
geo_preferences:
  - "Your Metro Area"
  - "Remote (US)"

# OPTIONAL: Compensation strategy
compensation:
  strategy: "flexible"  # or "fixed" with min_base, min_ote
  note: "Optimize for the right role/title, money follows"

# OPTIONAL: PDF generation threshold (jobs scoring >= this get auto-PDF)
auto_pdf_score_threshold: 4.0

# OPTIONAL: Search fine-tuning
search:
  titles:  # Add/remove titles relevant to you
    - "Customer Success Executive"
    - "Customer Success Manager"
    - "Account Manager"
    # ... add your specific target titles
  locations:
    - "Your Metro Area"
    - "Remote"
    - "Your State"
  exclude_titles:  # Add titles you NEVER want
    - "Intern"
    - "Junior"
    - "Entry Level"
    - "SDR"
    - "BDR"
    - "Business Development"

# OPTIONAL: Archetype framing (used by cover letter generator)
# Replace with YOUR career archetypes
archetypes:
  - name: "Your Archetype 1"
    signals: ["keyword1", "keyword2", "keyword3"]
    fit: "Your fit description here"
  - name: "Your Archetype 2"
    signals: ["keyword1", "keyword2"]
    fit: "Your fit description here"
```

### 2. Portal Configuration (`portals.yml`)

Controls WHERE the bot searches. Two mechanisms:

**Search Queries** (web_search with site: filters) — broad discovery:
```yaml
search_queries:
  - query: 'site:boards.greenhouse.io "Customer Success" "YOUR_METRO" OR "Remote"'
    name: "Greenhouse — CS YOUR_METRO/Remote"
    enabled: true
```
- Enable/disable queries with `enabled: true/false`
- Add company-specific ATS queries (Greenhouse, Ashby, Lever APIs)
- Adjust location terms for your geography

**Tracked Companies** — direct career page scanning:
```yaml
tracked_companies:
  - name: "Target Company"
    careers_url: "https://company.com/careers"
    enabled: true
    api: "https://boards-api.greenhouse.io/v1/boards/company/jobs"  # optional
    api_provider: "greenhouse"  # or "ashby", "lever"
    notes: "Why this company matches you"
```
- Add YOUR target companies (not the template examples)
- Include `api` + `api_provider` for Greenhouse/Ashby/Lever hosts for faster API scanning
- Set `enabled: false` to pause a company without deleting

**Title & Location Filters** — post-search filtering:
- `title_filter.positive`: Keywords that INCLUDE a job
- `title_filter.negative`: Keywords that EXCLUDE a job (SDR, BDR, Intern, etc.)
- `title_filter.seniority_boost`: Keywords that boost seniority score
- `location_filter.allow`: Locations to keep (your metro, remote, US)
- `location_filter.block`: Locations to exclude (SF, NYC, relocation required, etc.)

### 3. Model Configuration

**Option A: Environment Variables (recommended for portability)**
```bash
# ~/.bashrc or ~/.zshrc or Windows Environment Variables
export HERMES_LLM_ENDPOINT="https://ollama.com/v1"
export HERMES_LLM_API_KEY="sk-..."
export HERMES_LLM_MODEL="deepseek-v4-pro"
```

**Option B: Hermes Config (`~/.hermes/config.yaml`)**
```yaml
llm:
  endpoint: "https://ollama.com/v1"
  api_key: "sk-..."
  model: "deepseek-v4-pro"
```

**Supported Providers** (any OpenAI-compatible endpoint):
| Provider | Endpoint | Notes |
|----------|----------|-------|
| Ollama Cloud | `https://ollama.com/v1` | DeepSeek, Nemotron, Kimi, GLM, etc. |
| OpenRouter | `https://openrouter.ai/api/v1` | 300+ models, free tier available |
| Local Ollama | `http://127.0.0.1:11434/v1` | No API key needed usually |
| LMStudio | `http://127.0.0.1:1234/v1` | Local GGUF models |
| Groq | `https://api.groq.com/openai/v1` | Fast, free tier |
| Custom | Your endpoint | Any OpenAI-compatible API |

### 4. Telegram Integration (for cron alerts)

1. Create bot via `@BotFather` on Telegram
2. Get your user ID via `@userinfobot`
3. Create `.env` from template:
```bash
cp profile-config/.env.template .env
# Edit .env with your values
```
Required variables:
```bash
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_ALLOWED_USERS=123456789  # your user ID
TELEGRAM_HOME_CHANNEL=123456789   # chat ID for alerts
TELEGRAM_HOME_CHANNEL_NAME=YourName
OPENROUTER_API_KEY=sk-or-...      # for cron model
BROWSER_USE_API_KEY=...           # optional, for browser automation
```

### 5. Running the Bot

**First time (onboarding):**
```bash
hermes run jobgetter
# Bot will prompt you to drop files in onboard/processing/resumes/ and /cover_letters/
# Type "ready" when done
# Bot parses documents, asks 7 questions, generates profile_onboard.md + gap_analysis.md
```

**Ongoing (cron):**
```bash
# Cron runs automatically every 4 hours via Hermes scheduler
# Or manual run:
hermes run jobgetter -q "Run the job-getter bot scan cycle"
```

**Dashboard:**
```bash
# Double-click start.bat (Windows) or:
gunicorn -w 2 -b 0.0.0.0:5000 backend.server:app
# Open http://127.0.0.1:5000
```

---

## Troubleshooting

### Bot doesn't start / "skill not found"
```bash
# Ensure skills are in the right location
ls ~/Documents/job-getter-sanitized/skills/
# Should show: career-ops-llm/, career-ops-onboard/, etc.

# If using Hermes profile, ensure external_dirs includes the path:
# ~/.hermes/config.yaml → skills.external_dirs: ["~/Documents/job-getter-sanitized/skills"]
```

### No jobs found / scan returns empty
1. Check `portals.yml` search queries are enabled
2. Verify `config/profile.yml` search.titles match your targets
3. Check `data/scan-history.tsv` isn't blocking new URLs (dedup)
4. Run manual scan to see raw output:
```bash
hermes run jobgetter -q "Run web_search for site:boards.greenhouse.io Customer Success Remote"
```

### LLM calls failing
1. Verify `HERMES_LLM_ENDPOINT` and `HERMES_LLM_API_KEY` are set
2. Test endpoint manually:
```bash
curl -H "Authorization: Bearer $HERMES_LLM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-v4-pro","messages":[{"role":"user","content":"hi"}]}' \
  $HERMES_LLM_ENDPOINT/chat/completions
```
3. Check `career-ops-llm` skill logs for fallback chain

### Telegram alerts not arriving
1. Verify `.env` has correct `TELEGRAM_BOT_TOKEN` and `TELEGRAM_HOME_CHANNEL`
2. Test bot manually:
```bash
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
  -d chat_id=$TELEGRAM_HOME_CHANNEL -d text="Test from job-getter"
```
3. Check Hermes gateway is running: `hermes gateway status`

### Database / dashboard issues
```bash
# Recreate SQLite DB
rm backend/jobs.db
# Restart backend — it auto-creates schema from schema.sql
python backend/server.py
```

### PDF generation failing
1. Ensure `weasyprint` dependencies installed (system level):
   - Windows: `pip install weasyprint` (may need GTK)
   - Linux: `apt-get install libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0`
2. Check `career-ops-pdf` skill logs
3. Fallback: HTML output in `output/` can be printed to PDF manually

---

## Customization Examples

### Different Target Roles (e.g., Product Management)
```yaml
# config/profile.yml
target_roles:
  - "Product Manager"
  - "Senior Product Manager"
  - "Product Lead"
  - "Group Product Manager"
  - "Director of Product"

search:
  titles:
    - "Product Manager"
    - "Senior Product Manager"
    - "Product Lead"
    - "Technical Product Manager"
    - "Platform Product Manager"
  exclude_titles:
    - "Intern"
    - "Junior"
    - "Associate Product Manager"
    - "Product Owner"  # if you want PM not PO

archetypes:
  - name: "Technical PM"
    signals: ["API", "platform", "technical", "engineering", "data"]
    fit: "Your technical PM experience"
  - name: "Growth PM"
    signals: ["growth", "experimentation", "metrics", "activation", "retention"]
    fit: "Your growth experience"
```

### Different Geography (e.g., Bay Area + Remote)
```yaml
# config/profile.yml
location: "San Francisco, CA (Bay Area)"
geo_preferences:
  - "San Francisco Bay Area"
  - "Remote (US)"

search:
  locations:
    - "San Francisco"
    - "Bay Area"
    - "Remote"
    - "California"

# portals.yml location_filter:
location_filter:
  allow:
    - "san francisco"
    - "bay area"
    - "remote"
    - "california"
    - "united states"
  block:
    - "new york"
    - "seattle"
    - "relocation required"
```

### Adding a New Tracked Company
```yaml
# portals.yml
tracked_companies:
  - name: "Stripe"
    careers_url: "https://stripe.com/jobs"
    enabled: true
    api: "https://boards-api.greenhouse.io/v1/boards/stripe/jobs"
    api_provider: "greenhouse"
    notes: "Fintech, API-first, strong CS culture"
```

---

## Advanced Usage

### Manual Job Evaluation (single JD)
```bash
# Save JD to a file, then:
hermes run jobgetter -q "Evaluate this job: [paste JD or path to file]"
# Uses career-ops-evaluate skill for full A-G report
```

### Batch Processing (10+ jobs)
```bash
hermes run jobgetter -q "Batch evaluate all jobs in data/pipeline.md under Pending"
# Uses career-ops-batch for parallel processing
```

### Generate Tailored Resume + Cover Letter
```bash
hermes run jobgetter -q "Create tailored resume and cover letter for job ID [UUID]"
# Uses career-ops-pdf + job-hunt-cheat-code + humanizer
```

### Interview Prep for Specific Company
```bash
hermes run jobgetter -q "Generate interview prep for [Company Name] [Role]"
# Uses career-ops-interview-prep + career-ops-deep
```

### Negotiation Playbook from Offer
```bash
hermes run jobgetter -q "Create negotiation playbook from this offer letter: [paste text]"
# Uses salary-negotiation skill
```

### LinkedIn Network Scan
```bash
hermes run jobgetter -q "Scan my LinkedIn connections for warm intros at [Company]"
# Uses linkedin-network-scan + career-ops-contact
```

---

## File Structure Reference

```
job-getter-sanitized/
├── config/profile.yml           ← EDIT FIRST: your identity, roles, geo, comp
├── portals.yml                  ← EDIT SECOND: search queries, target companies
├── cv.md                        ← EDIT: fallback résumé (markdown)
├── modes/_profile.md            ← AUTO: archetypes, narrative, writing style
├── data/
│   ├── pipeline.md              ← AUTO: Kanban board (markdown)
│   ├── applications.md          ← AUTO: application tracker
│   ├── scan-history.tsv         ← AUTO: dedup history
│   ├── follow-ups.md            ← AUTO: follow-up log
│   └── profile_onboard.md       ← AUTO: onboarding synthesis
├── onboard/
│   ├── processing/resumes/      ← YOU: drop PDF/DOCX/TXT résumés here
│   ├── processing/cover_letters/← YOU: drop cover letters here
│   ├── template_questions.md    ← REFERENCE: 7 onboarding questions
│   ├── wait_for_ready.sh        ← SCRIPT: onboarding helper
│   └── gap_analysis.md          ← AUTO: readiness gaps
├── references/
│   ├── search-prompts.md        ← LLM prompts for extraction/scoring
│   ├── interview-guide-template.md ← 50-section interview guide template
│   ├── generation-instructions.md ← Resume/CL generation rules
│   ├── onboard_parse_prompt.md  ← Resume parsing prompt
│   └── data-tier-guidelines.md  ← Tier 1/2/3 analysis rules
├── scripts/
│   ├── scoring_engine.py        ← 3D scoring (Soul/Pocket/Path)
│   └── merge_onboard.py         ← Onboarding merge + gap analysis
├── skills/
│   ├── career-ops-llm/          ← Model-agnostic LLM wrapper
│   ├── career-ops-onboard/      ← Onboarding workflow
│   └── career-ops-hermes/       ← 23 career-ops skills (submodules)
├── backend/
│   ├── server.py                ← Flask API (10 endpoints)
│   ├── schema.sql               ← SQLite schema
│   └── requirements.txt         ← Python deps
├── frontend/                    ← React + Three.js dashboard
├── writing-samples/             ← YOU: past cover letters for voice calibration
├── output/                      ← AUTO: generated PDFs
├── reports/                     ← AUTO: per-job evaluation reports
├── jds/                         ← AUTO: extracted job descriptions
├── interview-prep/              ← AUTO: company-specific intel
└── start.bat                    ← Windows launcher
```

---

## Contributing

1. Fork the repo
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push: `git push origin feature/amazing-feature`
5. Open Pull Request

**Guidelines:**
- Keep personal info out — use template placeholders
- Update README for new features
- Follow existing code style (Python: black, JS: prettier)
- Test locally before PR

---

## Architecture Deep Dive

### Data Flow
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Discovery  │────▶│ Extraction  │────▶│ Intelligence │────▶│   Scoring   │
│ (web_search)│     │(web_extract)│     │ (LLM + 30-  │     │ (Python 3D) │
└─────────────┘     └─────────────┘     │  field JSON) │     └──────┬──────┘
                                         └─────────────┘            │
                                                   ┌────────────────┘
                                                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Dashboard  │◀────│  Storage    │◀────│  Strategy   │◀────│  Tailoring  │
│  (React)    │     │(SQLite+MD)  │     │   Kit Gen   │     │ (PDF/CL)    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

### Cron Cycle (every 4 hours)
1. **Scan**: `career-ops-scan` → discovers new URLs
2. **Extract**: `web_extract` → pulls full JD text
3. **Evaluate**: `career-ops-evaluate` → 30-field JSON + 3D scores
4. **Filter**: Score ≥ 3.5 → added to pipeline + SQLite
5. **Tier 1** (≥4.0): Full strategy kit + PDF generation
6. **Alert**: Telegram push with top 3 + follow-ups + urgent
7. **Follow-up check**: `career-ops-followup` → flags overdue

### Scoring Weights
- **Soul (35%)**: Mission alignment, location fit, red flags
- **Pocket (40%)**: Compensation, role title match, seniority
- **Path (25%)**: Application ease, network leverage, freshness

---

## FAQ

**Q: Can I use this without Hermes Agent?**
A: The skills are designed for Hermes, but the Python scripts (`scoring_engine.py`, `merge_onboard.py`) and Flask backend can run standalone. The LLM wrapper (`career-ops-llm`) works anywhere with Python.

**Q: How do I add a new job board source?**
A: Add a `search_query` entry in `portals.yml` with the appropriate `site:` filter, or add the company to `tracked_companies` with its careers URL.

**Q: Can I run the dashboard without the bot?**
A: Yes. `cd backend && python server.py` serves the dashboard at `:5000` reading from `jobs.db` and markdown files.

**Q: How does deduplication work?**
A: Every scanned URL is recorded in `data/scan-history.tsv` with timestamp. New scans check against this file before processing.

**Q: What's the difference between Tier 1/2/3?**
A: Tier 1 (top 5): Full 30-field extraction + strategy kit + tailored PDF. Tier 2 (6-10): Extraction only. Tier 3 (11+): Basic metadata only, scored by Python engine.

**Q: How do I reset onboarding?**
A: Delete `data/profile_onboard.md` and `onboard/gap_analysis.md`, then re-run the bot.

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