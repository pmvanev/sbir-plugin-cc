Feature: Switch Active Proposal Context
  As a solo SBIR proposal writer with multiple proposals
  I want to switch which proposal my commands operate on
  So that I can redirect my attention without confusion about which proposal is active

  Background:
    Given a workspace root directory exists

  # --- Happy Path ---

  @us-mpw-003
  Scenario: Switch updates active proposal pointer
    Given Phil has a multi-proposal workspace with proposals "af263-042" and "n244-012"
    And the active proposal is "n244-012"
    When Phil switches to proposal "af263-042"
    Then the active proposal file contains "af263-042"

  @us-mpw-003
  Scenario: Switch to completed proposal for debrief access
    Given Phil has a multi-proposal workspace with proposals "af263-042" and "n244-012"
    And the proposal "af263-042" is marked as completed
    And the active proposal is "n244-012"
    When Phil switches to proposal "af263-042"
    Then the active proposal file contains "af263-042"

  @us-mpw-003
  Scenario: Path resolution reflects switched proposal
    Given Phil has a multi-proposal workspace with proposals "af263-042" and "n244-012"
    And the active proposal is "n244-012"
    When Phil switches to proposal "af263-042"
    And Phil requests the workspace paths
    Then the state directory points to the "af263-042" proposal namespace
    And the artifact directory points to the "af263-042" artifact namespace

  # --- Idempotent Switch ---

  @us-mpw-003
  Scenario: Switching to already-active proposal is idempotent
    Given Phil has a multi-proposal workspace with proposals "af263-042" and "n244-012"
    And the active proposal is "af263-042"
    When Phil switches to proposal "af263-042"
    Then the active proposal file contains "af263-042"
    And the switch reports that the proposal is already active

  # --- Error Paths ---

  @us-mpw-003
  Scenario: Switch to nonexistent proposal produces error with available list
    Given Phil has a multi-proposal workspace with proposals "af263-042" and "n244-012"
    And the active proposal is "af263-042"
    When Phil switches to proposal "xyz-999"
    Then an error is returned indicating proposal "xyz-999" was not found
    And the error lists available proposals "af263-042" and "n244-012"
    And the active proposal file still contains "af263-042"

  @us-mpw-003
  Scenario: Switch in legacy workspace produces error
    Given Phil has a legacy workspace with proposal state at the root level
    When Phil attempts to switch proposals
    Then an error is returned indicating switching requires multi-proposal layout
