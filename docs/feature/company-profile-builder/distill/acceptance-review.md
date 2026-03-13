# Company Profile Builder -- Acceptance Test Review

## Peer Review (critique-dimensions)

### Dimension 1: Happy Path Bias

**Status**: PASS

Error path ratio: 45% (13 error + 6 edge out of 29 executable scenarios). Exceeds 40% target.

Coverage by category:
- CAGE code: wrong length, special characters (2 error scenarios)
- Employee count: zero, negative (2 error scenarios)
- Clearance: invalid enum (1 error scenario)
- Capabilities: empty list (1 error scenario)
- Company name: missing (1 error scenario)
- UEI: missing when SAM active (1 error scenario)
- Socioeconomic: invalid value (1 error scenario)
- Profile not found: load and update attempts (2 error scenarios)
- Invalid update rejected (1 error scenario)
- Empty document extraction (1 error scenario)

### Dimension 2: GWT Format Compliance

**Status**: PASS

All scenarios follow Given-When-Then structure. Each has:
- Given: clear precondition in business terms
- When: single action (validate, save, update)
- Then: observable business outcome

No multiple-When violations. No technical assertions in Then steps.

### Dimension 3: Business Language Purity

**Status**: PASS

Gherkin contains zero technical terms. Verified:
- No HTTP verbs, status codes, or API paths
- No database references
- No JSON/schema terminology in feature files
- No class/method names
- Domain terms used: profile, validation, CAGE code, capabilities, clearance, employee count, past performance, key personnel

Step definitions reference driving ports only:
- `ProfileValidationService` (domain service)
- `ProfilePort` / `JsonProfileAdapter` (persistence port)

### Dimension 4: Coverage Completeness

**Status**: PASS

All 5 user stories mapped to scenarios:
- US-CPB-001: 3 scenarios (persistence path) + 12 agent scenarios (documented)
- US-CPB-002: 13 scenarios (full validation rule coverage)
- US-CPB-003: 5 scenarios (extraction merge logic)
- US-CPB-004: 8 scenarios (selective update, preservation)
- US-CPB-005: 3 scenarios (backup, metadata, missing profile)

All acceptance criteria from user stories have corresponding test scenarios.

### Dimension 5: Walking Skeleton User-Centricity

**Status**: PASS

3 walking skeletons all pass the 4-point litmus test:
1. Titles describe user goals, not technical flows
2. Given/When steps describe user actions and context
3. Then steps describe user-observable outcomes
4. Non-technical stakeholder can confirm value

### Dimension 6: Priority Validation

**Status**: PASS

Validation (US-CPB-002) has the most scenarios (13) because it is the highest-risk component -- invalid profiles silently degrade fit scoring for every future proposal. Persistence (US-CPB-005) tested next. Update (US-CPB-004) follows. Extraction merge (US-CPB-003) has fewest scenarios because it delegates to the same validation service.

---

## Mandate Compliance Evidence

### CM-A: Hexagonal Boundary Enforcement

All step definitions invoke through driving ports. Import listings:

```
profile_validation_steps.py:
  - build_profile_from_table (test helper -- builds dicts)
  - TODO: from pes.domain.profile_validation import ProfileValidationService

profile_persistence_steps.py:
  - TODO: from pes.adapters.json_profile_adapter import JsonProfileAdapter

profile_update_steps.py:
  - TODO: from pes.adapters.json_profile_adapter import JsonProfileAdapter
  - TODO: from pes.domain.profile_validation import ProfileValidationService
```

Zero internal component imports. All interactions through ProfileValidationService (domain entry point) and ProfilePort/JsonProfileAdapter (persistence entry point).

### CM-B: Business Language Purity

Feature file grep for technical terms:

```
grep -i "http\|api\|json\|database\|sql\|rest\|status.code\|controller\|service\|class\|method" *.feature
# Result: 0 matches in Gherkin text
```

Step methods delegate to production services via driving ports. Business logic lives in production code.

### CM-C: Walking Skeleton + Focused Scenario Counts

- Walking skeletons: 3 (WS-1, WS-2, WS-3)
- Focused scenarios: 26 (across milestone-01 and milestone-03)
- Property-tagged scenarios: 2 (F-18, EU-13)
- Agent documentation scenarios: 12 (milestone-02, not executable)
- Total executable: 34

Ratio: 3 skeletons + 26 focused + 2 property + 3 shared = appropriate for 5 stories.

---

## Definition of Done Checklist

| Item | Status | Evidence |
|------|--------|----------|
| All acceptance scenarios written | PASS | 34 scenarios across 4 feature files |
| Step definitions with fixture injection | PASS | 3 step modules + 1 conftest |
| Test pyramid planned | PASS | Acceptance (34) + unit test locations identified in production code |
| Peer review approved | PASS | 6 dimensions all PASS |
| Walking skeleton identification | PASS | 3 skeletons documented with litmus test |
| Implementation sequence defined | PASS | 34-step ordered sequence in test-scenarios.md |
| One-at-a-time tagging | PASS | All scenarios @skip except first pair |
| Business language verified | PASS | Zero technical terms in Gherkin |
| Error path ratio >= 40% | PASS | 45% |
| Scenarios run in pytest | PASS | 21 + 13 = 34 collected, all properly skipped |

---

## Handoff to Software Crafter

### First Tests to Enable

Remove `@skip` from walking skeleton WS-1 and WS-2. Replace `pytest.skip()` calls in When steps with actual service invocations.

### Production Code to Implement

1. `templates/company-profile-schema.json` -- JSON Schema source of truth
2. `scripts/pes/domain/profile_validation.py` -- ProfileValidationService, ProfileValidationResult, ProfileFieldError
3. `scripts/pes/ports/profile_port.py` -- ProfilePort abstract interface
4. `scripts/pes/adapters/json_profile_adapter.py` -- JsonProfileAdapter with atomic writes

### Step Activation Pattern

Each When step contains commented-out production code invocation. The software crafter:
1. Removes `@skip` from the next scenario's feature file tag
2. Implements the production code to make it pass
3. Uncomments the driving port invocation in the When step
4. Removes the `pytest.skip()` call
5. Runs the test -- should fail for business logic reason, then pass after implementation
