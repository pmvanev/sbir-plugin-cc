Feature: Quality Artifact Persistence
  As a proposal author completing quality discovery
  I want my quality knowledge saved reliably to disk
  So that it persists across sessions and is available to downstream agents

  Background:
    Given the quality artifact directory exists at the company profile location

  # --- Walking Skeleton: Full Discovery Persistence ---

  @walking_skeleton
  Scenario: Full quality discovery persists all three artifacts
    Given quality preferences have been captured
    And winning patterns have been captured from 3 rated proposals
    And writing quality feedback has been captured
    When all quality artifacts are saved
    Then quality preferences file exists at the company profile location
    And winning patterns file exists at the company profile location
    And writing quality profile file exists at the company profile location
    And each file contains valid data matching its schema

  # --- Partial Discovery ---

  Scenario: Partial discovery creates only the artifact with data
    Given quality preferences have been captured
    And no winning patterns were captured
    And no writing quality feedback was captured
    When quality artifacts are saved
    Then quality preferences file exists at the company profile location
    And winning patterns file does not exist
    And writing quality profile file does not exist

  Scenario: Only evaluator feedback creates writing quality profile
    Given no quality preferences were captured
    And no winning patterns were captured
    And writing quality feedback has been captured
    When quality artifacts are saved
    Then quality preferences file does not exist
    And winning patterns file does not exist
    And writing quality profile file exists at the company profile location

  # --- Incremental Update / Merge ---

  Scenario: Adding practices to existing quality preferences preserves originals
    Given quality preferences file already exists with 3 practices to replicate
    When 2 new practices to replicate are added
    And the updated quality preferences are saved
    Then quality preferences file contains 5 practices to replicate
    And the updated timestamp is more recent than the original

  Scenario: Adding proposal ratings to existing winning patterns preserves originals
    Given winning patterns file already exists with 2 proposal ratings
    When 1 new proposal rating is added
    And the updated winning patterns are saved
    Then winning patterns file contains 3 proposal ratings
    And the updated timestamp is more recent than the original

  Scenario: Adding feedback entries to existing writing quality profile preserves originals
    Given writing quality profile already exists with 2 feedback entries
    When 1 new feedback entry is added
    And the updated writing quality profile is saved
    Then writing quality profile contains 3 feedback entries
    And the updated timestamp is more recent than the original

  # --- Error Paths ---

  Scenario: Saving artifact when directory does not exist creates it
    Given the quality artifact directory does not exist
    When quality preferences are saved
    Then the directory is created
    And the quality preferences file is written successfully

  Scenario: Loading quality preferences when file does not exist reports absence
    Given no quality preferences file exists
    When the system checks for existing quality preferences
    Then the system reports no quality preferences found

  Scenario: Loading winning patterns when file does not exist reports absence
    Given no winning patterns file exists
    When the system checks for existing winning patterns
    Then the system reports no winning patterns found

  Scenario: Loading writing quality profile when file does not exist reports absence
    Given no writing quality profile file exists
    When the system checks for existing writing quality profile
    Then the system reports no writing quality profile found

  @property
  Scenario: Quality preferences roundtrip preserves all data exactly
    Given any valid quality preferences artifact
    When the artifact is saved and then loaded
    Then the loaded artifact matches the original exactly

  @property
  Scenario: Winning patterns roundtrip preserves all data exactly
    Given any valid winning patterns artifact
    When the artifact is saved and then loaded
    Then the loaded artifact matches the original exactly

  @property
  Scenario: Writing quality profile roundtrip preserves all data exactly
    Given any valid writing quality profile artifact
    When the artifact is saved and then loaded
    Then the loaded artifact matches the original exactly
