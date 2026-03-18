Feature: PES Enforcement Parity Walking Skeletons
  As Phil Santos, a small business engineer preparing SBIR proposals,
  I want the enforcement system to perform full session housekeeping, validate
  completed work, track which agent is active, and record all decisions
  So that I have a reliable safety net and a complete audit trail

  # Walking Skeleton 1: Session housekeeping cleans up stale signals on startup
  # Validates: hook_adapter -> engine -> session_checker -> cleanup + audit log
  @walking_skeleton
  Scenario: Engineer starts a new session and stale crash signals are cleaned up
    Given Phil's previous session for proposal "AF243-001" ended abnormally leaving a crash signal
    And the enforcement rules are loaded from the standard configuration
    When Phil starts a new session
    Then the stale crash signal is removed
    And the session start is recorded in the audit trail

  # Walking Skeleton 2: Post-action validation confirms artifact placement
  # Validates: hook_adapter -> engine -> post-action check -> ALLOW/BLOCK + audit log
  @walking_skeleton
  Scenario: Engineer completes a writing action and the system confirms the artifact landed correctly
    Given Phil's proposal "AF243-001" is in Wave 4 drafting
    And the enforcement rules are loaded from the standard configuration
    When Phil completes writing the technical approach section
    Then the system confirms the artifact is in the correct location
    And the verification result is recorded in the audit trail

  # Walking Skeleton 3: Agent dispatch verification ensures correct agent for wave
  # Validates: hook_adapter -> engine -> agent lifecycle check -> ALLOW/BLOCK
  @walking_skeleton
  Scenario: The correct agent is dispatched for the current wave
    Given Phil's proposal "AF243-001" is in Wave 4 drafting
    And the enforcement rules are loaded from the standard configuration
    When the writer agent is dispatched for Wave 4 work
    Then the agent dispatch is allowed
    And the agent activation is recorded in the audit trail
