# Evolution: First-Time Setup

**Date**: 2026-03-16
**Feature**: first-time-setup
**Waves Completed**: DISCUSS > DESIGN > DELIVER

## Summary

Implemented the First-Time Setup wizard: a single-session interactive flow that guides new users from zero configuration to a fully validated SBIR plugin environment. Orchestrates prerequisite checks (Python 3.12+, Git, Claude Code), company profile creation (delegated to sbir-profile-builder), corpus document ingestion, Gemini API key detection, and a unified validation summary with concrete next-step commands. Markdown-only implementation reusing existing agents and adapters.

## Key Decisions

- **Delegation over duplication**: Profile creation delegated to sbir-profile-builder via Task tool rather than reimplementing interview/extraction logic. Corpus ingestion reuses existing pipeline.
- **Sequential gates with warnings-not-blockers**: Prerequisites halt setup, but inactive SAM.gov and missing API key produce warnings only. Setup completes with "READY (with warnings)" status.
- **Idempotent re-runs**: Every phase detects existing configuration. Returning users complete setup in under 30 seconds.
- **No new Python services**: Wizard uses existing JsonProfileAdapter for profile detection via a Python one-liner. No new PES rules needed.
- **Progressive confidence UX**: Visible `[ok]`/`[!!]`/`[--]` indicators after each step build confidence through the emotional arc.

## Components Delivered

### Agent
- `agents/sbir-setup-wizard.md` -- 6-phase orchestrator: PREREQUISITES, COMPANY PROFILE, CORPUS SETUP, API KEY, VALIDATION SUMMARY, NEXT STEPS. Supports cancel safety and idempotent re-runs. 186 lines.

### Skill
- `skills/setup-wizard/setup-domain.md` -- Prerequisite check commands, validation indicators, profile/corpus detection patterns, Gemini config instructions, delegation patterns. 122 lines.

### Command
- `commands/sbir-setup.md` -- `/sbir:setup` entry point. No arguments. Dispatches to @sbir-setup-wizard. 42 lines.

### Documentation Updates
- `README.md` -- Updated to lead with `/sbir:setup` as the primary entry point for new users. Documented setup phases, command reference, idempotency.

## Test Coverage

| Category | Count |
|----------|-------|
| BDD scenarios (journey feature file) | 28 |
| UAT scenarios (user stories) | 22 |
| Walking skeletons | N/A (markdown agent, manual validation) |
| **Total documented scenarios** | **50** |

## Roadmap Steps (4 steps, 2 phases)

1. **01-01**: Setup wizard agent with 6-phase orchestration workflow
2. **01-02**: Setup domain skill with check commands and display patterns
3. **01-03**: Setup command with agent dispatch
4. **02-01**: README update to lead with setup command

## Discovery Artifacts

- JTBD analysis: 5 job stories (JS-1 through JS-5) with emotional/social dimensions
- Journey mapping: YAML structure, visual ASCII diagrams, Gherkin feature file
- User stories: US-FTS-001 through US-FTS-005, 22 UAT scenarios, all DoR passed
- Shared artifacts registry: 12 artifacts with integration checkpoints
- DoR validation: All 5 stories passed 8-item hard gate, anti-pattern scan clean
