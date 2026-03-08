Feature: PES Foundation -- Enforcement System (US-006)
  As an engineer working across multiple sessions
  I want structural guarantees that process integrity is maintained
  So I never skip critical steps or lose work to session crashes

  Background:
    Given the proposal plugin is active

  # --- Session Startup ---

  Scenario: Session startup integrity check detects orphaned draft
    Given Phil's last session ended unexpectedly
    And a draft file exists for section 3.2 without a compliance matrix entry
    When Phil starts a new session
    Then the enforcement system detects the orphaned draft
    And Phil sees "Section 3.2 draft exists but has no compliance matrix entry"
    And Phil sees guidance to run the compliance check

  Scenario: Session startup with clean state is silent
    Given the proposal state is consistent with no orphaned files
    When Phil starts a new session
    Then the enforcement system runs silently
    And no warnings are displayed

  Scenario: Session startup detects deadline proximity
    Given Phil has an active proposal with 3 days remaining
    When Phil starts a new session
    Then Phil sees a critical deadline warning
    And Phil sees suggestions for prioritizing remaining work

  # --- Wave Ordering ---

  Scenario: Wave ordering blocks Wave 1 before Go decision
    Given Phil has an active proposal with Go/No-Go "pending"
    When Phil attempts to start Wave 1 strategy work
    Then the enforcement system blocks the action
    And Phil sees "Wave 1 requires Go decision in Wave 0"

  Scenario: Wave ordering allows Wave 1 after Go decision
    Given Phil has an active proposal with Go/No-Go "go"
    When Phil starts Wave 1 strategy work
    Then the action proceeds normally

  Scenario: Wave ordering blocks Wave 2 before strategy approval
    Given Phil has an active proposal in Wave 1
    And the strategy brief has not been approved
    When Phil attempts to start Wave 2 work
    Then the enforcement system blocks the action
    And Phil sees "Wave 2 requires strategy brief approval in Wave 1"

  # --- Compliance Gate ---

  Scenario: Compliance gate blocks drafting without matrix entry
    Given Phil has an active proposal with a compliance matrix
    And no matrix entry covers section 3.2
    When Phil attempts to draft section 3.2
    Then the enforcement system blocks the action
    And Phil sees "No compliance matrix entry covers section 3.2"
    And Phil sees guidance to add a compliance item

  # --- Audit ---

  Scenario: Enforcement decisions are recorded in audit log
    Given Phil has an active proposal with Go/No-Go "pending"
    When Phil attempts to start Wave 1 strategy work
    Then the enforcement system blocks the action
    And the block decision is recorded in the audit log with a timestamp

  # --- Extensibility ---

  @property
  Scenario: New enforcement rules can be added without engine changes
    Given any new enforcement rule defined in the configuration
    When the enforcement engine loads rules
    Then the new rule is evaluated alongside existing rules
    And the engine architecture remains unchanged

  # --- Error Paths ---

  Scenario: Enforcement system handles missing configuration gracefully
    Given the enforcement configuration file does not exist
    When the enforcement system attempts to load rules
    Then the system uses default enforcement rules
    And Phil sees a warning that the configuration was not found

  Scenario: Enforcement system handles corrupted state during checks
    Given the proposal state file is corrupted
    When the enforcement system runs its integrity check
    Then Phil sees "Proposal state appears corrupted"
    And Phil sees guidance for recovery
