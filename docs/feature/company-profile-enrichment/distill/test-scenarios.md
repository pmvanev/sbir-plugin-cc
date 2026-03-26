# Test Scenarios: Company Profile Enrichment

## Scenario Inventory

| # | Feature File | Scenario | Story | Type | Tag |
|---|-------------|----------|-------|------|-----|
| 1 | walking-skeleton | Founder enriches profile from UEI and receives data from three federal sources | US-CPE-001 | Walking Skeleton | @walking_skeleton |
| 2 | walking-skeleton | Founder receives partial enrichment when one federal source is unavailable | US-CPE-001 | Walking Skeleton | @walking_skeleton |
| 3 | walking-skeleton | Founder detects new SBIR award during profile update re-enrichment | US-CPE-003 | Walking Skeleton | @walking_skeleton |
| 4 | milestone-1 | Existing API key detected and reused without prompting | US-CPE-004 | Happy Path | |
| 5 | milestone-1 | New API key validated and saved securely | US-CPE-004 | Happy Path | |
| 6 | milestone-1 | Invalid API key rejected with clear guidance | US-CPE-004 | Error Path | @skip |
| 7 | milestone-1 | Expired API key detected during validation | US-CPE-004 | Error Path | @skip |
| 8 | milestone-1 | Enrichment skipped when founder declines API key setup | US-CPE-004 | Error Path | @skip |
| 9 | milestone-1 | Malformed API key file handled gracefully | US-CPE-004 | Edge Case | @skip |
| 10 | milestone-1 | API key never displayed in full after entry | US-CPE-004 | Edge Case | @skip |
| 11 | milestone-1 | API key never passed as a command-line argument | US-CPE-004 | Edge Case | @skip |
| 12 | milestone-2 | SAM.gov returns complete entity registration data | US-CPE-001 | Happy Path | @skip |
| 13 | milestone-2 | SBIR.gov returns award history including a forgotten award | US-CPE-001 | Happy Path | @skip |
| 14 | milestone-2 | USASpending returns federal award totals and business types | US-CPE-001 | Happy Path | @skip |
| 15 | milestone-2 | Full three-API cascade populates enrichment result | US-CPE-001 | Happy Path | @skip |
| 16 | milestone-2 | SAM.gov returns no entity for the entered UEI | US-CPE-001 | Error Path | @skip |
| 17 | milestone-2 | Invalid UEI format rejected before any API call | US-CPE-001 | Error Path | @skip |
| 18 | milestone-2 | SBIR.gov times out without blocking other sources | US-CPE-001 | Error Path | @skip |
| 19 | milestone-2 | SAM.gov failure prevents downstream API calls | US-CPE-001 | Error Path | @skip |
| 20 | milestone-2 | All three APIs fail and enrichment falls back to manual interview | US-CPE-001 | Error Path | @skip |
| 21 | milestone-2 | SBIR.gov returns multiple company matches requiring disambiguation | US-CPE-001 | Edge Case | @skip |
| 22 | milestone-2 | USASpending business types corroborate SAM.gov certifications | US-CPE-001 | Edge Case | @skip |
| 23 | milestone-2 | Enrichment result never contains fields without source attribution | US-CPE-001 | Property | @skip @property |
| 24 | milestone-3 | Founder confirms all enriched fields and they merge into the profile draft | US-CPE-002 | Happy Path | @skip |
| 25 | milestone-3 | Source attribution visible for every enriched field during review | US-CPE-002 | Happy Path | @skip |
| 26 | milestone-3 | Founder edits a NAICS code list to remove an irrelevant code | US-CPE-002 | Error Path | @skip |
| 27 | milestone-3 | Founder edits an enriched field value | US-CPE-002 | Error Path | @skip |
| 28 | milestone-3 | Founder skips a field to answer manually during the interview | US-CPE-002 | Error Path | @skip |
| 29 | milestone-3 | No enriched field enters the profile without explicit confirmation | US-CPE-002 | Error Path | @skip |
| 30 | milestone-3 | Past performance entries can be individually confirmed or removed | US-CPE-002 | Edge Case | @skip |
| 31 | milestone-3 | Interview only asks about fields not populated by enrichment | US-CPE-002 | Edge Case | @skip |
| 32 | milestone-3 | Confirmed enrichment data survives through preview and save | US-CPE-002 | Property | @skip @property |
| 33 | milestone-4 | Re-enrichment detects a new NAICS code added to SAM.gov | US-CPE-003 | Happy Path | @skip |
| 34 | milestone-4 | Re-enrichment detects a new SBIR award | US-CPE-003 | Happy Path | @skip |
| 35 | milestone-4 | Founder selects which changes to accept from the diff | US-CPE-003 | Happy Path | @skip |
| 36 | milestone-4 | Re-enrichment does not overwrite manually entered data | US-CPE-003 | Error Path | @skip |
| 37 | milestone-4 | Re-enrichment preserves user-entered fields not available from APIs | US-CPE-003 | Error Path | @skip |
| 38 | milestone-4 | Re-enrichment with SAM.gov failure falls back gracefully | US-CPE-003 | Error Path | @skip |
| 39 | milestone-4 | No changes detected during re-enrichment | US-CPE-003 | Edge Case | @skip |
| 40 | milestone-4 | Re-enrichment uses stored UEI without re-entry | US-CPE-003 | Edge Case | @skip |
| 41 | milestone-4 | Array reordering in API response is not treated as a change | US-CPE-003 | Edge Case | @skip |
| 42 | milestone-4 | Re-enrichment never modifies fields the user has not explicitly accepted | US-CPE-003 | Property | @skip @property |

## Coverage Analysis

### Story-to-Scenario Traceability

| Story | Scenarios | Happy | Error | Edge | Property |
|-------|-----------|-------|-------|------|----------|
| US-CPE-004 (API Key Setup) | 8 | 2 | 3 | 3 | 0 |
| US-CPE-001 (Enrichment Cascade) | 14 | 6 | 5 | 2 | 1 |
| US-CPE-002 (Review and Confirm) | 9 | 2 | 4 | 2 | 1 |
| US-CPE-003 (Re-Enrichment) | 11 | 4 | 3 | 3 | 1 |
| **Total** | **42** | **14** | **15** | **10** | **3** |

### Error Path Ratio

- Error + Edge + Property scenarios: 28 / 42 = 66.7%
- Error path only: 15 / 42 = 35.7%
- Including edge cases: 25 / 42 = 59.5%
- Target: >= 40% -- **PASSED**

### Scenario Type Breakdown

- Walking Skeletons: 3 (user-centric E2E integration)
- Focused Happy Path: 11
- Focused Error Path: 15
- Focused Edge Case: 10
- Property-Shaped: 3
- **Total: 42 scenarios**

## Implementation Sequence

One-at-a-time enablement order aligned to story delivery:

### Phase 1: Walking Skeletons (enabled first)
1. Founder enriches profile from UEI and receives data from three federal sources
2. Founder receives partial enrichment when one federal source is unavailable
3. Founder detects new SBIR award during profile update re-enrichment

### Phase 2: US-CPE-004 -- API Key Setup
4. Existing API key detected and reused
5. New API key validated and saved
6. Invalid API key rejected
7. Expired API key detected
8. Enrichment skipped
9. Malformed key file
10. Key never displayed in full
11. Key never passed as CLI arg

### Phase 3: US-CPE-001 -- Enrichment Cascade
12-23. SAM.gov entity data, SBIR.gov awards, USASpending totals, error paths, edge cases

### Phase 4: US-CPE-002 -- Review and Confirm
24-32. Confirm all, edit, skip, source attribution, past performance granularity

### Phase 5: US-CPE-003 -- Re-Enrichment
33-42. Diff detection, selective acceptance, manual data preservation, array comparison
