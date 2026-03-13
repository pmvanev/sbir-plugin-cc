Feature: Company Profile Builder Walking Skeleton
  As a small business founder pursuing SBIR/STTR grants
  I want to create a validated company profile
  So that fit scoring can accurately match me to solicitation topics

  # Walking Skeleton 1: Validate and persist a new company profile
  # Validates: profile dict -> validation service -> adapter write -> adapter read
  @walking_skeleton
  Scenario: Founder creates a valid company profile and retrieves it
    Given Rafael has no company profile
    And Rafael has prepared a complete valid profile for "Radiant Defense Systems, LLC"
    When Rafael submits the profile for validation and saving
    Then the profile passes validation with no errors
    And the profile is saved to the company profile location
    And when Rafael retrieves the profile the company name is "Radiant Defense Systems, LLC"
    And the retrieved profile contains 2 capabilities

  # Walking Skeleton 2: Validation catches errors before saving
  # Validates: invalid profile -> validation service -> errors reported -> save blocked
  @walking_skeleton
  Scenario: Founder sees validation errors before profile is saved
    Given Rafael has prepared a profile with CAGE code "7X2K" and employee count 0
    When Rafael submits the profile for validation
    Then validation reports 2 issues
    And one issue identifies the CAGE code as having wrong length
    And one issue identifies the employee count as invalid
    And the profile is not saved

  # Walking Skeleton 3: Update preserves existing data
  # Validates: existing profile -> section update -> re-validate -> save with preservation
  @walking_skeleton
  Scenario: Founder updates one section and all other sections are preserved
    Given Rafael has a saved company profile with 5 capabilities and 2 past performance entries
    When Rafael adds a past performance entry for agency "NASA" with topic "Lunar Surface Power" and outcome "awarded"
    And the updated profile is validated and saved
    Then the profile now has 3 past performance entries
    And the capabilities list still contains 5 entries
