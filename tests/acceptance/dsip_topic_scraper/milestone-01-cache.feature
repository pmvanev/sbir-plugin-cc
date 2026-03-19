Feature: Topic Cache with TTL-Based Freshness
  As a solo SBIR proposal writer
  I want enriched topic data cached locally with a time-based freshness check
  So that I can re-score topics without waiting for a full re-scrape each time

  Background:
    Given the cache system is available

  # --- US-DSIP-003 Cache: Happy Path ---

  # Happy path: cache write after enrichment
  Scenario: Cache enriched topic data after enrichment completes
    Given 42 topics have been enriched with descriptions and metadata
    When the cache writes the enriched topic data
    Then the cache file contains all 42 enriched topics
    And the cache file includes a scrape date timestamp
    And the cache file includes the data source identifier
    And the cache file includes enrichment completeness metrics

  # Happy path: cache freshness check within TTL
  Scenario: Cache recognized as fresh within the TTL window
    Given the cache was written 12 hours ago
    And the TTL is configured as 24 hours
    When the freshness check runs
    Then the cache is reported as fresh

  # Happy path: cache reuse for re-scoring
  @skip
  Scenario: Re-score cached data after company profile update
    Given Phil updated his company profile to add capability "laser systems"
    And the cache contains 42 enriched topics from a recent scrape
    And the cache is still fresh
    When Phil searches for matching solicitation topics
    Then scoring runs on the cached enriched data
    And results reflect the updated capability keywords
    And no new topic source requests are made

  # --- US-DSIP-003 Cache: Edge Cases ---

  # Edge: cache stale after TTL expires
  Scenario: Cache recognized as stale after TTL window expires
    Given the cache was written 36 hours ago
    And the TTL is configured as 24 hours
    When the freshness check runs
    Then the cache is reported as stale

  # Edge: cache invalidation on filter change
  @skip
  Scenario: Cache invalidated when search filters differ from cached filters
    Given the cache contains topics fetched with agency filter "Air Force"
    When Phil searches with agency filter "Navy"
    Then the cached data is not reused
    And a fresh fetch is initiated for Navy topics

  # Edge: atomic cache write survives interruption
  Scenario: Cache write uses atomic temp-backup-rename pattern
    Given 42 topics are ready to be cached
    When the cache writes the enriched topic data
    Then a temporary file is written first
    And the previous cache is backed up
    And the temporary file is renamed to the cache file
    And the cache file is valid after the operation completes

  # --- US-DSIP-003 Cache: Error Paths ---

  # Error: missing cache file handled gracefully
  @skip
  Scenario: Missing cache file triggers fresh fetch without error
    Given no cache file exists
    When Phil searches for matching solicitation topics
    Then the tool proceeds with a fresh fetch from the topic source
    And no error message is shown about missing cache

  # Error: corrupt cache file handled gracefully
  @skip
  Scenario: Corrupt cache file triggers fresh fetch with warning
    Given the cache file exists but contains invalid data
    When Phil searches for matching solicitation topics
    Then the tool warns that the cache could not be read
    And the tool proceeds with a fresh fetch from the topic source
    And the corrupt cache file is not used for scoring
