# Test Scenarios: Proposal Format Selection

## Scope

Tests cover the **Python-testable domain logic** only:

- `FormatConfigService` -- format validation, rework risk determination, state update
- `ProposalCreationService._build_initial_state()` -- output_format field inclusion
- State persistence -- output_format in proposal-state.json
- Schema validation -- valid/invalid format values

Agent interactive prompts (format selection prompt, solicitation hints, status display) are validated via forge checklist, not pytest.

## Story-to-Scenario Mapping

### US-PFS-001: Select Output Format During Proposal Setup (5 scenarios)

| # | Scenario | Type | Tags |
|---|----------|------|------|
| WS-1 | Engineer sets up proposal and format choice persists in state | walking_skeleton | @walking_skeleton @US_PFS_001 |
| 1 | New proposal includes output format defaulting to DOCX | happy_path | @US_PFS_001 |
| 2 | Format set to LaTeX is recorded in proposal state | happy_path | @US_PFS_001 |
| 3 | Missing output format defaults to DOCX on read | edge_case | @US_PFS_001 |
| 4 | Schema rejects invalid format value in state | error_path | @US_PFS_001 @property |

### US-PFS-002: Change Output Format Mid-Proposal (11 scenarios)

| # | Scenario | Type | Tags |
|---|----------|------|------|
| WS-2 | Engineer changes format before drafting and state updates cleanly | walking_skeleton | @walking_skeleton @US_PFS_002 |
| 5 | Format changed from DOCX to LaTeX before Wave 3 | happy_path | @US_PFS_002 |
| 6 | Format changed from LaTeX to DOCX before Wave 3 | happy_path | @US_PFS_002 |
| 7 | Format change at Wave 3 triggers rework warning | edge_case | @US_PFS_002 |
| 8 | Format change at Wave 4 triggers rework warning | happy_path | @US_PFS_002 |
| 9 | Format change at Wave 6 triggers rework warning | edge_case | @US_PFS_002 |
| 10 | Invalid format value rejected with error message | error_path | @US_PFS_002 |
| 11 | Empty format value rejected | error_path | @US_PFS_002 |
| 12 | Format change to same value succeeds without warning | edge_case | @US_PFS_002 |
| 13 | Format change at Wave 2 proceeds without warning | boundary | @US_PFS_002 |
| 14 | Rework warning includes wave context | happy_path | @US_PFS_002 |
| 15 | Valid format values are always accepted regardless of case | property | @US_PFS_002 @property |

## Scenario Counts

- **Total scenarios**: 16
- **Walking skeletons**: 2 (12.5%)
- **Happy path**: 6 (37.5%)
- **Error path**: 3 (18.75%)
- **Edge case**: 4 (25%)
- **Boundary**: 1 (6.25%)
- **Property-tagged**: 2

**Error + edge + boundary ratio**: 8/16 = 50% (exceeds 40% target)

## Walking Skeleton Litmus Test

### WS-1: Engineer sets up proposal and format choice persists in state
- Title describes user goal? YES -- "sets up proposal and format choice persists"
- Given/When describe user actions? YES -- creates proposal with format preference
- Then describes observable outcome? YES -- format is retrievable from state
- Stakeholder confirms? YES -- "the format I chose is saved with my proposal"

### WS-2: Engineer changes format before drafting and state updates cleanly
- Title describes user goal? YES -- "changes format" is the user action
- Given/When describe user actions? YES -- has proposal, requests format change
- Then describes observable outcome? YES -- format is updated, no warning shown
- Stakeholder confirms? YES -- "I can change my format early without issues"

## Property-Shaped Scenarios

| Scenario | Signal | Implementation Hint |
|----------|--------|-------------------|
| Schema rejects invalid format value | "any value not in allowed list" | Generate arbitrary strings, verify rejection |
| Valid format values always accepted | "always accepted regardless of case" | Generate case variations of latex/docx |
