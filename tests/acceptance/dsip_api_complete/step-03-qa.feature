Feature: Topic Q&A Retrieval
  As the sbir-topic-scout agent
  I want enrichment to fetch Q&A exchanges between proposers and the government
  So that I can assess government intent and clarify ambiguous requirements for go/no-go decisions

  Background:
    Given the enrichment system is available

  # --- US-DSIP-03: Happy Path ---

  @skip
  Scenario: Q&A entries fetched for topic with published questions
    Given topic A254-049 has 7 published Q&A entries
    When the enrichment service fetches Q&A for topic A254-049
    Then the enriched topic contains 7 Q&A entries
    And each Q&A entry has a question number, question text, answer text, and status

  @skip
  Scenario: Nested answer JSON is correctly parsed to extract content
    Given a Q&A entry has an answer containing nested content about seeker design
    When the enrichment service parses the Q&A entry
    Then the answer text is "The parameters listed as well as others are of importance, but seeker design is not of interest at this time."

  # --- US-DSIP-03: Edge Cases ---

  @skip
  Scenario: Topics with zero published questions skip the Q&A fetch
    Given topic XYZ254-001 has 0 published Q&A entries
    When the enrichment service processes topic XYZ254-001
    Then no Q&A request is made for this topic
    And the Q&A entries list is empty
    And Q&A completeness count is not incremented for this topic

  # --- US-DSIP-03: Error Paths ---

  @skip
  Scenario: Malformed answer JSON falls back to raw string
    Given a Q&A entry has an answer field that is not valid JSON
    When the enrichment service parses the Q&A entry
    Then the raw answer string is returned as the answer text
    And the Q&A entry is still included in the output

  @skip
  Scenario: Q&A endpoint failure isolates to the affected topic
    Given topics A254-049 and A254-P050 are queued for enrichment
    And the Q&A endpoint returns an error for topic A254-049
    When the enrichment service processes both topics
    Then topic A254-049 has empty Q&A entries and an error record
    And topic A254-P050 Q&A entries are retrieved successfully
