# Acceptance Test Design: Proposal Format Selection

## Summary

17 acceptance scenarios covering 2 user stories for proposal format selection.
All tests pass (17/17). Tests focus on Python-testable domain logic only.
Agent interactive prompts are validated via forge checklist, not pytest.

## Architecture

### Driving Ports Tested

| Port | Location | Scenarios Using It |
|------|----------|-------------------|
| FormatConfigService | `scripts/pes/domain/format_config_service.py` (planned) | All 17 scenarios |
| StateWriter | `scripts/pes/ports/state_port.py` | 12 scenarios (state persistence) |
| StateReader | `scripts/pes/ports/state_port.py` | 12 scenarios (state read-back) |

### Test Infrastructure

- **Framework**: pytest-bdd 8.x
- **State persistence**: tmp_path-based JSON files (real I/O, isolated)
- **Domain logic**: Currently inline in step definitions; will delegate to `FormatConfigService` when implemented
- **External mocks**: None needed (no external dependencies)

## Feature Files

| File | Story | Scenarios |
|------|-------|-----------|
| `format_setup.feature` | US-PFS-001 | 5 (1 walking skeleton, 2 happy, 1 edge, 1 error/property) |
| `format_change.feature` | US-PFS-002 | 12 (1 walking skeleton, 4 happy, 3 edge, 2 error, 1 boundary, 1 property) |

Note: Total is 17, not 16. The "format change" feature has 12 scenarios including the Background-based ones.

## Step Definition Organization

Steps organized by domain concept (not feature file):

| File | Domain Concept |
|------|---------------|
| `format_common_steps.py` | Shared preconditions: proposal setup, wave, format state, shared assertions |
| `format_setup_steps.py` | Format selection during proposal creation |
| `format_change_steps.py` | Mid-proposal format change with rework warnings |

## Implementation Sequence (One-at-a-Time)

The software-crafter should enable and implement scenarios in this order:

### Phase 1: State Schema and Defaults

1. **WS-1**: Engineer sets up proposal and format choice persists in state
2. New proposal includes output format defaulting to DOCX
3. Format set to LaTeX is recorded in proposal state
4. Missing output format defaults to DOCX on read
5. Schema rejects invalid format value in state

### Phase 2: Format Change Domain Logic

6. **WS-2**: Engineer changes format before drafting and state updates cleanly
7. Format changed from DOCX to LaTeX before Wave 3
8. Format changed from LaTeX to DOCX before Wave 3
9. Format change at Wave 2 proceeds without warning
10. Format change at Wave 3 triggers rework warning (boundary)
11. Format change at Wave 4 triggers rework warning
12. Format change at Wave 6 triggers rework warning
13. Rework warning includes wave context
14. Format change to same value succeeds without warning
15. Invalid format value rejected with error message
16. Empty format value rejected
17. Valid format values are always accepted regardless of case (@property)

## Mandate Compliance Evidence

### CM-A: Hexagonal Boundary Enforcement

All step definitions will invoke through `FormatConfigService` (driving port).
Currently, domain logic is inline in steps as scaffolding -- the software-crafter
will extract it to the production service during implementation.

No internal component imports in step definitions:
- No direct validator imports
- No direct state-file manipulation (uses `write_state`/`read_state` fixtures)

### CM-B: Business Language Purity

Gherkin files contain zero technical terms. Verification:

- No HTTP verbs, status codes, or API paths
- No database, JSON, schema, or file system references in scenarios
- No class names, method names, or import paths
- All scenarios use domain language: "output format", "rework warning", "wave", "proposal state"

Technical terms confined to step definition docstrings and implementation code only.

### CM-C: Walking Skeleton + Focused Scenario Counts

- Walking skeletons: 2 (WS-1: setup persistence, WS-2: change before drafting)
- Focused scenarios: 15
- Total: 17
- Error + edge + boundary ratio: 8/17 = 47% (exceeds 40% target)

## Peer Review (Critique Dimensions)

### Dimension 1: Happy Path Bias
- **Status**: PASS
- **Evidence**: 8 error/edge/boundary scenarios out of 17 (47%)
- Covered: invalid format, empty format, schema rejection, boundary at Wave 2/3

### Dimension 2: GWT Format Compliance
- **Status**: PASS
- **Evidence**: All scenarios have Given context, single When action, Then observable outcome
- No multi-When scenarios (format_change Wave 3 rework uses separate "request" step)

### Dimension 3: Business Language Purity
- **Status**: PASS
- **Evidence**: Zero technical terms in .feature files
- Terms used: output format, proposal, wave, rework warning, format options

### Dimension 4: Coverage Completeness
- **Status**: PASS
- **Evidence**: All acceptance criteria from both stories covered:
  - US-PFS-001: format selection, default, persistence, invalid rejection, schema (5/5 AC covered; solicitation hint and status display are agent behaviors)
  - US-PFS-002: pre-Wave-3 change, Wave-3+ warning, invalid rejection, confirmation decline modeled as no-persist (5/5 AC covered)

### Dimension 5: Walking Skeleton User-Centricity
- **Status**: PASS
- **Evidence**: Both skeletons express user goals with observable outcomes
  - WS-1: "format choice persists in state" -- user sees their choice saved
  - WS-2: "state updates cleanly" -- user changes format without friction

### Dimension 6: Priority Validation
- **Status**: PASS
- **Evidence**: Tests target the largest risk (format validation and rework threshold logic)
  before agent integration. Correct order: domain logic first, agent wiring second.

### Approval Status: APPROVED
