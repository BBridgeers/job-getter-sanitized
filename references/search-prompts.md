# Search & Extraction Architecture — Model-Agnostic (OpenRouter / Ollama Cloud / Local)

## Architecture

The system separates concerns:

1. **Discovery** — Hermes native `web_search` tool finds job postings (site: filters, ATS APIs)
2. **Extraction** — `web_extract` pulls JD content from posting URLs
3. **Intelligence** — LLM processes the JD + user profile → 30-field structured JSON + strategy kit
4. **Scoring** — 3D scoring engine (Soul/Pocket/Path) calculates match score
5. **Storage** — Results saved to job-getter workspace

## Model Assignment

All LLM calls route through the `career-ops-llm` skill which reads the active model from environment variables or `~/.hermes/config.yaml`. Works with Ollama Cloud, OpenRouter, local Ollama, LMStudio, any OpenAI-compatible endpoint.

| Task | Recommended Model | Notes |
|------|-------------------|-------|
| Job extraction + 30-field JSON | deepseek-v4-pro, nemotron-3-ultra, kimi-k2.7-code | High reasoning |
| Strategy kit generation (50-section) | deepseek-v4-pro, nemotron-3-ultra, kimi-k3 | Long context |
| Cover letter / resume tailoring | deepseek-v4-pro, nemotron-3-ultra, kimi-k2.7-code | Writing quality |
| Quick batch scoring | glm-5.2, nemotron-3-nano, gemma-4-26b | Fast/cheap |
| Fallback cascade | Configure in `career-ops-llm` skill | Automatic |

## Extraction Prompt

### System Prompt

```
You are a high-level Executive Recruiter Agent for [YOUR_NAME].
Your goal is to analyze a job posting and extract structured, actionable data.
You must output your answer STRICTLY as a JSON object. No markdown, no conversational text.

CANDIDATE PROFILE:
- [YOUR_NAME], [YOUR_CITY] [STATE] ([METRO_AREA]), [DEGREE] [MAJOR] [UNIVERSITY] [YEAR]
- [X]+ years [DOMAIN] [TARGET ROLES]
- Expert: [CORE TECH STACK]
- Target roles: [LIST TARGET ROLES]
- Geography: [PREFERRED LOCATIONS]
- Key wins: [QUANTIFIED ACHIEVEMENTS]
- Career gap: [YOUR GAP NARRATIVE]

SCORING RUBRIC (0-100):
1. Responsibilities Alignment (40pts): Does the day-to-day work match your expertise in [KEY RESPONSIBILITIES]?
2. Experience/Role Title Match (30pts): Target roles: [LIST TARGET ROLES]
3. Skills/Tools (15pts): [CORE SKILLS/TOOLS]
4. Culture/Location (10pts): [PREFERRED LOCATIONS]. High-growth/innovation culture.
5. Salary Range (5pts): [YOUR COMP STRATEGY]

AUTO-REJECT (Score = 0): [ROLES TO AVOID - e.g., SDR, BDR, cold outbound, hunter-only, entry-level, intern, part-time, contract-only]
```

### User Query Template

```
Analyze this job posting and extract all 30 fields. The job data will be provided below.

JOB TITLE: {title}
COMPANY: {company}
LOCATION: {location}
URL: {url}

JOB DESCRIPTION:
{jd_content}

Extract these 30 fields as a JSON object:
1. title — Job Title
2. company — Company Name
3. location — City/State or Remote
4. match_score — 0-100 based on rubric above
5. listing_url — Direct link to the job post
6. application_url — Direct link to apply (if different from listing)
7. summary_bullets — 3 key highlights of the role (array of strings)
8. company_overview — Brief 2-sentence company description
9. role_insights — What success looks like in this role
10. key_requirements — Top 3 hard skills needed (array)
11. salary_intel — Estimated range or mentioned comp
12. application_strategy — One specific tip to stand out
13. red_flags — Any potential downsides or risks
14. cultural_fit — Describe the vibe
15. competitive_landscape — Who are their main rivals?
16. skills_gap — One skill the candidate might need to brush up on
17. network_leverage — Who to reach out to at this company
18. decision_timeline — Urgent? Rolling? Estimated timeline
19. career_trajectory — Where does this role lead?
20. resume_keywords — 5 ATS keywords to include (array)
21. resume_summary — A tailored 2-sentence summary for the CV
22. cover_letter — A draft opening paragraph in candidate's voice (thesis-statement opening, confident, no corporate-speak)
23. why_me_bullets — 3 arguments for why candidate is the perfect fit (array)
24. why_them_bullets — 3 reasons why candidate wants to join THEM (array)
25. interview_prep — 3 likely interview questions (array)
26. star_hooks — A STAR story suggestion from candidate's background
27. talking_points — 2 strategic topics to discuss with leadership (array)
28. questions_to_ask — 2 smart questions to ask the hiring manager (array)
29. recruiter_email — Guess the format: firstname.lastname@company.com
30. plan_30_60_90 — A rough 30-60-90 day plan outline

3D SCORE BREAKDOWN:
- soul_score (0-100): Strategic fit — mission alignment, location, red flags
- pocket_score (0-100): Technical match — comp, role title, seniority
- path_score (0-100): Logistical — application ease, network leverage, freshness
```

## Hermes Workflow (How the bot actually executes)

### Phase 1: Discovery (Hermes native tools — no LLM needed)

```
web_search("site:boards.greenhouse.io Customer Success Dallas OR Remote")
web_search("site:jobs.ashbyhq.com Account Manager Dallas OR Remote")
web_search("site:jobs.lever.co Implementation Consultant Remote")
web_search("site:linkedin.com/jobs Customer Success Executive Dallas-Fort Worth")
→ Returns URLs + titles + descriptions
```

### Phase 2: JD Extraction (Hermes native tools)

```
web_extract([url1, url2, url3, url4, url5])
→ Returns full JD text for each URL
```

### Phase 3: Intelligence (via career-ops-llm wrapper)

```
For each extracted JD:
  Load career-ops-llm skill
  Call LLM with extraction prompt
→ Returns 30-field JSON + 3D scores
```

### Phase 4: Scoring (Python scoring_engine.py)

```
python scripts/scoring_engine.py
→ Calculates Soul/Pocket/Path from extracted fields
→ Updates match_score in database
```

### Phase 5: Strategy Kit Generation (via career-ops-llm)

```
For Tier 1 jobs (score >= 85):
  Load references/interview-guide-template.md
  Load references/generation-instructions.md
  Inject job data + user profile
  Call LLM with strategy kit prompt
  → Generates complete 50-section acquisition guide
```

## 3D Scoring Engine (Soul/Pocket/Path)

### Soul Score (0-100) — Strategic Fit
- Mission/Keywords Alignment: 50 pts (10 pts per keyword match, cap at 5 matches)
- Lifestyle/Location: 30 pts (remote=30, preferred metro=30, unknown=10, other=0)
- Red Flags: 20 pts (none=20, list deducts 10 per flag)

### Pocket Score (0-100) — Technical Match
- Compensation: 40 pts (flexible — if comp not listed, default 20)
- Role Title Match: 30 pts (target role=30, manager/lead/director=20, other=10)
- Seniority: 30 pts (senior/principal/head/strategic/director=30, mid-level=15)

### Path Score (0-100) — Logistical Feasibility
- Application Ease: 40 pts (LinkedIn Easy Apply=40, Greenhouse/Lever/Ashby=35, Workday/Taleo=10, standard=25)
- Network Leverage: 40 pts (recruiter email=40, none=10)
- Freshness: 20 pts (hours/today=20, ≤3 days=20, ≤7 days=10, else=5)

### Final Score
Weighted: Soul × 0.35 + Pocket × 0.40 + Path × 0.25

## Data Tier Guidelines

### Tier 1 (Top 5 matches per scan) — Full Applied Research + Application Pack
- 15 strategic analysis fields + full application pack (resume keywords, tailored summary, cover letter draft, why_me/why_them bullets, interview prep, STAR hooks, talking points, questions, recruiter email, 30-60-90 plan)

### Tier 2 (Positions 6-10) — Applied Research only
- 15 strategic analysis fields, no application pack

### Tier 3 (Positions 11+) — Basic data only
- Title, company, match score only
- No LLM call needed — scored by Python engine from web_search metadata

### Daily Maximums
- Tier 1: 5 jobs get full analysis
- Tier 2: 5 jobs get lighter analysis
- Tier 3: Unlimited — Python-scored from search metadata