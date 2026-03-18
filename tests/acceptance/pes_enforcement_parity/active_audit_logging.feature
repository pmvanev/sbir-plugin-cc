Feature: Active Audit Logging
  As Phil Santos, a small business engineer preparing SBIR proposals,
  I want all enforcement decisions to be recorded in the audit log
  So that I have a complete trail of what was allowed, blocked, and why

  Background:
    Given the enforcement rules are loaded from the standard configuration

  # --- Happy Path Scenarios ---

  Scenario: Allowed action is recorded in the audit log
    Given Phil's proposal "AF243-001" is in Wave 4 drafting with all prerequisites met
    When Phil uses a drafting tool
    Then the action is allowed
    And the audit log contains an entry with decision "allow"
    And the audit entry includes the proposal identifier "AF243-001"

  Scenario: Blocked action is recorded with the block reason
    Given Phil's proposal "AF243-001" is in Wave 5 but pre-draft checklist items are incomplete
    When Phil attempts to begin Wave 5 work
    Then the action is blocked
    And the audit log contains an entry with decision "block"
    And the audit entry includes the block reason

  Scenario: Session start integrity check is recorded
    Given Phil's proposal "AF243-001" has a clean workspace
    When Phil starts a new session
    Then the audit log contains an entry for session start
    And the audit entry includes the proposal identifier "AF243-001"

  Scenario: Audit entries are written to the audit directory on disk
    Given Phil's proposal "AF243-001" is in Wave 4 drafting with all prerequisites met
    And active audit logging is enabled in the configuration
    When Phil uses a drafting tool
    Then an audit file exists in the proposal audit directory
    And the file contains a timestamped entry for the action

  # --- Error Path Scenarios ---

  Scenario: Audit logging failure does not block the enforcement decision
    Given Phil's proposal "AF243-001" is in Wave 4 drafting with all prerequisites met
    And the audit directory is not writable
    When Phil uses a drafting tool
    Then the action is allowed
    And a warning is logged about the audit write failure

  Scenario: Audit entry captures multiple block reasons when several rules trigger
    Given Phil's proposal "AF243-001" is submitted and near deadline
    When Phil attempts to begin Wave 5 work
    Then the action is blocked
    And the audit entry includes all block reasons

  Scenario: Audit log handles concurrent session starts without data loss
    Given Phil has two proposals "AF243-001" and "AF243-002" with separate audit directories
    When both proposals start sessions simultaneously
    Then each proposal has its own audit entry
    And no entries are lost or mixed between proposals

  # --- Boundary / Property Scenarios ---

  @property
  Scenario: Every enforcement decision produces exactly one audit entry
    Given any valid proposal state and any tool action
    When the enforcement system processes the action
    Then exactly one audit entry is produced
    And the entry contains a timestamp, decision, and proposal identifier

  @property
  Scenario: Audit entries are never retroactively modified
    Given any sequence of enforcement decisions
    When new decisions are recorded
    Then previously written audit entries remain unchanged
