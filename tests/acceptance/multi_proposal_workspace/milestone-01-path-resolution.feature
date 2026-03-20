Feature: Proposal-Scoped Path Resolution
  As a solo SBIR proposal writer
  I want all commands to resolve paths for the correct proposal
  So that state reads and artifact writes never cross proposal boundaries

  Background:
    Given a workspace root directory exists

  # --- Happy Path ---

  @us-mpw-004
  Scenario: Multi-proposal layout detected when proposals directory exists
    Given the workspace contains a proposals directory with "af263-042"
    And the active proposal file contains "af263-042"
    When the workspace layout is detected
    Then the layout is "multi"
    And the active proposal ID is "af263-042"

  @us-mpw-004
  Scenario: State directory derived from active proposal
    Given Phil has a multi-proposal workspace with proposals "af263-042" and "n244-012"
    And the active proposal is "af263-042"
    When Phil requests the workspace paths
    Then the state directory ends with "proposals/af263-042"

  @us-mpw-004
  Scenario: Artifact base directory derived from active proposal
    Given Phil has a multi-proposal workspace with proposals "af263-042" and "n244-012"
    And the active proposal is "af263-042"
    When Phil requests the workspace paths
    Then the artifact base directory ends with "af263-042"

  @us-mpw-004
  Scenario: Audit directory scoped to active proposal
    Given Phil has a multi-proposal workspace with proposals "af263-042" and "n244-012"
    And the active proposal is "af263-042"
    When Phil requests the workspace paths
    Then the audit directory ends with "proposals/af263-042/audit"

  # --- Legacy Fallback ---

  @us-mpw-004 @us-mpw-005
  Scenario: Legacy layout detected when only root state file exists
    Given the workspace contains proposal state at the root level
    And no proposals directory exists
    When the workspace layout is detected
    Then the layout is "legacy"

  @us-mpw-004 @us-mpw-005
  Scenario: Legacy workspace returns root-level state directory
    Given Phil has a legacy workspace with proposal state at the root level
    When Phil requests the workspace paths
    Then the state directory is the root workspace directory
    And the active proposal ID is absent

  @us-mpw-004 @us-mpw-005
  Scenario: Legacy workspace returns root-level artifact directory
    Given Phil has a legacy workspace with proposal state at the root level
    When Phil requests the workspace paths
    Then the artifact base directory is the root artifact directory

  # --- Fresh Workspace ---

  @us-mpw-004
  Scenario: Fresh workspace detected when neither layout exists
    Given the workspace has no proposal state and no proposals directory
    When the workspace layout is detected
    Then the layout is "fresh"

  # --- Error Paths ---

  @us-mpw-004
  Scenario: Missing active-proposal file in multi-proposal workspace produces error
    Given the workspace contains a proposals directory with "af263-042" and "n244-012"
    And the active proposal file does not exist
    When Phil requests the workspace paths
    Then an error is returned indicating no active proposal is selected
    And the error lists available proposals "af263-042" and "n244-012"

  @us-mpw-004
  Scenario: Active proposal file references nonexistent proposal
    Given the workspace contains a proposals directory with "af263-042"
    And the active proposal file contains "xyz-999"
    When Phil requests the workspace paths
    Then an error is returned indicating the active proposal does not exist
    And the error lists available proposals including "af263-042"

  @us-mpw-004
  Scenario: Empty active-proposal file produces error
    Given the workspace contains a proposals directory with "af263-042"
    And the active proposal file is empty
    When Phil requests the workspace paths
    Then an error is returned indicating no active proposal is selected

  @us-mpw-004
  Scenario: Active proposal file with whitespace-only content produces error
    Given the workspace contains a proposals directory with "af263-042"
    And the active proposal file contains only whitespace
    When Phil requests the workspace paths
    Then an error is returned indicating no active proposal is selected

  # --- Property-Shaped ---

  @us-mpw-004 @property
  Scenario: Path resolution is consistent across repeated calls
    Given Phil has a multi-proposal workspace with active proposal "af263-042"
    When Phil requests the workspace paths multiple times
    Then every result returns identical state and artifact directories
