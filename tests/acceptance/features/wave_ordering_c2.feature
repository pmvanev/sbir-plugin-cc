Feature: Wave Ordering for Waves 2-4 (C2 Enforcement)
  As an engineer progressing through proposal waves
  I want the enforcement system to validate prerequisites for Waves 2-4
  So I cannot skip required steps and lose work quality

  Background:
    Given the proposal plugin is active

  # --- Happy Path ---

  @skip
  Scenario: Wave 2 allowed after strategy brief approval
    Given Phil has an active proposal with an approved strategy brief
    When Phil starts Wave 2 research work
    Then the action proceeds normally

  @skip
  Scenario: Wave 3 allowed after research review approval
    Given Phil has an active proposal with approved research review
    When Phil starts Wave 3 discrimination and outline work
    Then the action proceeds normally

  @skip
  Scenario: Wave 4 allowed after outline approval
    Given Phil has an active proposal with an approved proposal outline
    When Phil starts Wave 4 drafting work
    Then the action proceeds normally

  # --- Error Paths ---

  @skip
  Scenario: Wave 2 blocked before strategy brief approval
    Given Phil has an active proposal in Wave 1
    And the strategy brief has not been approved
    When Phil attempts to start Wave 2 research work
    Then the enforcement system blocks the action
    And Phil sees "Wave 2 requires strategy brief approval in Wave 1"

  @skip
  Scenario: Wave 3 blocked before research review approval
    Given Phil has an active proposal in Wave 2
    And the research review has not been approved
    When Phil attempts to start Wave 3 work
    Then the enforcement system blocks the action
    And Phil sees "Wave 3 requires research review approval in Wave 2"

  @skip
  Scenario: Wave 4 blocked before outline approval
    Given Phil has an active proposal in Wave 3
    And the proposal outline has not been approved
    When Phil attempts to start Wave 4 drafting work
    Then the enforcement system blocks the action
    And Phil sees "Wave 4 requires outline approval in Wave 3"

  @skip
  Scenario: Wave ordering blocks skipping from Wave 1 directly to Wave 3
    Given Phil has an active proposal in Wave 1
    When Phil attempts to start Wave 3 work
    Then the enforcement system blocks the action
    And Phil sees guidance about completing prerequisite waves

  @skip
  Scenario: Wave ordering blocks skipping from Wave 2 directly to Wave 4
    Given Phil has an active proposal in Wave 2
    When Phil attempts to start Wave 4 drafting work
    Then the enforcement system blocks the action
    And Phil sees guidance about completing prerequisite waves

  # --- Edge Cases ---

  @skip
  Scenario: Enforcement decisions for Waves 2-4 are recorded in audit log
    Given Phil has an active proposal in Wave 1
    And the strategy brief has not been approved
    When Phil attempts to start Wave 2 research work
    Then the block decision is recorded in the audit log with a timestamp
    And the audit entry includes the rule "wave-2-requires-strategy"
