Feature: Corpus Integrity Enforcement (US-PEW-004)
  As Phil Santos, recording win/loss outcomes for proposal learning,
  I want the system to protect recorded outcome tags from accidental overwrite
  So that the corpus learning system has accurate, immutable historical data

  # --- Happy Path ---

  Scenario: First outcome assignment is allowed
    Given Phil's proposal "AF243-001" has no recorded outcome
    And the enforcement rules are loaded from the standard configuration
    When Phil records outcome as "win"
    Then the action is allowed

  # --- Error Paths ---

  Scenario: Changing an existing outcome to a different value is blocked
    Given Phil's proposal "AF243-001" has a recorded outcome of "win"
    And Phil requests to change the outcome to "loss"
    And the enforcement rules are loaded from the standard configuration
    When Phil attempts to record a different outcome
    Then the action is blocked

  # --- Boundary/Edge ---

  Scenario: Re-recording the same outcome value is allowed
    Given Phil's proposal "AF243-001" has a recorded outcome of "win"
    And Phil requests to change the outcome to "win"
    And the enforcement rules are loaded from the standard configuration
    When Phil attempts to record a different outcome
    Then the action is allowed

  Scenario: Non-outcome tools are not affected by corpus integrity
    Given Phil's proposal "AF243-001" has a recorded outcome of "win"
    And the enforcement rules are loaded from the standard configuration
    When Phil uses a non-outcome-related tool
    Then the action is allowed

  Scenario: Missing learning field does not block outcome recording
    Given Phil's proposal "AF243-001" has no learning data
    And the enforcement rules are loaded from the standard configuration
    When Phil records outcome as "win"
    Then the action is allowed
