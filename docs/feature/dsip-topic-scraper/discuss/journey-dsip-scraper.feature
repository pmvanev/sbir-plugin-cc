Feature: DSIP Topic Scraping and Scoring Pipeline
  As Phil Santos, a small business engineer writing 2-3 SBIR proposals per year,
  I want to automatically scrape all DoD topics from the DSIP portal,
  so I can discover, evaluate, and score opportunities without manually browsing
  a slow Angular web application.

  Background:
    Given Phil Santos has a company profile at "~/.sbir/company-profile.json"
    And the profile lists capabilities including "directed energy", "autonomous navigation", and "edge computing"
    And the DSIP portal is accessible at "https://www.dodsbirsttr.mil/topics-app/"

  # --- Step 1: Validate DSIP Access ---

  Scenario: Successful connection to DSIP API
    Given the DSIP search API endpoint is reachable
    When Phil runs "/solicitation find --agency Air Force --phase I"
    Then the scraper confirms "DSIP API endpoint reachable"
    And the scraper reports the search parameters being used

  Scenario: DSIP portal unreachable with fallback guidance
    Given the DSIP search API endpoint is not reachable
    When Phil runs "/solicitation find"
    Then the scraper displays an error following the what/why/do pattern
    And the error suggests using "--file ./baa.pdf" as a fallback
    And no partial or corrupt data is written to disk

  Scenario: Company profile missing runs in degraded mode
    Given no company profile exists at "~/.sbir/company-profile.json"
    When Phil runs "/solicitation find"
    Then the scraper warns "Company profile not found. Scoring accuracy reduced."
    And the scraper proceeds to fetch topics without capability-based pre-filtering

  # --- Step 2: Fetch Topic Metadata ---

  Scenario: Fetch all open topics from DSIP API
    Given the DSIP API contains 247 topics with status "Open" or "Pre-Release"
    And the API returns results in pages of 100
    When the scraper fetches topic metadata
    Then all 247 topics are retrieved across 3 API pages
    And each topic has: topic_id, title, status, open_date, close_date, component, solicitation
    And the scraper reports "247 topics fetched" with a breakdown by status and agency

  Scenario: Handle paginated API responses
    Given the DSIP API reports total=247 topics
    When the scraper fetches page 1 with size=100
    And the scraper fetches page 2 with size=100
    And the scraper fetches page 3 with size=100
    Then 247 unique topics are collected with no duplicates
    And the scraper stops requesting pages when all topics are captured

  Scenario: Partial fetch failure with graceful degradation
    Given the DSIP API contains 247 topics
    And page 3 of the API returns HTTP 503
    When the scraper fetches topic metadata
    Then the scraper captures 200 topics from pages 1 and 2
    And the scraper warns "Partial results: 200 of ~247 topics fetched"
    And the partial results are still usable for scoring

  Scenario: API response format validation
    Given the DSIP API returns a response
    When the scraper parses the response
    Then it validates the presence of "total" and "data" keys
    And it validates each topic record has required fields (topicId, title, statusId)
    And malformed records are logged and skipped without crashing

  # --- Step 3: Enrich Topics with Details ---

  Scenario: Enrich topics with descriptions after capability pre-filter
    Given 247 topics were fetched from the DSIP API
    And 42 topics match Phil's company capability keywords
    When the scraper enriches the 42 matching topics
    Then each enriched topic includes a description field
    And the scraper reports progress as "[ N/42] TOPIC-ID  Title  [ok]"
    And enrichment completeness is reported: "Descriptions: 42/42"

  Scenario: Capture submission instructions for topics
    Given topic AF263-042 has submission instructions on its detail page
    When the scraper enriches topic AF263-042
    Then the enriched topic includes the submission instructions text
    And the instructions are stored alongside the topic metadata

  Scenario: Capture Q&A data for topics
    Given topic AF263-042 has 3 Q&A entries on its detail page
    When the scraper enriches topic AF263-042
    Then the enriched topic includes all 3 Q&A entries
    And each Q&A entry has a question text and answer text
    And the topic's qa_count field matches the number of captured entries

  Scenario: Handle topic with no Q&A gracefully
    Given topic MDA263-009 has zero Q&A entries
    When the scraper enriches topic MDA263-009
    Then the enriched topic has an empty Q&A list
    And the scraper reports "Q&A: 0 (none posted)" for that topic
    And this is not treated as an error

  Scenario: Description extraction failure for individual topic
    Given topic N261-099 has an unusual page structure
    When the scraper attempts to enrich topic N261-099
    Then the scraper logs "N261-099: description extraction failed"
    And the topic metadata (ID, title, dates, agency) is still preserved
    And the scraper continues enriching remaining topics

  # --- Step 4: Score and Rank ---

  Scenario: Score enriched topics against company profile
    Given 42 enriched topics with descriptions are available
    And Phil's company profile includes capabilities and past performance
    When the scoring pipeline runs
    Then each topic receives a five-dimension fit score (0.0 to 1.0 per dimension)
    And topics are ranked by composite score descending
    And each topic receives a recommendation: GO, EVALUATE, or NO-GO

  Scenario: Present ranked results with disqualified topics separated
    Given scoring has completed for 42 topics
    And 3 topics are disqualified (e.g., TS clearance required)
    When results are displayed
    Then 39 qualified topics appear in a ranked table with Score and Recommendation columns
    And 3 disqualified topics appear in a separate "Disqualified" section with reasons
    And results are saved to ".sbir/finder-results.json"

  Scenario: Cache scraped data for offline access
    Given the scraper has fetched and enriched 42 topics
    When the scraping pipeline completes
    Then enriched topic data is cached to ".sbir/dsip_topics.json"
    And the cache includes a scrape_date timestamp
    And the cache includes the source URL
    And subsequent scoring can use cached data without re-scraping

  Scenario: No topics match company capabilities
    Given 247 topics were fetched from the DSIP API
    And none match Phil's company capability keywords
    When pre-filtering completes
    Then the scraper reports "No topics matched your capability profile"
    And suggests "Try broadening search parameters or updating your company profile"
    And the raw topic data is still cached for manual review
