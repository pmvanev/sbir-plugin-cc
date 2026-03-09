Feature: Wave Names and Cross-Cutting State Expansion (C2 Foundation)
  As an engineer working through a multi-wave proposal
  I want accurate wave names and expanded state tracking for all 10 waves
  So I can orient myself and track progress across the full proposal lifecycle

  Background:
    Given the proposal plugin is active

  # --- Happy Path ---

  Scenario: Status displays correct names for all 10 waves
    Given Phil has an active proposal for AF243-001 with waves 0 through 9 initialized
    When Phil checks proposal status
    Then Phil sees "Wave 0: Intelligence & Fit"
    And Phil sees "Wave 1: Requirements & Strategy"
    And Phil sees "Wave 2: Research"
    And Phil sees "Wave 3: Discrimination & Outline"
    And Phil sees "Wave 4: Drafting"
    And Phil sees "Wave 5: Visual Assets"
    And Phil sees "Wave 6: Formatting & Assembly"
    And Phil sees "Wave 7: Final Review"
    And Phil sees "Wave 8: Submission"
    And Phil sees "Wave 9: Debrief & Learning"

  @skip
  Scenario: Expanded state includes research summary tracking
    Given Phil has an active proposal in Wave 2
    When Phil checks the proposal state
    Then the state includes a research summary section
    And the research summary tracks technical landscape, patent notes, prior awards, market research, commercialization pathway, and TRL refinement

  @skip
  Scenario: Expanded state includes discrimination table tracking
    Given Phil has an active proposal in Wave 3
    When Phil checks the proposal state
    Then the state includes a discrimination table section
    And the discrimination table tracks company, technical, and team discriminators

  @skip
  Scenario: Expanded state includes volumes tracking
    Given Phil has an active proposal in Wave 4
    When Phil checks the proposal state
    Then the state includes a volumes section
    And the volumes section tracks each proposal section with draft status and page count

  @skip
  Scenario: Expanded state includes open review items tracking
    Given Phil has an active proposal in Wave 4
    When Phil checks the proposal state
    Then the state includes an open review items section
    And review items track location, severity, and resolution status

  # --- Error Paths ---

  Scenario: Status handles unknown wave number gracefully
    Given Phil has an active proposal with current wave set to 99
    When Phil checks proposal status
    Then Phil sees "Wave 99" as the current wave name
    And no error is raised

  Scenario: Status handles missing wave entries in state
    Given Phil has an active proposal with no wave entries in the state
    When Phil checks proposal status
    Then Phil sees progress with zero waves completed
    And no error is raised
