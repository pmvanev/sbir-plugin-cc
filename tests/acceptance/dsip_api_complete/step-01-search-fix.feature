Feature: Correct Search Query Format
  As the sbir-topic-scout agent
  I want search requests to use the correct query format with status filtering
  So that I receive only current-cycle topics instead of all 32,638 historical topics

  Background:
    Given the DSIP topic source is available

  # --- US-DSIP-01: Happy Path ---

  # Regression: the core bug fix -- search returns ~24, not 32K
  Scenario: Search with status Open returns only current-cycle topics
    Given the current solicitation cycle has 24 active topics
    When the topic source searches with status filter "Open"
    Then at most 24 topics are returned
    And each topic has a hash identifier containing an underscore

  @skip
  Scenario: Search with status Pre-Release returns only pre-release topics
    Given the current solicitation cycle has pre-release topics
    When the topic source searches with status filter "Pre-Release"
    Then only topics with pre-release status are returned

  @skip
  Scenario: Search without status filter returns both open and pre-release topics
    Given the current solicitation cycle has both open and pre-release topics
    When the topic source searches without a status filter
    Then both open and pre-release topics are returned

  Scenario: Normalized topic includes cycle metadata from search response
    Given topic A254-049 is in the search results
    When the topic is normalized
    Then the topic has cycle name "DOD_SBIR_2025_P1_C4"
    And the topic has release number 12
    And the topic has component "ARMY"
    And the topic has 7 published Q&A entries

  # --- US-DSIP-01: Error Paths ---

  @skip
  Scenario: Search returns zero topics for a closed cycle
    Given the current solicitation cycle has no open topics
    When the topic source searches with status filter "Open"
    Then zero topics are returned
    And no error is reported

  @skip
  Scenario: Search handles API unavailability with clear message
    Given the DSIP topic source is temporarily unavailable
    When the topic source searches with status filter "Open"
    Then an error is reported indicating the source is unavailable
    And Phil is advised to use a downloaded solicitation document instead

  @skip
  Scenario: Search with partial page failure returns topics already fetched
    Given the first page of results was fetched successfully with 100 topics
    And the second page request fails
    When the topic source completes the search
    Then the 100 topics from the first page are returned as partial results
    And a warning indicates that results are incomplete
