#!/usr/bin/env python3
"""
Merge all parsed onboarding JSON files into a master profile (data/profile_onboard.md)
and generate a gap analysis (onboard/gap_analysis.md).

This script is called by the career-ops-onboard skill after the user has placed
resume/cover-letter files and they have been parsed into JSON.
"""

import json
import os
import glob
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Paths
ONBOARD_DIR = Path.home() / "Documents" / "job-getter" / "onboard"
PARSED_DIR = ONBOARD_DIR / "processing" / "parsed"
PROFILE_OUT = Path.home() / "Documents" / "job-getter" / "data" / "profile_onboard.md"
GAP_OUT = ONBOARD_DIR / "gap_analysis.md"


def load_all_parsed():
    """Load all JSON files from the parsed directory."""
    parsed_files = glob.glob(str(PARSED_DIR / "*.json"))
    all_data = []
    for f in parsed_files:
        try:
            with open(f, "r") as fp:
                data = json.load(fp)
                all_data.append(data)
        except Exception as e:
            print(f"Warning: Could not parse {f}: {e}")
    return all_data


def merge_experiences(all_data):
    """Deduplicate experiences by company+title+date."""
    seen = {}
    for data in all_data:
        for exp in data.get("experiences", []):
            key = (exp.get("company", "").lower().strip(),
                   exp.get("title", "").lower().strip(),
                   exp.get("start_date", "").strip(),
                   exp.get("end_date", "").strip())
            if key not in seen:
                seen[key] = exp
            else:
                # Merge bullets, preferring ones with metrics
                existing_bullets = seen[key].get("bullets", [])
                new_bullets = exp.get("bullets", [])
                # Simple merge: add new bullets that aren't already there
                for nb in new_bullets:
                    if nb not in existing_bullets:
                        existing_bullets.append(nb)
                seen[key]["bullets"] = existing_bullets
    # Sort chronologically (most recent first)
    experiences = list(seen.values())
    experiences.sort(key=lambda x: x.get("end_date", "") or x.get("start_date", ""), reverse=True)
    return experiences


def merge_skills(all_data):
    """Aggregate skills, taking highest proficiency."""
    skills_map = defaultdict(lambda: {"category": "", "name": "", "proficiency": ""})
    for data in all_data:
        for skill in data.get("skills", []):
            name = skill.get("name", "").lower().strip()
            if name:
                # Keep highest proficiency (simple string comparison for now)
                if not skills_map[name]["proficiency"] or skill.get("proficiency", "") > skills_map[name]["proficiency"]:
                    skills_map[name] = skill
    return list(skills_map.values())


def merge_voice(all_data):
    """Average voice metrics across all parsed documents."""
    voices = [data.get("voice", {}) for data in all_data if data.get("voice")]
    if not voices:
        return {}
    
    # Average numeric fields
    avg_len = sum(v.get("avg_sentence_length", 0) for v in voices) / len(voices)
    
    # Collect all verbs, quantifiers, etc.
    all_verbs = []
    all_quantifiers = []
    tones = []
    formalities = []
    
    for v in voices:
        all_verbs.extend(v.get("preferred_verbs", []))
        all_quantifiers.extend(v.get("quantifier_style", []))
        if v.get("tone"):
            tones.append(v["tone"])
        if v.get("formality"):
            formalities.append(v["formality"])
    
    # Most common tone/formality
    from collections import Counter
    top_tone = Counter(tones).most_common(1)[0][0] if tones else "professional"
    top_formality = Counter(formalities).most_common(1)[0][0] if formalities else "moderate"
    
    return {
        "tone": top_tone,
        "avg_sentence_length": round(avg_len, 1),
        "preferred_verbs": list(set(all_verbs))[:10],  # top 10 unique
        "quantifier_style": list(set(all_quantifiers))[:5],
        "formality": top_formality
    }


def generate_profile_markdown(experiences, skills, voice, user_answers=None):
    """Generate the profile_onboard.md content."""
    lines = []
    lines.append("# User Profile (On-Boarded)\n")
    lines.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")
    
    # Career Narrative
    lines.append("## Career Narrative")
    if voice.get("summary"):
        lines.append(voice["summary"])
    else:
        lines.append("(auto-generated summary from parsed documents)")
    lines.append("")
    
    # Experience
    lines.append("## Experience (chronological)")
    for exp in experiences:
        company = exp.get("company", "Unknown Company")
        title = exp.get("title", "Unknown Title")
        start = exp.get("start_date", "")
        end = exp.get("end_date", "Present")
        lines.append(f"- **{company}** - {title} ({start} - {end})")
        for bullet in exp.get("bullets", []):
            text = bullet.get("text", "") if isinstance(bullet, dict) else bullet
            lines.append(f"    - {text}")
        lines.append("")
    
    # Skills
    lines.append("## Skills Inventory")
    by_category = defaultdict(list)
    for skill in skills:
        cat = skill.get("category", "Other")
        name = skill.get("name", "")
        prof = skill.get("proficiency", "")
        if prof:
            by_category[cat].append(f"{name} ({prof})")
        else:
            by_category[cat].append(name)
    
    for cat, items in sorted(by_category.items()):
        lines.append(f"- **{cat}**: {', '.join(sorted(items))}")
    lines.append("")
    
    # Writing Voice
    lines.append("## Writing Voice")
    lines.append(f"- **Tone**: {voice.get('tone', 'professional')}")
    lines.append(f"- **Avg sentence length**: {voice.get('avg_sentence_length', 'N/A')} words")
    lines.append(f"- **Preferred verbs**: {', '.join(voice.get('preferred_verbs', [])) or 'N/A'}")
    lines.append(f"- **Quantifier style**: {', '.join(voice.get('quantifier_style', [])) or 'N/A'}")
    lines.append(f"- **Formality**: {voice.get('formality', 'moderate')}")
    lines.append("")
    
    # User Answers
    if user_answers:
        lines.append("## User-Provided Answers")
        for i, (q, a) in enumerate(user_answers, 1):
            lines.append(f"**Q{i}:** {q}")
            lines.append(f"**A{i}:** {a}")
            lines.append("")
    
    return "\n".join(lines)


def generate_gap_analysis(experiences, skills, voice, user_answers=None):
    """Generate a gap analysis against CSE/AM/IC/CP/SAE archetypes."""
    lines = []
    lines.append("# Gap Analysis - CSE/AM/IC/CP/SAE readiness\n")
    lines.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")
    
    # Soul: Mission alignment
    soul_score = 3.0  # baseline
    soul_notes = "Baseline score - adjust based on mission keywords in answers."
    
    # Check for mission-driven language in answers
    if user_answers:
        mission_keywords = ["mission", "impact", "purpose", "nonprofit", "social", "meaningful", "values", "cause"]
        answer_text = " ".join(a for _, a in user_answers).lower()
        hits = sum(1 for kw in mission_keywords if kw in answer_text)
        if hits >= 3:
            soul_score = 4.0
            soul_notes = "Strong mission-oriented language detected in answers."
        elif hits >= 1:
            soul_score = 3.5
            soul_notes = "Some mission alignment present; could be more explicit."
    
    # Pocket: Compensation
    pocket_score = 3.0
    pocket_notes = "No explicit salary floor provided; assuming flexible."
    if user_answers:
        answer_text = " ".join(a for _, a in user_answers).lower()
        import re
        salary_match = re.search(r'\$?(\d{2,3})[kK]?', answer_text)
        if salary_match:
            val = int(salary_match.group(1))
            if val >= 90:
                pocket_score = 4.0
                pocket_notes = f"Salary floor of ${val}K+ indicated - solid for DFW market."
            elif val >= 70:
                pocket_score = 3.5
                pocket_notes = f"Salary floor of ${val}K indicated - reasonable for DFW."
    
    # Path: Career trajectory
    path_score = 3.0
    path_notes = "Experience shows solid execution; consider highlighting strategic ownership."
    
    # Count promotions/scope expansions
    promo_count = 0
    leadership_bullets = 0
    for exp in experiences:
        for bullet in exp.get("bullets", []):
            text = bullet.get("text", "") if isinstance(bullet, dict) else bullet
            text_lower = text.lower()
            if any(kw in text_lower for kw in ["promot", "lead", "manag", "direct", "supervis", "mentor", "coach", "head of", "vp", "director"]):
                leadership_bullets += 1
    if leadership_bullets >= 5:
        path_score = 4.0
        path_notes = f"Strong leadership evidence ({leadership_bullets} leadership-oriented bullets)."
    elif leadership_bullets >= 2:
        path_score = 3.5
        path_notes = f"Some leadership evidence ({leadership_bullets} bullets); could emphasize more."
    
    lines.append(f"**Soul: {soul_score}/5**   - {soul_notes}")
    lines.append(f"**Pocket: {pocket_score}/5** - {pocket_notes}")
    lines.append(f"**Path: {path_score}/5**   - {path_notes}")
    lines.append("")
    
    lines.append("## Suggested focus for upcoming applications")
    suggestions = []
    
    if soul_score < 4.0:
        suggestions.append('- Add a "Strategic Impact" bullet to each role showing how you influenced renewal/expansion.')
        suggestions.append('- In cover letters, lead with a mission-aligned hook (see archetype notes in _profile.md).')
    
    if pocket_score < 4.0:
        suggestions.append('- Research market rates for target roles in DFW/Remote; be ready to state a confident range.')
    
    if path_score < 4.0:
        suggestions.append('- Highlight cross-functional leadership and strategic ownership in resume bullets.')
        suggestions.append('- Prepare STAR stories that demonstrate scope expansion and influence without authority.')
    
    if not suggestions:
        suggestions.append('- Profile is well-aligned; focus on tailoring each application to the specific JD.')
    
    lines.extend(suggestions)
    lines.append("")
    
    return "\n".join(lines)


def main():
    print("Loading parsed onboarding data...")
    all_data = load_all_parsed()
    
    if not all_data:
        print("No parsed data found. Run the document parsing step first.")
        return
    
    print(f"   Found {len(all_data)} parsed document(s)")
    
    print("Merging experiences...")
    experiences = merge_experiences(all_data)
    print(f"   {len(experiences)} unique experiences after deduplication")
    
    print("Merging skills...")
    skills = merge_skills(all_data)
    print(f"   {len(skills)} unique skills aggregated")
    
    print("Merging voice profile...")
    voice = merge_voice(all_data)
    
    # Load user answers if they exist
    answers_file = ONBOARD_DIR / "user_answers.json"
    user_answers = []
    if answers_file.exists():
        with open(answers_file, "r") as f:
            user_answers = json.load(f)
    
    print("Generating profile_onboard.md...")
    profile_md = generate_profile_markdown(experiences, skills, voice, user_answers)
    PROFILE_OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(PROFILE_OUT, "w") as f:
        f.write(profile_md)
    print(f"   Written to {PROFILE_OUT}")
    
    print("Generating gap_analysis.md...")
    gap_md = generate_gap_analysis(experiences, skills, voice, user_answers)
    GAP_OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(GAP_OUT, "w") as f:
        f.write(gap_md)
    print(f"   Written to {GAP_OUT}")
    
    print("\nOnboarding merge complete!")
    print(f"   Profile: {PROFILE_OUT}")
    print(f"   Gap Analysis: {GAP_OUT}")


if __name__ == "__main__":
    main()