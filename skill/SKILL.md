---
name: job-getter-bot
description: "Use when you say 'job getter', 'find jobs', 'run bot'."
---

# Job Getter Bot — Autonomous Job Acquisition Engine

Orchestrates the full job search lifecycle: scan → evaluate → tailor → apply → follow up → interview prep → negotiate. Runs autonomously via cron and on-demand.

## Quick Start

Three modes:

| Trigger | Mode | What happens |
|---|---|---|
| "scan jobs" / "find jobs" / "run the bot" | Scan | Discover new jobs, score, add to pipeline |
| "process pipeline" / "work the queue" | Pipeline | Evaluate pending jobs, generate reports + PDFs, auto-apply |
| "job hunt status" / "what's happening" | Status | Show dashboard: pipeline, applications, follow-ups, interviews |
| Cron fires (every 4 hours) | Auto | Scan + process + alert on new opportunities |

## Workspace

All job-getter operations live in `~/Documents/job-getter/`:

```
job-getter/
├── cv.md                    # Your CV (source of truth)
├── portals.yml              # Scanner config: tracked companies, search queries, filters
├── config/
│   └── profile.yml          # Your profile: contact, target roles, geography, comp
├── modes/
│   └── _profile.md          # Archetypes, narrative, writing style, deployment table
├── data/
│   ├── applications.md      # Application tracker (TSV table)
│   ├── pipeline.md          # Pending + processed job URLs
│   ├── scan-history.tsv     # All URLs ever scanned (dedup)
│   └── follow-ups.md        # Follow-up cadence tracker
├── reports/                 # Per-job evaluation reports (A-G blocks)
├── jds/                     # Extracted job descriptions
├── interview-prep/          # Company-specific interview intelligence
├── writing-samples/         # Your cover letters for voice calibration
├── output/                  # Generated PDFs (tailored resumes)
├── batch/                   # Batch processing state
│   ├── tracker-additions/
│   └── logs/
└── scripts/                 # Automation scripts
```

## Your Search Parameters (EDIT THESE)

- **Target roles:** [YOUR_TARGET_ROLES] (e.g., Customer Success Engineer, Account Manager)
- **Geography:** [YOUR_METRO] / [YOUR_STATE] + Remote (US)
- **Compensation:** [STRATEGY] — optimize for [YOUR_PRIORITY]
- **Autonomy:** Fully autonomous — find, tailor, and apply without your review
- **Deployment:** Always-on cron (every 4 hours) + on-demand

## Skills Arsenal (17 career-ops + 6 standalone)

### Career-Ops Pipeline (loaded in order):
1. `career-ops-shared` — System context, scoring, writing style, ethical rules
2. `career-ops-scan` — Portal scanner: 4-level discovery (parser, ATS API, browser, web search)
3. `career-ops-evaluate` — Full A-G evaluation (role summary, CV match, comp, legitimacy)
4. `career-ops-pdf` — ATS-optimized PDF generation with keyword injection
5. `career-ops-apply` — Live application assistant (form detection, response generation)
6. `career-ops-pipeline` — URL inbox processor (extract JD → evaluate → report → PDF → tracker)
7. `career-ops-batch` — Mass batch processing with parallel sub-agents
8. `career-ops-contact` — LinkedIn outreach (recruiter, HM, peer, interviewer targeting)
9. `career-ops-followup` — Follow-up cadence tracker with tailored drafts
10. `career-ops-deep` — Deep company research (6-axis structured prompt)
11. `career-ops-interview-prep` — Company-specific interview intelligence
12. `career-ops-tracker` — Application tracker viewer + statistics dashboard
13. `career-ops-compare` — Multi-offer comparison (10 weighted dimensions)
14. `career-ops-patterns` — Rejection pattern detector + actionable recommendations
15. `career-ops-pdf` (ATS verification) — pdftotext verification after generation
16. `career-ops-project` — Portfolio project evaluation (6 dimensions)
17. `career-ops-training` — Course/certification evaluation (6 dimensions)

### Standalone Job-Hunt Skills:
18. `job-hunt-cheat-code` — Turn a job posting into tailored resume + outreach plan
19. `job-match` — Score fit and generate cover letter from JD + CV
20. `jd-decoder` — Decode any JD into actionable offer strategy
21. `salary-negotiation` — Turn offer letter into negotiation playbook
22. `linkedin-network-scan` — Scan connections for warm-intro opportunities
23. `behavioral-interview` — Build reusable STAR story bank for behavioral interviews
24. `resume-builder` — Generate beautified resumes with 13 print-ready templates

## Workflow

### Phase 1: SCAN (Discover new opportunities)

Discovery uses Hermes native `web_search` tool — no external API needed.

1. **Discovery**: `web_search` with site: filters (Greenhouse, Ashby, Lever, LinkedIn, Indeed) + tracked company career pages
2. **Extraction**: `web_extract` pulls full JD text from discovered URLs
3. **Intelligence**: `deepseek-v4-pro` (ollama-cloud) processes JD + your profile → 30-field structured JSON + 3D scores
4. **Scoring**: Python `scoring_engine.py` (Soul/Pocket/Path) calculates dimensional match score
5. **Strategy Kit**: For Tier 1 jobs, `deepseek-v4-pro` generates complete 50-section acquisition guide from template

**Model assignment:**

| Task | Model | Provider |
|------|-------|----------|
| Job extraction + 30-field JSON | deepseek-v4-pro | ollama-cloud (fallback: opencode-go) |
| Strategy kit generation (50-section) | deepseek-v4-pro | ollama-cloud (fallback: kimi-k3 via opencode-go) |
| Cover letter / resume tailoring | deepseek-v4-pro | ollama-cloud |
| Quick batch scoring | glm-5.2 | ollama-cloud |
| Fallback cascade | glm-5.3 → kimi-k3 → deepseek-v4-flash → minimax-m3 → qwen3.8-max | either |

**Supported Providers:**
- **Ollama Cloud:** deepseek-v4-pro, deepseek-v4-flash, kimi-k2.7-code, glm-5.2, nemotron-3-ultra, qwen3.5, etc.
- **OpenCode Go:** grok-4.5, glm-5.3, kimi-k3, minimax-m3, deepseek-v4-pro, etc.

**Workflow:**
1. Read `portals.yml` for tracked companies + search queries
2. Read `data/scan-history.tsv` for dedup
3. Execute `web_search` queries (Level 3 — site: filters for ATS platforms + job boards)
4. For Greenhouse/Ashby/Lever companies: `web_extract` their API endpoints (Level 2)
5. Filter by title (positive/negative/seniority_boost keywords from portals.yml)
6. Filter by location ([YOUR_METRO] + Remote only)
7. Deduplicate against scan-history, applications, pipeline
8. For each new job: `web_extract` the posting URL → get full JD text
9. For each JD: run extraction prompt via `deepseek-v4-pro` → 30-field JSON + 3D scores
10. Add verified new jobs to `data/pipeline.md` Pending section
11. Record all URLs in `data/scan-history.tsv`

**Parallel execution:** Launch sub-agents for batches of 3-5 companies to maximize speed.

### Phase 2: EVALUATE (Score and prioritize)

For each pending URL in pipeline.md:

1. Load `career-ops-evaluate` for the A-G evaluation workflow
2. Load `career-ops-shared` for scoring system + archetype detection
3. Read `cv.md`, `modes/_profile.md`, `config/profile.yml`
4. Extract JD (browser_navigate → browser_snapshot, fallback web_extract, fallback web_search)
5. Detect archetype (match against your archetypes in modes/_profile.md)
6. Execute 7 blocks:
   - Block A: Role Summary
   - Block B: Match with CV (map each JD requirement to CV lines)
   - Block C: Level and Strategy
   - Block D: Comp and Demand (web_search for salary data)
   - Block E: Customization Plan (top 5 CV + LinkedIn changes)
   - Block F: Interview Plan (6-10 STAR+R stories)
   - Block G: Posting Legitimacy (ghost job detection)
7. Save report to `reports/{###}-{company-slug}-{YYYY-MM-DD}.md`
8. Record in `data/applications.md` tracker
9. If score >= 4.0 → generate tailored PDF (Phase 3)
10. If score < 3.5 → mark as SKIP, don't invest further time

**Parallel execution:** 3+ pending URLs → launch sub-agents in parallel.

### Phase 3: TAILOR (Generate application materials)

For jobs scoring >= 4.0:

1. Load `career-ops-pdf` for ATS-optimized PDF generation
2. Extract 15-20 JD keywords
3. Detect role archetype → adapt framing per `modes/_profile.md`
4. Rewrite Professional Summary with JD keywords + your narrative bridge
5. Select top 3-4 most relevant projects from CV
6. Reorder experience bullets by JD relevance
7. Build competency grid from JD requirements
8. Inject keywords naturally (NEVER invent experience)
9. Generate HTML from template + personalized content
10. Write to `/tmp/cv-[YOUR_NAME]-{company}.html`
11. Render PDF (browser-based or node generate-pdf.mjs)
12. ATS text-layer verification (pdftotext → verify contact info, reading order, keywords)
13. Save to `output/cv-[YOUR_NAME]-{company}-{YYYY-MM-DD}.pdf`
14. Update tracker: PDF ✅

Also load `job-hunt-cheat-code` for:
- Honest fit assessment (Strong/Moderate/Stretch)
- Tailored resume (.docx)
- Keyword table with honest gap analysis
- Outreach plan (targets → sequence → messages)

### Phase 4: APPLY (Submit applications)

For jobs scoring >= 4.0 with PDFs generated:

1. Load `career-ops-apply` for live application assistant
2. Navigate to the application URL (browser_navigate)
3. Detect form questions (text fields, dropdowns, yes/no, salary, uploads)
4. Generate personalized responses from evaluation report
5. Fill form fields (browser_type, browser_click for dropdowns)
6. Upload tailored resume PDF
7. Submit application
8. Update tracker: Status → Applied
9. Record application in `data/applications.md`

**Safety rules:**
- NEVER submit to a job scoring < 4.0
- NEVER fabricate experience or metrics in application responses
- NEVER share phone number in generated LinkedIn messages
- ALWAYS include cover letter if form allows it
- ALWAYS verify form is fully completed before submitting

### Phase 5: OUTREACH (LinkedIn + direct contact)

For each applied job:

1. Load `career-ops-contact` for LinkedIn outreach
2. web_search for: hiring manager, recruiter, 2-3 team peers
3. Classify each contact (recruiter, hiring manager, peer, interviewer)
4. Generate 3-sentence messages per contact type:
   - Recruiter: Fit → Proof → CTA
   - Hiring Manager: Hook (specific challenge) → Proof → CTA
   - Peer: Interest (their work) → Connection → CTA
5. Max 300 characters (LinkedIn limit)
6. Also load `linkedin-network-scan` if connections CSV available
7. Draft outreach sequence (day 0-14 campaign per `job-hunt-cheat-code` playbook)

### Phase 6: FOLLOW UP (Cadence tracking)

1. Load `career-ops-followup` for cadence tracker
2. Run cadence analysis on all applications
3. Flag overdue (>7 days no response) and urgent (company replied)
4. Generate tailored follow-up email/LinkedIn drafts
5. Present drafts for review
6. Record sent follow-ups in `data/follow-ups.md`

### Phase 7: INTERVIEW PREP (When interview secured)

1. Load `career-ops-interview-prep` for company-specific intelligence
2. Load `behavioral-interview` for STAR story bank
3. web_search: Glassdoor interview process, Blind posts, Levels.fyi comp
4. Build audience map (recruiter-screen, hiring-manager, peer-tech, panel-mixed)
5. Generate likely questions per audience with prepared answers
6. Map STAR stories from story-bank to questions
7. Create technical prep checklist
8. Save to `interview-prep/{company-slug}-{role-slug}.md`
9. Also load `career-ops-deep` for 6-axis company research

### Phase 8: NEGOTIATE (When offer received)

1. Load `salary-negotiation` for negotiation playbook
2. Collect offer details (base, RSU, sign-on, bonus, location, deadline)
3. Collect context (competing offers, deadline flex, risk tolerance, priorities)
4. Generate HTML playbook:
   - Offer Diagnosis (each component tagged LOW/MED/HIGH leverage)
   - Leverage Map
   - Strategy (priority-ordered ask table)
   - Scripts (phone + email, word-for-word)
   - Counter Simulation (3 pushbacks × 2 rounds)
   - Final Recommendation (SIGN / WALK / FREEZE stop-lines)
5. Save to `~/Documents/salary-negotiation-{company}-{role}-{YYYYMM}.html`

## Cron Deployment

The bot runs on a cron schedule for always-on monitoring:

```
Schedule: every 4 hours
Mode: Scan + Process + Alert
Prompt: "Run the job-getter bot: scan for new [YOUR_TARGET_ROLES] roles in [YOUR_METRO] + Remote, 
         evaluate any new finds, auto-apply to anything scoring 4.0+, 
         check follow-ups, alert me on anything needing attention."
Skills: [career-ops-shared, career-ops-scan, career-ops-evaluate, 
         career-ops-pdf, career-ops-apply, career-ops-pipeline,
         career-ops-contact, career-ops-followup, career-ops-tracker]
Deliver: origin (alert in chat)
```

## Output Format

### Scan Report
```
Job Getter Bot — Scan Report {YYYY-MM-DD HH:MM}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Companies scanned: {N}
Jobs found: {N} total
Title-filtered: {N} relevant
Location-filtered: {N} [YOUR_METRO]/Remote
Duplicates: {N} (already tracked)
New to pipeline: {N}

  + {company} | {title} | {location} | {source}
  ...

→ {N} new jobs queued for evaluation
```

### Status Dashboard
```
Job Getter Bot — Status Dashboard
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pipeline: {N} pending evaluation
Applications: {N} total ({N} applied, {N} responded, {N} interview, {N} offer)
Follow-ups needed: {N} overdue, {N} urgent
Interviews scheduled: {N}

Top opportunities:
  1. {company} | {role} | Score {X.X}/5 | Status: {status}
  2. ...

Next actions:
  - {action item}
```

## Reference Assets

The bot workspace includes reference templates:

- `references/interview-guide-template.md` — 50-section template for complete Job Opportunity Acquisition Guides with {{VARIABLE}} placeholders
- `references/generation-instructions.md` — Quality standards for AI generation: minimum word counts, quantification rules, tone guidelines
- `references/search-prompts.md` — Extraction prompts for deepseek-v4-pro: 30-field JSON, scoring rubrics, 3D Soul/Pocket/Path engine
- `references/data-tier-guidelines.txt` — Tiered data architecture: Tier 1 (top 5), Tier 2 (6-10), Tier 3 (11+)
- `scripts/scoring_engine.py` — Python 3D scoring engine (Soul/Pocket/Path) with weighted final score

## Advanced

- `career-ops-batch` — Mass batch processing for 10+ jobs in parallel
- `career-ops-patterns` — Rejection pattern analysis after 5+ applications
- `career-ops-compare` — Multi-offer comparison when 2+ offers arrive
- `resume-builder` — 13 print-ready resume templates for different audiences
- `job-hunt-cheat-code` — One-job-at-a-time deep attack with outreach playbook

## Safety Rules (Enforced)

- ❌ NEVER apply to jobs scoring < 4.0
- ❌ NEVER fabricate experience or metrics
- ❌ NEVER skip ATS verification (pdftotext check)
- ❌ NEVER send LinkedIn messages without your review
- ❌ NEVER ignore scan-history dedup
- ✅ ALWAYS check posting legitimacy (Block G - ghost job detection)
- ✅ ALWAYS read cv.md and _profile.md fresh each run
