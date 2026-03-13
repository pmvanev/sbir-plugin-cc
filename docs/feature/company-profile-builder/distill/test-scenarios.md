# Company Profile Builder -- Test Scenarios

## Scenario Inventory

Total: 34 executable scenarios across 4 feature files.

### Walking Skeletons (3 scenarios)

| # | Scenario | Driving Ports | Status |
|---|----------|---------------|--------|
| WS-1 | Founder creates a valid company profile and retrieves it | ProfileValidationService, ProfilePort | skip (first to enable) |
| WS-2 | Founder sees validation errors before profile is saved | ProfileValidationService | skip (first to enable) |
| WS-3 | Founder updates one section and all other sections are preserved | ProfilePort, ProfileValidationService | skip |

### Milestone 01: Foundation (18 scenarios)

Covers: US-CPB-002 (validation), US-CPB-005 + US-CPB-001 (persistence)

| # | Scenario | Type | Story |
|---|----------|------|-------|
| F-01 | Complete profile passes all validation checks | Happy | US-CPB-002 |
| F-02 | CAGE code with wrong length is rejected | Error | US-CPB-002 |
| F-03 | CAGE code with special characters is rejected | Error | US-CPB-002 |
| F-04 | Invalid security clearance value is rejected | Error | US-CPB-002 |
| F-05 | Employee count of zero is rejected | Error | US-CPB-002 |
| F-06 | Negative employee count is rejected | Error | US-CPB-002 |
| F-07 | Profile with no capabilities is rejected | Error | US-CPB-002 |
| F-08 | Profile missing company name is rejected | Error | US-CPB-002 |
| F-09 | Missing UEI with active SAM.gov is rejected | Error | US-CPB-002 |
| F-10 | Invalid socioeconomic certification is rejected | Error | US-CPB-002 |
| F-11 | Profile with inactive SAM.gov does not require CAGE/UEI | Boundary | US-CPB-002 |
| F-12 | Multiple validation errors reported in a single result | Edge | US-CPB-002 |
| F-13 | New profile is persisted atomically | Happy | US-CPB-001 |
| F-14 | Saving over an existing profile creates a backup | Happy | US-CPB-005 |
| F-15 | Profile directory is created if absent | Error | US-CPB-001 |
| F-16 | Existing profile metadata is retrieved for overwrite protection | Happy | US-CPB-005 |
| F-17 | Loading a profile that does not exist reports the absence | Error | US-CPB-005 |
| F-18 | Profile roundtrip preserves all data exactly | Property | US-CPB-002 |

### Milestone 02: Agent and Commands (0 executable Python scenarios)

Agent and command behavior (US-CPB-001, US-CPB-002, US-CPB-005) is validated through the markdown agent protocol. The `milestone-02-agent-commands.feature` file contains 12 Gherkin scenarios documenting expected agent behavior for stakeholder review, but these are not executable in pytest-bdd since they test LLM-driven conversational flows.

### Milestone 03: Extraction and Update (13 scenarios)

Covers: US-CPB-003 (extraction merge logic), US-CPB-004 (selective update)

| # | Scenario | Type | Story |
|---|----------|------|-------|
| EU-01 | Extracted fields from a document populate the profile draft | Happy | US-CPB-003 |
| EU-02 | Data from multiple documents combines into a single profile | Happy | US-CPB-003 |
| EU-03 | Partially extracted profile identifies missing fields | Edge | US-CPB-003 |
| EU-04 | Extraction with no profile data leaves the draft empty | Error | US-CPB-003 |
| EU-05 | Extracted data with invalid values is caught during validation | Error | US-CPB-003 |
| EU-06 | Adding a past performance entry to an existing profile | Happy | US-CPB-004 |
| EU-07 | Adding a team member preserves existing personnel | Happy | US-CPB-004 |
| EU-08 | Updating employee count replaces the value | Happy | US-CPB-004 |
| EU-09 | Updating a profile that does not exist reports the absence | Error | US-CPB-004 |
| EU-10 | Updating one section leaves all other sections intact | Edge | US-CPB-004 |
| EU-11 | Update that introduces invalid data is rejected | Error | US-CPB-004 |
| EU-12 | Activating SAM.gov registration requires CAGE and UEI | Edge | US-CPB-004 |
| EU-13 | Updating a section never changes unrelated sections | Property | US-CPB-004 |

---

## Coverage Analysis

### Error Path Ratio

| Feature File | Happy | Error | Edge/Boundary | Property | Total | Error % |
|-------------|-------|-------|---------------|----------|-------|---------|
| Walking Skeleton | 1 | 1 | 1 | 0 | 3 | 33% |
| Milestone 01 | 4 | 8 | 2 | 1 | 15 | 53% |
| Milestone 03 | 3 | 4 | 3 | 1 | 11 | 36% |
| **Overall** | **8** | **13** | **6** | **2** | **29** | **45%** |

Note: 5 agent-command scenarios (milestone-02) excluded from ratio since they are not executable Python tests.

Error path ratio: **45%** (exceeds 40% target).

### Story Coverage

| Story | Scenarios | Coverage |
|-------|-----------|----------|
| US-CPB-001 | WS-1, F-13, F-15, + agent scenarios | Full (Python: persistence; Agent: interview) |
| US-CPB-002 | WS-2, F-01 through F-12, F-18 | Full (13 validation scenarios) |
| US-CPB-003 | EU-01 through EU-05 | Full (extraction merge logic) |
| US-CPB-004 | WS-3, EU-06 through EU-13 | Full (8 update scenarios) |
| US-CPB-005 | F-14, F-16, F-17, + agent scenarios | Full (Python: backup/metadata; Agent: dialog) |

### Property-Tagged Scenarios

| Scenario | Signal | Implementation Note |
|----------|--------|-------------------|
| F-18: Profile roundtrip preserves all data exactly | Roundtrip | Generate profiles, save/load, assert equality |
| EU-13: Updating a section never changes unrelated sections | Invariant ("never") | Generate profiles + section updates, verify unmodified sections |

---

## Implementation Sequence

One test at a time. Enable, implement, commit, repeat.

### Phase 1: Enable Walking Skeletons

1. WS-1: Founder creates a valid company profile and retrieves it
   - Requires: ProfileValidationService, ProfilePort, JsonProfileAdapter
   - Proves: end-to-end validate-save-load works

2. WS-2: Founder sees validation errors before profile is saved
   - Requires: ProfileValidationService with CAGE and employee_count rules
   - Proves: validation catches errors, prevents save

### Phase 2: Validation Service (Milestone 01)

3. F-01: Complete profile passes all validation checks
4. F-02: CAGE code with wrong length is rejected
5. F-03: CAGE code with special characters is rejected
6. F-04: Invalid security clearance value is rejected
7. F-05: Employee count of zero
8. F-06: Negative employee count
9. F-07: Empty capabilities
10. F-08: Missing company name
11. F-09: Missing UEI with active SAM.gov
12. F-10: Invalid socioeconomic
13. F-11: Inactive SAM.gov boundary
14. F-12: Multiple errors

### Phase 3: Persistence (Milestone 01)

15. F-13: New profile persisted atomically
16. F-14: Backup before overwrite
17. F-15: Directory creation
18. F-16: Existing profile metadata
19. F-17: Load non-existent
20. F-18: Roundtrip property

### Phase 4: Update (Milestone 03)

21. EU-06: Add past performance
22. EU-07: Add key personnel
23. EU-08: Update scalar
24. EU-09: Update non-existent
25. EU-10: Preserve unmodified
26. EU-11: Invalid update rejected
27. EU-12: SAM.gov activation
28. WS-3: Walking skeleton update
29. EU-13: Update invariant property

### Phase 5: Extraction Merge (Milestone 03)

30. EU-01: Extraction populates draft
31. EU-02: Multiple document merge
32. EU-03: Partial extraction gaps
33. EU-04: Empty extraction
34. EU-05: Invalid extraction validation
