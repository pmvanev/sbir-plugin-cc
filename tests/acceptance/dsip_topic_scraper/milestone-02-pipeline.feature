Feature: Pipeline Integration -- Fetch, Filter, Enrich, Score
  As a solo SBIR proposal writer
  I want enriched DSIP topics to flow seamlessly into the scoring pipeline
  So that I get ranked recommendations in one continuous workflow from scrape to results

  Background:
    Given the solicitation finder system is available

  # --- US-DSIP-001 + US-DSIP-003: Happy Path ---

  # Happy path: end-to-end pipeline
  @skip
  Scenario: End-to-end scrape to scored and ranked results
    Given Phil has a company profile with capabilities "directed energy" and "autonomous systems"
    And the topic source has 42 Air Force topics
    And each candidate topic has a downloadable description document
    When Phil searches for Air Force topics with enrichment
    Then topics are fetched from the topic source
    And pre-filtered to candidates matching company capabilities
    And candidates are enriched with descriptions
    And enriched candidates are scored with five-dimension fit analysis
    And results are displayed in a ranked table with GO, EVALUATE, and NO-GO recommendations
    And results are saved to the finder results file

  # Happy path: cached data reuse skips fetch and enrich
  @skip
  Scenario: Use cached enriched data for immediate scoring
    Given enriched topic data was cached with a recent scrape date
    And the cache is fresh within the configured TTL
    When Phil searches for matching solicitation topics
    Then the tool offers to use the cached data
    And Phil accepts to use the cache
    And scoring runs immediately on the cached enriched data
    And no new requests are made to the topic source

  # Happy path: pursue topic from DSIP-sourced results
  @skip
  Scenario: Pursue a DSIP-sourced topic and transition to proposal creation
    Given finder results contain DSIP topic "AF263-042" with score 0.84 and recommendation GO
    And topic "AF263-042" is "Compact Directed Energy for C-UAS" by "Air Force" Phase "I" with deadline "2026-05-15"
    When Phil chooses to pursue topic "AF263-042"
    And Phil confirms the selection
    Then the proposal workflow begins with topic "AF263-042" pre-loaded
    And the proposal has agency "Air Force", phase "I", and deadline "2026-05-15"

  # --- US-DSIP-001: Pagination ---

  # Happy path: paginated fetch collects all topics
  @skip
  Scenario: Paginated fetch collects all topics across multiple pages
    Given the topic source has 247 topics across 3 pages of 100
    When the finder fetches topic metadata
    Then all 247 topics are collected with no duplicates
    And the fetch summary reports 247 topics across 3 pages

  # --- US-DSIP-003: Error Paths ---

  # Error: topics with unmappable fields reported separately
  @skip
  Scenario: Topics with missing required fields reported without blocking valid topics
    Given the topic source returned 42 topics
    And 3 topics are missing the deadline field
    When the pipeline transforms topics for scoring
    Then 39 valid topics proceed to scoring
    And 3 invalid topics are reported with the missing field name
    And the user is advised to check the topic source field mapping

  # Error: topic source unreachable triggers fallback guidance
  @skip
  Scenario: Unreachable topic source produces actionable guidance
    Given Phil has a company profile
    And the topic source is unreachable
    When Phil searches for matching solicitation topics
    Then the error message explains what happened
    And the error message explains why it may have happened
    And the error message suggests using a solicitation document file as a fallback
    And no partial or corrupt data is written

  # Error: partial fetch with enrichment of available topics
  @skip
  Scenario: Partial fetch results are enriched and scored when available
    Given the topic source returns 200 topics before rate limiting
    And Phil has a company profile with capabilities "directed energy"
    When Phil searches for matching solicitation topics with enrichment
    Then the tool warns about the partial fetch
    And the available 200 topics are pre-filtered and enriched
    And enriched candidates are scored and ranked
    And the partial nature is noted in the saved results
