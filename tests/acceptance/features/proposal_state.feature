Feature: Proposal State Schema and Persistence (US-007)
  As an engineer working across multiple sessions
  I want reliable state that survives restarts without corruption
  So I never lose work or see inconsistent proposal state

  Background:
    Given the proposal plugin is active

  # --- Happy Path ---

  Scenario: State persists across sessions
    Given Phil completed the Go/No-Go decision for AF243-001
    And Phil closed the session
    When Phil opens a new session and checks proposal status
    Then Phil sees the exact state from the previous session
    And the Go/No-Go decision shows "go"
    And the deadline countdown is current

  Scenario: State saved after every meaningful action
    Given Phil has an active proposal for AF243-001
    When Phil completes a Go/No-Go decision of "go"
    Then the proposal state is persisted to disk immediately
    And the state file contains the Go/No-Go value "go"

  # --- Error Paths ---

  Scenario: Missing state file handled gracefully
    Given no proposal exists in the current directory
    When Phil checks proposal status
    Then Phil sees "No active proposal found"
    And Phil sees the suggestion to start with "/proposal new"

  @property
  Scenario: State file is never partially written
    Given any proposal state update is in progress
    When the update completes
    Then the state file is written atomically
    And a backup of the previous state exists

  Scenario: Corrupted state file detected and recovered
    Given the proposal state file was partially written due to a crash
    When Phil starts a new session
    Then the enforcement system detects the corruption
    And attempts recovery from the backup
    And Phil sees what was recovered or lost
