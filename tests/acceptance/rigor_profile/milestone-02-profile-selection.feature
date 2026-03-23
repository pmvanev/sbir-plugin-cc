Feature: Rigor Profile Selection and Persistence
  As an SBIR proposal author
  I want to select a rigor profile for my active proposal
  So that subsequent waves execute at the configured quality level

  # --- Happy Path ---

  @skip
  Scenario: Set thorough profile and view per-role diff
    Given Elena has an active proposal "AF243-001" at "standard" rigor
    When Elena sets the rigor to "thorough"
    Then the active rigor profile is "thorough"
    And the diff shows writer model changed from "standard" to "strongest"
    And the diff shows reviewer model changed from "standard" to "strongest"
    And the diff shows critique iterations changed from 2 to 3

  @skip
  Scenario: Set lean profile for cost-conscious screening
    Given Marcus has an active proposal "N244-015" at "standard" rigor
    When Marcus sets the rigor to "lean"
    Then the active rigor profile is "lean"
    And the diff shows all agent roles changed to "basic" model tier

  @skip
  Scenario: History entry records from, to, timestamp, and wave
    Given Elena has an active proposal "AF243-001" at "standard" rigor on wave 3
    When Elena sets the rigor to "thorough"
    Then the history contains an entry with from "standard" and to "thorough"
    And the history entry includes wave number 3
    And the history entry includes a timestamp

  # --- Error Paths ---

  @skip
  Scenario: No active proposal returns guidance
    Given no proposal is currently active
    When the user attempts to set rigor to "thorough"
    Then the operation fails with a no-active-proposal error

  @skip
  Scenario: Same profile is a no-op with no history entry
    Given Elena has an active proposal "AF243-001" at "thorough" rigor
    When Elena sets the rigor to "thorough"
    Then the operation confirms rigor is already "thorough"
    And no history entry is appended
    And the rigor state file is not modified

  # --- Edge Cases ---

  @skip
  Scenario: Multiple rigor changes accumulate in history
    Given Elena has an active proposal "AF243-001" at "standard" rigor on wave 0
    When Elena sets the rigor to "thorough"
    And Elena sets the rigor to "exhaustive"
    Then the history contains 2 entries
    And the first entry records standard to thorough
    And the second entry records thorough to exhaustive

  @skip
  Scenario: Downgrade from exhaustive to lean is permitted
    Given Elena has an active proposal "AF243-001" at "exhaustive" rigor
    When Elena sets the rigor to "lean"
    Then the active rigor profile is "lean"
    And the diff shows all agent roles changed to "basic" model tier
