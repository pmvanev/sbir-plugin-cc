Feature: Enrichment Review and Confirm (US-CPE-002)
  As a small business founder reviewing data pulled from federal databases
  I want to confirm, edit, or skip each enriched field with full source transparency
  So that only verified data enters my profile and I can correct any stale API values

  Background:
    Given the enrichment system is available
    And enrichment has returned results from federal sources

  # --- Happy Path ---

  @skip
  Scenario: Founder confirms all enriched fields and they merge into the profile draft
    Given enrichment returned company name "Radiant Defense Systems, LLC" from SAM.gov
    And enrichment returned CAGE code "7X2K9" from SAM.gov
    And enrichment returned 3 NAICS codes from SAM.gov
    And enrichment returned 3 past performance entries from SBIR.gov
    When Rafael confirms all enriched fields
    Then all confirmed values are included in the profile draft
    And each field retains its federal source in the profile metadata

  @skip
  Scenario: Source attribution visible for every enriched field during review
    Given enrichment returned fields from SAM.gov, SBIR.gov, and USASpending
    When the review presents each field
    Then SAM.gov fields display source "SAM.gov"
    And SBIR.gov fields display source "SBIR.gov"
    And USASpending fields display source "USASpending.gov"

  # --- Error Paths ---

  @skip
  Scenario: Founder edits a NAICS code list to remove an irrelevant code
    Given enrichment returned NAICS codes "334511", "541715", and "334220" from SAM.gov
    When Rafael removes "334220" from the NAICS code list
    Then the profile draft contains NAICS codes "334511" and "541715" only
    And the source is recorded as "user (overriding SAM.gov)"

  @skip
  Scenario: Founder edits an enriched field value
    Given enrichment returned CAGE code "7X2K9" from SAM.gov
    When Rafael changes the CAGE code to "7X2K8"
    Then the profile draft uses CAGE code "7X2K8"
    And the source is recorded as "user (overriding SAM.gov)"

  @skip
  Scenario: Founder skips a field to answer manually during the interview
    Given enrichment returned socioeconomic certifications as empty from SAM.gov
    And Rafael's recent certification is not yet reflected in SAM.gov
    When Rafael chooses to enter socioeconomic certifications manually
    Then the field is left empty in the enrichment result
    And socioeconomic certifications appears in the missing fields list for the interview

  @skip
  Scenario: No enriched field enters the profile without explicit confirmation
    Given enrichment returned 8 fields from 3 federal sources
    When the review step completes with 5 confirmed and 3 skipped
    Then only the 5 confirmed fields are in the profile draft
    And the 3 skipped fields are not in the profile draft
    And the 3 skipped fields are added to the interview questions list

  # --- Edge Cases ---

  @skip
  Scenario: Past performance entries can be individually confirmed or removed
    Given enrichment returned 3 past performance entries from SBIR.gov
    When Rafael confirms 2 entries and removes the third
    Then the profile draft contains 2 past performance entries
    And the removed entry is not in the profile draft

  @skip
  Scenario: Interview only asks about fields not populated by enrichment
    Given enrichment populated company name, CAGE code, NAICS codes, registration status, and past performance
    When the interview step begins after enrichment review
    Then the interview asks about capabilities, security clearance, ITAR status, employee count, key personnel, and research partners
    And the interview does not re-ask about enrichment-populated fields

  @skip
  @property
  Scenario: Confirmed enrichment data survives through preview and save
    Given any set of confirmed enrichment fields
    When the profile is previewed and then saved
    Then the saved profile contains all confirmed enrichment values
    And the saved profile includes source attribution for every enriched field
