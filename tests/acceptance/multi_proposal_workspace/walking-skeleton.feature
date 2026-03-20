Feature: Multi-Proposal Workspace Walking Skeleton
  As a solo SBIR proposal writer managing multiple proposals
  I want each proposal isolated in its own namespace
  So that I can work on any proposal without risking another

  # Walking Skeleton 1: Path resolution in multi-proposal workspace
  # Validates: layout detection -> active proposal read -> path derivation
  # Driving port: path resolution module (new adapter)
  @walking_skeleton
  Scenario: Phil resolves paths for his active proposal in a multi-proposal workspace
    Given Phil has a multi-proposal workspace with proposals "af263-042" and "n244-012"
    And the active proposal is "af263-042"
    When Phil requests the workspace paths
    Then the state directory points to the "af263-042" proposal namespace
    And the artifact directory points to the "af263-042" artifact namespace
    And the workspace is identified as multi-proposal layout

  # Walking Skeleton 2: Legacy workspace continues working unchanged
  # Validates: layout detection -> legacy fallback -> root paths
  # Driving port: path resolution module (legacy branch)
  @walking_skeleton
  Scenario: Phil's existing single-proposal workspace works after plugin update
    Given Phil has a legacy workspace with proposal state at the root level
    And artifacts exist at the root artifact directory
    When Phil requests the workspace paths
    Then the state directory points to the root workspace directory
    And the artifact directory points to the root artifact directory
    And the workspace is identified as legacy layout

  # Walking Skeleton 3: Creating a second proposal preserves existing work
  # Validates: namespace creation -> state isolation -> active pointer update
  # Driving port: filesystem operations (namespace creation service)
  @walking_skeleton
  Scenario: Phil starts a second proposal and his first proposal is untouched
    Given Phil has a multi-proposal workspace with active proposal "af263-042"
    And the proposal "af263-042" has state with topic title "Compact Directed Energy"
    When Phil creates a new proposal with topic ID "n244-012"
    Then the proposal "n244-012" namespace exists with its own state
    And the proposal "af263-042" state is unchanged
    And the active proposal is now "n244-012"
