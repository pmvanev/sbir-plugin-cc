Feature: Rigor Profile Validation and Registry
  As an SBIR proposal author
  I want profile names validated against known profiles
  So that typos and invalid names are caught before any state changes

  Background:
    Given the plugin provides four rigor profiles: lean, standard, thorough, exhaustive

  # --- Happy Path ---

  Scenario: Valid profile name is accepted
    Given Elena has an active proposal "AF243-001" at "standard" rigor
    When Elena sets the rigor to "thorough"
    Then the active rigor profile is "thorough"

  Scenario: All four profile names are recognized
    When each profile name is validated: "lean", "standard", "thorough", "exhaustive"
    Then all four are accepted as valid

  # --- Error Paths ---

  Scenario: Unknown profile name is rejected with available options
    Given Elena has an active proposal "AF243-001" at "standard" rigor
    When Elena sets the rigor to "ultra"
    Then the operation fails with an invalid profile error
    And the error message includes "ultra"
    And the error lists available profiles: lean, standard, thorough, exhaustive

  Scenario: Empty profile name is rejected
    Given Elena has an active proposal "AF243-001" at "standard" rigor
    When Elena sets the rigor to ""
    Then the operation fails with an invalid profile error

  Scenario: Profile name validation is case-sensitive
    Given Elena has an active proposal "AF243-001" at "standard" rigor
    When Elena sets the rigor to "Thorough"
    Then the operation fails with an invalid profile error
    And the error lists available profiles: lean, standard, thorough, exhaustive

  # --- Boundary ---

  Scenario: Profile definitions include all eight agent roles
    When the "thorough" profile definition is loaded
    Then the profile includes model tier for strategist
    And the profile includes model tier for writer
    And the profile includes model tier for reviewer
    And the profile includes model tier for researcher
    And the profile includes model tier for orchestrator
    And the profile includes model tier for compliance
    And the profile includes model tier for analyst
    And the profile includes model tier for formatter

  Scenario: Each profile defines valid model tiers only
    When all profile definitions are loaded
    Then every model tier value is one of: basic, standard, strongest
