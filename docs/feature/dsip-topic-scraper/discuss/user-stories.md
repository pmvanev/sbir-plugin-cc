<!-- markdownlint-disable MD024 -->

# User Stories: DSIP Topic Scraper

Feature: `dsip-topic-scraper`
Job traces: All stories trace to JTBD analysis in `jtbd-analysis.md`.

---

## US-DSIP-001: Fetch All DSIP Topics via API

### Problem

Phil Santos is a small business engineer who writes 2-3 SBIR proposals per year. He finds it tedious and error-prone to manually browse the DSIP portal (dodsbirsttr.mil/topics-app/) to discover open DoD SBIR/STTR topics because the Angular-based SPA is slow, paginated, and does not export data. He currently spends 1-2 hours clicking through the portal each solicitation cycle and worries he has missed relevant topics hidden on later pages.

### Who

- Small business engineer | Starting a new proposal cycle | Wants complete topic coverage without manual portal browsing

### Solution

A scraping port that connects to the DSIP internal API endpoint, fetches all topics matching search criteria (status, agency, phase) in paginated batches, normalizes the metadata into the existing TopicInfo schema, and outputs structured JSON consumable by the topic-scout scoring pipeline.

### Domain Examples

#### 1: Happy Path -- Phil finds all Air Force Phase I topics

Phil Santos runs `/solicitation find --agency "Air Force" --phase I`. The scraper connects to the DSIP API at `dodsbirsttr.mil/topics/api/public/topics/search`, requests topics with `statusId=592` (Open) and `component=USAF`. The API returns `total: 42` with `data[]` containing 42 topic records. Each record includes `topicId: "AF263-042"`, `title: "Compact Directed Energy for C-UAS"`, `statusId: 592`, `openDate: "2026-04-01"`, `closeDate: "2026-05-15"`, `component: "USAF"`, and `solicitationTitle: "DoD SBIR 2026.3"`. All 42 topics are parsed into TopicInfo objects and cached to `.sbir/dsip_topics.json`.

#### 2: Edge Case -- Large result set requiring pagination

Phil runs `/solicitation find` with no filters. The API reports `total: 247`. The scraper requests page 0 (100 results), page 1 (100 results), and page 2 (47 results). All 247 unique topics are collected. The scraper reports: "247 topics fetched. Open: 183, Pre-Release: 64."

#### 3: Error Path -- DSIP portal unreachable

Phil runs `/solicitation find` but the DSIP portal returns a connection timeout after 30 seconds. The scraper displays: "WHAT: Cannot connect to DSIP topic search API. WHY: The portal may be down or your network blocks it. DO: Try --file ./baa.pdf to search from a downloaded BAA, or retry later." No partial data is written. Exit gracefully.

#### 4: Error Path -- API response format changed

Phil runs `/solicitation find`. The API returns JSON but the expected `data` key is now called `results`. The scraper detects the missing key and reports: "WHAT: Unexpected DSIP API response structure. WHY: DSIP may have updated their API format. DO: Check for scraper updates or use --file fallback." The raw response is logged for diagnostics.

### UAT Scenarios (BDD)

#### Scenario: Fetch all open topics from DSIP API

Given the DSIP API contains 42 topics with status "Open" and component "USAF"
And Phil Santos has a company profile at "~/.sbir/company-profile.json"
When Phil runs "/solicitation find --agency Air Force --phase I"
Then the scraper connects to the DSIP search API endpoint
And retrieves all 42 topics in a single API page
And each topic is parsed into a TopicInfo with topic_id, title, agency, deadline, and status
And the topics are cached to ".sbir/dsip_topics.json" with a scrape_date timestamp

#### Scenario: Handle paginated results across multiple API pages

Given the DSIP API reports total=247 topics matching the search criteria
And results are returned in pages of 100
When the scraper fetches topic metadata
Then it requests pages 0, 1, and 2
And collects all 247 unique topics with no duplicates
And reports a summary by status (Open/Pre-Release) and agency

#### Scenario: DSIP portal unreachable with actionable error

Given the DSIP search API endpoint is not reachable (connection timeout)
When Phil runs "/solicitation find"
Then the scraper displays an error with WHAT, WHY, and DO sections
And the DO section suggests "--file ./baa.pdf" as a fallback
And no partial or corrupt data is written to disk

#### Scenario: API response structure validation

Given the DSIP API returns a JSON response
When the scraper parses the response
Then it validates the presence of "total" and "data" keys
And validates each topic record has required fields (topicId, title, statusId)
And logs and skips malformed records without crashing

### Acceptance Criteria

- [ ] Scraper connects to DSIP API and fetches topics matching search parameters
- [ ] Pagination handled: all pages fetched until total topics captured
- [ ] Each topic parsed into TopicInfo with: topic_id, title, status, agency, open_date, close_date, solicitation
- [ ] Results cached to `.sbir/dsip_topics.json` with scrape_date and source URL
- [ ] Connection failure produces what/why/do error message with --file fallback suggestion
- [ ] API format change detected and reported with actionable guidance

### Technical Notes

- DSIP uses an internal API at `/topics/api/public/topics/search` with `size=100` parameter for pagination
- Status IDs: 591 = Pre-Release, 592 = Open
- API response uses `total`/`data` keys (not `totalElements`/`content`)
- Playwright/Chromium required for initial session establishment (Angular SPA sets cookies), but actual data comes from REST API
- Must work on Windows (Git Bash) and in Docker
- Depends on: existing TopicInfo schema in `scripts/pes/domain/solicitation.py`
- Depends on: company profile at `~/.sbir/company-profile.json` (optional, degrades gracefully)

### Job Story Trace

- Job Story 1: Comprehensive Topic Discovery
- Job Story 3: Seamless Pipeline Integration

---

## US-DSIP-002: Enrich Topics with Descriptions, Instructions, and Q&A

### Problem

Phil Santos has a list of DSIP topic IDs and titles from the API, but making go/no-go decisions requires reading the full description, understanding submission instructions, checking component-specific instructions, and reviewing Q&A for each topic. Currently he clicks into each topic on the portal individually, which takes 3-5 minutes per topic. For 20+ potentially relevant topics, this is over an hour of clicking and reading.

### Who

- Small business engineer | Evaluating multiple topics for fit | Wants complete detail for each candidate topic without per-topic portal clicks

### Solution

An enrichment step that, for each pre-filtered topic, fetches the full description text, submission instructions, component-specific instructions, and all Q&A entries. Reports completeness metrics so the user knows what was captured.

### Domain Examples

#### 1: Happy Path -- Full enrichment of AF263-042

After pre-filtering, topic AF263-042 ("Compact Directed Energy for C-UAS") is a candidate. The scraper fetches its detail page and extracts: a 1,847-character description covering Background, Phase I expectations, and Phase II expectations. Submission instructions (general DoD SBIR instructions link). USAF component instructions. 3 Q&A entries: Q1 about TRL expectations (answered "TRL 3 entry, TRL 5 exit"), Q2 about teaming (answered "STTR not required"), Q3 about prior art (answered "See references"). All data attached to the topic record.

#### 2: Edge Case -- Topic with no Q&A entries

Topic MDA263-009 ("Hypersonic Tracking Algorithms") has zero Q&A entries because it was recently posted. The scraper reports "Q&A: 0 (none posted)" for this topic. The empty Q&A list is stored as `qa_entries: []`. This is not an error -- many topics have no Q&A.

#### 3: Error Path -- Description extraction fails for one topic

Topic N261-099 has an unusual DOM structure that the description extractor cannot parse. The scraper logs "N261-099: description extraction failed" and continues to the next topic. The topic's metadata (ID, title, dates, agency) is preserved. Enrichment completeness reports "Descriptions: 41/42" so Phil knows one topic needs manual review.

### UAT Scenarios (BDD)

#### Scenario: Enrich topic with full description, instructions, and Q&A

Given topic AF263-042 was fetched from the DSIP API
And AF263-042 has a description, submission instructions, and 3 Q&A entries on its detail page
When the scraper enriches topic AF263-042
Then the enriched topic includes a description field with at least 500 characters
And the enriched topic includes submission instructions text
And the enriched topic includes 3 Q&A entries each with question and answer text
And the topic's qa_count matches the number of captured entries

#### Scenario: Handle topic with no Q&A entries

Given topic MDA263-009 was fetched from the DSIP API
And MDA263-009 has zero Q&A entries on its detail page
When the scraper enriches topic MDA263-009
Then the enriched topic has an empty Q&A list
And the enrichment report shows "Q&A: 0" for this topic
And this is not treated as an error or warning

#### Scenario: Continue enrichment after individual topic failure

Given 42 topics are queued for enrichment
And topic N261-099 has an unusual page structure that prevents description extraction
When the scraper enriches all 42 topics
Then 41 topics have descriptions successfully captured
And N261-099 is logged as "description extraction failed"
And N261-099 metadata (ID, title, dates, agency) is still preserved
And enrichment completeness reports "Descriptions: 41/42"

#### Scenario: Report enrichment completeness metrics

Given 42 topics were enriched
And 42 have descriptions, 38 have instructions, and 29 have Q&A entries
When enrichment completes
Then the scraper reports "Descriptions: 42/42 | Instructions: 38/42 | Q&A: 29/42"
And the per-topic enrichment status is included in the cached JSON

#### Scenario: Progress indication during enrichment

Given 42 topics are queued for enrichment
When the scraper begins enriching topics
Then progress is displayed as "[ N/42] TOPIC-ID  Title  [ok/warn]"
And each completed topic shows its enrichment result inline

### Acceptance Criteria

- [ ] Each enriched topic includes description text from the topic detail page
- [ ] Submission instructions captured when available
- [ ] Component-specific instructions captured when available
- [ ] All Q&A entries captured with question and answer text
- [ ] Topics with no Q&A stored as empty list, not treated as error
- [ ] Individual enrichment failures logged but do not stop remaining topics
- [ ] Completeness metrics reported: description count, instruction count, Q&A count
- [ ] Progress indication shown during enrichment with per-topic status

### Technical Notes

- Enrichment requires expanding topic detail views or hitting per-topic API endpoints
- The prototype uses DOM traversal to find topic rows and click expand toggles -- this is brittle
- Prefer API-based detail fetching if a per-topic endpoint exists (check network tab)
- Q&A may require following additional links for full answer text
- Rate limiting: add configurable delay between topic detail requests to avoid DSIP throttling
- Description text may contain HTML entities, tables, and special formatting -- normalize to plain text
- Depends on: US-DSIP-001 (topic metadata fetched first)

### Job Story Trace

- Job Story 2: Topic Detail Enrichment

---

## US-DSIP-003: Integrate Scraped DSIP Data into Scoring Pipeline

### Problem

Phil Santos has scraped DSIP topic data in JSON format, but it sits in a standalone file disconnected from the existing `/solicitation find` scoring workflow. He finds it frustrating to have data from the scraper that he cannot automatically score and rank against his company profile. Currently, the topic-scout agent expects input from a BAA PDF file or manual entry, not from a scraped JSON cache.

### Who

- Small business engineer | Has scraped topic data and wants scored recommendations | Wants seamless pipeline from scrape to ranked results

### Solution

An adapter that transforms scraped DSIP topic data into TopicInfo objects consumable by the existing `TopicScoringService`, enabling the full pre-filter -> score -> rank -> display pipeline to run on DSIP-sourced data.

### Domain Examples

#### 1: Happy Path -- End-to-end scrape and score

Phil Santos runs `/solicitation find --agency "Air Force"`. The scraper fetches 42 Air Force topics from DSIP. Pre-filtering against his company capabilities (directed energy, autonomous systems, edge AI) reduces the list to 12 topics. Each is enriched with descriptions and Q&A. The 12 enriched topics are scored against his company profile: AF263-042 scores 0.84 (GO), AF263-078 scores 0.62 (GO), AF263-115 scores 0.41 (EVALUATE). Results displayed in ranked table. Phil types "pursue AF263-042" and the topic metadata flows into `/proposal new`.

#### 2: Edge Case -- Cached data reuse without re-scraping

Phil ran `/solicitation find` yesterday and the results are cached in `.sbir/dsip_topics.json` (scrape_date: 2026-03-18). Today he runs `/solicitation find` again. The scraper detects fresh cached data (less than 24 hours old) and asks: "Cached DSIP data from 2026-03-18 available. Use cache or re-scrape?" Phil chooses cache. Scoring runs immediately on cached data without waiting for a new scrape.

#### 3: Error Path -- Scraper output missing required fields

The DSIP API changed and the scraper captured topics but the `closeDate` field is now `endDate`. The adapter detects that the required `deadline` field cannot be mapped and reports: "3 topics missing deadline field. Topics cannot be scored without deadline. Check DSIP API field mapping." The 39 topics with valid deadlines proceed to scoring; the 3 invalid topics are listed separately.

### UAT Scenarios (BDD)

#### Scenario: End-to-end scrape to scored results

Given Phil Santos has a company profile with capabilities "directed energy" and "autonomous systems"
And the DSIP API contains 42 Air Force topics
When Phil runs "/solicitation find --agency Air Force"
Then topics are fetched from DSIP API
And pre-filtered to 12 topics matching company capabilities
And enriched with descriptions and Q&A
And scored with five-dimension fit analysis
And displayed in a ranked table with GO/EVALUATE/NO-GO recommendations
And results saved to ".sbir/finder-results.json"

#### Scenario: Pursue top-scored topic transitions to proposal new

Given finder results contain topic AF263-042 with score 0.84 and recommendation GO
And the topic has deadline 2026-05-15
When Phil types "pursue AF263-042"
Then the system displays topic confirmation: AF263-042, "Compact Directed Energy for C-UAS", Air Force, Phase I, deadline 2026-05-15, score 0.84
And Phil can confirm to transition to "/proposal new" with TopicInfo pre-loaded

#### Scenario: Use cached data instead of re-scraping

Given DSIP topic data was cached to ".sbir/dsip_topics.json" with scrape_date "2026-03-18"
And the current date is "2026-03-18" (cache is less than 24 hours old)
When Phil runs "/solicitation find"
Then the scraper offers to use cached data
And if Phil accepts, scoring runs immediately on cached data
And no new API requests are made to DSIP

#### Scenario: Handle topics with missing required fields

Given the scraper captured 42 topics from DSIP
And 3 topics are missing the deadline field due to API format change
When the adapter transforms topics into TopicInfo objects
Then 39 valid topics proceed to scoring
And 3 invalid topics are reported with the specific missing field
And the user is advised to check the DSIP API field mapping

### Acceptance Criteria

- [ ] Scraped DSIP topics are transformed into TopicInfo objects compatible with existing scoring service
- [ ] Pre-filtering by company capability keywords works on DSIP-sourced topics
- [ ] Scored results display in the same ranked table format as BAA-sourced results
- [ ] Results persisted to `.sbir/finder-results.json` in existing format
- [ ] `pursue <topic-id>` works for DSIP-sourced topics, pre-loading TopicInfo into `/proposal new`
- [ ] Cached data can be reused within a configurable TTL to avoid unnecessary re-scraping
- [ ] Topics with unmappable fields are reported separately without blocking valid topics

### Technical Notes

- Adapter layer maps DSIP API field names to TopicInfo schema fields
- DSIP field mapping: `topicId` -> `topic_id`, `component` -> `agency` (with standardization), `closeDate` -> `deadline` (ISO format)
- Status mapping: `statusId 591` -> "Pre-Release", `statusId 592` -> "Open"
- Cache TTL should be configurable (default: 24 hours)
- Must integrate with existing `TopicScoringService.score_batch()` in `scripts/pes/domain/topic_scoring.py`
- Must integrate with existing `finder-results.json` schema
- Depends on: US-DSIP-001 (fetch), US-DSIP-002 (enrich)
- Depends on: existing TopicScoringService, FitScoring dataclass, company-profile.json

### Job Story Trace

- Job Story 3: Seamless Pipeline Integration

---

## US-DSIP-004: Scraper Resilience and Observability

### Problem

Phil Santos is concerned that the DSIP scraper will break silently when the portal updates its API or DOM structure, leaving him with stale or incomplete data and no indication that something went wrong. The prototype scraper has no retry logic, no timeout handling beyond Playwright defaults, and no progress indication during long-running operations.

### Who

- Small business engineer | Running the scraper regularly each solicitation cycle | Needs confidence that the scraper either works completely or fails clearly

### Solution

Resilience features for the DSIP scraper: configurable timeouts, retry logic for transient failures, progress reporting during long operations, and clear diagnostics when the scraper detects structural changes in the DSIP API or DOM.

### Domain Examples

#### 1: Happy Path -- Progress indication during a 2-minute scrape

Phil runs `/solicitation find`. The scraper reports: "Connecting to DSIP... done. Fetching topics (page 1/3)... done. Fetching topics (page 2/3)... done. Fetching topics (page 3/3)... done. 247 topics fetched. Enriching 42 matching topics... [1/42] AF263-042 [ok]... [42/42] CBD263-003 [ok]. Scoring..." Phil sees continuous feedback and knows the tool is working.

#### 2: Edge Case -- Transient failure with automatic retry

The DSIP API returns HTTP 503 on the first request for page 2. The scraper waits 5 seconds and retries. The retry succeeds. The scraper logs: "Page 2: HTTP 503, retrying (1/3)... success." Phil sees the retry in the progress output but does not need to intervene.

#### 3: Error Path -- Structural change detected

The DSIP API now returns topic data under a `topics` key instead of `data`. The scraper detects this: "WHAT: DSIP API response structure changed (expected 'data' key, found 'topics'). WHY: DSIP updated their API format. DO: Report this issue and use --file fallback until the scraper is updated." The raw API response is saved to `.sbir/dsip_debug_response.json` for diagnostic purposes.

### UAT Scenarios (BDD)

#### Scenario: Progress reporting during multi-step scrape

Given the DSIP API contains 247 topics across 3 pages
And 42 topics will be enriched after pre-filtering
When the scraper runs
Then progress is reported for each phase: connection, fetching (per page), enrichment (per topic), scoring
And each phase completes with a timing indication
And the user never waits more than 10 seconds without seeing progress output

#### Scenario: Automatic retry on transient HTTP failure

Given the DSIP API returns HTTP 503 on the first request for page 2
When the scraper attempts to fetch page 2
Then the scraper waits 5 seconds and retries
And the retry succeeds on the second attempt
And the scraper logs the retry but continues normally
And the final result includes all topics from all pages

#### Scenario: Configurable timeout for DSIP connection

Given the DSIP portal does not respond within 30 seconds
When the scraper attempts to connect
Then the connection attempt times out after the configured timeout (default 30 seconds)
And the error message includes the timeout duration
And the user is not left waiting indefinitely

#### Scenario: Save diagnostic data on structural change

Given the DSIP API response contains a "topics" key instead of the expected "data" key
When the scraper parses the response
Then it detects the structural mismatch
And saves the raw API response to ".sbir/dsip_debug_response.json"
And displays a what/why/do error message explaining the change

### Acceptance Criteria

- [ ] Progress reported for each scraping phase (connect, fetch pages, enrich topics, score)
- [ ] No user-facing silence longer than 10 seconds during scraping
- [ ] Transient HTTP failures (503, 429, timeout) retried up to 3 times with exponential backoff
- [ ] Connection timeout configurable with sensible default (30 seconds)
- [ ] API structural changes detected and reported with diagnostic data saved
- [ ] All error messages follow the what/why/do pattern

### Technical Notes

- Retry strategy: exponential backoff starting at 5 seconds, max 3 retries per request
- Rate limiting: respect HTTP 429 with Retry-After header if present
- Diagnostic response saved to `.sbir/dsip_debug_response.json` (overwritten each run)
- Progress output via stderr (not stdout) to keep JSON output clean
- Timeout hierarchy: connection (30s), page load (60s), API response (30s), enrichment per-topic (15s)
- Depends on: US-DSIP-001 (fetch infrastructure), US-DSIP-002 (enrichment infrastructure)

### Job Story Trace

- Job Story 1: Comprehensive Topic Discovery (Forces: Anxiety about reliability)
- Job Story 2: Topic Detail Enrichment (Forces: Anxiety about completeness)
