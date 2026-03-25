Feature: Solicitation and Component Instruction Documents
  As the sbir-topic-scout agent
  I want enrichment to download and extract text from instruction PDFs
  So that I can check submission requirements like page limits, volume structure, and evaluation criteria

  Background:
    Given the enrichment system is available

  # --- US-DSIP-04: Happy Path ---

  @skip
  Scenario: Solicitation instructions extracted from BAA preface PDF
    Given topic A254-049 has cycle name "DOD_SBIR_2025_P1_C4" and release number 12
    When the enrichment service fetches solicitation instructions
    Then the enriched topic contains solicitation instructions with extracted text
    And the extracted text is non-empty

  @skip
  Scenario: Component instructions extracted for ARMY topic
    Given topic A254-049 has component "ARMY", cycle name "DOD_SBIR_2025_P1_C4", and release number 12
    When the enrichment service fetches component instructions
    Then the enriched topic contains component instructions with extracted text

  @skip
  Scenario: Instruction PDFs cached per cycle and component to avoid redundant downloads
    Given topics A254-049 and A254-P050 share cycle "DOD_SBIR_2025_P1_C4", component "ARMY", and release 12
    When the enrichment service enriches both topics
    Then the ARMY instructions PDF is downloaded once
    And both topics reference the same extracted instruction text

  # --- US-DSIP-04: Error Paths ---

  @skip
  Scenario: Missing component instructions result in null field without error
    Given topic CBD254-005 has component "CBD" with no published component instructions
    When the enrichment service attempts to fetch component instructions
    Then component instructions are null for topic CBD254-005
    And solicitation instructions are still fetched successfully
    And other topics in the batch are unaffected

  @skip
  Scenario: Instruction download failure after retries results in partial enrichment
    Given the instruction download endpoint is temporarily unavailable
    When the enrichment service retries with exponential backoff and all attempts fail
    Then solicitation instructions and component instructions are null for affected topics
    And description and Q&A data are still present for affected topics
    And enrichment status is "partial" for affected topics
