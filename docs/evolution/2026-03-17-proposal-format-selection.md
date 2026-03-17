# Evolution: Proposal Format Selection

**Date**: 2026-03-17
**Feature**: proposal-format-selection
**Waves Completed**: DISCOVER > DISCUSS > DESIGN > DISTILL > DELIVER

## Summary

Implemented the Proposal Format Selection feature: an explicit output format choice (LaTeX or DOCX) added to the `/proposal new` setup flow. The selection persists in `proposal-state.json` as `output_format` and is consumed by all downstream agents. A separate `/proposal config format` command allows mid-proposal format changes with rework warnings at Wave 3+. Eliminates the problem of late format discovery at Wave 6 causing content rework.

## Key Decisions

- **State-driven orchestrator prompt, not PES hook** (ADR-023): Format selection is a user preference, not a compliance invariant. The orchestrator agent owns the interactive prompt; PES handles only state persistence and validation. Rejected PES hook enforcement and separate config file alternatives.
- **Additive schema change**: `output_format` field added to `proposal-state-schema.json` with default `"docx"`. Existing proposals without the field remain valid (ADR-012 pattern). No migration required.
- **Rework warning threshold at Wave 3**: Format changes at Wave 3 (Outline) and above trigger a rework warning. Changes before Wave 3 proceed without warning. Same-format change is a no-op.
- **FormatConfigService as pure domain service**: Validates format values, determines rework risk, persists via existing StateWriter port. No new ports or adapters needed.

## Components Delivered

### Agent Modification
- `agents/sbir-orchestrator.md` -- Added format selection prompt to `/proposal new` flow (after fit scoring, before Go/No-Go). Added `/proposal config format` routing. Added format display in `/proposal status` dashboard. PDF-submission hints surface LaTeX recommendation.

### Domain Service
- `scripts/pes/domain/format_config_service.py` -- New domain service with setup-phase methods (`apply_selected_format`, `apply_default_format`, `get_effective_format`, `validate_format`) and mid-proposal change method (`change_format`). Pure domain logic, no infrastructure imports.

### Command
- `commands/sbir-proposal-config-format.md` -- `/proposal config format <latex|docx>`. Dispatches to @sbir-orchestrator. Documents rework warning flow and examples.

### Schema Update
- `templates/proposal-state-schema.json` -- `output_format` property added (enum: `"latex"`, `"docx"`, default: `"docx"`)

### Integration Updates
- `scripts/pes/domain/proposal_service.py` -- `_build_initial_state()` includes `output_format` with default `"docx"`
- `skills/common/proposal-state-schema.md` -- Documents `output_format` field for agent knowledge
- `skills/orchestrator/wave-agent-mapping.md` -- `proposal config format` added to routing table

## Test Coverage

| Category | Count |
|----------|-------|
| Acceptance tests (format setup, US-PFS-001) | 5 passed |
| Acceptance tests (format change, US-PFS-002) | 12 passed |
| Unit tests (FormatConfigService) | 26 passed |
| **Total** | **43 passed** |

### Mutation Testing

| Metric | Value |
|--------|-------|
| Tool | mutmut 2.4.x (Docker) |
| Target | `scripts/pes/domain/format_config_service.py` |
| Mutants generated | 71 |
| Killed | 59 |
| Survived | 12 |
| **Kill rate** | **83.1%** (gate: >= 80%) |

## Roadmap Steps (4 steps, 2 phases)

### Phase 01: State Schema and Domain Logic
1. **01-01**: Add `output_format` to state schema and initial state builder
2. **01-02**: FormatConfigService for mid-proposal format changes

### Phase 02: Agent and Command Integration
3. **02-01**: Orchestrator format prompt and status display
4. **02-02**: Config format command and routing

All 4 steps executed through DES (PREPARE > RED_ACCEPTANCE > RED_UNIT > GREEN > COMMIT). Steps 02-01 and 02-02 skipped RED_UNIT (markdown files have no unit tests).

## Discovery Artifacts

- User stories: US-PFS-001 (5 scenarios), US-PFS-002 (4 scenarios)
- Architecture: C4 L2 container diagram, component boundaries (4 tiers), data model change, integration patterns
- ADR-023: Format selection as state-driven orchestrator prompt
- 2 rejected simpler alternatives documented (default-only, defer-to-Wave-6)
