Feature: Debrief Request Letter Draft (US-016)
  As an engineer whose proposal was not selected
  I want a ready-to-send debrief request letter with minimal effort
  So I do not skip requesting a debrief due to administrative friction

  Background:
    Given the proposal plugin is active
    And Phil has a submitted proposal for AF243-001

  # --- Happy Path ---

  Scenario: Generate debrief request letter for DoD submission
    Given AF243-001 was not selected
    And the submission confirmation is "DSIP-2026-AF243-001-7842"
    When Phil requests a debrief letter draft
    Then the tool generates a letter referencing AF243-001 and the confirmation number
    And the letter cites FAR 15.505(a)(1)
    And the draft is written to the learning artifacts directory

  Scenario: Generate debrief request for NASA submission
    Given N244-012 was submitted to NSPIRES and not selected
    When Phil requests a debrief letter draft
    Then the tool generates a letter using NASA-specific debrief procedures

  # --- Edge Case ---

  Scenario: Skip debrief request
    Given AF243-001 was not selected
    When Phil decides not to request a debrief
    Then the tool records "debrief not requested"
    And proceeds to outcome recording without creating a request letter
