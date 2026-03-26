Feature: Three-API Profile Enrichment from UEI (US-CPE-001)
  As a small business founder with an active SAM.gov registration
  I want to enter my UEI and have the system pull data from three federal databases
  So that my profile is populated with authoritative government data without manual transcription

  Background:
    Given the enrichment system is available
    And Rafael has a valid SAM.gov API key stored

  # --- Happy Path ---

  @skip
  Scenario: SAM.gov returns complete entity registration data
    Given SAM.gov will return entity data for UEI "DKJF84NXLE73"
    When Rafael requests enrichment for UEI "DKJF84NXLE73"
    Then enrichment returns the legal name "Radiant Defense Systems, LLC"
    And enrichment returns the CAGE code "7X2K9"
    And enrichment returns NAICS codes "334511", "541715", and "334220"
    And enrichment returns registration status "Active" expiring "2027-01-15"
    And enrichment returns no socioeconomic certifications
    And every SAM.gov field is tagged with source "SAM.gov"

  @skip
  Scenario: SBIR.gov returns award history including a forgotten award
    Given SAM.gov resolved the company name as "Radiant Defense Systems, LLC"
    And SBIR.gov will return 3 awards for "Radiant Defense Systems, LLC"
    When enrichment queries SBIR.gov for award history
    Then enrichment returns 3 past performance entries
    And one entry is agency "Air Force" with topic "Compact DE for Maritime UAS" and phase "Phase I"
    And one entry is agency "DARPA" with topic "High-Power RF Source" and outcome "Completed"
    And one entry is agency "Navy" with topic "Shipboard Power Conditioning" and phase "Phase I"
    And every SBIR.gov field is tagged with source "SBIR.gov"

  @skip
  Scenario: USASpending returns federal award totals and business types
    Given SAM.gov resolved the company name as "Radiant Defense Systems, LLC"
    And USASpending will return recipient data for "Radiant Defense Systems, LLC"
    When enrichment queries USASpending for federal awards
    Then enrichment returns a total federal award amount of "$2.4M"
    And enrichment returns 5 transactions
    And enrichment returns business types "Small Business, For-Profit"

  @skip
  Scenario: Full three-API cascade populates enrichment result
    Given SAM.gov will return entity data for UEI "DKJF84NXLE73"
    And SBIR.gov will return 3 awards for "Radiant Defense Systems, LLC"
    And USASpending will return federal award totals for "Radiant Defense Systems, LLC"
    When Rafael requests enrichment for UEI "DKJF84NXLE73"
    Then enrichment returns fields from all three federal sources
    And the missing fields list contains "capabilities", "security_clearance", and "key_personnel"
    And every enriched field shows which federal source it came from

  # --- Error Paths ---

  @skip
  Scenario: SAM.gov returns no entity for the entered UEI
    Given SAM.gov will return no entity for UEI "XYZABC123456"
    When Rafael requests enrichment for UEI "XYZABC123456"
    Then enrichment reports "No entity found in SAM.gov for UEI XYZABC123456"
    And the system suggests checking for transposed characters
    And the system offers to re-enter the UEI or skip enrichment

  @skip
  Scenario: Invalid UEI format rejected before any API call
    When Rafael enters UEI "SHORT"
    Then the system reports the UEI must be 12 alphanumeric characters
    And no API calls are made
    And Rafael can re-enter the UEI

  @skip
  Scenario: SBIR.gov times out without blocking other sources
    Given SAM.gov will return entity data for UEI "DKJF84NXLE73"
    And SBIR.gov will time out after 10 seconds
    And USASpending will return federal award totals for "Radiant Defense Systems, LLC"
    When Rafael requests enrichment for UEI "DKJF84NXLE73"
    Then SAM.gov and USASpending fields are available
    And SBIR.gov fields are marked as "unavailable"
    And the user can continue with partial data or retry SBIR.gov

  @skip
  Scenario: SAM.gov failure prevents downstream API calls
    Given SAM.gov will return an authentication error
    When Rafael requests enrichment for UEI "DKJF84NXLE73"
    Then enrichment reports SAM.gov authentication failed
    And SBIR.gov and USASpending are not called
    And the system offers to re-enter the API key or skip enrichment

  @skip
  Scenario: All three APIs fail and enrichment falls back to manual interview
    Given SAM.gov will time out
    And SBIR.gov will time out
    And USASpending will time out
    When Rafael requests enrichment for UEI "DKJF84NXLE73"
    Then enrichment reports all federal sources are unavailable
    And the profile builder continues with the manual interview flow

  # --- Edge Cases ---

  @skip
  Scenario: SBIR.gov returns multiple company matches requiring disambiguation
    Given SAM.gov resolved the company name as "Radiant Defense Systems, LLC"
    And SBIR.gov will return 3 companies matching "Radiant Defense"
    When enrichment queries SBIR.gov for award history
    Then enrichment returns 3 company candidates with name, location, and award count
    And the first candidate is "Radiant Defense Systems, LLC" in "Huntsville, AL" with 3 awards
    And disambiguation is needed before SBIR.gov awards can be included

  @skip
  Scenario: USASpending business types corroborate SAM.gov certifications
    Given SAM.gov returned socioeconomic certifications including "8(a)"
    And USASpending returned business types including "8(a) Business Development"
    When enrichment assembles the result
    Then the socioeconomic certifications show corroboration between SAM.gov and USASpending

  @skip
  @property
  Scenario: Enrichment result never contains fields without source attribution
    Given any successful enrichment result from any combination of API responses
    When the enrichment result is assembled
    Then every field in the result has a non-empty source name
    And every field has an access timestamp
