Feature: Rigor Profile Diff Computation
  As an SBIR proposal author changing rigor mid-proposal
  I want to see exactly what changed between the old and new profiles
  So that I understand the impact of the quality/cost tradeoff

  # --- Happy Path ---

  @skip
  Scenario: Diff from standard to thorough shows role-level changes
    When a diff is computed from "standard" to "thorough"
    Then the diff includes the writer role changing from "standard" to "strongest"
    And the diff includes the strategist role changing from "standard" to "strongest"
    And the diff includes critique iterations changing from 2 to 3

  @skip
  Scenario: Diff from standard to lean shows downgrade to basic
    When a diff is computed from "standard" to "lean"
    Then the diff includes the writer role changing from "standard" to "basic"
    And the diff includes review passes changing from 2 to 1
    And the diff includes critique iterations changing from 2 to 0

  @skip
  Scenario: Diff from thorough to exhaustive shows targeted upgrades
    When a diff is computed from "thorough" to "exhaustive"
    Then the diff includes review passes changing from 2 to 3
    And the diff includes critique iterations changing from 3 to 4
    And the diff includes the researcher role changing from "standard" to "strongest"

  # --- Edge Cases ---

  @skip
  Scenario: Diff between same profile produces no changes
    When a diff is computed from "standard" to "standard"
    Then the diff contains zero changes

  @skip
  Scenario: Diff includes only roles that actually changed
    When a diff is computed from "standard" to "thorough"
    Then the diff does not include the formatter role
    And the diff does not include the topic-scout role

  # --- Error Path ---

  @skip
  Scenario: Diff with invalid profile name fails gracefully
    When a diff is computed from "standard" to "ultra"
    Then the diff operation fails with an invalid profile error
