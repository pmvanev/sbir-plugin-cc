<!-- markdownlint-disable MD024 -->

# User Stories: Solicitation Finder

Scope: Automated discovery and scoring of SBIR/STTR solicitation topics against company profile.
All stories trace to JTBD analysis (Job Stories 1-4) and opportunity scores (O1-O5).

---

## US-SF-001: Fetch Open Topics from DSIP API

### Problem

Phil Santos is a solo SBIR proposal writer at Radiant Defense Systems, LLC who writes 2-5 proposals per year. He finds it exhausting to manually browse 300-500 topics on dodsbirsttr.mil every solicitation cycle, spending 2-6 hours scrolling through pages of results. Today he opens the Topics App in his browser, applies basic filters, and reads each title one by one.

### Who

- Solo proposal writer | New solicitation cycle just opened | Wants to get all open topics into a scoreable format without manual browsing

### Solution

A Python script that fetches open topic listings from the DSIP public API (`/topics/api/public/topics/search`), with optional filters for agency, phase, and solicitation cycle. Falls back to prompting the user for a BAA PDF when the API is unavailable.

### Domain Examples

#### 1: Happy Path -- Phil fetches all open DoD topics

Phil Santos runs `/sbir:solicitation find` at the start of the DOD_SBIR_2026_P1_C3 cycle. The script hits the DSIP API and retrieves 347 open topics across all agencies (Army, Navy, Air Force, DARPA, MDA, DTRA, CBD, OSD). The tool displays "347 topics retrieved" with a progress bar. Phil sees his company name "Radiant Defense Systems, LLC" confirming the correct profile is loaded.

#### 2: Edge Case -- Phil filters by agency and phase

Phil runs `/sbir:solicitation find --agency "Air Force" --phase I` because he only wants to pursue Air Force Phase I topics this cycle. The script fetches 89 matching topics instead of 347. The active filters are displayed: "agency=Air Force, phase=I".

#### 3: Error Path -- API unavailable, fallback to BAA PDF

Phil runs `/sbir:solicitation find` but the DSIP API times out (server maintenance). The tool displays "DSIP API unavailable (connection timeout)" and suggests providing a BAA PDF: `/sbir:solicitation find --file ./solicitations/baa-2026-3.pdf`. Phil downloads the BAA from dodsbirsttr.mil and re-runs with the file. The tool extracts 47 topics from the PDF and proceeds.

### UAT Scenarios (BDD)

#### Scenario: Fetch all open topics from DSIP API

Given Phil Santos has a company profile at ~/.sbir/company-profile.json for "Radiant Defense Systems, LLC"
And the DSIP API has 347 open topics for the current cycle
When Phil runs "/sbir:solicitation find"
Then the tool displays "Radiant Defense Systems, LLC" as the company name
And the tool displays a progress indicator during fetching
And the tool displays "347 topics retrieved"

#### Scenario: Fetch with agency and phase filters

Given Phil Santos has a company profile
And the DSIP API has 89 open Air Force Phase I topics
When Phil runs "/sbir:solicitation find --agency 'Air Force' --phase I"
Then the tool displays "89 topics retrieved (filtered)"
And the tool displays "agency=Air Force, phase=I" as active filters

#### Scenario: API unavailable triggers fallback guidance

Given the DSIP API is unreachable (connection timeout)
When Phil runs "/sbir:solicitation find"
Then the tool displays "DSIP API unavailable"
And the tool suggests the --file flag with a BAA PDF
And the tool displays the download URL for dodsbirsttr.mil

#### Scenario: Fall back to BAA PDF

Given the DSIP API is unreachable
And Phil has a BAA PDF at ./solicitations/baa-2026-3.pdf containing 47 topics
When Phil runs "/sbir:solicitation find --file ./solicitations/baa-2026-3.pdf"
Then the tool extracts 47 topics from the PDF
And the tool displays "Source: BAA PDF (47 topics extracted)"

#### Scenario: API rate limiting with partial results

Given the DSIP API returns 200 topics then rate-limits further requests
When Phil runs "/sbir:solicitation find"
Then the tool displays "DSIP API rate limit reached after 200 topics"
And the tool offers to score partial results or retry or use --file fallback

### Acceptance Criteria

- [ ] Tool fetches open topic listings from DSIP API without authentication
- [ ] Tool accepts --agency, --phase, and --solicitation filter flags
- [ ] Tool displays company name from profile and topic count after fetch
- [ ] Tool displays progress indication during API fetch
- [ ] Tool falls back to BAA PDF when API is unavailable, with clear guidance
- [ ] Tool handles API rate limiting gracefully with options for the user

### Technical Notes

- DSIP API endpoint: `GET /topics/api/public/topics/search` (public, unauthenticated)
- Query parameters: `topicStatus`, `numPerPage`, `baa` (solicitation filter)
- Individual topic PDFs: `GET /topics/api/public/topics/{hash_id}/download/PDF`
- API returns metadata only (no full descriptions) -- PDFs needed for enrichment
- Depends on: company profile (existing `ProfilePort` / `JsonProfileAdapter`)
- Rate limiting: batch requests with small delays (1-2 seconds between pages)

---

## US-SF-002: Score and Rank Topics Against Company Profile

### Problem

Phil Santos has 347 open topics but no systematic way to assess which ones fit his company. He finds it impossible to mentally cross-reference each topic against his capabilities, certifications, clearance level, past performance, and personnel expertise. Today he reads each title and skims descriptions, relying on gut feel and memory to assess fit, missing topics that use different terminology for the same technical domain.

### Who

- Solo proposal writer | Has a list of open topics | Wants quantitative fit scoring so he can focus on the highest-probability topics

### Solution

A two-pass matching pipeline: keyword pre-filter reduces 300-500 topics to 20-50 candidates, then LLM semantic scoring using the existing five-dimension fit model (SME, PP, Cert, Elig, STTR) produces a ranked shortlist with GO/EVALUATE/NO-GO recommendations.

### Domain Examples

#### 1: Happy Path -- 347 topics scored down to 5 GO recommendations

Phil runs the finder against 347 topics. Keyword pre-filter eliminates 305 obviously irrelevant topics (biodefense, social science, medical). The remaining 42 candidates are scored. Topic AF263-042 ("Compact Directed Energy for C-UAS") scores 0.82 composite -- SME 0.95 (core competency), PP 0.80 (prior Air Force Phase I win in DE), Cert 1.00 (SAM active, Secret clearance sufficient), Elig 1.00 (Phase I, 15 employees), STTR 1.00 (SBIR topic). Recommendation: GO. Three topics are disqualified: AF263-099 requires TS clearance, N263-S05 is STTR with no institution partner, A263-200 has zero SME match.

#### 2: Edge Case -- Terminology mismatch caught by semantic matching

Topic N263-018 ("Shipboard RF Power Management") does not contain the keyword "directed energy" but the LLM recognizes that RF power systems are a core capability listed in Phil's profile (Marcus Chen's expertise). The semantic matcher scores SME at 0.70 despite no keyword overlap. Without semantic matching, this topic would have been missed.

#### 3: Error Path -- Sparse company profile degrades scoring

Phil's company profile has only 3 capability keywords and no past_performance entries. The tool warns "Profile incomplete: past_performance empty (scoring accuracy degraded)." Past performance scores 0.0 for all topics, but recommendations cap at EVALUATE rather than NO-GO (absence of data is not disqualifying). The tool suggests enriching the profile for better results.

### UAT Scenarios (BDD)

#### Scenario: Keyword pre-filter reduces candidate set

Given the DSIP API returned 347 open topics
And the company profile has capabilities "directed energy", "RF power systems", "thermal management"
When the keyword pre-filter runs
Then 42 candidate topics are identified
And 305 topics are eliminated
And progress shows "Keyword match: 42 candidate topics (305 eliminated)"

#### Scenario: Five-dimension scoring produces ranked results

Given 42 candidate topics have been enriched with full descriptions
And the company profile has capabilities, certifications (SAM active, Secret clearance), 15 employees, and past performance (Air Force Phase I in directed energy)
When the LLM scores each candidate
Then topic AF263-042 scores composite 0.82 with recommendation GO
And topic N263-044 scores composite 0.34 with recommendation EVALUATE
And topics are ranked by composite score descending

#### Scenario: Disqualifiers produce NO-GO recommendations

Given topic AF263-099 requires TS clearance
And the company profile has security_clearance "secret"
When the topic is scored
Then AF263-099 receives recommendation NO-GO
And the disqualification reason is "Requires TS clearance (profile: Secret)"

#### Scenario: STTR topic without research institution partner

Given topic N263-S05 is an STTR solicitation
And the company profile has no research_institution_partners
When the topic is scored
Then N263-S05 receives recommendation NO-GO
And the disqualification reason is "No research institution partner"

#### Scenario: Incomplete profile degrades scoring with warning

Given the company profile has no past_performance entries
When scoring runs
Then past_performance dimension scores 0.0 for all topics
And recommendations cap at EVALUATE (not NO-GO from data absence)
And the tool warns "Profile incomplete: past_performance empty"

#### Scenario: Zero candidates after pre-filter

Given no topics match company capability keywords
When the pre-filter completes
Then zero candidates are identified
And the tool displays "No topics matched your company profile"
And the tool suggests reviewing the profile or broadening filters

### Acceptance Criteria

- [ ] Keyword pre-filter reduces topic set before LLM scoring
- [ ] Each scored topic receives five-dimension breakdown (SME, PP, Cert, Elig, STTR)
- [ ] Composite score is weighted average per fit-scoring-methodology
- [ ] Topics ranked by composite score descending, then deadline ascending
- [ ] Recommendations follow threshold rules: GO >= 0.6, EVALUATE 0.3-0.6, NO-GO < 0.3 or hard disqualifier
- [ ] Disqualified topics shown separately with explicit reasons
- [ ] Incomplete profile triggers warning and degrades gracefully (no false NO-GO from data absence)
- [ ] Progress indication during scoring ("Scoring topic 18 of 42...")
- [ ] End-to-end scoring completes within 10 minutes for 50 candidate topics

### Technical Notes

- Reuse fit-scoring-methodology five-dimension model and weights (SME 0.35, PP 0.25, Cert 0.15, Elig 0.15, STTR 0.10)
- Two-pass: keyword pre-filter (Python, fast) then LLM semantic scoring (Claude, 1500-2500 tokens per topic)
- Batch topics in groups of 10-20 for LLM scoring to manage context
- Token budget: ~100-200K tokens per full run (50 candidates)
- Depends on: US-SF-001 (topic fetching), company profile, fit-scoring-methodology skill

---

## US-SF-003: Review Results and Drill Into Topic Details

### Problem

Phil Santos has a ranked shortlist of topics but needs to understand WHY each topic scored the way it did before making a Go/No-Go decision. A bare score number is not enough -- he needs to see which dimensions are strong, which are weak, and which personnel would lead the effort. Today he makes these assessments mentally with no structured breakdown.

### Who

- Solo proposal writer | Has a scored shortlist | Wants transparent scoring breakdown to make an informed pursuit decision

### Solution

A ranked results table with summary view (rank, ID, agency, title, score, recommendation, deadline) and a detail drilldown command (`details <topic-id>`) showing the full five-dimension breakdown, rationale, and key personnel match.

### Domain Examples

#### 1: Happy Path -- Phil reviews ranked table and drills into top topic

Phil sees the ranked table with 5 GO topics and 3 disqualified topics. He types `details AF263-042` and sees: SME 0.95 (core competency in directed energy), PP 0.80 (prior Air Force Phase I win), Cert 1.00, Elig 1.00, STTR 1.00. Key personnel: Dr. Elena Vasquez (directed energy, laser physics), Marcus Chen (RF power, thermal management). He feels confident this is a strong fit.

#### 2: Edge Case -- Phil reviews a disqualified topic to understand why

Phil types `details AF263-099` to understand the disqualification. The tool shows: "Requires TS clearance (company profile: Secret)". The Cert dimension is 0.0. Phil confirms this is correct -- his company cannot pursue classified topics. The tool does not offer "pursue" as an action for disqualified topics.

#### 3: Edge Case -- Topic with deadline in 5 days flagged URGENT

Phil sees HR001126-01 (DARPA) with an URGENT flag. The detail view shows "5 days remaining -- URGENT" in the header. The score is 0.52 (EVALUATE). Phil decides the deadline pressure plus borderline score means he should skip this one.

### UAT Scenarios (BDD)

#### Scenario: Display ranked results table

Given scoring has completed for 42 candidate topics
And 5 topics scored GO, 4 scored EVALUATE, and 3 were disqualified
When the results are displayed
Then the ranked table shows all 9 scored topics in descending score order
And disqualified topics are listed in a separate section below
And each row shows topic ID, agency, title, score, recommendation, and deadline

#### Scenario: Drill into topic detail

Given finder results include topic AF263-042 with composite 0.82
And AF263-042 scored SME=0.95, PP=0.80, Cert=1.00, Elig=1.00, STTR=1.00
When Phil types "details AF263-042"
Then the tool displays all five dimension scores with rationale
And the tool displays matching key personnel from company profile
And the tool shows "61 days" remaining to the deadline
And the tool offers "pursue AF263-042" and "back" actions

#### Scenario: Drill into disqualified topic

Given finder results include topic AF263-099 with NO-GO for TS clearance
When Phil types "details AF263-099"
Then the disqualification reason is displayed prominently
And the tool shows which profile field triggered the disqualification
And the tool does not offer "pursue" as an action

#### Scenario: Deadline urgency flags

Given topic HR001126-01 has a deadline within 3 days
And topic AF263-042 has a deadline in 61 days
When the results table is displayed
Then HR001126-01 shows an "URGENT" flag
And AF263-042 shows the deadline without a flag

#### Scenario: Results persisted for later reference

Given scoring has completed
When the results are displayed
Then results are saved to .sbir/finder-results.json
And the file includes all scored topics with dimension breakdowns
And the file includes metadata (run_id, date, source, company, profile_hash)

### Acceptance Criteria

- [ ] Results table shows rank, topic ID, agency, title, score, recommendation, deadline
- [ ] Disqualified topics shown in separate section with explicit reasons
- [ ] Detail view shows all five dimension scores with human-readable rationale
- [ ] Detail view shows matching key personnel from company profile
- [ ] Deadline within 3 days flagged URGENT; expired topics flagged EXPIRED
- [ ] Results saved to .sbir/finder-results.json with complete data
- [ ] Detail view reads from persisted results (no re-scoring)

### Technical Notes

- Results table renders to terminal with aligned columns
- Detail view reads from .sbir/finder-results.json, not from re-scoring
- Expired topics: deadline < current date, shown for reference but "pursue" disabled
- Depends on: US-SF-002 (scoring), .sbir/finder-results.json schema

---

## US-SF-004: Select Topic and Transition to Proposal Creation

### Problem

Phil Santos has reviewed the scored shortlist and decided to pursue topic AF263-042. He finds it tedious to copy the topic ID, agency, title, phase, and deadline from the finder results into the proposal creation command. Today he manually types or pastes this metadata, risking typos and wasted time.

### Who

- Solo proposal writer | Has decided which topic to pursue | Wants seamless transition from finder results into proposal creation workflow

### Solution

A `pursue <topic-id>` command within the finder results context that displays a confirmation summary and transitions directly to `/sbir:proposal new` with all topic data pre-loaded as TopicInfo.

### Domain Examples

#### 1: Happy Path -- Phil selects AF263-042 and starts a proposal

Phil types `pursue AF263-042` after reviewing the scored results. The tool shows a confirmation: "AF263-042 -- Compact Directed Energy for C-UAS, Air Force, Phase I, deadline 2026-05-15, score 0.82, recommendation GO." Phil confirms with "y". The tool transitions to `/sbir:proposal new` with topic_id, agency, phase, deadline, and title pre-loaded. Phil starts the Go/No-Go evaluation immediately.

#### 2: Edge Case -- Phil cancels the selection

Phil types `pursue N263-044` but sees the confirmation showing score 0.34 (EVALUATE). He reconsiders and types "n" to cancel. The tool returns to the results list without creating a proposal.

#### 3: Error Path -- Phil tries to pursue an expired topic

Phil types `pursue AF263-042` but the topic deadline was 2026-03-01, which has passed. The tool warns "Topic AF263-042 deadline has expired (2026-03-01). Cannot create a new proposal for an expired topic." Phil returns to the results list.

### UAT Scenarios (BDD)

#### Scenario: Select topic and see confirmation

Given Phil is viewing finder results
And topic AF263-042 has recommendation GO with score 0.82
When Phil types "pursue AF263-042"
Then the tool displays topic ID, title, agency, phase, deadline, and score
And the tool prompts "Proceed to create proposal? (y/n)"

#### Scenario: Confirm selection transitions to proposal workflow

Given Phil has typed "pursue AF263-042" and the confirmation is displayed
When Phil confirms with "y"
Then the tool transitions to /sbir:proposal new
And TopicInfo is pre-loaded with topic_id="AF263-042", agency="Air Force", phase="I", deadline="2026-05-15", title="Compact Directed Energy for C-UAS"
And Phil does not re-enter any topic metadata

#### Scenario: Cancel selection returns to results

Given Phil has typed "pursue N263-044" and the confirmation is displayed
When Phil declines with "n"
Then the tool returns to the results list
And no proposal is created

#### Scenario: Pursue expired topic blocked

Given topic AF263-042 has a deadline of 2026-03-01 which has passed
When Phil types "pursue AF263-042"
Then the tool displays "Topic deadline has expired (2026-03-01)"
And the tool does not offer the confirmation prompt
And the tool returns to the results list

### Acceptance Criteria

- [ ] `pursue <topic-id>` shows confirmation summary before transitioning
- [ ] Confirmation includes topic ID, title, agency, phase, deadline, score, recommendation
- [ ] "y" transitions to /sbir:proposal new with TopicInfo pre-loaded
- [ ] "n" returns to results list without side effects
- [ ] Expired topics cannot be pursued; clear error message displayed
- [ ] TopicInfo maps to existing dataclass (topic_id, agency, phase, deadline, title)

### Technical Notes

- TopicInfo data mapped from .sbir/finder-results.json entry
- Must match existing `TopicInfo` dataclass in `scripts/pes/domain/solicitation.py`
- Depends on: US-SF-003 (results display), US-SF-001 (TopicInfo schema), existing `/sbir:proposal new` command

---

## US-SF-005: Handle No Company Profile Gracefully

### Problem

Phil Santos wants to try the solicitation finder before setting up a full company profile. He finds it frustrating when tools refuse to work at all because a prerequisite is missing. Today there is no partial-functionality mode -- the tool either has what it needs or it fails.

### Who

- New plugin user | Has not created company profile yet | Wants to see the finder work (even at reduced accuracy) before investing time in profile setup

### Solution

When no company profile exists, display a clear error explaining what the profile provides and how to create one. Optionally, allow scoring to proceed without a profile (keyword matching only, no five-dimension scoring) so the user can see the tool's value before investing in profile creation.

### Domain Examples

#### 1: Happy Path -- Phil sees clear error and creates profile

Phil runs `/sbir:solicitation find` without having created a company profile. The tool displays: "No company profile found at ~/.sbir/company-profile.json." It explains that the profile enables capability matching, eligibility screening, and personnel alignment. It suggests `/sbir:proposal profile setup` to create one.

#### 2: Edge Case -- Phil provides BAA PDF without profile

Phil runs `/sbir:solicitation find --file baa.pdf` without a profile. The tool warns that scoring accuracy will be severely degraded without a profile but proceeds with basic keyword extraction from the BAA. Topics are listed but not scored against company capabilities. Phil sees the value of the extraction and decides to create a profile.

#### 3: Edge Case -- Profile exists but is incomplete

Phil has a profile with company_name and 3 capabilities but no certifications, no past_performance, no key_personnel. The tool warns about each missing section and proceeds with degraded accuracy. Certifications dimension defaults to 0.0 with warning. Past performance defaults to 0.0 with warning.

### UAT Scenarios (BDD)

#### Scenario: No profile -- clear error with guidance

Given no company profile exists at ~/.sbir/company-profile.json
When Phil runs "/sbir:solicitation find"
Then the tool displays "No company profile found"
And the tool explains what the profile provides (matching, eligibility, personnel)
And the tool suggests "/sbir:proposal profile setup"

#### Scenario: No profile with --file flag -- degraded mode

Given no company profile exists
And Phil provides a BAA PDF via --file
When Phil runs "/sbir:solicitation find --file baa.pdf"
Then the tool warns "No company profile: scoring accuracy severely degraded"
And the tool extracts topics from the PDF
And the tool lists topics without five-dimension scoring

#### Scenario: Incomplete profile with missing sections

Given the company profile exists with company_name and capabilities only
And the profile has no certifications, past_performance, or key_personnel
When Phil runs "/sbir:solicitation find"
Then the tool warns about each missing section
And scoring proceeds with defaults (0.0) for missing dimensions
And recommendations cap at EVALUATE for dimensions with missing data

### Acceptance Criteria

- [ ] No profile -> clear error message explaining what profile provides
- [ ] No profile -> suggestion to run profile setup command
- [ ] No profile + --file -> degraded mode with topics listed but not scored
- [ ] Incomplete profile -> per-section warnings with degraded scoring
- [ ] Missing dimensions default to 0.0 with explicit warning
- [ ] No false NO-GO from missing data (cap at EVALUATE)

### Technical Notes

- Reads profile via existing ProfilePort.exists() and ProfilePort.read()
- Profile completeness checks: required fields (company_name, capabilities), optional fields (certifications, past_performance, key_personnel, research_institution_partners)
- Depends on: existing ProfilePort / JsonProfileAdapter
