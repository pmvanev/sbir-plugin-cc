# DESIGN Wave Handoff -- SBIR Proposal Plugin (Phase C1)

## Handoff Metadata

- Feature: sbir-proposal-plugin
- Phase: C1 (Walking Skeleton)
- Source wave: DESIGN
- Target waves: DEVOPS (platform-architect), then DISTILL (acceptance-designer)
- Architecture document: `docs/architecture/architecture.md`
- ADRs: `docs/adrs/adr-001-*.md` through `adr-006-*.md`
- User stories: `docs/feature/sbir-proposal-plugin/discuss/user-stories.md`
- Specification: `sbir-proposal-plugin.md`

---

## Architecture Summary

Claude Code plugin. No server, no database, no web UI. Everything runs locally.

| Component | Implementation | Count (C1) |
|-----------|---------------|------------|
| Agents | Markdown files | 7 |
| Commands | Markdown files | 9 |
| Skills | Markdown files | 5 |
| PES Python | Ports-and-adapters | ~12 files |
| State | JSON on disk | 2 schemas |
| Templates | JSON/Markdown | 3 |

---

## For Platform Architect (DEVOPS Wave)

### What infrastructure does this plugin need?

Minimal. This is a Claude Code plugin, not a deployed application.

**Required:**
- Python 3.12+ on user's machine (for PES hooks)
- Claude Code installed and configured

**Project-level initialization (`/proposal new`):**
- Create `.sbir/` directory
- Write `proposal-state.json` from template
- Copy `pes-config.json` from template
- Create `.sbir/audit/` directory

**No CI/CD required for the plugin itself** -- it is installed via `claude plugin install`. However, the plugin repository benefits from:
- Python linting (ruff) and type checking (mypy) for `scripts/pes/`
- pytest for PES unit/integration tests
- Markdown linting for agents/commands/skills

### PES Python Dependencies

- Python 3.12+ (standard library only for core)
- `jsonschema` (MIT) -- for proposal-state.json validation
- `pytest` (MIT) -- dev dependency for testing
- `ruff` (MIT) -- dev dependency for linting

### Hook Configuration

See `docs/architecture/architecture.md` section "PES Hook Integration" for the `hooks.json` structure.

---

## For Acceptance Designer (DISTILL Wave)

### Scope

9 user stories, 39 scenarios. All in Phase C1.

### Story Priority Order (build sequence)

1. US-007: Proposal State Schema & Persistence (foundation)
2. US-006: PES Foundation (partial -- engine and hook setup)
3. US-003: Directory-Based Corpus Ingestion
4. US-002: Start New Proposal from Solicitation
5. US-001: Proposal Status & Reorientation
6. US-004: Automated Compliance Matrix (generation + manual add)
7. US-005: TPOC Question Generation & Answer Ingestion
8. US-009: Strategy Brief & Wave 1 Checkpoint
9. US-006: PES Foundation (complete -- wave ordering, session startup)
10. US-008: Simplified Compliance Check

### Roadmap Steps (12 steps)

| Step | Title | Story |
|------|-------|-------|
| 01-01 | Plugin skeleton and proposal state schema | US-007 |
| 01-02 | PES enforcement engine and hook integration | US-006 |
| 02-01 | Directory-based corpus ingestion | US-003 |
| 02-02 | Solicitation parsing and new proposal creation | US-002 |
| 03-01 | Proposal status and reorientation | US-001 |
| 03-02 | Compliance matrix generation and manual editing | US-004 |
| 03-03 | TPOC question generation | US-005 |
| 03-04 | TPOC answer ingestion and delta analysis | US-005 |
| 03-05 | Strategy brief generation and Wave 1 checkpoint | US-009 |
| 04-01 | PES wave ordering enforcement | US-006 |
| 04-02 | PES session startup integrity check | US-006 |
| 04-03 | Simplified compliance check command | US-008 |

### Development Paradigm

- **PES Python code:** OOP with ports-and-adapters. TDD with pytest.
- **Agents/commands/skills:** Markdown files. Validated via forge checklist, not unit tests.

### Key Architectural Constraints for Acceptance Tests

1. PES enforcement happens at hook layer (Python), not agent layer (markdown)
2. State persistence uses atomic writes (tmp -> bak -> rename)
3. Corpus search is Claude Code native file reading (no vector DB)
4. TPOC "pending" is a valid terminal state that blocks nothing
5. All human checkpoints follow approve/revise/skip/quit pattern
6. Compliance matrix is a single living markdown file, not copies per wave

### What the Acceptance Designer Needs to Produce

Given-When-Then acceptance tests for each of the 39 scenarios. The UAT scenarios in `user-stories.md` are the starting point -- they need to be formalized into executable acceptance criteria that the software crafter can implement against.

Focus areas:
- PES blocking behavior (exit codes, messages)
- State transitions (go_no_go, wave status, tpoc_status)
- File system operations (corpus paths, artifact paths, state atomicity)
- Error paths (missing files, corrupted state, empty corpus)
- Human checkpoint flow (approve/revise/skip outcomes)

---

## Quality Gates Checklist

- [x] Requirements traced to components (9 stories -> 12 steps)
- [x] Component boundaries with clear responsibilities (7 components)
- [x] Technology choices in ADRs with alternatives (6 ADRs)
- [x] Quality attributes addressed (maintainability, usability, reliability, security, observability)
- [x] Dependency-inversion compliance (PES ports-and-adapters)
- [x] C4 diagrams L1+L2+L3 in Mermaid
- [x] Integration patterns specified (checkpoint, async event, hook, atomic write)
- [x] OSS preference validated (Python PSF, jsonschema MIT)
- [x] Roadmap step ratio 0.38 (under 2.5 threshold)
- [x] AC behavioral, not implementation-coupled
- [x] Development paradigm documented in CLAUDE.md
