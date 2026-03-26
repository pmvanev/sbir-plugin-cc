# Handoff to DESIGN Wave: Company Profile Enrichment

## Feature Summary

Automated company profile enrichment from three federal APIs (SAM.gov, SBIR.gov, USASpending.gov) integrated into the existing profile builder flow. When a user provides their UEI during profile creation or update, the system retrieves registration data, SBIR award history, and federal award totals, then presents enriched data with source attribution for user confirmation before merging into the profile draft.

## Delivery Artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| JTBD Analysis | `docs/feature/company-profile-enrichment/discuss/jtbd-analysis.md` | 3 job stories, forces analysis, opportunity scoring (7 outcomes) |
| Journey Visual | `docs/feature/company-profile-enrichment/discuss/journey-enrichment-visual.md` | ASCII flow, TUI mockups (5 steps + 5 error paths), emotional arc |
| Journey Schema | `docs/feature/company-profile-enrichment/discuss/journey-enrichment.yaml` | Structured YAML with steps, artifacts, integration checkpoints |
| Gherkin Scenarios | `docs/feature/company-profile-enrichment/discuss/journey-enrichment.feature` | 26 scenarios covering all steps, error paths, and update flow |
| Shared Artifacts | `docs/feature/company-profile-enrichment/discuss/shared-artifacts-registry.md` | 8 tracked artifacts, 7 integration checkpoints |
| User Stories | `docs/feature/company-profile-enrichment/discuss/user-stories.md` | 4 stories with DoR validation (all PASSED) |
| API Research | `docs/research/company-profile-enrichment-apis.md` | 18-source research on SAM.gov, SBIR.gov, USASpending APIs |

## User Stories Summary

| ID | Title | Effort | Scenarios | MoSCoW | Dependencies |
|----|-------|--------|-----------|--------|--------------|
| US-CPE-004 | SAM.gov API Key Setup and Validation | 1 day | 4 | Must Have | ~/.sbir/ directory |
| US-CPE-001 | Three-API Profile Enrichment from UEI | 3 days | 5 | Must Have | US-CPE-004, profile builder agent |
| US-CPE-002 | Enrichment Review and Confirm | 1 day | 5 | Must Have | US-CPE-001 |
| US-CPE-003 | Re-Enrichment During Profile Update | 2 days | 5 | Should Have | US-CPE-001, US-CPE-004, US-CPB-004 |

**Total effort estimate**: ~7 days
**Total scenarios**: 19 (stories) + 7 additional in Gherkin feature file = 26 unique scenarios

**Recommended delivery order**: US-CPE-004 -> US-CPE-001 -> US-CPE-002 -> US-CPE-003

## Delivery Surfaces

This feature has two delivery surfaces (consistent with project pattern):

1. **Python TDD** (`scripts/pes/`): Enrichment port, three API adapters (SAM.gov, SBIR.gov, USASpending), enrichment service, CLI entry point, API key management. Ports-and-adapters pattern. Full TDD with pytest. Mutation testing target >= 80%.

2. **Markdown Forge**: Updates to `sbir-profile-builder` agent (enrichment integration into MODE SELECT and INTERVIEW phases), new enrichment skill file, updated profile builder command.

## Architecture Constraints for DESIGN Wave

These constraints are derived from requirements (solution-neutral) and existing system patterns:

1. **Ports-and-adapters**: Enrichment logic in `scripts/pes/` following existing PES architecture. Domain rules (field mapping, diff logic) are pure Python with no infrastructure imports.

2. **Agent-to-Python bridge**: Agent invokes enrichment via Bash tool calling Python CLI. No WebFetch for API calls (sidesteps URL-in-context restriction, keeps HTTP client logic testable).

3. **API key security**: Key in separate file from profile (`~/.sbir/api-keys.json`). Never in CLI args. Never displayed in full. Owner-only file permissions.

4. **Propose, never overwrite**: Enrichment data is always presented to the user for confirmation. No enriched field enters the profile without explicit user action.

5. **Partial results acceptable**: If one API fails, data from the other two is still usable. The system degrades gracefully.

6. **Existing flow preserved**: When enrichment is skipped (no API key, user declines), the profile builder behaves exactly as today (US-CPB-001 through US-CPB-005 unchanged).

7. **Schema compatibility**: Enriched data must map to existing `templates/company-profile-schema.json` field paths. The schema may need extension for NAICS codes (currently not a top-level field).

## Knowledge Gaps for DESIGN to Resolve

1. **SAM.gov API exact field paths**: The business type certification flags (8(a), HUBZone, etc.) may use `businessTypeCode` values rather than boolean flags. DESIGN should load the OpenAPI spec and run a test query to map exact JSON paths.

2. **SBIR.gov UEI search support**: The documented query parameter is `keyword` (company name). Direct `?uei=` parameter may not be supported. DESIGN should validate and implement fallback to name search with UEI filtering in response.

3. **NAICS codes in profile schema**: Current `company-profile-schema.json` does not have a top-level `naics_codes` field. DESIGN must decide: add to schema (requires sbir-topic-scout update) or store as informational metadata in `sources`.

4. **USASpending recipient ID resolution**: The USASpending API requires a recipient hash/ID, not a UEI directly. The lookup path is: autocomplete by name -> get recipient_id -> fetch recipient details. DESIGN must implement this two-step resolution.

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| SAM.gov API field structure differs from documentation | Medium | Medium | Test query during DESIGN spike; adapter maps response dynamically |
| SBIR.gov API unreliable (maintenance notice) | Medium | Low | Graceful degradation; partial enrichment accepted |
| USASpending rate limiting (undocumented) | Low | Low | Exponential backoff; single-company use is well under any likely limit |
| Schema extension for NAICS breaks existing topic scout | Medium | High | ADR required; backward-compatible addition with default handling |
| API key management complexity | Low | Medium | Simple JSON file; proven pattern from existing project |

## Peer Review

### Review Summary

Self-review against review dimensions (formal peer review via Task deferred to DESIGN wave entry):

**Confirmation Bias**: No technology bias (solution-neutral -- "Python service" and "ports-and-adapters" are existing project patterns, not new prescriptions). Happy path bias addressed with 5 error paths in journey visual and error/edge scenarios in every story. No availability bias detected.

**Completeness**: Three stakeholder perspectives covered (user/Rafael, system/topic-scout integration, security/API key handling). Error scenarios comprehensive (invalid key, entity not found, API timeout, ambiguous match, data conflicts). NFRs addressed in technical notes (rate limits, timeouts, file permissions).

**Clarity**: All AC are observable and measurable. No vague performance requirements. No ambiguous terms.

**Testability**: All scenarios in Given-When-Then with concrete data. All AC derivable from scenarios.

**Priority**: Opportunity scoring validates these are the highest-value outcomes. Simpler alternative (manual entry) is the current state being improved.

### DoR Status

All 4 stories PASSED DoR validation. See individual validations in `user-stories.md`.

## Handoff Checklist

- [x] JTBD analysis with job stories, forces, and opportunity scoring
- [x] Journey visual with ASCII mockups and emotional arc
- [x] Journey YAML schema with integration checkpoints
- [x] Gherkin scenarios (26 total)
- [x] Shared artifacts registry (8 artifacts, 7 checkpoints)
- [x] User stories with LeanUX template (4 stories)
- [x] DoR validation (all 4 PASSED)
- [x] Risk assessment
- [x] Knowledge gaps documented for DESIGN resolution
- [x] Delivery surface identification (Python TDD + Markdown Forge)
- [x] Dependency chain documented (CPE-004 -> CPE-001 -> CPE-002 -> CPE-003)
