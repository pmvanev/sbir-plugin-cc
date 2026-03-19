Feature: Topic Enrichment with Descriptions, Instructions, and Q&A
  As a solo SBIR proposal writer
  I want each candidate topic enriched with its full description, instructions, and Q&A
  So that I can make informed go/no-go decisions without per-topic portal clicks

  Background:
    Given the enrichment system is available

  # --- US-DSIP-002: Happy Path ---

  # Happy path: full enrichment of a single topic
  @skip
  Scenario: Enrich topic with full description, instructions, and Q&A
    Given topic "AF263-042" was identified as a candidate
    And the topic detail document contains a 1847-character description
    And the topic detail document contains submission instructions
    And the topic detail document contains 3 Q&A entries
    When the enrichment service processes topic "AF263-042"
    Then the enriched topic includes a description with at least 500 characters
    And the enriched topic includes submission instructions text
    And the enriched topic includes 3 Q&A entries each with question and answer
    And the topic's Q&A count is 3

  # Happy path: batch enrichment with progress
  @skip
  Scenario: Enrich batch of candidate topics with progress indication
    Given 42 topics are queued for enrichment
    And each topic has a downloadable detail document
    When the enrichment service processes all 42 topics
    Then progress is reported for each topic as it completes
    And 42 topics are enriched successfully
    And enrichment completeness reports "Descriptions: 42/42"

  # Happy path: completeness metrics across all content types
  @skip
  Scenario: Report enrichment completeness metrics after batch enrichment
    Given 42 topics were enriched
    And 42 have descriptions, 38 have instructions, and 29 have Q&A entries
    When enrichment completes
    Then the completeness report shows "Descriptions: 42/42 | Instructions: 38/42 | Q&A: 29/42"
    And the per-topic enrichment status is included in the cached data

  # --- US-DSIP-002: Edge Cases ---

  # Edge: topic with no Q&A entries
  @skip
  Scenario: Handle topic with no Q&A entries gracefully
    Given topic "MDA263-009" was identified as a candidate
    And the topic detail document has zero Q&A entries
    When the enrichment service processes topic "MDA263-009"
    Then the enriched topic has an empty Q&A list
    And the topic's Q&A count is 0
    And this is not treated as an error or warning

  # Edge: topic with component-specific instructions
  @skip
  Scenario: Capture component-specific instructions when available
    Given topic "AF263-042" was identified as a candidate
    And the topic detail document includes Air Force component instructions
    When the enrichment service processes topic "AF263-042"
    Then the enriched topic includes component-specific instructions
    And the instructions are stored alongside the general submission instructions

  # --- US-DSIP-002: Error Paths ---

  # Error: description extraction fails for one topic
  @skip
  Scenario: Continue enrichment after individual topic extraction failure
    Given 42 topics are queued for enrichment
    And topic "N261-099" has an unparseable detail document
    When the enrichment service processes all 42 topics
    Then 41 topics have descriptions successfully captured
    And topic "N261-099" is logged as having failed description extraction
    And topic "N261-099" metadata is still preserved with topic ID, title, dates, and agency
    And enrichment completeness reports "Descriptions: 41/42"

  # Error: detail document download fails for one topic
  @skip
  Scenario: Handle topic detail download failure without stopping batch
    Given 42 topics are queued for enrichment
    And the detail document for topic "CBD263-003" is not downloadable
    When the enrichment service processes all 42 topics
    Then 41 topics are enriched successfully
    And topic "CBD263-003" is logged as having failed document download
    And enrichment continues for remaining topics

  # Error: enrichment timeout for slow topic
  @skip
  Scenario: Enrichment times out for a slow topic without blocking others
    Given 42 topics are queued for enrichment
    And the detail document for topic "DTRA263-011" takes longer than the timeout
    When the enrichment service processes all 42 topics
    Then topic "DTRA263-011" is skipped with a timeout warning
    And remaining topics complete enrichment normally
    And completeness metrics reflect the skipped topic
