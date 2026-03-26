<!-- markdownlint-disable MD024 -->

# Company Profile Enrichment -- User Stories

Scope: Automated profile enrichment from three federal APIs (SAM.gov, SBIR.gov, USASpending.gov) integrated into the existing company profile builder flow.
All stories trace to JTBD analysis jobs in `jtbd-analysis.md` and journey steps in `journey-enrichment.yaml`.

---

## US-CPE-001: Three-API Profile Enrichment from UEI

### Problem

Rafael Medina is a technical founder at Radiant Defense Systems (23 employees) who is creating his company profile with the profile builder (US-CPB-001). When the builder asks for his CAGE code, NAICS codes, socioeconomic certifications, and past performance, he has to minimize the terminal, open SAM.gov in a browser, log in, navigate to his entity page, and copy values one at a time. Then he opens SBIR.gov and searches for his company to find award history. This tab-switching and copy-pasting takes 15-20 minutes and he still misses a Navy Phase I award because it was listed under a slightly different company name variant. He finds it frustrating to retype data that already exists in government databases he registered with.

### Who

- Small business technical founder | Creating or updating company profile | Has active SAM.gov registration with UEI, has won prior SBIR awards | Wants authoritative data from government sources without manual transcription

### Solution

An enrichment step integrated into the profile builder that accepts the user's UEI, calls SAM.gov (legal name, CAGE, NAICS, certifications, registration status), SBIR.gov (award history, ownership flags), and USASpending.gov (federal award totals, business type corroboration), then presents the combined results with source attribution for user review before merging into the profile draft.

### Domain Examples

#### 1: Happy Path -- Rafael enriches profile from UEI

Rafael Medina runs `/sbir:proposal profile setup`, chooses "both" mode (documents + interview), and the builder detects a SAM.gov API key in `~/.sbir/api-keys.json`. Rafael enters UEI "DKJF84NXLE73". The system calls all three APIs in sequence. SAM.gov returns legal name "Radiant Defense Systems, LLC", CAGE "7X2K9", NAICS codes 334511/541715/334220, active registration expiring 2027-01-15, no socioeconomic certifications. SBIR.gov returns 3 awards: Air Force Phase I, DARPA completed, and a Navy Phase I Rafael had forgotten. USASpending returns $2.4M total federal awards across 5 transactions. The builder displays all results with source labels. Rafael is surprised to see the Navy award -- "I forgot about that subcontract!" He confirms all fields and the data merges into his profile draft. The interview then asks only about capabilities, security clearance, ITAR, employee count, key personnel, and research partners -- the fields no API could provide.

#### 2: Edge Case -- SBIR.gov returns multiple company matches

Rafael enters UEI "DKJF84NXLE73". SAM.gov returns his company data. But SBIR.gov, which searches by company name rather than UEI directly, returns 3 matches: "Radiant Defense Systems, LLC (Huntsville, AL) -- 3 awards", "Radiant Defense Technologies (San Diego, CA) -- 1 award", and "Radiant Defense Corp (Arlington, VA) -- 7 awards." The builder presents the list and Rafael selects his company (option 1). Only awards for his company are included in enrichment results.

#### 3: Error Path -- SAM.gov returns no entity for the UEI

Rafael enters UEI "XYZABC123456" (a typo -- transposed two characters). SAM.gov returns no entity. The builder reports: "No entity found in SAM.gov for UEI XYZABC123456. Check for transposed characters, or look up your UEI at sam.gov/search." Rafael re-enters the correct UEI and enrichment proceeds.

### UAT Scenarios (BDD)

#### Scenario: Full three-API enrichment from valid UEI

Given Rafael Medina has a SAM.gov API key in ~/.sbir/api-keys.json
And Rafael is in the profile builder setup flow
When Rafael enters UEI "DKJF84NXLE73"
Then the system calls SAM.gov Entity API and returns legal name, CAGE, NAICS, registration status, and certifications
And the system calls SBIR.gov Company API and returns 3 SBIR awards with agency, topic, and phase
And the system calls USASpending.gov and returns total federal award amount and business types
And the builder displays all results grouped by source
And each field shows which API it came from

#### Scenario: Enrichment results include forgotten SBIR award

Given Rafael's profile currently lists 2 past performance entries (Air Force, DARPA)
When enrichment queries SBIR.gov for "Radiant Defense Systems"
Then SBIR.gov returns 3 awards including a Navy Phase I not in Rafael's memory
And the builder highlights the Navy award as a new discovery

#### Scenario: SBIR.gov returns multiple company matches

Given SAM.gov resolved the company name as "Radiant Defense Systems, LLC"
When SBIR.gov returns 3 companies matching "Radiant Defense"
Then the builder displays all 3 with name, location, and award count
And Rafael selects his company from the list
And only awards for the selected company are included

#### Scenario: SAM.gov returns no entity for UEI

Given Rafael enters UEI "XYZABC123456"
When SAM.gov responds with no matching entity
Then the builder reports "No entity found in SAM.gov"
And suggests checking for transposed characters or looking up at sam.gov/search
And offers to re-enter UEI or skip enrichment

#### Scenario: One API fails but others succeed (partial enrichment)

Given SAM.gov returns entity data successfully
And SBIR.gov times out after 10 seconds
And USASpending returns recipient data successfully
When enrichment results are assembled
Then SAM.gov and USASpending fields are available for review
And SBIR.gov fields are listed as "unavailable"
And the user can continue with partial data or retry SBIR.gov

### Acceptance Criteria

- [ ] Enrichment accepts UEI as the single required input from the user
- [ ] SAM.gov Entity API called with UEI; returns legal name, CAGE, NAICS, registration status, certification flags
- [ ] SBIR.gov Company API called with resolved company name; returns award count and award details
- [ ] USASpending.gov called with company name; returns total federal awards and business types
- [ ] All enriched fields display source attribution (API name)
- [ ] Partial enrichment accepted when one or two APIs fail -- available data still usable
- [ ] Ambiguous SBIR.gov matches presented to user for selection
- [ ] No enriched data enters the profile without user confirmation (handled in US-CPE-002)

### Technical Notes

- Enrichment runs as a Python service in `scripts/pes/` following ports-and-adapters pattern
- Port: `EnrichmentPort` with method `enrich_from_uei(uei: str, api_key: str) -> EnrichmentResult`
- Three adapters: `SamGovAdapter`, `SbirGovAdapter`, `UsaSpendingAdapter`
- Composed in `CompanyEnrichmentService` with fallback logic: all three attempted, partial results accepted
- Agent invokes via Bash tool: `python scripts/pes/enrichment_cli.py --uei DKJF84NXLE73`
- API key read from `~/.sbir/api-keys.json` by the Python service, not passed as CLI argument
- SAM.gov rate limit: 1,000 requests/day (personal key with entity role) -- no concern for onboarding use
- SBIR.gov: no auth required, no documented rate limit, "maintenance" notice on docs page -- implement timeout and retry
- USASpending: no auth required, no documented rate limit
- Depends on: US-CPE-004 (API key must be set up), existing profile builder agent flow

### Job Story Trace

- Job 4: Automated Profile Enrichment from Federal APIs
- Opportunity Scores: #1 (17.6), #3 (14.8)

---

## US-CPE-002: Enrichment Review and Confirm

### Problem

Rafael Medina is reviewing data that the enrichment service pulled from federal APIs. He trusts SAM.gov for his registration data but is unsure whether SBIR.gov's award list is complete -- he thinks there might be a subcontract that is not listed. He also knows his SAM.gov NAICS codes include 334220 but he has never actually bid on a topic in that code. He finds it risky to accept API data without reviewing it because stale or incorrect data in his profile will propagate into fit scoring and produce wrong recommendations.

### Who

- Small business technical founder | Reviewing enrichment results | Needs to verify each field before it becomes the basis for scoring | Wants transparency about where each value came from

### Solution

A field-by-field review step where each enriched value is displayed with its API source. The user can confirm, edit, or skip each field. Confirmed fields merge into the profile draft. Edited fields use the user's value with source noted as "user override." Skipped fields become interview questions.

### Domain Examples

#### 1: Happy Path -- Rafael confirms all fields

Rafael reviews enrichment results: legal name from SAM.gov, CAGE from SAM.gov, 3 NAICS codes from SAM.gov, registration active from SAM.gov, no socioeconomic certs from SAM.gov, 3 past performance entries from SBIR.gov. He confirms each field. The profile draft is populated with all confirmed values and source metadata is preserved.

#### 2: Edge Case -- Rafael edits an enriched field

Rafael sees NAICS codes 334511, 541715, 334220 from SAM.gov. He knows 334220 (communications equipment) is listed on his SAM.gov registration but does not represent a core capability. He edits the NAICS list to remove 334220, keeping only 334511 and 541715. The source for NAICS is recorded as "user (overriding SAM.gov)."

#### 3: Error Path -- Rafael skips socioeconomic certifications to enter manually

SAM.gov returned no socioeconomic certifications, but Rafael's 8(a) application was just approved last week and SAM.gov has not been updated yet. He skips the enriched value and plans to enter "8(a)" manually during the interview step.

### UAT Scenarios (BDD)

#### Scenario: User confirms all enriched fields

Given enrichment returned legal_name "Radiant Defense Systems, LLC", cage_code "7X2K9", naics_codes [334511, 541715, 334220], registration_status "Active", and 3 past_performance entries
When Rafael reviews each field with its source attribution
And Rafael confirms all fields
Then all confirmed values merge into the profile draft
And each field retains its API source in metadata

#### Scenario: User edits an enriched NAICS list

Given enrichment returned naics_codes [334511, 541715, 334220] from SAM.gov
When Rafael removes 334220 from the list during review
Then the profile draft contains naics_codes [334511, 541715]
And the source is recorded as "user (overriding SAM.gov)"

#### Scenario: User skips a field to answer manually

Given enrichment returned socioeconomic_certifications as empty from SAM.gov
And Rafael's 8(a) certification was approved after the last SAM.gov update
When Rafael chooses "enter manually" for socioeconomic certifications
Then the field is left empty in the enrichment result
And socioeconomic_certifications appears in the missing fields list for the interview step

#### Scenario: Source attribution visible for every field

Given enrichment returned fields from SAM.gov, SBIR.gov, and USASpending
When the review screen displays each field
Then SAM.gov fields show "Source: SAM.gov"
And SBIR.gov fields show "Source: SBIR.gov"
And USASpending fields show "Source: USASpending.gov"

#### Scenario: No enriched field enters profile without confirmation

Given enrichment returned 8 fields from 3 APIs
When the review step completes
Then only fields with explicit "confirm" or "edit" status are in the profile draft
And fields with "skip" status are not in the profile draft

### Acceptance Criteria

- [ ] Every enriched field displayed with its API source name
- [ ] User can confirm, edit, or skip each field independently
- [ ] Confirmed fields merge into profile draft with source metadata
- [ ] Edited fields use user's value with source "user (overriding {api_name})"
- [ ] Skipped fields added to missing_fields_list for interview fallback
- [ ] No enriched data enters the profile draft without explicit user action
- [ ] Past performance entries can be individually confirmed, edited, added to, or removed

### Technical Notes

- Review is conversational (agent-driven), not a separate UI component
- Source metadata stored in profile's `sources.web_references` array with API URL and access timestamp
- Depends on: US-CPE-001 (enrichment must produce results to review)
- This step replaces no existing functionality -- it inserts between enrichment and the existing interview

### Job Story Trace

- Job 4: Automated Profile Enrichment (Confirm step)
- Opportunity Scores: #2 (16.2), #4 (16.0)

---

## US-CPE-003: Re-Enrichment During Profile Update

### Problem

Rafael Medina's SAM.gov registration renewed 2 months ago with an updated NAICS code list (he added 541715 for R&D in physical sciences). He also won a Phase I from Navy last quarter. His profile still has the old NAICS codes and only 2 past performance entries. The topic scout is not matching him to Navy-relevant topics because his profile is stale. He finds it tedious to manually check three government websites for changes and update his profile field by field.

### Who

- Small business technical founder | Has an existing valid profile | SAM.gov registration renewed or new SBIR award received | Wants to detect what changed without manually checking government sites

### Solution

A re-enrichment option during profile update that calls the same three APIs, compares results against the current profile, and shows a diff of changes. The user selects which changes to accept. Existing user-entered data (capabilities, key personnel, etc.) is never modified by re-enrichment.

### Domain Examples

#### 1: Happy Path -- Re-enrichment detects new NAICS code and new award

Rafael runs `/sbir:proposal profile update` and selects "re-enrich from APIs." The system calls all three APIs using his stored UEI. SAM.gov now returns NAICS codes [334511, 541715, 334220] -- his profile had [334511, 541715]. SBIR.gov returns 3 awards -- his profile had 2. The diff shows: "1 new NAICS code: 334220" and "1 new award: Navy Shipboard Power Conditioning Phase I." Rafael accepts both changes. His capabilities list (entered manually) is untouched.

#### 2: Edge Case -- No changes detected

Rafael runs re-enrichment but all API data matches his current profile. The system reports: "No differences found between your profile and federal databases. Your profile is current." No changes are made.

#### 3: Error Path -- Re-enrichment would overwrite manual edits

Rafael manually set his socioeconomic certifications to ["8(a)"] in a previous update (his SAM.gov registration had not yet reflected the approval). Re-enrichment from SAM.gov still shows no certifications. The diff shows: "Socioeconomic certifications -- current: [8(a)], SAM.gov: (none)." Rafael chooses "keep current" to preserve his manual entry.

### UAT Scenarios (BDD)

#### Scenario: Re-enrichment detects new NAICS code

Given Rafael has an existing profile with naics_codes [334511, 541715]
And Rafael runs profile update with re-enrichment
When SAM.gov returns naics_codes [334511, 541715, 334220]
Then the diff shows "1 new NAICS code: 334220"
And Rafael can choose to add it
And existing NAICS codes are not removed

#### Scenario: Re-enrichment detects new SBIR award

Given Rafael has an existing profile with 2 past_performance entries
And Rafael runs profile update with re-enrichment
When SBIR.gov returns 3 awards (1 new: Navy Shipboard Power Conditioning)
Then the diff shows "1 new award found"
And Rafael can choose to add the new award
And existing past_performance entries are unchanged

#### Scenario: No changes detected during re-enrichment

Given Rafael has an existing profile matching current API data
When re-enrichment runs and compares results
Then the system reports "No differences found"
And no changes are made to the profile

#### Scenario: Re-enrichment preserves user-entered data not in APIs

Given Rafael manually entered socioeconomic certifications as ["8(a)"]
And SAM.gov still shows no socioeconomic certifications
When re-enrichment shows the diff
Then Rafael chooses "keep current" for socioeconomic certifications
And the manual entry ["8(a)"] is preserved

#### Scenario: User selects which changes to accept from diff

Given re-enrichment found 2 changes (new NAICS code and new award)
When Rafael accepts the new NAICS code but declines the new award
Then only the NAICS code change is applied to the profile
And the declined award is not added

### Acceptance Criteria

- [ ] Re-enrichment available as an option during profile update flow
- [ ] Uses stored UEI and API key -- no re-entry required
- [ ] Compares API results against current profile field by field
- [ ] Diff displayed showing additions, changes, and matches
- [ ] User selects which changes to accept (per-field granularity)
- [ ] User-entered data not available from APIs is never modified
- [ ] "No changes" result clearly communicated

### Technical Notes

- Reuses the same Python enrichment service and adapters from US-CPE-001
- Diff logic compares enrichment result against current profile JSON
- Must handle array comparison (NAICS codes, past performance) -- detect additions without treating reordering as a change
- Depends on: US-CPE-001 (enrichment service), US-CPE-004 (API key), US-CPB-004 (profile update flow)

### Job Story Trace

- Job 5: Enrichment During Profile Update
- Opportunity Scores: #6 (14.0), #3 (14.8)

---

## US-CPE-004: SAM.gov API Key Setup and Validation

### Problem

Rafael Medina wants to use profile enrichment but the system requires a SAM.gov API key. He does not know where to get one or whether it costs money. He finds it confusing when tools require API keys without clear instructions, especially government APIs where the documentation is spread across multiple sites. If the setup takes more than 2 minutes, he will skip enrichment and type the data manually.

### Who

- Small business technical founder | First time using enrichment | Has a SAM.gov account (required for SBIR) but has never generated an API key | Needs friction-free setup in under 2 minutes

### Solution

A guided API key setup that detects whether a key exists, explains how to obtain one (with the exact URL), validates the key with a live test call, stores it securely in `~/.sbir/api-keys.json` with restricted permissions, and confirms it is ready. The setup runs once; the key is reused in all future enrichment sessions.

### Domain Examples

#### 1: Happy Path -- Rafael sets up API key in 90 seconds

Rafael starts profile setup, the builder offers enrichment, and no API key is found. The builder displays: "To get a free SAM.gov API key, log in to SAM.gov, go to sam.gov/profile/details, click Generate under Public API Key, and paste it here." Rafael opens the link, generates the key, pastes it. The system validates it with a test call (HTTP 200), saves it to `~/.sbir/api-keys.json` with 600 permissions, and confirms: "Key saved. You won't need to enter this again."

#### 2: Edge Case -- Rafael already has a key from a previous session

Rafael starts a new profile setup. The builder checks `~/.sbir/api-keys.json`, finds a valid key (ending in "...x7Kf"), and reports: "SAM.gov API key found." No setup needed. Rafael proceeds directly to entering his UEI.

#### 3: Error Path -- Rafael pastes an invalid key

Rafael pastes an expired or mistyped API key. The system tests it against SAM.gov and gets HTTP 403. The builder reports: "API key validation failed (403 Forbidden). This can happen if the key was mistyped or expired." Options: re-enter key, generate a new one at sam.gov/profile/details, or skip enrichment.

### UAT Scenarios (BDD)

#### Scenario: First-time API key setup with valid key

Given no SAM.gov API key exists in ~/.sbir/api-keys.json
When the profile builder offers enrichment
And Rafael enters his SAM.gov API key "abc123def456ghi789jkl012"
And the system validates the key against SAM.gov (HTTP 200)
Then the key is saved to ~/.sbir/api-keys.json
And file permissions are set to owner-read-write only
And the system confirms "Key saved. You won't need to enter this again"
And Rafael is prompted for his UEI

#### Scenario: Existing API key reused

Given Rafael has a SAM.gov API key stored in ~/.sbir/api-keys.json from a previous session
When the profile builder offers enrichment
Then the system reports "SAM.gov API key found" with last 4 characters shown
And does not prompt for a new key
And proceeds to UEI input

#### Scenario: Invalid API key rejected with guidance

Given Rafael enters an invalid SAM.gov API key
When the system validates the key and SAM.gov returns HTTP 403
Then the system reports "API key validation failed"
And explains possible causes (mistyped, expired, revoked)
And offers: re-enter key, generate new at sam.gov/profile/details, or skip enrichment

#### Scenario: User skips API key setup

Given no SAM.gov API key exists
When Rafael chooses to skip enrichment
Then no API key file is created
And the profile builder continues with the manual interview flow
And SBIR.gov and USASpending data is not available (they depend on SAM.gov resolving the company name first)

### Acceptance Criteria

- [ ] System checks for existing key at `~/.sbir/api-keys.json` before prompting
- [ ] Setup instructions include the exact URL: `https://sam.gov/profile/details`
- [ ] Key validated with a live test call to SAM.gov before saving
- [ ] Invalid key produces clear error with specific remediation steps
- [ ] Key stored in `~/.sbir/api-keys.json` with owner-only file permissions
- [ ] Key never displayed in full after entry (show last 4 characters only)
- [ ] Key never passed as a command-line argument
- [ ] Skip option available -- enrichment is optional, not mandatory

### Technical Notes

- Key storage file `~/.sbir/api-keys.json` is separate from `~/.sbir/company-profile.json` for security hygiene
- File schema: `{"sam_gov_api_key": "..."}` -- extensible for future API keys
- Validation test call: `GET https://api.sam.gov/entity-information/v3/entities?ueiSAM=TEST&api_key={KEY}` -- any response other than 403/401 confirms the key is valid
- File permissions: `chmod 600` on Unix; on Windows, rely on user directory ACLs
- Depends on: `~/.sbir/` directory existing (created during first-time setup)
- No dependency on other CPE stories -- this is an enabler

### Job Story Trace

- Job 6: SAM.gov API Key Setup
- Opportunity Scores: #5 (13.3)

---

# Definition of Ready Validation

## US-CPE-001: Three-API Profile Enrichment from UEI

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | Specific persona (Rafael Medina), concrete pain (15-20 min tab-switching, missed Navy award), domain language (fit scoring, UEI, CAGE, NAICS) |
| User/persona identified | PASS | Small business technical founder, 23 employees, active SAM.gov registration, 2+ prior SBIR awards |
| 3+ domain examples | PASS | 3 examples: full enrichment, ambiguous SBIR.gov match, SAM.gov entity not found |
| UAT scenarios (3-7) | PASS | 5 scenarios: full enrichment, forgotten award, multiple matches, entity not found, partial failure |
| AC derived from UAT | PASS | 8 AC items covering UEI input, three API calls, source attribution, partial results, disambiguation, confirmation gate |
| Right-sized (1-3 days) | PASS | ~3 days effort (Python adapters + service + CLI entry point), 5 scenarios |
| Technical notes | PASS | Ports-and-adapters pattern, three adapters, CLI invocation, rate limits, API auth requirements, dependencies |
| Dependencies tracked | PASS | Depends on US-CPE-004 (API key), existing profile builder agent flow, Python service infrastructure |

### DoR Status: PASSED

---

## US-CPE-002: Enrichment Review and Confirm

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | Specific pain (stale NAICS in SAM.gov, risk of incorrect data in fit scoring), domain language (source attribution, fit scoring) |
| User/persona identified | PASS | Same persona reviewing enrichment results, needs confidence and transparency |
| 3+ domain examples | PASS | 3 examples: confirm all, edit NAICS list, skip socioeconomic to enter manually |
| UAT scenarios (3-7) | PASS | 5 scenarios: confirm all, edit field, skip field, source attribution display, no-confirm-no-merge gate |
| AC derived from UAT | PASS | 7 AC items covering display, confirm/edit/skip, source metadata, no-auto-merge gate, past performance granularity |
| Right-sized (1-3 days) | PASS | ~1 day effort (conversational review logic in agent), 5 scenarios |
| Technical notes | PASS | Conversational review, source metadata persistence, dependency on US-CPE-001 |
| Dependencies tracked | PASS | Depends on US-CPE-001 (enrichment results) |

### DoR Status: PASSED

---

## US-CPE-003: Re-Enrichment During Profile Update

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | Specific pain (stale NAICS after SAM.gov renewal, missed Navy award, manual checking of 3 sites), domain language |
| User/persona identified | PASS | Founder with existing profile, company change (renewed registration, new award) |
| 3+ domain examples | PASS | 3 examples: detect new NAICS+award, no changes, re-enrichment would overwrite manual edit |
| UAT scenarios (3-7) | PASS | 5 scenarios: new NAICS, new award, no changes, preserve manual data, selective acceptance |
| AC derived from UAT | PASS | 7 AC items covering re-enrichment option, stored credentials, diff display, per-field acceptance, manual data protection, no-change reporting |
| Right-sized (1-3 days) | PASS | ~2 days effort (diff logic + update flow integration), 5 scenarios |
| Technical notes | PASS | Reuses enrichment service, diff logic, array comparison semantics, dependencies |
| Dependencies tracked | PASS | Depends on US-CPE-001, US-CPE-004, US-CPB-004 (profile update flow) |

### DoR Status: PASSED

---

## US-CPE-004: SAM.gov API Key Setup and Validation

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | Specific pain (doesn't know where to get API key, confusion about cost, 2-minute patience threshold), domain language |
| User/persona identified | PASS | First-time enrichment user, has SAM.gov account but no API key, low tolerance for setup friction |
| 3+ domain examples | PASS | 3 examples: first-time setup in 90 seconds, key reused from previous session, invalid key rejected |
| UAT scenarios (3-7) | PASS | 4 scenarios: first-time valid key, existing key reused, invalid key rejected, skip enrichment |
| AC derived from UAT | PASS | 8 AC items covering key detection, setup instructions, validation, error handling, secure storage, masking, no-CLI-arg, skip option |
| Right-sized (1-3 days) | PASS | ~1 day effort (key storage + validation logic), 4 scenarios |
| Technical notes | PASS | Separate file, validation test call, file permissions, extensible schema, directory dependency |
| Dependencies tracked | PASS | Depends on ~/.sbir/ directory (created during first-time setup). No dependency on other CPE stories. |

### DoR Status: PASSED
