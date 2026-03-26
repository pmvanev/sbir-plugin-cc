Feature: SAM.gov API Key Setup and Validation (US-CPE-004)
  As a small business founder preparing for profile enrichment
  I want to set up and validate my SAM.gov API key with clear guidance
  So that enrichment can access federal databases on my behalf

  Background:
    Given the enrichment system is available

  # --- Happy Path ---

  Scenario: Existing API key detected and reused without prompting
    Given Rafael stored a SAM.gov API key in a previous session
    When the system checks for an existing API key
    Then the system reports the key is available
    And the key is identified by its last 4 characters only
    And Rafael is not prompted to enter a new key

  Scenario: New API key validated and saved securely
    Given no SAM.gov API key is stored
    When Rafael provides a valid SAM.gov API key
    And the system validates the key against SAM.gov
    Then the key passes validation
    And the key is saved to the secure key storage location
    And the saved file has owner-only access permissions

  # --- Error Paths ---

  @skip
  Scenario: Invalid API key rejected with clear guidance
    Given no SAM.gov API key is stored
    When Rafael provides an invalid SAM.gov API key
    And the system validates the key against SAM.gov
    Then the key fails validation
    And the system explains the key may be mistyped or expired
    And the system offers to re-enter the key or skip enrichment

  @skip
  Scenario: Expired API key detected during validation
    Given Rafael stored a SAM.gov API key that has since expired
    When the system validates the stored key against SAM.gov
    Then the key fails validation
    And the system explains the key may need to be regenerated
    And the system provides the URL to generate a new key

  @skip
  Scenario: Enrichment skipped when founder declines API key setup
    Given no SAM.gov API key is stored
    When Rafael chooses to skip enrichment
    Then no API key file is created
    And the enrichment step is bypassed
    And the profile builder continues with the manual interview flow

  # --- Edge Cases ---

  @skip
  Scenario: Malformed API key file handled gracefully
    Given the API key file exists but contains invalid data
    When the system checks for an existing API key
    Then the system reports no valid key was found
    And offers to set up a new key

  @skip
  Scenario: API key never displayed in full after entry
    Given Rafael provides a valid SAM.gov API key "abc123def456ghi789jkl012"
    When the key is saved successfully
    Then any subsequent display shows only the last 4 characters "l012"
    And the full key value is never included in output

  @skip
  Scenario: API key never passed as a command-line argument
    Given Rafael has a valid SAM.gov API key stored
    When the enrichment service reads the API key
    Then the key is read from the secure key file
    And the key is not present in any process arguments
