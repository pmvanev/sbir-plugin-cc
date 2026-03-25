Feature: CLI Output and Completeness Metrics
  As the sbir-topic-scout agent
  I want enriched topic output to include all 4 data types with completeness metrics
  So that I can assess data coverage and use all available intelligence for recommendations

  # --- US-DSIP-05: Happy Path ---

  @skip
  Scenario: Enriched topic output includes all new fields
    Given 24 topics have been enriched with all 4 data types
    When the enrichment results are returned
    Then each enriched topic contains description, objective, keywords, and technology areas
    And each enriched topic contains focus areas, ITAR status, and CMMC level
    And each enriched topic contains Q&A entries with Q&A count
    And each enriched topic contains solicitation instructions and component instructions
    And each enriched topic contains an enrichment status

  @skip
  Scenario: Completeness metrics report all 4 data type counts
    Given 24 topics were enriched
    And 24 have descriptions, 18 have Q&A, 24 have solicitation instructions, and 20 have component instructions
    When the completeness report is generated
    Then the report shows "Descriptions: 24/24"
    And the report shows "Q&A: 18/24"
    And the report shows "Solicitation instructions: 24/24"
    And the report shows "Component instructions: 20/24"

  # --- US-DSIP-05: Edge Case ---

  @skip
  Scenario: Completeness metrics handle zero enrichment gracefully
    Given zero topics were enriched because the search returned no results
    When the completeness report is generated
    Then the report shows counts of 0 for all data types
    And no error is reported
