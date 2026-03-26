---
description: "Run first-time SBIR plugin setup -- prerequisites, profile, corpus, API key, and validation"
argument-hint: "- No arguments required"
---

# /setup

Guide a user through complete SBIR proposal plugin setup in one interactive session.

## Usage

```
/sbir:setup
```

## Flow

1. **Prerequisites** -- Check Python 3.12+, Git, Claude Code. Block if any fail.
2. **Company Profile** -- Detect existing or create new via profile builder agent
3. **Partner Profiles** -- Offer research institution partner setup for STTR proposals (optional)
4. **Corpus Setup** -- Accept document directories or skip
5. **API Key** -- Check GEMINI_API_KEY, offer skip or configure instructions
6. **Validation** -- Re-verify all items, display unified checklist
7. **Next Steps** -- Show concrete commands to start using the plugin

## Prerequisites

- Claude Code authenticated (implicit -- user is running this command)
- No other prerequisites -- this command checks for everything else

## Context Files

- `~/.sbir/company-profile.json` -- checked for existing profile
- `.sbir/corpus/` -- checked for existing corpus documents
- `skills/setup-wizard/setup-domain.md` -- domain knowledge for checks and display patterns

## Agent Invocation

@sbir-setup-wizard

Run the full first-time setup flow. Check prerequisites, guide profile creation (delegate to sbir-profile-builder), offer partner profile setup (delegate to sbir-partner-builder), offer corpus ingestion, check API key, validate everything, and display next steps.

SKILL_LOADING: Load skills from `skills/setup-wizard/` before beginning work.
