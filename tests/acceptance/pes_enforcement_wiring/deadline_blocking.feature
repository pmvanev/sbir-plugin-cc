Feature: Deadline Blocking Enforcement (US-PEW-002)
  As Phil Santos, sometimes losing track of deadlines while working,
  I want the system to block non-essential wave work when the deadline is near
  So that I focus on finalizing and submitting instead of wasting time on lower-priority work

  # --- Happy Path ---

  Scenario: Non-essential wave allowed when deadline is far away
    Given Phil's proposal "AF243-001" has a deadline 10 days from now
    And Phil is working in Wave 2
    And the enforcement rules are loaded from the standard configuration
    When Phil attempts Wave 2 research work
    Then the action is allowed

  # --- Error Paths ---

  Scenario: Non-essential wave blocked when deadline is within critical threshold
    Given Phil's proposal "AF243-001" has a deadline 2 days from now
    And Phil is working in Wave 2
    And the enforcement rules are loaded from the standard configuration
    When Phil attempts Wave 2 research work
    Then the action is blocked
    And the block reason mentions "days remaining until deadline"
    And the block reason mentions "submit with available work or skip non-essential waves"

  Scenario: Essential wave allowed even when deadline is near
    Given Phil's proposal "AF243-001" has a deadline 2 days from now
    And Phil is working in Wave 5
    And the enforcement rules are loaded from the standard configuration
    When Phil attempts Wave 5 drafting work
    Then the action is allowed

  # --- Boundary/Edge ---

  Scenario: No deadline set means no blocking
    Given Phil's proposal "AF243-001" has no deadline set
    And Phil is working in Wave 2
    And the enforcement rules are loaded from the standard configuration
    When Phil attempts Wave 2 research work
    Then the action is allowed

  Scenario: Invalid deadline format does not block
    Given Phil's proposal "AF243-001" has an unparseable deadline value
    And Phil is working in Wave 2
    And the enforcement rules are loaded from the standard configuration
    When Phil attempts Wave 2 research work
    Then the action is allowed
