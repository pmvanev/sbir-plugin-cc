Feature: Simplified Compliance Check Command (US-008)
  As an engineer mid-proposal
  I want a quick compliance health check
  So I know my coverage status without opening files

  Background:
    Given the proposal plugin is active

  # --- Happy Path ---

  Scenario: Compliance check reports full coverage breakdown
    Given a compliance matrix exists with 47 items
    And 32 items are covered, 5 partial, 8 missing, and 2 waived
    When Phil runs the compliance check
    Then Phil sees "47 items | 32 covered | 5 partial | 8 missing | 2 waived"

  Scenario: Compliance check on fresh matrix shows all not started
    Given a compliance matrix was just generated with 47 items
    When Phil runs the compliance check
    Then Phil sees "47 items | 0 covered | 0 partial | 47 not started | 0 waived"

  # --- Error Paths ---

  Scenario: Compliance check with no matrix
    Given no compliance matrix exists
    When Phil runs the compliance check
    Then Phil sees "No compliance matrix found"
    And Phil sees guidance to generate one with the strategy wave command

  Scenario: Compliance check with malformed matrix file
    Given the compliance matrix file exists but has invalid formatting
    When Phil runs the compliance check
    Then Phil sees "Could not parse compliance matrix"
    And Phil sees guidance to verify the file format
