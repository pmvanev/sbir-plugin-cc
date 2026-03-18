Feature: Session Start Housekeeping
  As Phil Santos, a small business engineer preparing SBIR proposals,
  I want the enforcement system to perform housekeeping at session start
  So that stale signals are cleaned up, audit logs are rotated, and
  my workspace stays healthy without manual intervention

  Background:
    Given the enforcement rules are loaded from the standard configuration

  # --- Happy Path Scenarios ---

  Scenario: Stale crash signal from previous session is removed
    Given Phil's previous session for proposal "AF243-001" ended abnormally leaving a crash signal
    When Phil starts a new session
    Then the stale crash signal is removed
    And the session start is recorded in the audit trail

  Scenario: Audit log is rotated when entries exceed the retention window
    Given Phil's proposal "AF243-001" has audit entries older than the 365-day retention window
    When Phil starts a new session
    Then audit entries older than 365 days are archived
    And current audit entries are preserved
    And the log rotation is recorded in the audit trail

  Scenario: Audit log file is rotated when it exceeds size limit
    Given Phil's proposal "AF243-001" has an audit log file larger than the size limit
    When Phil starts a new session
    Then the oversized log file is archived with a timestamp
    And a fresh audit log file is started
    And the file rotation is recorded in the audit trail

  # --- Error Path Scenarios ---

  Scenario: Multiple crash signals are cleaned up in a single session start
    Given Phil's previous session for proposal "AF243-001" left 3 crash signal files
    When Phil starts a new session
    Then all 3 crash signals are removed
    And each cleanup is recorded in the audit trail

  Scenario: Session start succeeds even when crash signal file is locked
    Given Phil's previous session for proposal "AF243-001" ended abnormally leaving a crash signal
    And the crash signal file is read-only
    When Phil starts a new session
    Then Phil sees a warning that the crash signal could not be removed
    And the session continues without blocking

  Scenario: Session start succeeds when no crash signals exist
    Given Phil's proposal "AF243-001" has a clean workspace with no crash signals
    When Phil starts a new session
    Then no cleanup actions are performed
    And the session start is recorded in the audit trail

  # --- Boundary / Edge Scenarios ---

  Scenario: Audit entries exactly at the retention boundary are preserved
    Given Phil's proposal "AF243-001" has audit entries from exactly 365 days ago
    When Phil starts a new session
    Then audit entries from exactly 365 days ago are preserved
    And no entries are archived

  Scenario: Audit entries one day past the retention boundary are archived
    Given Phil's proposal "AF243-001" has audit entries from 366 days ago
    When Phil starts a new session
    Then audit entries from 366 days ago are archived
    And recent entries are preserved
