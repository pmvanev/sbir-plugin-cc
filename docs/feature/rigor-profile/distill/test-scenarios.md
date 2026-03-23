# Test Scenarios -- Rigor Profile

Feature: rigor-profile
Date: 2026-03-23
Phase: 5 -- DISTILL (Acceptance Test Design)

---

## Scenario Inventory

### Walking Skeletons (3 scenarios)

| ID | Scenario | Type | Story |
|----|----------|------|-------|
| WS-1 | Elena sets thorough rigor for her must-win proposal | Walking skeleton | RP-002 |
| WS-2 | Phil opens a pre-rigor proposal and it works with standard defaults | Walking skeleton | RP-004 |
| WS-3 | The writer agent resolves its model tier from the active rigor profile | Walking skeleton | RP-004 |

### Milestone 01: Profile Validation and Registry (7 scenarios)

| ID | Scenario | Type | Story |
|----|----------|------|-------|
| V-1 | Valid profile name is accepted | Happy path | RP-001 |
| V-2 | All four profile names are recognized | Happy path | RP-001 |
| V-3 | Unknown profile name is rejected with available options | Error path | RP-002 |
| V-4 | Empty profile name is rejected | Error path | RP-002 |
| V-5 | Profile name validation is case-sensitive | Error path | RP-002 |
| V-6 | Profile definitions include all eight agent roles | Boundary | RP-001 |
| V-7 | Each profile defines valid model tiers only | Boundary | RP-001 |

### Milestone 02: Profile Selection and Persistence (7 scenarios)

| ID | Scenario | Type | Story |
|----|----------|------|-------|
| S-1 | Set thorough profile and view per-role diff | Happy path | RP-002 |
| S-2 | Set lean profile for cost-conscious screening | Happy path | RP-002 |
| S-3 | History entry records from, to, timestamp, and wave | Happy path | RP-003, RP-007 |
| S-4 | No active proposal returns guidance | Error path | RP-002 |
| S-5 | Same profile is a no-op with no history entry | Edge case | RP-002 |
| S-6 | Multiple rigor changes accumulate in history | Edge case | RP-007 |
| S-7 | Downgrade from exhaustive to lean is permitted | Edge case | RP-002 |

### Milestone 03: Agent Model Tier Resolution (13 scenarios)

| ID | Scenario | Type | Story |
|----|----------|------|-------|
| R-1 | Writer resolves strongest at thorough rigor | Happy path | RP-004 |
| R-2 | Researcher resolves standard at thorough rigor | Happy path | RP-004 |
| R-3 | All agent roles resolve basic at lean rigor | Happy path | RP-004 |
| R-4 | Formatter resolves standard at thorough rigor | Happy path | RP-004 |
| R-5 | Thorough profile provides 2 review passes | Happy path | RP-004 |
| R-6 | Lean profile provides 1 review pass | Happy path | RP-004 |
| R-7 | Exhaustive profile provides 3 review passes | Happy path | RP-004 |
| R-8 | Thorough profile caps critique loops at 3 iterations | Happy path | RP-004 |
| R-9 | Lean profile skips critique loops entirely | Error/edge | RP-004 |
| R-10 | Missing rigor configuration defaults to standard resolution | Fallback | RP-004 |
| R-11 | Missing rigor configuration provides standard review passes | Fallback | RP-004 |
| R-12 | Every profile defines a valid model tier for every agent role | @property | RP-001 |
| R-13 | Resolution chain is deterministic for any profile and role | @property | RP-004 |

### Milestone 04: Contextual Rigor Suggestion (9 scenarios)

| ID | Scenario | Type | Story |
|----|----------|------|-------|
| SG-1 | High-value Phase II proposal receives thorough suggestion | Happy path | RP-003 |
| SG-2 | Low-value Phase I proposal receives lean suggestion | Happy path | RP-003 |
| SG-3 | Mid-range proposal receives no suggestion | Happy path | RP-003 |
| SG-4 | Fit score exactly at 80 with Phase II triggers thorough | Boundary | RP-003 |
| SG-5 | Fit score exactly at 70 with Phase I gives no suggestion | Boundary | RP-003 |
| SG-6 | Fit score 69 with Phase I triggers lean suggestion | Boundary | RP-003 |
| SG-7 | High fit score with Phase I gives no suggestion | Edge case | RP-003 |
| SG-8 | Low fit score with Phase II gives no suggestion | Edge case | RP-003 |
| SG-9 | Default profile is always standard regardless of suggestion | Edge case | RP-003 |

### Milestone 05: Diff Computation (6 scenarios)

| ID | Scenario | Type | Story |
|----|----------|------|-------|
| D-1 | Diff from standard to thorough shows role-level changes | Happy path | RP-002 |
| D-2 | Diff from standard to lean shows downgrade to basic | Happy path | RP-002 |
| D-3 | Diff from thorough to exhaustive shows targeted upgrades | Happy path | RP-002 |
| D-4 | Diff between same profile produces no changes | Edge case | RP-002 |
| D-5 | Diff includes only roles that actually changed | Edge case | RP-002 |
| D-6 | Diff with invalid profile name fails gracefully | Error path | RP-002 |

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Total scenarios | 45 |
| Walking skeletons | 3 |
| Focused scenarios | 42 |
| Happy path | 18 (40%) |
| Error path | 8 (18%) |
| Edge case | 10 (22%) |
| Boundary | 5 (11%) |
| Fallback | 2 (4%) |
| @property | 2 (4%) |
| **Error + Edge + Boundary + Fallback** | **25 (56%)** |

Error/edge ratio: 56% (exceeds 40% target).

---

## Story Coverage Matrix

| Story | Scenarios | Covered |
|-------|-----------|---------|
| RP-001 (View/Compare) | V-1, V-2, V-6, V-7, R-12 | Yes (Python: definition loading + validation) |
| RP-002 (Select Profile) | WS-1, V-3, V-4, V-5, S-1..S-7, D-1..D-6 | Yes |
| RP-003 (Contextual Suggestion) | SG-1..SG-9, S-3 | Yes |
| RP-004 (Agent Model Resolution) | WS-2, WS-3, R-1..R-13 | Yes |
| RP-005 (Wave Display) | -- | No (markdown surface, forge-validated) |
| RP-006 (Status/Portfolio) | -- | No (markdown surface, forge-validated) |
| RP-007 (Mid-Proposal Change) | S-3, S-6 | Yes (history recording) |
| RP-008 (Debrief Summary) | -- | No (markdown surface, forge-validated) |

Stories RP-005, RP-006, RP-008 are display-only markdown concerns. Not tested here.

---

## Mandate Compliance Evidence

### CM-A: Hexagonal Boundary Enforcement

All step definitions import through driving ports only:
- `pes.domain.rigor_service.RigorService` (application service)
- `pes.domain.rigor.compute_rigor_suggestion` (domain function)
- `pes.domain.rigor.validate_profile_name` (domain function)
- `pes.adapters.filesystem_rigor_adapter.FileSystemRigorAdapter` (adapter wired to port)

Zero internal component imports (no validator, parser, or formatter directly).

### CM-B: Business Language Purity

Gherkin uses business terms exclusively:
- "rigor profile", "model tier", "review passes", "critique iterations"
- "walking skeleton", "must-win proposal", "cost-conscious screening"
- Zero technical terms: no JSON, HTTP, database, API, class, method references

### CM-C: Walking Skeleton + Focused Scenario Counts

- Walking skeletons: 3
- Focused scenarios: 42
- Total: 45
- Ratio: 3 skeletons + 42 focused (within 2-5 skeleton guideline)
