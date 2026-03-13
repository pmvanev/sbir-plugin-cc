Feature: Company Profile Foundation
  As a small business founder pursuing SBIR/STTR grants
  I want profile validation and reliable persistence
  So that my company data is accurate and safely stored

  Background:
    Given the profile builder system is available

  # --- US-CPB-002: Profile Validation Service ---

  # Happy path: complete valid profile
  Scenario: Complete profile passes all validation checks
    Given a complete valid profile for "Radiant Defense Systems, LLC" with 5 capabilities
    When the profile is validated
    Then validation passes with no errors

  # Error: CAGE code wrong length
  Scenario: CAGE code with wrong length is rejected
    Given a profile with CAGE code "7X2K" and SAM.gov active
    When the profile is validated
    Then validation fails with an error on field "certifications.sam_gov.cage_code"
    And the error message mentions "5 alphanumeric"

  # Error: CAGE code with non-alphanumeric characters
  Scenario: CAGE code with special characters is rejected
    Given a profile with CAGE code "7X-K9" and SAM.gov active
    When the profile is validated
    Then validation fails with an error on field "certifications.sam_gov.cage_code"

  # Error: invalid security clearance value
  @skip
  Scenario: Invalid security clearance value is rejected
    Given a profile with security clearance "classified"
    When the profile is validated
    Then validation fails with an error on field "certifications.security_clearance"
    And the error message mentions the allowed values

  # Error: employee count zero
  @skip
  Scenario: Employee count of zero is rejected
    Given a profile with employee count 0
    When the profile is validated
    Then validation fails with an error on field "employee_count"
    And the error message indicates the count must be positive

  # Error: employee count negative
  @skip
  Scenario: Negative employee count is rejected
    Given a profile with employee count -5
    When the profile is validated
    Then validation fails with an error on field "employee_count"

  # Error: empty capabilities list
  @skip
  Scenario: Profile with no capabilities is rejected
    Given a profile with an empty capabilities list
    When the profile is validated
    Then validation fails with an error on field "capabilities"
    And the error message indicates at least one capability is required

  # Error: missing required field
  @skip
  Scenario: Profile missing company name is rejected
    Given a profile with no company name
    When the profile is validated
    Then validation fails with an error on field "company_name"

  # Error: UEI missing when SAM.gov active
  @skip
  Scenario: Missing UEI with active SAM.gov is rejected
    Given a profile with SAM.gov active and CAGE code "7X2K9" but no UEI
    When the profile is validated
    Then validation fails with an error on field "certifications.sam_gov.uei"

  # Error: invalid socioeconomic certification
  @skip
  Scenario: Invalid socioeconomic certification is rejected
    Given a profile with socioeconomic certification "InvalidCert"
    When the profile is validated
    Then validation fails with an error on field "certifications.socioeconomic"

  # Boundary: SAM.gov inactive skips conditional requirements
  @skip
  Scenario: Profile with inactive SAM.gov does not require CAGE code or UEI
    Given a profile with SAM.gov inactive and no CAGE code or UEI
    When the profile is validated
    Then validation passes with no errors

  # Edge: multiple validation errors reported together
  @skip
  Scenario: Multiple validation errors are reported in a single result
    Given a profile with CAGE code "AB" and employee count -1 and clearance "invalid"
    When the profile is validated
    Then validation reports 3 or more issues
    And each issue identifies the specific field and expected format

  # --- US-CPB-005 + US-CPB-001: Profile Persistence ---

  # Happy path: atomic write creates new profile
  @skip
  Scenario: New profile is persisted atomically
    Given Rafael has no company profile
    And a valid profile for "Radiant Defense Systems, LLC"
    When the profile is saved
    Then the profile file exists at the expected location
    And the file contains valid data matching the saved profile

  # Happy path: backup created before overwrite
  @skip
  Scenario: Saving over an existing profile creates a backup
    Given Rafael has an existing profile for "Radiant Defense Systems, LLC"
    When a new profile for "Radiant Defense Updated" is saved
    Then a backup file exists with the previous profile data
    And the current profile contains "Radiant Defense Updated"

  # Error: profile directory does not exist
  @skip
  Scenario: Profile directory is created if absent
    Given the profile directory does not exist
    When a valid profile is saved
    Then the profile directory is created
    And the profile file is written successfully

  # Happy path: detect existing profile metadata
  @skip
  Scenario: Existing profile metadata is retrieved for overwrite protection
    Given Rafael has a saved profile for "Radiant Defense Systems, LLC"
    When the system checks for an existing profile
    Then the check reports the profile exists
    And the company name "Radiant Defense Systems, LLC" is returned

  # Error: load non-existent profile
  @skip
  Scenario: Loading a profile that does not exist reports the absence
    Given no company profile exists
    When the system attempts to load the profile
    Then the system reports that no profile was found

  @property
  @skip
  Scenario: Profile roundtrip preserves all data exactly
    Given any valid company profile
    When the profile is saved and then loaded
    Then the loaded profile matches the original exactly
