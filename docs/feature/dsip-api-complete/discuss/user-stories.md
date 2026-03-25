<!-- markdownlint-disable MD024 -->

# User Stories: dsip-api-complete

## US-DSIP-01: Correct Search Query Format

### Problem
The sbir-topic-scout agent is a solicitation intelligence agent that calls `dsip_cli.py enrich --status Open` to scan for matching SBIR topics. It finds that the search returns all 32,638 historical topics regardless of the status filter because the DsipApiAdapter uses the wrong query format (flat params with `numPerPage` and `topicStatus`). The agent receives numeric topic IDs that cannot be used with detail/Q&A endpoints, and the real topic count is buried in noise.

### Who
- sbir-topic-scout agent | Scanning for open SBIR topics | Needs filtered results with hash IDs to proceed to enrichment

### Solution
Fix DsipApiAdapter to use JSON `searchParam` format with `topicReleaseStatus` status IDs, `size` pagination parameter, and `solicitationCycleNames` filter.

### Domain Examples

#### 1: Agent scans for open topics -- happy path
The sbir-topic-scout agent runs `python scripts/dsip_cli.py fetch --status Open` during the DOD SBIR 2025.4 cycle. The adapter builds `searchParam={"topicReleaseStatus":[592],"solicitationCycleNames":["openTopics"],"sortBy":"finalTopicCode,asc"}&size=100&page=0`. The API returns 24 matching topics. Each topic has hash ID `7051b2da4a1e4c52bd0e7daf80d514f7_86352`, `cycleName: DOD_SBIR_2025_P1_C4`, `releaseNumber: 12`, `component: ARMY`.

#### 2: Agent scans for pre-release topics
The agent runs `python scripts/dsip_cli.py fetch --status Pre-Release`. The adapter maps "Pre-Release" to `topicReleaseStatus: [591]`. The API returns topics in pre-release status only.

#### 3: Agent scans with no status filter (all active)
The agent runs `python scripts/dsip_cli.py fetch` with no `--status` flag. The adapter uses `topicReleaseStatus: [591, 592]` to return both pre-release and open topics. This is the "show me everything active" case.

#### 4: API returns zero results for closed cycle
The agent runs `python scripts/dsip_cli.py fetch --status Open` but the current cycle has no open topics (all closed). The API returns `{"total": 0, "data": []}`. The CLI outputs JSON with `total: 0` and empty topics array. No error.

### UAT Scenarios (BDD)

#### Scenario: Search uses JSON searchParam format
Given the DSIP API is accessible
When the DsipApiAdapter builds a search request with status filter "Open"
Then the request URL contains `searchParam` as a URL-encoded JSON string
And the JSON contains `topicReleaseStatus: [592]`
And the pagination parameter is `size` (not `numPerPage`)

#### Scenario: Search returns only matching topics with hash IDs
Given the current cycle DOD_SBIR_2025_P1_C4 has 24 active topics
When the adapter fetches with status "Open"
Then the result contains at most 24 topics
And each topic's topic_id is a hash ID containing an underscore (e.g., `7051b2da...86352`)
And each topic includes cycle_name, release_number, and component

#### Scenario: Status filter maps to correct status IDs
Given the agent specifies status "Pre-Release"
When the adapter builds the searchParam
Then topicReleaseStatus is [591]

#### Scenario: No status filter returns all active topics
Given the agent does not specify a status filter
When the adapter builds the searchParam
Then topicReleaseStatus is [591, 592]

#### Scenario: Search response includes metadata for instruction URL construction
Given the API returns topic A254-049 with cycleName "DOD_SBIR_2025_P1_C4", releaseNumber 12, component "ARMY"
When the adapter normalizes the topic
Then the normalized topic has cycle_name "DOD_SBIR_2025_P1_C4"
And release_number 12
And published_qa_count 7

### Acceptance Criteria
- [ ] Search requests use JSON `searchParam` format, not flat query params
- [ ] Pagination uses `size` parameter, not `numPerPage`
- [ ] Status filter "Open" maps to `topicReleaseStatus: [592]`, "Pre-Release" to `[591]`
- [ ] No status filter defaults to `[591, 592]` (all active)
- [ ] Normalized topics include cycle_name, release_number, component, published_qa_count from search response
- [ ] Topic IDs are hash IDs (not numeric)

### Technical Notes
- `searchParam` value must be URL-encoded JSON string
- `User-Agent: Mozilla/5.0` header already present (required or API returns 403)
- Existing retry/backoff/pagination logic unchanged -- only query format changes
- `_normalize_topic` must map new fields: `cycleName` -> `cycle_name`, `releaseNumber` -> `release_number`, `noOfPublishedQuestions` -> `published_qa_count`
- Depends on: none (first story in sequence)

---

## US-DSIP-02: Structured Topic Details via API

### Problem
The sbir-topic-scout agent receives topic descriptions extracted from PDF documents via pypdf. The PDF extraction is lossy (loses HTML structure), misses structured fields (technology areas, focus areas, ITAR flag, CMMC level), and is slower than an API call. The `/details` endpoint returns all this data as structured JSON, but the enrichment adapter does not use it.

### Who
- sbir-topic-scout agent | Enriching topics with detailed descriptions | Needs structured fields (technology areas, ITAR) for accurate scoring

### Solution
Add a details API call to the enrichment adapter that fetches `/topics/{hash_id}/details` and returns structured JSON fields alongside the description.

### Domain Examples

#### 1: Topic A254-049 details -- happy path
The enrichment adapter calls `GET /topics/api/public/topics/7051b2da4a1e4c52bd0e7daf80d514f7_86352/details`. The response includes `description` (HTML), `objective` (HTML), `phase1Description`, `phase2Description`, `keywords: "Radar; antenna; metamaterials"`, `technologyAreas: ["Information Systems", "Materials"]`, `focusAreas: ["Advanced Computing and Software", "Microelectronics"]`, `itar: false`, `cmmcLevel: ""`.

#### 2: Topic with ITAR restriction
The enrichment adapter fetches details for a DARPA topic. The response has `itar: true`. The normalized topic sets `itar: true`, which the scoring service uses as a disqualifier if the company lacks ITAR registration.

#### 3: Details endpoint returns 500
The enrichment adapter calls details for topic CBD254-005. The endpoint returns HTTP 500. The adapter records an error for this topic, sets description to empty string, and continues enrichment with Q&A and instructions. The `enrichment_status` is "partial".

### UAT Scenarios (BDD)

#### Scenario: Details API returns structured topic description
Given topic A254-049 has hash ID "7051b2da4a1e4c52bd0e7daf80d514f7_86352"
When the enrichment adapter fetches details for this topic
Then the enriched topic contains description with HTML content from the API
And the enriched topic contains objective "The objective of this topic is to provide low-cost..."
And the enriched topic contains keywords ["Radar", "antenna", "metamaterials", "scanning", "array"]
And the enriched topic contains technology_areas ["Information Systems", "Materials"]
And the enriched topic contains itar as false

#### Scenario: Details provide richer data than PDF extraction
Given topic A254-049 details are fetched via API
When compared to the previous PDF-only extraction
Then technology_areas and focus_areas are available as structured arrays (not available in PDF)
And keywords are parsed from semicolon-separated string into a list
And HTML structure is preserved in description and phase descriptions

#### Scenario: Details failure isolates to single topic
Given the details endpoint returns 500 for topic CBD254-005
When the enrichment adapter processes this topic
Then the topic's description is empty
And Q&A and instruction enrichment still proceeds for this topic
And other topics in the batch are unaffected

### Acceptance Criteria
- [ ] Enrichment calls `/topics/{hash_id}/details` instead of (or in addition to) PDF download for descriptions
- [ ] Normalized enrichment output includes: description, objective, phase descriptions, keywords (list), technology_areas (list), focus_areas (list), itar (boolean), cmmc_level
- [ ] Keywords parsed from semicolon-separated string to list
- [ ] Details endpoint failure does not block Q&A or instruction enrichment for same topic
- [ ] Details endpoint failure does not block enrichment of other topics in batch

### Technical Notes
- HTML content in description/objective/phase fields should be preserved as-is (agent can interpret HTML)
- Keywords field from API is semicolon-separated string: `"Radar; antenna; metamaterials"` -- split and trim
- `referenceDocuments` array from details response is bonus data (not required for MVP but valuable)
- Depends on: US-DSIP-01 (hash IDs from search)

---

## US-DSIP-03: Topic Q&A Retrieval

### Problem
The sbir-topic-scout agent has zero visibility into government Q&A exchanges for topics. Q&A data is critical for understanding government intent, clarifying ambiguous requirements, and assessing whether a company's approach aligns with what the TPOC actually wants. Today the agent makes GO/EVALUATE/NO-GO recommendations without this intelligence. Topic A254-049 has 7 published Q&A entries with detailed government responses that reveal radar emulation requirements, bandwidth specs, and TRL expectations -- none of which are visible to the agent.

### Who
- sbir-topic-scout agent | Assessing government intent for GO/NO-GO | Needs Q&A to understand what the TPOC actually wants
- Dr. Sarah Chen, proposal manager | Reviewing agent recommendations | Needs to trust that recommendations account for government clarifications

### Solution
Add Q&A endpoint call to the enrichment adapter. Parse the nested answer JSON format. Skip Q&A fetch for topics with zero published questions.

### Domain Examples

#### 1: Topic A254-049 with 7 Q&A entries -- happy path
The enrichment adapter calls `GET /topics/api/public/topics/7051b2da4a1e4c52bd0e7daf80d514f7_86352/questions`. The response is a JSON array of 7 entries. Entry 1 has `questionNo: 1`, question about RADAR functionality parameters, and answer `{"content": "<p>The parameters listed as well as others are of importance, but seeker design is not of interest at this time.</p>"}`. The adapter double-parses the answer field, extracting "The parameters listed as well as others are of importance, but seeker design is not of interest at this time."

#### 2: Topic with zero published questions
Topic CBD254-005 has `noOfPublishedQuestions: 6` (actually has questions) but a topic in a new cycle has `noOfPublishedQuestions: 0`. The adapter skips the Q&A endpoint call for the zero-question topic, saves an HTTP request, and returns an empty qa_entries array.

#### 3: Q&A answer with malformed nested JSON
A topic's Q&A answer field contains `{"content": null}` or a malformed JSON string. The adapter falls back to returning the raw answer string, logs a warning, and does not fail the enrichment.

### UAT Scenarios (BDD)

#### Scenario: Q&A entries fetched for topic with published questions
Given topic A254-049 has noOfPublishedQuestions 7
When the enrichment adapter fetches Q&A
Then it calls GET /topics/api/public/topics/7051b2da...86352/questions
And the enriched topic contains 7 qa_entries
And each entry has question_no, question text, answer text, and status

#### Scenario: Nested answer JSON correctly parsed
Given Q&A entry has answer '{"content": "<p>The parameters listed...</p>"}'
When the adapter parses the Q&A
Then the answer text is extracted from the nested content field
And HTML tags are preserved (agent can interpret HTML)

#### Scenario: Zero-question topics skip Q&A endpoint
Given topic XYZ has noOfPublishedQuestions 0
When the enrichment adapter processes this topic
Then no HTTP request is made to the Q&A endpoint
And qa_entries is an empty array
And qa_count in completeness metrics is not incremented

#### Scenario: Malformed answer JSON falls back gracefully
Given Q&A entry has answer field that is not valid JSON
When the adapter parses the Q&A
Then the raw answer string is returned as the answer text
And a warning is logged
And the qa_entry is still included in the output

#### Scenario: Q&A endpoint failure isolates to single topic
Given the Q&A endpoint returns 500 for topic A254-049
When the enrichment adapter processes the batch
Then topic A254-049 has empty qa_entries and an error record
And other topics' Q&A is unaffected

### Acceptance Criteria
- [ ] Enrichment calls `/topics/{hash_id}/questions` for topics with `published_qa_count > 0`
- [ ] Q&A endpoint skipped for topics with `published_qa_count == 0`
- [ ] Answer field double-parsed: outer JSON string containing `{"content": "<HTML>"}`, extract HTML
- [ ] Malformed answer JSON falls back to raw string (no crash)
- [ ] Each qa_entry has: question_no, question (text), answer (text), status
- [ ] Q&A endpoint failure isolates per-topic, does not block other data types or other topics

### Technical Notes
- Answer field format: `"answer": "{\"content\": \"<p>HTML here</p>\"}"` -- JSON string containing JSON object with content key
- Some answers have `"length": 0` with only an oembed URL (video link) -- treat as empty answer with note
- `questionSubmittedOn` is Unix milliseconds -- normalize to ISO 8601 if included
- Depends on: US-DSIP-01 (hash IDs from search), US-DSIP-02 (enrichment adapter refactor)

---

## US-DSIP-04: Solicitation and Component Instruction Documents

### Problem
The sbir-topic-scout agent cannot access solicitation instructions (BAA preface) or component-specific instructions (e.g., Army annex). These documents contain critical submission requirements: page limits, font requirements, volume structure, evaluation criteria, and component-specific technical focus areas. Without them, the agent's GO/EVALUATE/NO-GO recommendation is uninformed about whether the company can even comply with submission requirements.

### Who
- sbir-topic-scout agent | Assessing submission feasibility | Needs instruction documents to check compliance requirements
- Dr. Sarah Chen, proposal manager | Planning proposal effort | Needs to know page limits, volume structure, evaluation criteria before committing resources

### Solution
Add instruction document download and text extraction to the enrichment adapter. Construct download URLs from search response fields (cycleName, releaseNumber, component).

### Domain Examples

#### 1: ARMY topic with both instruction types -- happy path
Topic A254-049 has cycleName "DOD_SBIR_2025_P1_C4", releaseNumber 12, component "ARMY". The adapter downloads BAA preface from `?solicitation=DOD_SBIR_2025_P1_C4&release=12&documentType=RELEASE_PREFACE` (658KB PDF). Then downloads ARMY instructions from `?solicitation=DOD_SBIR_2025_P1_C4&documentType=INSTRUCTIONS&component=ARMY&release=12` (990KB PDF). Both PDFs are parsed with pypdf and text is extracted.

#### 2: Component with no published instructions yet
Topic from a new SOCOM solicitation has `baaInstructions` array without `COMPONENT_FINAL_DOCUMENT_UPLOAD` entry. The adapter attempts download, receives 404, records null for component_instructions, and continues. The solicitation instructions (BAA preface) are still available because they are cycle-level, not component-level.

#### 3: Same instructions shared across topics in same cycle/component
Topics A254-049 and A254-P050 are both ARMY topics in DOD_SBIR_2025_P1_C4 release 12. They share the same BAA preface and ARMY annex documents. The adapter can cache instruction PDFs per cycle+component to avoid redundant downloads.

### UAT Scenarios (BDD)

#### Scenario: Solicitation instructions downloaded from BAA preface
Given topic A254-049 has cycleName "DOD_SBIR_2025_P1_C4" and releaseNumber 12
When the enrichment adapter fetches solicitation instructions
Then it downloads from /submissions/api/public/download/solicitationDocuments
  with solicitation "DOD_SBIR_2025_P1_C4" and release "12" and documentType "RELEASE_PREFACE"
And the PDF text is extracted via pypdf
And the enriched topic contains solicitation_instructions with extracted text

#### Scenario: Component instructions downloaded
Given topic A254-049 has component "ARMY"
When the enrichment adapter fetches component instructions
Then it downloads from the same base URL
  with documentType "INSTRUCTIONS" and component "ARMY"
And the PDF text is extracted
And the enriched topic contains component_instructions with extracted text

#### Scenario: Missing component instructions handled gracefully
Given topic CBD254-005 component "CBD" has no published component instructions
When the adapter attempts to download component instructions
And the endpoint returns 404
Then component_instructions is null
And an informational message is logged
And solicitation_instructions are still fetched successfully
And other topics are unaffected

#### Scenario: Instruction documents cached per cycle and component
Given topics A254-049 and A254-P050 share cycleName "DOD_SBIR_2025_P1_C4" and component "ARMY"
When the enrichment adapter enriches both topics
Then the ARMY instructions PDF is downloaded once
And both topics reference the same extracted text

#### Scenario: Instruction download failure does not block enrichment
Given the instruction download endpoint is temporarily unavailable (HTTP 503)
When the adapter retries with exponential backoff (3 attempts)
And all attempts fail
Then solicitation_instructions and component_instructions are null for affected topics
And description and Q&A data are still present
And enrichment_status is "partial"

### Acceptance Criteria
- [ ] Solicitation instructions fetched from BAA preface endpoint using cycleName and releaseNumber from search
- [ ] Component instructions fetched using cycleName, releaseNumber, and component from search
- [ ] PDF text extracted via pypdf
- [ ] 404 on instruction download results in null field (not error)
- [ ] Instruction PDFs cached per cycle+component to avoid redundant downloads within a batch
- [ ] Completeness metrics track solicitation_instructions and component_instructions counts separately

### Technical Notes
- Instruction download URL base: `https://www.dodsbirsttr.mil/submissions/api/public/download/solicitationDocuments`
- Same `User-Agent: Mozilla/5.0` header required
- PDFs are large (658KB-990KB) -- rate limiting between downloads important
- `baaInstructions` array in search response can indicate available document types via `uploadTypeCode` -- use as hint but not gate
- Depends on: US-DSIP-01 (cycleName, releaseNumber, component from search)

---

## US-DSIP-05: CLI and Agent Skill Update

### Problem
The dsip-cli-usage skill and the CLI itself document the old behavior. The skill shows `topic_id: "68492"` (numeric) and describes "PDF enrichment" only. After the adapter fixes, the CLI output has new fields (objective, keywords, technology_areas, qa_entries, solicitation_instructions, component_instructions), the detail command needs to accept hash IDs, and the agent skill needs to document the richer data available for analysis.

### Who
- sbir-topic-scout agent | Learning CLI capabilities from skill file | Needs accurate documentation of new fields and capabilities
- Future developers | Maintaining the CLI | Need accurate docstrings and examples

### Solution
Update CLI output format, detail command, and dsip-cli-usage skill to reflect all 4 data types and new field names.

### Domain Examples

#### 1: Agent reads updated skill and uses new fields
The sbir-topic-scout agent loads `skills/topic-scout/dsip-cli-usage.md`. The skill now documents that enriched topics include `qa_entries`, `solicitation_instructions`, `component_instructions`, `technology_areas`, `keywords`, `itar`, and `objective`. The agent uses Q&A entries to assess government intent and technology_areas for scoring.

#### 2: Detail command with hash ID
Dr. Sarah Chen asks the agent to investigate topic A254-049. The agent runs `python scripts/dsip_cli.py detail --topic-id 7051b2da4a1e4c52bd0e7daf80d514f7_86352`. The output includes all 4 data types in a single JSON response.

#### 3: Completeness metrics in CLI output
The agent runs `python scripts/dsip_cli.py enrich --status Open`. The output includes a `completeness` section: `{"descriptions": 24, "qa": 18, "solicitation_instructions": 24, "component_instructions": 20, "total": 24}`. The agent sees that 6 topics have no Q&A and 4 have no component instructions -- normal for some topics.

### UAT Scenarios (BDD)

#### Scenario: Enriched topic output includes all new fields
Given the agent runs "python scripts/dsip_cli.py enrich --status Open"
When the CLI returns enriched topics
Then each topic object contains: description, objective, phase descriptions, keywords, technology_areas, focus_areas, itar, cmmc_level, qa_entries, qa_count, solicitation_instructions, component_instructions, enrichment_status

#### Scenario: Detail command accepts hash ID
Given the agent runs "python scripts/dsip_cli.py detail --topic-id 7051b2da4a1e4c52bd0e7daf80d514f7_86352"
Then the output contains all 4 data types for topic A254-049
And the output includes qa_entries with 7 entries

#### Scenario: Skill file documents new capabilities
Given the dsip-cli-usage skill is loaded by the agent
Then the skill describes qa_entries, solicitation_instructions, component_instructions as available fields
And the skill shows a realistic example topic with hash ID format
And the skill documents the completeness metrics section

### Acceptance Criteria
- [ ] CLI output JSON includes new fields: objective, keywords, technology_areas, focus_areas, itar, cmmc_level, qa_entries, qa_count, solicitation_instructions, component_instructions, enrichment_status
- [ ] Detail command works with hash ID format
- [ ] dsip-cli-usage skill updated with new field documentation and examples
- [ ] Completeness metrics include all 4 data type counts

### Technical Notes
- Skill file at `skills/topic-scout/dsip-cli-usage.md`
- CLI at `scripts/dsip_cli.py`
- No new CLI flags needed -- existing interface preserved
- Depends on: US-DSIP-01 through US-DSIP-04 (all adapter changes complete)
