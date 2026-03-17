Feature: Submission Immutability Enforcement (US-PEW-003)
  As Phil Santos, sometimes re-opening a project after submission,
  I want the system to block all modifications to a submitted proposal
  So that submitted artifacts remain consistent with what was delivered to the agency

  # --- Happy Path ---

  Scenario: Writes allowed when proposal is still in draft
    Given Phil's proposal "AF243-001" has submission status "draft" and is not finalized
    And the enforcement rules are loaded from the standard configuration
    When Phil attempts any action on the proposal
    Then the action is allowed

  # --- Error Paths ---

  Scenario: All modifications blocked after submission and finalization
    Given Phil's proposal "AF243-001" has been submitted and marked as finalized
    And the enforcement rules are loaded from the standard configuration
    When Phil attempts any action on the proposal
    Then the action is blocked
    And Phil sees "Proposal AF243-001 is submitted. Artifacts are read-only."

  Scenario: Submitted but not finalized still allows writes
    Given Phil's proposal "AF243-001" has submission status "submitted" but is not marked finalized
    And the enforcement rules are loaded from the standard configuration
    When Phil attempts any action on the proposal
    Then the action is allowed

  # --- Boundary/Edge ---

  Scenario: Missing submission field allows writes
    Given Phil's proposal "AF243-001" has no submission information
    And the enforcement rules are loaded from the standard configuration
    When Phil attempts any action on the proposal
    Then the action is allowed

  Scenario: Block message uses default text when proposal identifier is unavailable
    Given Phil's proposal has been submitted and finalized but has no topic identifier
    And the enforcement rules are loaded from the standard configuration
    When Phil attempts any action on the proposal
    Then the action is blocked
    And the block reason uses the configured default message
