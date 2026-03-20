Feature: Multi-Proposal Workspace Integration Checkpoints
  As a solo SBIR proposal writer
  I want all workspace components to agree on which proposal is active
  So that state reads and artifact writes never cross proposal boundaries

  Background:
    Given a workspace root directory exists

  # --- Checkpoint 1: Proposal Creation Isolation ---

  @integration @checkpoint-1
  Scenario: New proposal creation does not write to existing proposal directories
    Given Phil has a multi-proposal workspace with active proposal "af263-042"
    And the proposal "af263-042" has state and artifacts
    And a filesystem snapshot of "af263-042" directories is recorded
    When Phil creates a new proposal with topic ID "n244-012"
    Then the "af263-042" state directory contents are identical to the snapshot
    And the "af263-042" artifact directory contents are identical to the snapshot

  # --- Checkpoint 2: Path Resolution Consistency ---

  @integration @checkpoint-2
  Scenario: State directory and artifact directory agree on active proposal
    Given Phil has a multi-proposal workspace with proposals "af263-042" and "n244-012"
    And the active proposal is "af263-042"
    When Phil requests the workspace paths
    Then the state directory and artifact directory both reference "af263-042"

  @integration @checkpoint-2
  Scenario: Path resolution after switch reflects new proposal
    Given Phil has a multi-proposal workspace with proposals "af263-042" and "n244-012"
    And the active proposal is "af263-042"
    When Phil switches to proposal "n244-012"
    And Phil requests the workspace paths
    Then the state directory and artifact directory both reference "n244-012"

  # --- Checkpoint 3: Dashboard Enumeration ---

  @integration @checkpoint-3
  Scenario: Dashboard enumeration finds all proposals regardless of active pointer
    Given Phil has a multi-proposal workspace with proposals "af263-042", "n244-012", and "da-26-003"
    And the active proposal is "af263-042"
    When all proposals are enumerated from the workspace
    Then 3 proposals are found
    And the enumeration includes "af263-042", "n244-012", and "da-26-003"

  @integration @checkpoint-3
  Scenario: Dashboard enumeration handles one corrupted state file gracefully
    Given Phil has a multi-proposal workspace with proposals "af263-042" and "n244-012"
    And the proposal "af263-042" has corrupted state
    When all proposals are enumerated from the workspace
    Then 2 entries are returned
    And the entry for "af263-042" is marked as corrupted
    And the entry for "n244-012" has valid state data

  # --- Checkpoint 4: Backward Compatibility ---

  @integration @checkpoint-4
  Scenario: Legacy workspace operations never create proposals directory
    Given Phil has a legacy workspace with proposal state at the root level
    When Phil requests the workspace paths
    Then the proposals directory does not exist
    And the state directory is the root workspace directory

  @integration @checkpoint-4
  Scenario: Migration followed by path resolution uses new layout
    Given Phil has a legacy workspace with proposal "af263-042" at the root level
    When Phil migrates the legacy workspace
    And Phil requests the workspace paths
    Then the workspace is identified as multi-proposal layout
    And the state directory points to the "af263-042" proposal namespace

  # --- Checkpoint 5: Dashboard Resilience ---

  @integration @checkpoint-5
  Scenario: Enumeration with all proposals corrupted returns all-error list
    Given Phil has a multi-proposal workspace with proposals "af263-042" and "n244-012"
    And both proposals have corrupted state
    When all proposals are enumerated from the workspace
    Then 2 entries are returned
    And all entries are marked as corrupted
