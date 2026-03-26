Feature: Company Profile Enrichment Walking Skeleton
  As a small business founder creating a company profile
  I want to provide my UEI and receive enriched profile data from federal databases
  So that I can populate my profile without manually copying from government websites

  # Walking Skeleton 1: UEI in, enriched profile fields out
  # Validates: UEI -> enrichment service -> SAM.gov + SBIR.gov + USASpending -> enrichment result
  # Driving port: CompanyEnrichmentService.enrich_from_uei()
  @walking_skeleton
  Scenario: Founder enriches profile from UEI and receives data from three federal sources
    Given Rafael has a valid SAM.gov API key stored
    And SAM.gov will return entity data for UEI "DKJF84NXLE73"
    And SBIR.gov will return 3 awards for "Radiant Defense Systems, LLC"
    And USASpending will return federal award totals for "Radiant Defense Systems, LLC"
    When Rafael requests enrichment for UEI "DKJF84NXLE73"
    Then enrichment returns the legal name "Radiant Defense Systems, LLC"
    And enrichment returns the CAGE code "7X2K9"
    And enrichment returns 3 NAICS codes
    And enrichment returns 3 past performance entries from SBIR awards
    And enrichment returns a federal award total
    And every enriched field shows which federal source it came from

  # Walking Skeleton 2: Partial failure still delivers usable data
  # Validates: one API fails -> partial result -> user sees what is available
  # Driving port: CompanyEnrichmentService.enrich_from_uei()
  @walking_skeleton
  Scenario: Founder receives partial enrichment when one federal source is unavailable
    Given Rafael has a valid SAM.gov API key stored
    And SAM.gov will return entity data for UEI "DKJF84NXLE73"
    And SBIR.gov is unavailable
    And USASpending will return federal award totals for "Radiant Defense Systems, LLC"
    When Rafael requests enrichment for UEI "DKJF84NXLE73"
    Then enrichment returns SAM.gov fields successfully
    And enrichment returns USASpending fields successfully
    And SBIR.gov fields are marked as unavailable
    And the unavailable fields are listed for manual entry during the interview

  # Walking Skeleton 3: Re-enrichment detects changes since last profile save
  # Validates: existing profile + fresh API data -> diff -> additions detected
  # Driving port: CompanyEnrichmentService.diff_against_profile()
  @walking_skeleton
  Scenario: Founder detects new SBIR award during profile update re-enrichment
    Given Rafael has an existing profile with 2 past performance entries
    And Rafael has a valid SAM.gov API key stored
    And SAM.gov will return current entity data for UEI "DKJF84NXLE73"
    And SBIR.gov will return 3 awards including a new Navy Phase I
    And USASpending will return current federal award totals
    When Rafael requests re-enrichment to compare against his current profile
    Then the diff shows 1 new past performance entry from SBIR.gov
    And the diff shows the new award is "Navy" agency with topic "Shipboard Power Conditioning"
    And existing profile entries are not modified in the diff
