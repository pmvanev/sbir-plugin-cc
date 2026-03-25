Feature: Structured Topic Details via API
  As the sbir-topic-scout agent
  I want enrichment to fetch structured topic details from the API
  So that I have technology areas, keywords, ITAR status, and full descriptions for accurate scoring

  Background:
    Given the enrichment system is available

  # --- US-DSIP-02: Happy Path ---

  @skip
  Scenario: Details API returns structured description and metadata for a topic
    Given topic A254-049 has hash ID "7051b2da4a1e4c52bd0e7daf80d514f7_86352"
    When the enrichment service fetches details for topic A254-049
    Then the enriched topic contains a description about Ka-Band radar and metamaterials
    And the enriched topic contains an objective about low-cost Ka-Band radar solutions
    And the enriched topic contains keywords including "Radar", "antenna", and "metamaterials"
    And the enriched topic contains technology areas including "Information Systems" and "Materials"
    And the enriched topic has ITAR status false

  @skip
  Scenario: Keywords are parsed from semicolon-separated string into a list
    Given topic A254-049 has keywords "Radar; antenna; metamaterials; scanning; array"
    When the enrichment service normalizes the details
    Then the keywords list contains 5 entries
    And each keyword is trimmed of whitespace

  # --- US-DSIP-02: Error Paths ---

  @skip
  Scenario: Details failure for one topic does not block other topics
    Given topics A254-049 and CBD254-005 are queued for enrichment
    And the details endpoint returns an error for topic CBD254-005
    When the enrichment service processes both topics
    Then topic A254-049 has a complete description
    And topic CBD254-005 has an empty description
    And topic CBD254-005 has enrichment status "partial"

  @skip
  Scenario: Details failure does not block Q&A or instruction enrichment for same topic
    Given topic CBD254-005 is queued for enrichment
    And the details endpoint returns an error for topic CBD254-005
    And the Q&A endpoint works for topic CBD254-005
    When the enrichment service processes topic CBD254-005
    Then Q&A entries are still retrieved for topic CBD254-005
    And instruction documents are still fetched for topic CBD254-005
    And enrichment status is "partial"

  @skip
  Scenario: Topic with ITAR restriction is flagged for scoring
    Given topic DARPA254-010 has ITAR status true
    When the enrichment service fetches details for topic DARPA254-010
    Then the enriched topic has ITAR status true
