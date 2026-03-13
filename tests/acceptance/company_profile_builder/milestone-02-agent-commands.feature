Feature: Company Profile Agent and Commands
  As a small business founder pursuing SBIR/STTR grants
  I want a guided interview and preview before saving
  So that I can create an accurate profile without hand-editing files

  Background:
    Given the profile builder system is available

  # --- US-CPB-001: Guided Interview ---

  # Happy path: full interview produces valid profile
  @skip
  Scenario: Guided interview produces a complete validated profile
    Given Rafael has no company profile
    When Rafael provides company name "Radiant Defense Systems, LLC"
    And Rafael provides capabilities "directed energy, RF systems, power electronics"
    And Rafael provides SAM.gov details as active with CAGE "7X2K9" and UEI "DKJF84NXLE73"
    And Rafael provides security clearance "secret"
    And Rafael provides ITAR registered as true
    And Rafael provides employee count 23
    And Rafael provides key personnel "Rafael Medina" as "CEO" with expertise "directed energy"
    And Rafael provides past performance for "Air Force" on "Compact Directed Energy" with outcome "awarded"
    And Rafael provides research partner "Georgia Tech Research Institute"
    And the profile is validated
    Then validation passes with no errors
    And the profile can be saved successfully

  # Edge: SAM.gov not yet registered
  @skip
  Scenario: Founder without SAM.gov registration creates profile with inactive status
    Given Rafael is creating a profile for a new company
    When Rafael indicates SAM.gov registration is not active
    Then the profile records SAM.gov as inactive
    And no CAGE code or UEI is required
    And validation passes with no errors

  # Error: cancel during interview
  @skip
  Scenario: Canceling the interview saves no profile
    Given Rafael has started creating a profile
    And Rafael has provided company name "Radiant Defense Systems, LLC"
    When Rafael cancels the profile creation
    Then no profile file is written
    And the partial data is discarded

  # --- US-CPB-002: Preview and Validation Gate ---

  # Happy path: preview displays all fields
  @skip
  Scenario: Profile preview displays all sections for review
    Given a complete profile draft for "Radiant Defense Systems, LLC" with 5 capabilities
    When the profile preview is generated
    Then the preview includes the company name
    And the preview includes 5 capabilities
    And the preview includes the SAM.gov registration status
    And the preview includes the employee count
    And the preview includes key personnel entries
    And the preview includes past performance entries

  # Error: preview with validation failures blocks save
  @skip
  Scenario: Profile with validation failures cannot be saved
    Given a profile draft with CAGE code "7X2K" and employee count 0
    When the profile is validated before save
    Then validation reports issues
    And the profile cannot be saved until issues are resolved

  # Edge: edit during preview corrects and re-validates
  @skip
  Scenario: Correcting a field during preview produces a valid profile
    Given a profile draft with CAGE code "7X2K"
    When the CAGE code is corrected to "7X2K9"
    And the profile is re-validated
    Then the CAGE code error is resolved
    And validation passes with no errors

  # --- US-CPB-005: Overwrite Protection ---

  # Happy path: detect existing profile
  @skip
  Scenario: Setup detects existing profile and provides options
    Given Rafael has an existing profile for "Radiant Defense Systems, LLC"
    When Rafael starts profile setup
    Then the system detects the existing profile
    And the company name "Radiant Defense Systems, LLC" is displayed

  # Happy path: start fresh with backup
  @skip
  Scenario: Starting fresh creates backup of existing profile
    Given Rafael has an existing profile for "Radiant Defense Systems, LLC"
    When Rafael chooses to start fresh
    Then the existing profile is backed up
    And a new profile can be created

  # Edge: cancel preserves existing profile
  @skip
  Scenario: Canceling setup preserves the existing profile unchanged
    Given Rafael has an existing profile for "Radiant Defense Systems, LLC"
    When Rafael cancels the setup
    Then the existing profile is unchanged
    And no backup file is created

  # Error: backup failure blocks overwrite
  @skip
  Scenario: Backup failure prevents starting fresh
    Given Rafael has an existing profile
    And the backup location is not writable
    When Rafael chooses to start fresh
    Then the system reports the backup failed
    And the existing profile is not overwritten
