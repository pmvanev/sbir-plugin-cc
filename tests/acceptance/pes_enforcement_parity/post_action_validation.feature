Feature: Post-Action Validation
  As Phil Santos, a small business engineer preparing SBIR proposals,
  I want the enforcement system to verify that artifacts landed in the
  correct directory after write operations
  So that I am alerted immediately if something went to the wrong place

  Background:
    Given the enforcement rules are loaded from the standard configuration

  # --- Happy Path Scenarios ---

  @skip
  Scenario: Artifact written to correct wave directory is confirmed
    Given Phil's proposal "AF243-001" is in Wave 4 drafting
    When Phil completes writing the technical approach section
    Then the system confirms the artifact is in the correct location
    And the verification result is recorded in the audit trail

  @skip
  Scenario: State file is verified as valid after a write operation
    Given Phil's proposal "AF243-001" is in Wave 4 drafting
    When Phil saves the proposal state after updating the compliance matrix
    Then the system confirms the state file is well-formed
    And the verification result is recorded in the audit trail

  # --- Error Path Scenarios ---

  @skip
  Scenario: Artifact written to wrong wave directory is flagged
    Given Phil's proposal "AF243-001" is in Wave 4 drafting
    When Phil completes writing and the artifact lands in the Wave 3 directory
    Then the system warns that the artifact is misplaced
    And the warning includes the expected directory and actual directory
    And the misplacement is recorded in the audit trail

  @skip
  Scenario: State file is corrupted after a write operation
    Given Phil's proposal "AF243-001" is in Wave 4 drafting
    When Phil saves the proposal state and the resulting file is malformed
    Then the system warns that the state file appears corrupted
    And the corruption is recorded in the audit trail

  @skip
  Scenario: Artifact file is missing after a reported write
    Given Phil's proposal "AF243-001" is in Wave 4 drafting
    When Phil completes writing but no artifact file is found
    Then the system warns that the expected artifact was not created
    And the missing artifact is recorded in the audit trail

  @skip
  Scenario: Post-action validation succeeds even when audit directory is missing
    Given Phil's proposal "AF243-001" is in Wave 4 drafting
    And the audit directory does not exist
    When Phil completes writing the technical approach section
    Then the system confirms the artifact is in the correct location
    And the audit directory is created automatically

  # --- Boundary Scenarios ---

  @skip
  Scenario: Read-only tool use does not trigger post-action validation
    Given Phil's proposal "AF243-001" is in Wave 4 drafting
    When Phil checks proposal status
    Then no post-action validation is performed
