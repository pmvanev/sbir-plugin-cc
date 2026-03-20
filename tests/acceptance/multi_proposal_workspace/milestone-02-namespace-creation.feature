Feature: Per-Proposal Namespace Creation and Legacy Migration
  As a solo SBIR proposal writer
  I want to start additional proposals in my workspace
  So that I can evaluate new solicitations without disrupting existing work

  Background:
    Given a workspace root directory exists

  # --- Happy Path: Create Additional Proposal ---

  @us-mpw-001
  Scenario: Second proposal creates isolated namespace
    Given Phil has a multi-proposal workspace with active proposal "af263-042"
    And the proposal "af263-042" has state with topic title "Compact Directed Energy"
    When Phil creates a new proposal with topic ID "n244-012"
    Then the state directory for "n244-012" exists under the proposals directory
    And the artifact directory for "n244-012" exists
    And the active proposal is now "n244-012"

  @us-mpw-001
  Scenario: Existing proposal state unchanged after new proposal creation
    Given Phil has a multi-proposal workspace with active proposal "af263-042"
    And the proposal "af263-042" has state with topic title "Compact Directed Energy"
    And the "af263-042" state file checksum is recorded
    When Phil creates a new proposal with topic ID "n244-012"
    Then the "af263-042" state file checksum is unchanged

  @us-mpw-001
  Scenario: First proposal in fresh workspace uses multi-proposal layout
    Given Phil has a fresh workspace with no proposals
    When Phil creates a new proposal with topic ID "af263-042"
    Then the state directory for "af263-042" exists under the proposals directory
    And the active proposal file contains "af263-042"
    And no root-level proposal state file exists

  @us-mpw-001
  Scenario: New proposal state contains correct topic ID
    Given Phil has a multi-proposal workspace with active proposal "af263-042"
    When Phil creates a new proposal with topic ID "n244-012"
    Then the "n244-012" proposal state contains topic ID "N244-012"

  @us-mpw-001
  Scenario: Custom namespace via name override
    Given Phil has a multi-proposal workspace with active proposal "af263-042"
    When Phil creates a new proposal with topic ID "af263-042" and name "af263-042-resub"
    Then the state directory for "af263-042-resub" exists under the proposals directory
    And the "af263-042-resub" proposal state records original topic ID "AF263-042"
    And the "af263-042-resub" proposal state records namespace "af263-042-resub"

  # --- Error Paths: Namespace Creation ---

  @us-mpw-001
  Scenario: Namespace collision with existing proposal produces error
    Given Phil has a multi-proposal workspace with active proposal "af263-042"
    When Phil creates a new proposal with topic ID "af263-042"
    Then the creation fails with error mentioning "af263-042" already exists
    And the error suggests using a custom name flag
    And no new files are created in the workspace

  @us-mpw-001
  Scenario: Custom name collision also produces error
    Given Phil has a multi-proposal workspace with proposals "af263-042" and "af263-042-resub"
    When Phil creates a new proposal with topic ID "af263-042" and name "af263-042-resub"
    Then the creation fails with error mentioning "af263-042-resub" already exists

  # --- Legacy Migration ---

  @us-mpw-005
  Scenario: Legacy workspace works unchanged without migration
    Given Phil has a legacy workspace with proposal state at the root level
    And root-level artifacts exist for wave 3
    When the workspace layout is detected
    Then the layout is "legacy"
    And the proposals directory does not exist

  @us-mpw-005
  Scenario: Migration moves state to namespaced directory
    Given Phil has a legacy workspace with proposal "af263-042" at the root level
    When Phil migrates the legacy workspace
    Then the state directory for "af263-042" exists under the proposals directory
    And the active proposal file contains "af263-042"

  @us-mpw-005
  Scenario: Migration preserves original state file as safety net
    Given Phil has a legacy workspace with proposal "af263-042" at the root level
    When Phil migrates the legacy workspace
    Then the original root state file is preserved with migrated suffix
    And the migrated-suffix file contains the original proposal data

  @us-mpw-005
  Scenario: Migration moves artifacts to namespaced directory
    Given Phil has a legacy workspace with proposal "af263-042" at the root level
    And root-level artifacts exist for wave 1 and wave 3
    When Phil migrates the legacy workspace
    Then wave 1 artifacts exist under the "af263-042" artifact namespace
    And wave 3 artifacts exist under the "af263-042" artifact namespace

  @us-mpw-005
  Scenario: Migration preserves audit log
    Given Phil has a legacy workspace with proposal "af263-042" at the root level
    And root-level audit log exists
    When Phil migrates the legacy workspace
    Then the audit log exists under the "af263-042" proposal namespace

  # --- Property-Shaped ---

  @us-mpw-001 @property
  Scenario: Creating any number of proposals never corrupts existing state
    Given Phil has a multi-proposal workspace with 3 existing proposals
    When Phil creates 2 additional proposals
    Then all 5 proposal state files are valid and independently readable

  @us-mpw-005 @property
  Scenario: Migration is reversible by removing migrated suffix
    Given Phil has a legacy workspace that was migrated
    When the migrated-suffix file is restored to its original name
    And the proposals directory is removed
    Then the workspace is detected as legacy layout
