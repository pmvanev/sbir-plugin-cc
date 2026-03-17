Feature: Winning Pattern Confidence Levels
  As a proposal author reviewing quality intelligence
  I want confidence levels that reflect the size of my win corpus
  So that I know how much to trust the winning patterns

  # --- Happy Path: Confidence Tiers ---

  Scenario: Confidence is low when fewer than 10 wins are analyzed
    Given winning patterns assembled from 3 winning proposals
    When confidence level is calculated
    Then confidence level is "low"

  Scenario: Confidence is low at boundary of 9 wins
    Given winning patterns assembled from 9 winning proposals
    When confidence level is calculated
    Then confidence level is "low"

  Scenario: Confidence is medium when 10 or more wins are analyzed
    Given winning patterns assembled from 10 winning proposals
    When confidence level is calculated
    Then confidence level is "medium"

  Scenario: Confidence is medium at boundary of 19 wins
    Given winning patterns assembled from 19 winning proposals
    When confidence level is calculated
    Then confidence level is "medium"

  Scenario: Confidence is high when 20 or more wins are analyzed
    Given winning patterns assembled from 20 winning proposals
    When confidence level is calculated
    Then confidence level is "high"

  # --- Edge Cases ---

  Scenario: Confidence is low with zero wins
    Given winning patterns assembled from 0 winning proposals
    When confidence level is calculated
    Then confidence level is "low"

  Scenario: Confidence recalculates after adding wins
    Given winning patterns with confidence "low" from 7 wins
    When 3 new winning proposals are added
    And confidence level is recalculated
    Then confidence level is "medium"
    And win count is 10

  # --- Error Path ---

  Scenario: Negative win count is not valid
    Given a winning patterns artifact with win count -1
    When the artifact is validated
    Then validation fails because win count must not be negative
