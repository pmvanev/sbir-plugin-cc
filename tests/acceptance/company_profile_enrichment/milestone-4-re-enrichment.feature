Feature: Re-Enrichment During Profile Update (US-CPE-003)
  As a small business founder with an existing profile
  I want to re-run enrichment to detect changes in federal databases since my last profile save
  So that my profile stays current without manually checking three government websites

  Background:
    Given the enrichment system is available
    And Rafael has a valid SAM.gov API key stored
    And Rafael has an existing profile with stored UEI "DKJF84NXLE73"

  # --- Happy Path ---

  @skip
  Scenario: Re-enrichment detects a new NAICS code added to SAM.gov
    Given Rafael's profile has NAICS codes "334511" and "541715"
    And SAM.gov now returns NAICS codes "334511", "541715", and "334220"
    When Rafael requests re-enrichment to compare against his current profile
    Then the diff shows 1 new NAICS code: "334220"
    And existing NAICS codes "334511" and "541715" are shown as matching
    And Rafael can choose to add the new NAICS code

  @skip
  Scenario: Re-enrichment detects a new SBIR award
    Given Rafael's profile has 2 past performance entries
    And SBIR.gov now returns 3 awards including a new Navy Phase I
    When Rafael requests re-enrichment to compare against his current profile
    Then the diff shows 1 new past performance entry
    And the new entry is agency "Navy" with topic "Shipboard Power Conditioning"
    And existing past performance entries are shown as unchanged

  @skip
  Scenario: Founder selects which changes to accept from the diff
    Given re-enrichment found a new NAICS code and a new SBIR award
    When Rafael accepts the new NAICS code but declines the new award
    Then only the NAICS code change is applied to the profile
    And the declined award is not added to the profile

  # --- Error Paths ---

  @skip
  Scenario: Re-enrichment does not overwrite manually entered data
    Given Rafael manually entered socioeconomic certifications as "8(a)"
    And SAM.gov still shows no socioeconomic certifications
    When re-enrichment compares API data against the current profile
    Then the diff shows socioeconomic certifications as "current: 8(a), API: none"
    And Rafael can choose to keep his manual entry
    And the manual entry "8(a)" is preserved when Rafael keeps current

  @skip
  Scenario: Re-enrichment preserves user-entered fields not available from APIs
    Given Rafael manually entered capabilities and key personnel
    And no API provides capabilities or key personnel data
    When re-enrichment runs
    Then capabilities and key personnel are listed as "not available from APIs"
    And the manually entered values are not modified

  @skip
  Scenario: Re-enrichment with SAM.gov failure falls back gracefully
    Given SAM.gov is unavailable during re-enrichment
    When Rafael requests re-enrichment
    Then the system reports SAM.gov data could not be retrieved
    And no changes are proposed for SAM.gov-sourced fields
    And the profile remains unchanged

  # --- Edge Cases ---

  @skip
  Scenario: No changes detected during re-enrichment
    Given Rafael's profile matches current API data exactly
    When Rafael requests re-enrichment to compare against his current profile
    Then the system reports no differences found between the profile and federal databases
    And no changes are made to the profile

  @skip
  Scenario: Re-enrichment uses stored UEI without re-entry
    Given Rafael's profile contains UEI "DKJF84NXLE73"
    When Rafael requests re-enrichment
    Then the system uses UEI "DKJF84NXLE73" from the stored profile
    And Rafael is not prompted to re-enter the UEI

  @skip
  Scenario: Array reordering in API response is not treated as a change
    Given Rafael's profile has NAICS codes "541715" and "334511"
    And SAM.gov returns NAICS codes "334511" and "541715" in different order
    When Rafael requests re-enrichment to compare against his current profile
    Then the diff shows NAICS codes as matching
    And no change is proposed for NAICS codes

  @skip
  @property
  Scenario: Re-enrichment never modifies fields the user has not explicitly accepted
    Given any existing profile with any combination of enriched and manual fields
    When re-enrichment proposes changes
    Then only fields with explicit user acceptance are modified
    And all other fields retain their current values exactly
