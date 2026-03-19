Feature: Scraper Resilience and Observability
  As a solo SBIR proposal writer
  I want the scraper to retry transient failures, report progress, and detect structural changes
  So that I am confident the scraper either works completely or fails clearly

  Background:
    Given the solicitation finder system is available

  # --- US-DSIP-004: Happy Path ---

  # Happy path: progress reporting during multi-phase pipeline
  @skip
  Scenario: Progress reported during each phase of the scraping pipeline
    Given the topic source has 247 topics across 3 pages
    And 42 topics will be enriched after pre-filtering
    When the scraper runs the full pipeline
    Then progress is reported for the connection phase
    And progress is reported for each page fetch
    And progress is reported for each topic enrichment
    And progress is reported for the scoring phase
    And the user never waits more than 10 seconds without progress output

  # Happy path: automatic retry succeeds
  Scenario: Automatic retry succeeds after transient failure
    Given the topic source returns a transient error on the first request for page 2
    When the scraper attempts to fetch page 2
    Then the scraper waits and retries
    And the retry succeeds
    And the scraper logs the retry but continues normally
    And all topics from all pages are included in the final result

  # --- US-DSIP-004: Edge Cases ---

  # Edge: retry with exponential backoff
  Scenario: Retry uses exponential backoff between attempts
    Given the topic source returns transient errors for the first 2 requests
    When the scraper retries with exponential backoff
    Then the first retry waits approximately 5 seconds
    And the second retry waits approximately 10 seconds
    And the third attempt succeeds

  # Edge: configurable connection timeout
  Scenario: Connection timeout is configurable with sensible default
    Given the topic source does not respond
    When the scraper attempts to connect with the default timeout
    Then the connection attempt times out after 30 seconds
    And the error message includes the timeout duration
    And the user is not left waiting indefinitely

  # --- US-DSIP-004: Error Paths ---

  # Error: structural change detected in topic source response
  Scenario: Structural change in topic source response detected and reported
    Given the topic source response uses an unexpected data structure
    When the scraper parses the response
    Then it detects the structural mismatch
    And the raw response is saved for diagnostic purposes
    And the error message explains what changed
    And the error message explains why it may have changed
    And the error message suggests using a solicitation document file as a fallback

  # Error: all retries exhausted
  Scenario: All retries exhausted produces clear failure message
    Given the topic source returns transient errors for all 3 retry attempts
    When the scraper exhausts all retries for page 2
    Then the scraper reports that the fetch failed after 3 retries
    And the error follows the what-why-do pattern
    And partial results from successful pages are preserved
    And the user can choose to score partial results or retry later

  # Error: enrichment rate limiting respected
  @skip
  Scenario: Rate limiting signal from topic source is respected
    Given the topic source indicates a rate limit with a retry delay
    When the scraper encounters the rate limit during enrichment
    Then the scraper pauses for the indicated delay before continuing
    And enrichment resumes after the pause
    And the rate limit event is logged

  @property @skip
  Scenario: Error messages always follow the what-why-do pattern
    Given any error condition encountered during scraping
    When the error is reported to the user
    Then the message contains a "what happened" explanation
    And the message contains a "why it may have happened" explanation
    And the message contains a "what to do about it" suggestion
