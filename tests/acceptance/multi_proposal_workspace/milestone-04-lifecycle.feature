Feature: Completed Proposal Lifecycle Management
  As a solo SBIR proposal writer with a mix of active and completed proposals
  I want completed proposals separated from active ones
  So that I can focus on deadlines without clutter from past submissions

  Background:
    Given a workspace root directory exists

  # --- Happy Path ---

  @us-mpw-006
  Scenario: Auto-switch to sole remaining active proposal after submission
    Given Phil has a multi-proposal workspace with proposals "af263-042" and "n244-012"
    And the active proposal is "af263-042"
    And the proposal "n244-012" is marked as active
    When proposal "af263-042" is marked as completed
    And auto-switch logic is evaluated
    Then the active proposal is now "n244-012"

  @us-mpw-006
  Scenario: All proposals completed shows no active proposal
    Given Phil has a multi-proposal workspace with proposals "af263-042" and "n244-012"
    And both proposals are marked as completed
    When the active proposals are enumerated
    Then the active proposal count is 0
    And the completed proposal count is 2

  @us-mpw-006
  Scenario: Completed proposal remains accessible for debrief
    Given Phil has a multi-proposal workspace with proposals "af263-042" and "n244-012"
    And the proposal "af263-042" is marked as completed
    When Phil switches to proposal "af263-042"
    Then the active proposal file contains "af263-042"
    And the "af263-042" proposal state is fully readable

  # --- Edge Cases ---

  @us-mpw-006
  Scenario: Multiple active proposals remain after one completes -- no auto-switch
    Given Phil has a multi-proposal workspace with proposals "af263-042", "n244-012", and "da-26-003"
    And the active proposal is "af263-042"
    And proposals "n244-012" and "da-26-003" are marked as active
    When proposal "af263-042" is marked as completed
    And auto-switch logic is evaluated
    Then the active proposal is not automatically changed
    And 2 active proposals are available for selection

  @us-mpw-006
  Scenario: Proposal completed via no-go decision is treated as completed
    Given Phil has a multi-proposal workspace with proposals "af263-042" and "n244-012"
    And the active proposal is "af263-042"
    And the proposal "af263-042" has go-no-go set to "no-go"
    When the completion status of "af263-042" is checked
    Then the proposal "af263-042" is classified as completed

  @us-mpw-006
  Scenario: Proposal completed via archive flag is treated as completed
    Given Phil has a multi-proposal workspace with proposals "af263-042" and "n244-012"
    And the proposal "af263-042" has archived set to true
    When the completion status of "af263-042" is checked
    Then the proposal "af263-042" is classified as completed

  # --- Error Path ---

  @us-mpw-006
  Scenario: Auto-switch with zero remaining active proposals does not crash
    Given Phil has a multi-proposal workspace with only proposal "af263-042"
    And the active proposal is "af263-042"
    When proposal "af263-042" is marked as completed
    And auto-switch logic is evaluated
    Then no auto-switch occurs
    And the result indicates all proposals are completed
