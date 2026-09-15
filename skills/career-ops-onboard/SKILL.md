---
name: career-ops-onboard
description: Use when the job-getter bot starts and needs to gather the user's resume, cover letters, writing voice, and career goals before any job scanning or evaluation.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Career Ops Onboard — Personalized Profile Builder

This skill runs **once per user session** (or whenever the user says "reset my profile") and produces a synthesized `data/profile_onboard.md` that the rest of the pipeline (especially `career-ops-shared` writing-style extraction and `career-ops-evaluate`) consumes.

## Quick Start

When the bot starts (e.g., via the `job-getter-bot` skill's "scan jobs" trigger), it first executes:

```
Agent(
    subagent_type="general-purpose",
    prompt="Load skill career-ops-onboard and run its onboarding workflow",
    run_in_background=True
)
```

## Workflow

### Step 1 – Prompt for file placement
The bot prints a friendly message asking the user to drop files into specific folders:

```
Hi! I'm your Job Getter Bot. Before I start hunting for roles, I'd like to get to know you better.

Please place your files in the following folders (you can drag-and-drop or use File Explorer):
  Resumes (PDF, DOCX, TXT)   → ~/Documents/job-getter/onboard/processing/resumes/
  Cover letters (PDF, DOCX, TXT) → ~/Documents/job-getter/onboard/processing/cover_letters/

When you're done, type "ready" and press Enter.
```

The bot then waits (via a simple `read` loop in a helper script) until the user signals readiness.

### Step 2 – Ingest and parse documents
For each file placed in the folders:

1. **Read raw text** using `read_file` (PDF/DOCX are converted to text via `pdftotext`/`antiword` – we assume those utilities are available in the Hermes environment; if not, fall back to asking the user to provide a TXT version).  
2. **Run a parsing prompt** through `deepseek-v4-pro` (Ollama Cloud) that extracts:
   - **Chronology** (company, title, dates)  
   - **Key achievements** (metrics, impact numbers)  
   - **Skills & tools** (technical, soft, certifications)  
   - **Writing voice cues** (tone, sentence length, favorite verbs, use of quantifiers)  

   *Example extraction prompt (kept in `references/onboard_parse_prompt.md`):*

   ```
   You are an expert resume parser. Given the following resume/cover-letter text, output a JSON object with:
   - experiences: [{company, title, start_date, end_date, bullets: [{text, metrics?}]}]
   - skills: [{category, name, proficiency?}]
   - voice: {tone, avg_sentence_length, preferred_verbs, quantifier_style, formality}
   - summary: (2-3 sentence professional summary in the user's voice)
   Return ONLY valid JSON.
   ```

3. **Store the parsed JSON** temporarily in `onboard/processing/parsed/<filename>.json`.

### Step 3 – Merge all parsed docs into a master profile
A small Python helper (`scripts/merge_onboard.py`) reads all JSON files and:

- **Deduplicates experiences** (by company+title+date).  
- **Aggregates skills** (taking the highest proficiency indicated).  
- **Composes a voice profile** by averaging metrics (sentence length, etc.) and noting recurring stylistic choices.  
- **Generates a markdown profile** `data/profile_onboard.md` with sections:

   ```
   # User Profile (On-Boarded)

   ## Career Narrative
   (auto-generated summary)

   ## Experience (chronological)
   - **Company** – Title (MM/YYYY – MM/YYYY)
       - Bullet 1 (with metrics)
       - …

   ## Skills Inventory
   - Technical: …  
   - Soft: …
   - Certifications: …

   ## Writing Voice
   - Tone: …  
   - Avg sentence length: … words  
   - Preferred verbs: …  
   - Quantifier style: …  
   - Formality: …

   ## User-Provided Answers (see Step 4)
   ```

### Step 4 – Targeted questionnaire
After the document phase, the bot asks a short set of **open-ended** questions (defined in `onboard/template_questions.md`). Example:

```
Please answer the following in your own words (feel free to be as brief or detailed as you like):

1. What are your top 3 career goals for the next 12-24 months?  
2. Which industries or company missions excite you most (e.g., climate tech, enterprise SaaS, healthcare AI)?  
3. Do you have any geographic restrictions or strong preferences beyond DFW/Remote?  
4. Are there any roles/titles you *definitely* want to avoid?  
5. What is your preferred work-arrangement (fully remote, hybrid, on-site) and why?  
6. Any personal constraints (e.g., visa sponsorship needs, desired start date, salary floor) that I should know upfront?  
7. Is there anything about your background that isn't captured in your resume/cover letters (e.g., freelance projects, volunteer leadership, side-gigs)?
```

The bot captures each answer and appends them under a `## User-Provided Answers` section in `data/profile_onboard.md`.

### Step 5 – Gap analysis against target archetypes
Using the synthesized profile, the bot runs a **gap analysis** that feeds directly into the 3D scoring model:

| Dimension | What we check | How we derive a gap score |
|-----------|---------------|--------------------------|
| **Soul (mission alignment)** | Does the user's stated mission/goals match the archetype's narrative (from `_profile.md`)? | Compare keywords from user's answers to archetype description; assign 0-5. |
| **Pocket (compensation)** | Any explicit salary floor or flexibility mentioned? | If user gave a number → map to market quartiles; else assume flexible → 3. |
| **Path (career trajectory)** | Evidence of upward momentum, leadership, skill-growth in experience? | Count promotions, scope expansion, mentorship bullets; map to 0-5. |

The gap analysis produces a **readiness report** (saved to `onboard/gap_analysis.md`) that looks like:

```
## Gap Analysis — CSE/AM/IC/CP/SAE readiness

Soul: 3.5/5   → You mention impact-driven work but could tie it more explicitly to customer-success narratives.
Pocket: 4.0/5 → You indicated a $90K base floor – solid for DFW.
Path:  3.0/5   → Your experience shows strong execution; consider highlighting more strategic-ownership or cross-functional leadership.

Suggested focus for upcoming applications:
- Add a "Strategic Impact" bullet to each role showing how you influenced renewal/expansion.
- In cover letters, lead with a mission-aligned hook (see archetype notes in _profile.md).
```

This report is **displayed to the user** after onboarding and before the first scan, so they know exactly where to bolster their profile (or where the bot will emphasize strengths).

### Step 6 – Make the profile available to the rest of the pipeline
- `career-ops-shared` already reads `cv.md`, `article-digest.md`, and `_profile.md` for writing style.  
- We augment it to **also read `data/profile_onboard.md`** (if present) and treat it as the authoritative source for:
  - **Voice** → overrides any writing-sample extraction.  
  - **Experience & skills** → supplements or replaces the static `cv.md` (you can keep `cv.md` as a fallback; the onboard profile wins if both exist).  
- The `career-ops-evaluate` skill's **Block B (Match with CV)** will now compare JD requirements against the *on-boarded* experience list, yielding a far more accurate match score.  

---

### Integration into existing bot flow

Edit the `job-getter-bot` skill (or create a small wrapper skill) so that its **scan jobs** mode begins with:

```
1️⃣ Run career-ops-onboard (onboarding workflow)
2️⃣ If data/profile_onboard.md exists → proceed to scanning
3️⃣ Else → abort with a friendly reminder to complete onboarding first.
```

Pseudocode (to be added to `job-getter-bot`'s `SCAN` mode handler):

```python
def handle_scan_jobs():
    # Step 0 – On-boarding
    onboard_path = os.path.expanduser("~/Documents/job-getter/onboard")
    profile_path = os.path.join(onboard_path, "..", "data", "profile_onboard.md")
    if not os.path.exists(profile_path):
        print("First-time setup: let's get to know you.")
        run_skill("career-ops-onboard")   # this blocks until user finishes
        if not os.path.exists(profile_path):
            print("On-boarding incomplete. Please run the onboarding steps and try again.")
            return
    # Step 1 – Continue with normal scan/pipeline logic
    run_skill("career-ops-scan")
    run_skill("career-ops-evaluate")
    # …etc.
```

---

### Files this skill provides

| File | Purpose |
|------|---------|
| `references/onboard_parse_prompt.md` | LLM prompt to extract structured data from resume/cover-letter text |
| `onboard/template_questions.md` | Questionnaire for the user (7 targeted questions) |
| `onboard/wait_for_ready.sh` | Helper script that prompts user to place files and type "ready" |
| `scripts/merge_onboard.py` | Python script to merge all parsed JSONs into `data/profile_onboard.md` and generate gap analysis |

These files should be created alongside the skill (see setup instructions below).