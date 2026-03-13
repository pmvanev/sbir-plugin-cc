<!-- markdownlint-disable MD024 -->

# Company Profile Builder -- User Stories

Scope: Complete company profile builder feature -- guided creation, document extraction, validation, and selective update.
All stories trace to JTBD analysis jobs in `jtbd-analysis.md` and journey steps in `journey-profile-builder.yaml`.

---

## US-CPB-001: Guided Company Profile Interview

### Problem

Rafael Medina is a technical founder at Radiant Defense Systems (23 employees) who pursues 3-5 SBIR proposals per year. He installed the SBIR proposal plugin and ran `/sbir:proposal new` to evaluate a solicitation, but the topic scout warned: "Company profile not found. Certifications and eligibility score 0.0." He finds it frustrating to figure out the JSON schema from documentation, hand-craft a nested JSON file with the correct field names, and hope the data types are right. Today he opens the schema in source code, copies it, and manually fills in values -- a 30-60 minute detour from evaluating solicitations.

### Who

- Small business technical founder | First-time plugin setup | Wants to get through administrative setup quickly to start scoring topics

### Solution

A conversational profile builder that asks plain-English questions section by section, explains why each field matters for fit scoring, and produces a validated `~/.sbir/company-profile.json` without the user touching JSON.

### Domain Examples

#### 1: Happy Path -- Rafael creates profile through interview

Rafael Medina runs `/sbir:proposal profile setup` and chooses "interview" mode. The builder asks for his company name ("Radiant Defense Systems, LLC"), core capabilities (he lists "directed energy, RF systems, power electronics, thermal management, embedded firmware"), SAM.gov details (active, CAGE 7X2K9, UEI DKJF84NXLE73), socioeconomic status (none), clearance level (Secret), ITAR (registered), employee count (23), two key personnel (himself as CEO/Chief Engineer and Dr. Lena Park as VP Engineering), two past performance entries (Air Force Phase I awarded, DARPA project completed), and one research partner (Georgia Tech Research Institute). The builder shows a preview, Rafael confirms, and the profile is saved in under 10 minutes.

#### 2: Edge Case -- Rafael has no SAM.gov registration

Rafael is setting up the profile for a brand-new company that has not yet completed SAM.gov registration. When the builder asks about SAM.gov, Rafael says "not yet." The builder records `sam_gov.active: false` and warns: "Without active SAM.gov registration, fit scoring will rate certifications as 0.0 and recommendations will be capped at no-go. Register at SAM.gov and run `/sbir:proposal profile update` when your registration is active."

#### 3: Error Path -- Rafael enters invalid CAGE code

Rafael enters CAGE code "7X2K" (4 characters instead of 5). During the preview step, validation catches the error: "CAGE code '7X2K' is 4 characters (expected 5 alphanumeric)." Rafael corrects it to "7X2K9" and validation passes.

### UAT Scenarios (BDD)

#### Scenario: Create profile through guided interview

Given Rafael Medina has no company profile at ~/.sbir/company-profile.json
And Rafael runs "/sbir:proposal profile setup"
And Rafael chooses "interview" mode
When the builder asks about company name
And Rafael responds "Radiant Defense Systems, LLC"
And the builder asks about capabilities
And Rafael responds "directed energy, RF systems, power electronics, thermal management, embedded firmware"
And the builder asks about SAM.gov registration
And Rafael responds "active, CAGE 7X2K9, UEI DKJF84NXLE73"
And the builder asks about remaining certification fields
And the builder asks about employee count, key personnel, past performance, and research partners
Then the builder displays a complete profile preview
And validation status shows "PASSED"
And Rafael confirms and the profile is saved to ~/.sbir/company-profile.json

#### Scenario: Interview explains why each field matters

Given Rafael is in interview mode
When the builder asks about capabilities
Then the builder explains "Capabilities are matched against solicitation keywords for subject matter expertise scoring (35% of fit score)"
And when the builder asks about SAM.gov
Then the builder explains "Active SAM.gov registration is required for all federal contracts. Without it, fit scoring rates certifications as 0.0"

#### Scenario: Handle missing SAM.gov registration

Given Rafael is creating a profile for a new company
When the builder asks about SAM.gov registration
And Rafael responds "not yet registered"
Then the builder records sam_gov.active as false
And the builder warns about the impact on fit scoring
And the builder suggests registering at SAM.gov and updating later

#### Scenario: Validation catches invalid CAGE code

Given Rafael has completed the interview
And Rafael entered CAGE code "7X2K" (4 characters)
When the builder validates the profile draft
Then validation reports "CAGE code '7X2K' is 4 characters (expected 5 alphanumeric)"
And Rafael is prompted to correct the value
And after correction to "7X2K9" validation passes

#### Scenario: Cancel interview without saving

Given Rafael is partway through the profile interview
When Rafael cancels the process
Then no file is written to ~/.sbir/company-profile.json
And the builder confirms no changes were made

### Acceptance Criteria

- [ ] Builder asks about each profile schema section in conversational English
- [ ] Builder explains the fit scoring impact of each field when asking
- [ ] Builder validates all fields before presenting preview (CAGE code format, clearance enum, employee count > 0)
- [ ] Builder shows complete preview and requires explicit confirmation before writing
- [ ] Profile saved as valid JSON matching the schema expected by sbir-topic-scout
- [ ] Cancel at any point results in no file written

### Technical Notes

- Profile written to `~/.sbir/company-profile.json` using atomic write pattern (write .tmp, backup .bak, rename)
- Schema must match what `sbir-topic-scout` reads in Phase 3 SCORE (defined in `skills/topic-scout/fit-scoring-methodology.md`)
- Builder runs as the `sbir-profile-builder` agent dispatched by the `/sbir:proposal profile setup` command
- Depends on: `~/.sbir/` directory existing or being creatable
- File permissions: profile contains sensitive data (CAGE code, UEI, clearance level, ITAR status). Set restrictive permissions on the file (e.g., 600 on Unix). The file should not be committed to version control -- add `~/.sbir/` to `.gitignore` patterns.

### Job Story Trace

- Job 1: Initial Profile Creation
- Opportunity Scores: #1 (18.1), #5 (14.5), #6 (13.2)

---

## US-CPB-002: Profile Preview and Validation Gate

### Problem

Rafael Medina is entering company data for his profile and worries about accuracy. He fat-fingered his CAGE code once before in a different tool and did not notice for weeks, causing incorrect eligibility assessments. He finds it risky to save profile data without reviewing it first, because errors in the profile propagate silently into fit scoring -- a wrong clearance level or missing capability keyword means the topic scout gives wrong recommendations.

### Who

- Small business technical founder | Completing profile setup | Needs confidence that the data is correct before it becomes the basis for scoring decisions

### Solution

A mandatory preview step that displays all profile fields in human-readable format with schema validation results, requiring explicit user confirmation before writing. Validation catches format errors (CAGE code length, clearance enum), completeness gaps (missing required fields), and logical errors (employee count = 0).

### Domain Examples

#### 1: Happy Path -- Clean validation and confirm

Rafael Medina finishes entering all profile data. The preview shows: company "Radiant Defense Systems, LLC", 23 employees, 5 capabilities, SAM.gov active with CAGE 7X2K9, Secret clearance, ITAR registered, 2 key personnel, 2 past performance entries, 1 research partner. Validation status: "PASSED (all required fields present)." Rafael says "yes" and the profile is saved.

#### 2: Edge Case -- Edit a field during preview

Rafael sees the preview and notices "thermal managment" (typo) in capabilities. He says "edit capabilities" and the builder presents the current list. He corrects the typo to "thermal management" and the preview updates.

#### 3: Error Path -- Multiple validation failures

Rafael's draft has CAGE code "7X2K" (4 chars), employee_count 0, and security_clearance "classified" (not a valid enum value). The preview shows 3 validation failures with specific messages for each. Rafael must fix all three before the save option becomes available.

### UAT Scenarios (BDD)

#### Scenario: Preview displays all fields with validation passed

Given Rafael has completed entering all profile data
And all fields pass schema validation
When the builder displays the profile preview
Then the preview shows company name "Radiant Defense Systems, LLC"
And the preview shows employee count 23
And the preview shows 5 capabilities
And the preview shows SAM.gov status, clearance, ITAR, key personnel, past performance, and research partners
And validation status shows "PASSED"
And Rafael can choose "yes" to save, "edit" to modify, or "cancel" to discard

#### Scenario: Preview shows validation failures blocking save

Given Rafael's profile draft has CAGE code "7X2K" and employee_count 0
When the builder displays the profile preview
Then validation status shows "2 issues found"
And the builder lists each issue with field name and expected format
And the "save" option is not available until issues are resolved

#### Scenario: Edit field during preview

Given the profile preview is displayed with validation passed
When Rafael says "edit capabilities"
Then the builder shows the current capabilities list
And Rafael can add, remove, or correct entries
And the preview refreshes with updated values and re-validates

### Acceptance Criteria

- [ ] Preview displays every profile field in human-readable format (not raw JSON)
- [ ] Validation checks: CAGE code is 5 alphanumeric characters, clearance is valid enum, employee count > 0, required fields present
- [ ] Validation failures show specific field name, current value, and expected format
- [ ] Save blocked when any validation failure exists
- [ ] Edit flow allows correcting individual fields without re-entering the entire profile
- [ ] Confirmation is explicit ("yes" / "edit" / "cancel") -- no auto-save

### Technical Notes

- Validation rules must match the schema constraints that sbir-topic-scout depends on
- Security clearance enum: "none", "confidential", "secret", "top_secret"
- Socioeconomic valid values: "8(a)", "HUBZone", "WOSB", "SDVOSB", "VOSB"
- Depends on: US-CPB-001 (interview produces the draft to validate)

### Job Story Trace

- Job 1: Initial Profile Creation (Confirm step)
- Opportunity Scores: #2 (15.5), #5 (14.5)

---

## US-CPB-003: Profile Creation from Documents

### Problem

Rafael Medina has a 4-page capability statement PDF that contains his company name, capabilities, certifications, key personnel, and past performance -- the same information the profile needs. He finds it tedious to manually transcribe data from his existing documents into a JSON file, especially when the information already exists in structured or semi-structured form. The transcription process takes 20+ minutes and introduces copy-paste errors.

### Who

- Small business technical founder | Has existing company documents (capability statement, SAM.gov profile) | Wants to leverage existing documents rather than re-entering data

### Solution

A document extraction capability that reads user-provided files (PDFs, text files) and URLs (SAM.gov entity pages), extracts profile-relevant fields, displays what was found and what is missing, and merges extracted data into the profile draft for the user to review and correct.

### Domain Examples

#### 1: Happy Path -- Extract from capability statement PDF

Rafael provides `./docs/radiant-cap-statement.pdf`. The builder extracts: company name "Radiant Defense Systems, LLC", 5 capabilities, employee count 23, 2 key personnel with names and expertise areas, 2 past performance entries with agency and topic. The builder reports 5 missing fields (SAM.gov details, socioeconomic, clearance, ITAR, research partners) and transitions to targeted interview for just those gaps.

#### 2: Edge Case -- Extract from SAM.gov URL

Rafael provides his SAM.gov entity page URL. The builder fetches the page and extracts: SAM.gov active, CAGE code 7X2K9, UEI DKJF84NXLE73, and socioeconomic certifications (none listed). Combined with the capability statement extraction, only clearance, ITAR, and research partners remain as gaps.

#### 3: Error Path -- Document has no extractable profile data

Rafael provides a technical white paper that contains no company profile information. The builder reports: "No profile fields found in this document. I looked for company name, capabilities, personnel, certifications, and past performance. Try a capability statement, SAM.gov profile, or company overview document instead."

### UAT Scenarios (BDD)

#### Scenario: Extract profile data from capability statement PDF

Given Rafael chose "documents first" approach
When Rafael provides path "./docs/radiant-cap-statement.pdf"
And the builder reads and analyzes the document
Then the builder extracts company name "Radiant Defense Systems, LLC"
And the builder extracts capabilities including "directed energy" and "RF systems"
And the builder extracts 2 key personnel with names and expertise
And the builder extracts 2 past performance entries with agency and outcome
And the builder lists 5 fields not found in the document

#### Scenario: Extract SAM.gov data from URL

Given Rafael provides a SAM.gov entity page URL
When the builder fetches and analyzes the page content
Then the builder extracts SAM.gov registration status as active
And the builder extracts CAGE code and UEI
And the builder extracts any listed socioeconomic certifications

#### Scenario: Multiple documents contribute to profile

Given Rafael provides a capability statement PDF
And then Rafael provides a SAM.gov entity page URL
When both documents are processed
Then the builder merges extracted data from both sources
And the builder shows the combined extraction result
And only fields not found in any document remain as interview gaps

#### Scenario: Document format not supported

Given Rafael provides a .docx file
When the builder attempts to read the file
Then the builder reports the format is not supported
And suggests: export to PDF, copy to text file, or skip to interview
And the profile draft is unchanged

#### Scenario: Partial extraction from poorly formatted document

Given Rafael provides a capability statement with unusual formatting
When the builder analyzes the document
And the builder extracts company name "Radiant Defense Systems, LLC" and employee count 23
But the builder cannot parse the capabilities section due to formatting
Then the builder shows which fields were extracted successfully
And the builder lists capabilities as "not extracted" alongside the other missing fields
And the interview step asks about capabilities along with other gaps

#### Scenario: No profile data found in document

Given Rafael provides a technical white paper with no company info
When the builder analyzes the document
Then the builder reports no profile fields were found
And lists what it searched for (company name, capabilities, personnel, etc.)
And suggests trying a different document type

### Acceptance Criteria

- [ ] Builder reads PDF and plain text files provided by the user
- [ ] Builder can fetch and parse web URLs (SAM.gov entity pages)
- [ ] Extraction displays each found field with its value for user verification
- [ ] Missing fields are explicitly listed to drive targeted interview
- [ ] Multiple documents can contribute to the same profile draft (additive)
- [ ] Unsupported formats produce clear error with alternatives
- [ ] Extracted data is treated as a draft -- user confirms before it enters the profile

### Technical Notes

- Document reading uses the agent's Read tool for local files and Bash (curl) for URLs
- Extraction is best-effort -- the agent interprets document content, not a structured parser
- User must confirm or correct every extracted field (extract-then-confirm pattern)
- Depends on: US-CPB-001 (setup flow), US-CPB-002 (preview validates the merged result)

### Job Story Trace

- Job 3: Profile Creation from Existing Documents
- Opportunity Scores: #3 (16.0), #1 (18.1)

---

## US-CPB-004: Selective Profile Section Update

### Problem

Rafael Medina's company won a Phase I award from NASA three months ago, but his company profile still shows no NASA past performance. The topic scout scored a NASA Phase II topic as "evaluate" instead of "go" because past_performance was 0.0 for NASA. He finds it annoying that updating one piece of data means re-running the entire profile setup or hand-editing JSON, so he keeps deferring the update. Today he opens the JSON in a text editor, carefully adds an entry to the past_performance array, and hopes he does not break the JSON syntax.

### Who

- Small business technical founder | Has an existing valid profile | Needs to update one section after a company change (new award, new hire, new certification)

### Solution

A targeted update command that lets the user select which profile section to modify, shows the current data for that section, accepts additions or changes, validates the updated profile, and saves -- all without touching unrelated sections.

### Domain Examples

#### 1: Happy Path -- Add NASA past performance

Rafael runs `/sbir:proposal profile update`, selects "past_performance", sees his 2 existing entries, adds a third: agency "NASA", topic_area "Lunar Surface Power Systems", outcome "awarded". The builder validates and saves. Total time: under 2 minutes.

#### 2: Edge Case -- Add new key personnel

Rafael's company hired Dr. James Chen as a signal processing specialist. Rafael runs `/sbir:proposal profile update`, selects "key_personnel", sees 2 existing entries, adds a third: name "Dr. James Chen", role "Senior RF Engineer", expertise ["signal processing", "antenna design"]. Existing personnel entries are unchanged.

#### 3: Error Path -- Update when no profile exists

Rafael runs `/sbir:proposal profile update` but has no existing profile. The builder responds: "No company profile found at ~/.sbir/company-profile.json. Run `/sbir:proposal profile setup` to create one first."

### UAT Scenarios (BDD)

#### Scenario: Add past performance entry to existing profile

Given Rafael has an existing company profile with 2 past performance entries
When Rafael runs "/sbir:proposal profile update"
And Rafael selects "past_performance" section
And the builder shows the 2 existing entries
And Rafael adds: agency "NASA", topic_area "Lunar Surface Power Systems", outcome "awarded"
Then the builder validates the updated profile
And the profile now has 3 past performance entries
And all other profile sections are unchanged

#### Scenario: Update preserves unmodified sections

Given Rafael has an existing profile with 5 capabilities and 2 key personnel
When Rafael updates the key_personnel section to add Dr. James Chen
Then the capabilities list still contains all 5 original entries
And the certifications, employee_count, and other sections are unchanged

#### Scenario: Update when no profile exists

Given no company profile exists at ~/.sbir/company-profile.json
When Rafael runs "/sbir:proposal profile update"
Then the builder reports "No company profile found"
And suggests running "/sbir:proposal profile setup" first

#### Scenario: Update SAM.gov certification after registration completes

Given Rafael has an existing profile with sam_gov.active set to false
When Rafael runs "/sbir:proposal profile update"
And selects "certifications"
And updates sam_gov.active to true with CAGE code "7X2K9" and UEI "DKJF84NXLE73"
Then the builder validates the CAGE code format
And saves the updated certifications
And notes that fit scoring will now include certification scores

### Acceptance Criteria

- [ ] Update command shows which sections can be modified
- [ ] Selected section displays current values before modification
- [ ] Additions to array fields (capabilities, key_personnel, past_performance) append without removing existing entries
- [ ] Modifications to scalar fields (employee_count, security_clearance) replace the value
- [ ] Unselected sections are untouched in the saved file
- [ ] Validation runs on the complete updated profile before saving
- [ ] Atomic write pattern used (same as initial save)

### Technical Notes

- Reads existing profile, applies modifications to the selected section, validates the merged result, writes back
- Same atomic write pattern as US-CPB-001 (write .tmp, backup .bak, rename)
- Must handle concurrent modification risk: read, modify, write as a single operation
- Depends on: US-CPB-001 (profile must exist), US-CPB-002 (validation logic reused)

### Job Story Trace

- Job 2: Profile Update After Company Change
- Opportunity Scores: #4 (13.0), #7 (12.6)

---

## US-CPB-005: Existing Profile Overwrite Protection

### Problem

Rafael Medina has spent 10 minutes building his company profile and saved it successfully. Two weeks later, a colleague who shares the machine runs `/sbir:proposal profile setup` not realizing a profile already exists. Without protection, the existing profile is silently overwritten and Rafael's data is lost. He finds it unacceptable that a setup command could destroy existing data without warning.

### Who

- Small business technical founder | Has an existing valid profile | Expects the system to protect existing data from accidental overwrite

### Solution

When the profile builder starts and detects an existing profile, it warns the user, shows the existing company name and last modified date, and offers three options: start fresh (with automatic backup), update the existing profile (redirect to update flow), or cancel.

### Domain Examples

#### 1: Happy Path -- Choose to start fresh with backup

Rafael runs `/sbir:proposal profile setup` and the builder finds an existing profile for "Radiant Defense Systems, LLC" last modified 2026-01-15. Rafael chooses "start fresh." The existing file is copied to `company-profile.json.bak`, and the builder proceeds with a clean setup.

#### 2: Edge Case -- Choose to update instead

Rafael runs `/sbir:proposal profile setup` and sees the existing profile warning. He realizes he just wanted to add a past performance entry. He chooses "update existing" and the builder redirects to the update flow (US-CPB-004).

#### 3: Error Path -- Backup fails due to permissions

Rafael chooses "start fresh" but the backup cannot be written due to file permissions. The builder refuses to proceed: "Cannot back up existing profile to company-profile.json.bak (permission denied). Resolve the permission issue or manually back up the file before proceeding."

### UAT Scenarios (BDD)

#### Scenario: Warn when existing profile detected

Given Rafael has an existing company profile at ~/.sbir/company-profile.json
And the profile contains company_name "Radiant Defense Systems, LLC"
And the file was last modified on 2026-01-15
When Rafael runs "/sbir:proposal profile setup"
Then the builder warns that an existing profile was found
And displays company name "Radiant Defense Systems, LLC" and date 2026-01-15
And offers: start fresh (with backup), update existing, or cancel

#### Scenario: Start fresh creates backup

Given Rafael has an existing profile and chose "start fresh"
When the builder proceeds
Then the existing profile is copied to ~/.sbir/company-profile.json.bak
And the builder confirms the backup was created
And the builder starts a clean profile setup

#### Scenario: Redirect to update flow

Given Rafael has an existing profile and chose "update existing"
When the builder processes the choice
Then the builder transitions to the update flow (same as /sbir:proposal profile update)

#### Scenario: Cancel preserves existing profile

Given Rafael has an existing profile and chose "cancel"
When the builder processes the choice
Then no files are modified
And the builder confirms the existing profile is unchanged

### Acceptance Criteria

- [ ] Builder detects existing profile before starting setup
- [ ] Warning displays company name and last modified date from existing profile
- [ ] "Start fresh" creates a .bak backup before proceeding
- [ ] "Update existing" redirects to the update flow
- [ ] "Cancel" makes no file changes
- [ ] Backup failure blocks the overwrite (no data loss)

### Technical Notes

- Existing profile detection: check if `~/.sbir/company-profile.json` exists and is valid JSON
- Backup uses the same atomic write pattern (copy to .bak before any modification)
- Last modified date from file system metadata
- Depends on: US-CPB-004 (update flow for redirect option)

### Job Story Trace

- Job 1: Initial Profile Creation (anxiety path -- fear of data loss)
- Cross-cutting: addresses the "anxiety" force from forces analysis

---

# Definition of Ready Validation

## US-CPB-001: Guided Company Profile Interview

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | Specific persona (Rafael Medina), concrete pain (30-60 min JSON detour), domain language (fit scoring, topic scout) |
| User/persona identified | PASS | Small business technical founder, first-time setup, 23-employee company |
| 3+ domain examples | PASS | 3 examples: happy path (full interview), edge case (no SAM.gov), error (invalid CAGE) |
| UAT scenarios (3-7) | PASS | 5 scenarios covering happy path, field explanations, missing SAM, validation error, cancel |
| AC derived from UAT | PASS | 6 AC items traced to scenario outcomes |
| Right-sized (1-3 days) | PASS | ~2 days effort, 5 scenarios, single demonstrable flow |
| Technical notes | PASS | Atomic write pattern, schema dependency, agent/command structure, directory dependency |
| Dependencies tracked | PASS | ~/.sbir/ directory, schema compatibility with sbir-topic-scout |

### DoR Status: PASSED

---

## US-CPB-002: Profile Preview and Validation Gate

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | Specific pain (fat-fingered CAGE code, wrong scoring for weeks), domain language |
| User/persona identified | PASS | Same persona completing setup, needs confidence in data accuracy |
| 3+ domain examples | PASS | 3 examples: clean validation, edit during preview, multiple validation failures |
| UAT scenarios (3-7) | PASS | 3 scenarios covering display, validation blocking, and edit flow |
| AC derived from UAT | PASS | 6 AC items covering display, validation rules, blocking, edit, confirmation |
| Right-sized (1-3 days) | PASS | ~1 day effort, 3 scenarios, tightly scoped |
| Technical notes | PASS | Validation rules specified, enum values listed, dependency on US-CPB-001 |
| Dependencies tracked | PASS | Depends on US-CPB-001 for draft input |

### DoR Status: PASSED

---

## US-CPB-003: Profile Creation from Documents

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | Specific pain (20+ min manual transcription, copy-paste errors), domain language |
| User/persona identified | PASS | Founder with existing capability statement PDF and SAM.gov profile |
| 3+ domain examples | PASS | 3 examples: PDF extraction, SAM.gov URL extraction, no-data document |
| UAT scenarios (3-7) | PASS | 5 scenarios covering PDF extraction, URL extraction, multi-document, unsupported format, no data |
| AC derived from UAT | PASS | 7 AC items covering file types, URLs, display, missing fields, multi-doc, errors, draft status |
| Right-sized (1-3 days) | PASS | ~3 days effort, 5 scenarios (extraction logic is the heaviest lift) |
| Technical notes | PASS | Read tool for files, curl for URLs, extract-then-confirm pattern, dependencies noted |
| Dependencies tracked | PASS | Depends on US-CPB-001 (setup flow) and US-CPB-002 (preview validates result) |

### DoR Status: PASSED

---

## US-CPB-004: Selective Profile Section Update

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | Specific pain (missed NASA Phase II opportunity due to stale profile), domain language |
| User/persona identified | PASS | Founder with existing profile, company change (new award, new hire) |
| 3+ domain examples | PASS | 3 examples: add past performance, add key personnel, no profile exists |
| UAT scenarios (3-7) | PASS | 4 scenarios covering add entry, preserve unmodified, no profile, update certification |
| AC derived from UAT | PASS | 7 AC items covering section selection, display, append, replace, preservation, validation, atomic write |
| Right-sized (1-3 days) | PASS | ~2 days effort, 4 scenarios |
| Technical notes | PASS | Atomic write, concurrent modification, dependencies on US-CPB-001 and US-CPB-002 |
| Dependencies tracked | PASS | Depends on US-CPB-001 (profile must exist) and US-CPB-002 (validation reused) |

### DoR Status: PASSED

---

## US-CPB-005: Existing Profile Overwrite Protection

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | Specific pain (colleague overwrites profile, data lost), domain language |
| User/persona identified | PASS | Founder with existing valid profile, accidental overwrite scenario |
| 3+ domain examples | PASS | 3 examples: start fresh with backup, redirect to update, backup fails |
| UAT scenarios (3-7) | PASS | 4 scenarios covering warning, backup, redirect, cancel |
| AC derived from UAT | PASS | 6 AC items covering detection, warning display, backup, redirect, cancel, backup failure |
| Right-sized (1-3 days) | PASS | ~1 day effort, 4 scenarios, tightly scoped |
| Technical notes | PASS | File existence check, atomic backup, file system metadata, dependency on US-CPB-004 |
| Dependencies tracked | PASS | Depends on US-CPB-004 (update flow for redirect) |

### DoR Status: PASSED
