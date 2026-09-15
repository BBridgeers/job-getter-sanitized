#!/usr/bin/env python3
"""
3D Scoring Engine — Soul/Pocket/Path
For Job Getter Bot
Calculates dimensional match scores from extracted job data.
No external API dependencies — pure Python scoring.

USER: Replace the PROFILE dict below with your own profile data.
"""

import json
import os
import re

# USER PROFILE — REPLACE WITH YOUR OWN DATA
# Load from config/profile.yml or fill in directly here
PROFILE = {
    'core_competencies': [
        'customer success', 'account management', 'strategic relationships',
        'client retention', 'expansion', 'saas', 'enterprise',
        'qbr', 'sbr', 'adoption', 'health scoring', 'churn prevention',
        'salesforce', 'gainsight', 'salesloft', 'meddic', 'challenger',
        'implementation', 'onboarding', 'digital transformation',
        'c-suite engagement', 'stakeholder management', 'renewal',
        'upsell', 'cross-sell', 'voice of customer', 'advocacy'
    ],
    'target_roles': [
        'customer success executive', 'customer success manager',
        'account manager', 'implementation consultant',
        'client partner', 'strategic account executive',
        'client success manager', 'customer experience manager',
        'enterprise account manager', 'strategic relationship manager',
        'onboarding manager', 'engagement manager',
        'solutions consultant', 'enablement manager',
        'renewal manager', 'expansion manager'
    ],
    'location': 'your_metro_area',
    'min_salary': 90000,
    'skills': [
        'salesforce', 'gainsight', 'salesloft', 'meddic', 'challenger',
        'customer success', 'saas', 'qbr', 'account management',
        'churn prevention', 'health scoring', 'onboarding',
        'stakeholder management', 'c-suite', 'retention', 'expansion'
    ]
}

def load_profile_from_config():
    """Attempt to load profile from config/profile.yml if it exists."""
    try:
        import yaml
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'profile.yml')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                # Merge config values into PROFILE
                if config.get('target_roles'):
                    PROFILE['target_roles'] = [r.lower() for r in config['target_roles']]
                if config.get('search', {}).get('titles'):
                    PROFILE['target_roles'].extend([t.lower() for t in config['search']['titles']])
                if config.get('geo_preferences'):
                    PROFILE['location'] = config['geo_preferences'][0].lower().split(',')[0]
                if config.get('compensation', {}).get('strategy') == 'flexible':
                    PROFILE['min_salary'] = 90000  # default for flexible
    except Exception:
        pass  # Use defaults

# Try loading on import
load_profile_from_config()


def calculate_strategic_fit(job_data):
    """
    Soul Score (0-100): Alignment with values, mission, and lifestyle.
    """
    score = 0
    max_score = 0

    # 1. Mission/Keywords Alignment (50 pts)
    keywords = PROFILE.get('core_competencies', []) + PROFILE.get('target_roles', [])
    keywords = [k.lower() for k in keywords]

    job_text = (
        (job_data.get('title') or '') + " " +
        (job_data.get('company') or '') + " " +
        (job_data.get('description') or '') + " " +
        (job_data.get('summary_bullets') or '') + " " +
        (job_data.get('role_insights') or '')
    ).lower()

    matches = sum(1 for k in keywords if k in job_text)
    score += min(matches * 10, 50)
    max_score += 50

    # 2. Lifestyle/Location (30 pts)
    location = (job_data.get('location') or '').lower()
    target_location = PROFILE.get('location', '').lower()

    if 'remote' in location:
        score += 30
    elif target_location and target_location in location:
        score += 30
    elif not location:
        score += 10  # Neutral if unknown
    else:
        score += 0  # On-site elsewhere

    max_score += 30

    # 3. Red Flags (20 pts)
    red_flags = job_data.get('red_flags')
    if not red_flags or red_flags == 'None' or red_flags == [] or red_flags == '':
        score += 20
    else:
        if isinstance(red_flags, list):
            score += max(0, 20 - (len(red_flags) * 10))
        else:
            score += 10

    max_score += 20

    return min(score, 100)


def calculate_technical_match(job_data):
    """
    Pocket Score (0-100): Compensation, Skills, and Role Level.
    """
    score = 0

    # 1. Compensation (40 pts) — User is flexible, so unknown comp gets neutral score
    salary_str = str(job_data.get('salary_intel') or job_data.get('salary_text') or '0')
    salary_nums = re.findall(r'\d+', salary_str.replace(',', ''))

    salary_val = 0
    if salary_nums:
        candidates = [int(x) for x in salary_nums if int(x) > 30000]
        if candidates:
            salary_val = max(candidates)

    if salary_val >= 90000:
        score += 40
    elif salary_val >= 70000:
        score += 30
    elif salary_val > 0:
        score += 10
    else:
        score += 20  # Unknown salary gets neutral (user is flexible on comp)

    # 2. Role Title Match (30 pts)
    title = (job_data.get('title') or '').lower()
    target_roles = [r.lower() for r in PROFILE.get('target_roles', [])]

    if any(r in title for r in target_roles):
        score += 30
    elif 'manager' in title or 'lead' in title or 'director' in title:
        score += 20
    else:
        score += 10

    # 3. Experience/Seniority (30 pts)
    if any(x in title for x in ['senior', 'sr.', 'principal', 'head', 'lead', 'strategic', 'director', 'executive', 'vp']):
        score += 30
    else:
        score += 15  # Mid-level assumption

    return min(score, 100)


def calculate_logistical_feasibility(job_data):
    """
    Path Score (0-100): Ease of application, network leverage, timeline.
    """
    score = 0

    # 1. Application Ease (40 pts)
    app_url = (job_data.get('application_url') or job_data.get('listing_url') or job_data.get('url') or '').lower()

    if 'linkedin' in app_url and 'easy' in app_url:
        score += 40
    elif 'greenhouse' in app_url or 'lever' in app_url or 'ashby' in app_url:
        score += 35  # Good ATS
    elif 'workday' in app_url or 'taleo' in app_url:
        score += 10  # Painful ATS
    else:
        score += 25  # Standard

    # 2. Network Leverage (40 pts)
    if job_data.get('recruiter_email') or job_data.get('network_leverage'):
        score += 40
    else:
        score += 10

    # 3. Freshness (20 pts)
    date_posted = job_data.get('posted_date') or job_data.get('date_posted') or ''
    if 'hour' in date_posted.lower() or 'minute' in date_posted.lower() or 'today' in date_posted.lower():
        score += 20
    elif 'day' in date_posted.lower():
        try:
            days = int(re.search(r'(\d+)', date_posted).group(1))
            if days <= 3:
                score += 20
            elif days <= 7:
                score += 10
            else:
                score += 5
        except:
            score += 10
    else:
        score += 10  # Unknown

    return min(score, 100)


def calculate_final_score(job_data):
    """
    Returns dict with final score and breakdown.
    Weights: Soul 35%, Pocket 40%, Path 25%
    """
    soul = calculate_strategic_fit(job_data)
    pocket = calculate_technical_match(job_data)
    path = calculate_logistical_feasibility(job_data)

    final = (soul * 0.35) + (pocket * 0.40) + (path * 0.25)

    return {
        'final_score': int(round(final)),
        'soul_score': soul,
        'pocket_score': pocket,
        'path_score': path,
        'breakdown': {
            'soul': soul,
            'pocket': pocket,
            'path': path
        }
    }


def score_from_json(json_data):
    """Score a job from its JSON representation (30-field extraction output)."""
    if isinstance(json_data, str):
        json_data = json.loads(json_data)
    return calculate_final_score(json_data)


if __name__ == '__main__':
    # Test with sample data
    test_job = {
        'title': 'Customer Success Executive',
        'company': 'Example Company',
        'location': 'Remote',
        'description': 'Customer success, retention, expansion, QBRs, C-suite engagement, SaaS platform adoption, health scoring, churn prevention',
        'salary_intel': '$106K-$120K',
        'application_url': 'https://boards.greenhouse.io/example',
        'red_flags': '',
        'posted_date': '2 days ago'
    }

    result = calculate_final_score(test_job)
    print(f"""
🎯 SCORING TEST RESULTS
======================
Final Score: {result['final_score']}/100

Soul (Strategic Fit): {result['soul_score']}/100
Pocket (Technical Match): {result['pocket_score']}/100
Path (Logistical): {result['path_score']}/100
""")