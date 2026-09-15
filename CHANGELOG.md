# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-09-15

### Added
- **Full-stack job acquisition engine** with 24 integrated skills
- **Model-agnostic LLM wrapper** supporting Ollama Cloud, OpenRouter, local Ollama
- **Onboarding workflow** with resume/cover letter parsing and gap analysis
- **8-phase automation pipeline**: Scan → Evaluate → Tailor → Apply → Outreach → Follow-up → Interview Prep → Negotiate
- **3D job scoring engine** (Soul/Pocket/Path dimensions)
- **ATS-optimized resume generation** with keyword injection
- **LinkedIn outreach automation** with recruiter/hiring manager targeting
- **Interview prep intelligence** with company research and STAR story mapping
- **Salary negotiation playbook** generation from offer letters
- **Flask backend API** with SQLite application tracking
- **React dashboard** with Hermes Agent integration
- **Hermes Agent skill** for autonomous 4-hour cron scheduling
- Complete configuration templates (profile.yml, portals.yml, cv.md)
- Comprehensive documentation with 750+ line README

### Features
- ✅ Scan phase: Multi-level job discovery (ATS APIs, web search, career pages)
- ✅ Evaluate phase: A-G evaluation blocks with legitimacy checks
- ✅ Tailor phase: ATS-verified resume generation
- ✅ Apply phase: Form automation with safety thresholds
- ✅ Outreach phase: LinkedIn message generation
- ✅ Follow-up phase: Cadence tracking with drafts
- ✅ Interview prep: Company research + STAR mapping
- ✅ Negotiation: Playbook generation with leverage analysis
- ✅ Parallel execution: Sub-agent batching for 10+ jobs
- ✅ Deduplication: Scan history tracking
- ✅ Safety rules: Scoring gates, experience verification, dedup checks

### Documentation
- README with 750+ lines (quickstart, architecture, workflow, configuration, troubleshooting)
- Detailed walkthrough guides for each phase
- Configuration examples for different job search paths
- Troubleshooting section with 7+ common issues
- Architecture deep-dive with data flow diagrams
- Reference assets (interview guide template, generation instructions, scoring rubrics)

## [Unreleased]

### Planned
- Multi-language support for job postings
- Advanced rejection pattern analysis
- Competing offer comparison dashboard
- Resume version control (A/B testing)
- Email campaign automation
- Phone screening prep (mock interview)
- Network effect scoring (alumni connections)

---

## Guidelines

- **[MAJOR]** — Breaking changes (new required config, API changes)
- **[MINOR]** — New features, backward compatible
- **[PATCH]** — Bug fixes, documentation, small improvements
