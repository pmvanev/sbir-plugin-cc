# Walking Skeleton: Company Profile Enrichment

## Walking Skeletons (3 total)

### WS-1: Founder enriches profile from UEI and receives data from three federal sources

**User Goal**: Rafael provides his UEI and the system pulls data from SAM.gov, SBIR.gov, and USASpending.gov, returning enriched profile fields with source attribution.

**Why this is the skeleton**: This is the simplest complete user journey that delivers the primary value proposition -- "type UEI once, get profile data from three government databases." A non-technical stakeholder can confirm "yes, that is what users need."

**Layers touched**: UEI validation (domain) -> enrichment service (orchestration) -> three API adapters (driven ports) -> enrichment result assembly (domain)

**Stakeholder demo**: "Given a valid UEI and API key, the system returns legal name, CAGE code, NAICS codes, past performance, and federal award totals -- each tagged with its government source."

### WS-2: Founder receives partial enrichment when one federal source is unavailable

**User Goal**: When one API is down, Rafael still receives data from the APIs that responded. Unavailable fields are flagged for manual entry.

**Why this is the skeleton**: Partial failure is the most common real-world scenario with government APIs. If the system only works when all three APIs respond, it will frequently fail. This skeleton proves graceful degradation delivers usable data.

**Stakeholder demo**: "When SBIR.gov is unavailable, the system still returns SAM.gov entity data and USASpending award totals. SBIR.gov fields are marked for the interview step."

### WS-3: Founder detects new SBIR award during profile update re-enrichment

**User Goal**: Rafael runs re-enrichment on an existing profile and the system shows what changed since the last save -- a new Navy Phase I award appeared in SBIR.gov.

**Why this is the skeleton**: Re-enrichment is the update-flow analog of initial enrichment. Without it, profiles go stale. This skeleton proves the diff logic detects additions without treating existing entries as changed.

**Stakeholder demo**: "Given an existing profile with 2 awards, the system detects a new Navy Phase I from SBIR.gov and shows it as an addition. Existing entries are unchanged."

## Litmus Test Results

| Criterion | WS-1 | WS-2 | WS-3 |
|-----------|------|------|------|
| Title describes user goal (not technical flow) | Yes: "enriches profile from UEI" | Yes: "receives partial enrichment" | Yes: "detects new SBIR award" |
| Given/When describe user actions | Yes: "has API key", "requests enrichment" | Yes: same | Yes: "has existing profile", "requests re-enrichment" |
| Then describe user observations | Yes: "returns legal name", "shows source" | Yes: "returns fields", "marked unavailable" | Yes: "diff shows new entry" |
| Non-technical stakeholder can confirm value | Yes | Yes | Yes |

## Driving Ports Used

- **CompanyEnrichmentService.enrich_from_uei()** -- WS-1, WS-2
- **CompanyEnrichmentService.diff_against_profile()** -- WS-3
- **ApiKeyPort.read_key()** -- all three (precondition)

No internal components (adapters, domain objects, validators) are invoked directly by test code. All exercise happens through the service layer.
