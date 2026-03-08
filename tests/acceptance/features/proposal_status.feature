Feature: Proposal Status and Reorientation (US-001)
  As an engineer returning to a proposal after days away
  I want to see the complete state in seconds
  So I regain context without digging through files

  Background:
    Given the proposal plugin is active

  # --- Happy Path ---

  Scenario: Status shows current wave, progress, and deadline
    Given Phil has an active proposal for topic AF243-001 in Wave 1
    And 18 days remain until the deadline
    When Phil checks proposal status
    Then Phil sees the current wave as "Wave 1: Requirements & Strategy"
    And Phil sees "18 days to deadline"

  Scenario: Status shows pending async events
    Given Phil has an active proposal for AF243-001
    And TPOC questions were generated 5 days ago with status "pending"
    When Phil checks proposal status
    Then Phil sees "TPOC questions generated -- PENDING CALL"
    And Phil sees the suggested next action "Have TPOC call, then /proposal tpoc ingest"

  Scenario: Status shows completed waves and per-wave detail
    Given Phil has an active proposal with Wave 0 completed with Go approved
    And Wave 1 is active with strategy brief not yet started
    When Phil checks proposal status
    Then Wave 0 shows as completed with "Go: approved"
    And Wave 1 shows as active with detail for each sub-task
    And subsequent waves show as "not started"

  # --- Edge Cases ---

  Scenario: Status shows deadline warning at critical threshold
    Given Phil has an active proposal for topic N244-012 in Wave 4
    And 4 days remain until the deadline
    When Phil checks proposal status
    Then Phil sees a deadline warning "4 days remaining -- critical threshold"
    And Phil sees suggestions to prioritize the highest-impact incomplete work

  # --- Error Paths ---

  Scenario: Status with no active proposal
    Given no proposal exists in the current directory
    When Phil checks proposal status
    Then Phil sees "No active proposal found"
    And Phil sees the suggestion to start with "/proposal new"
