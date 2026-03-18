Feature: Agent Lifecycle Tracking
  As Phil Santos, a small business engineer preparing SBIR proposals,
  I want the enforcement system to verify the correct agent is dispatched
  for my current wave and track agent start and stop events
  So that the wrong agent cannot accidentally do work in the wrong wave

  Background:
    Given the enforcement rules are loaded from the standard configuration

  # --- Happy Path Scenarios ---

  @skip
  Scenario: Writer agent is allowed for Wave 4 drafting
    Given Phil's proposal "AF243-001" is in Wave 4 drafting
    When the writer agent is dispatched for Wave 4 work
    Then the agent dispatch is allowed
    And the agent activation is recorded in the audit trail

  @skip
  Scenario: Reviewer agent is allowed for Wave 7 final review
    Given Phil's proposal "AF243-001" is in Wave 7 review
    When the reviewer agent is dispatched for Wave 7 work
    Then the agent dispatch is allowed
    And the agent activation is recorded in the audit trail

  @skip
  Scenario: Agent stop event is recorded when agent completes work
    Given Phil's proposal "AF243-001" is in Wave 4 drafting
    And the writer agent is currently active
    When the writer agent completes its work
    Then the agent deactivation is recorded in the audit trail
    And the audit entry includes the agent name and wave number

  # --- Error Path Scenarios ---

  @skip
  Scenario: Researcher agent is blocked from Wave 4 drafting work
    Given Phil's proposal "AF243-001" is in Wave 4 drafting
    When the researcher agent is dispatched for Wave 4 work
    Then the agent dispatch is blocked
    And Phil sees "researcher is not authorized for Wave 4" in the block reason
    And the rejected dispatch is recorded in the audit trail

  @skip
  Scenario: Writer agent is blocked from Wave 2 research work
    Given Phil's proposal "AF243-001" is in Wave 2 research
    When the writer agent is dispatched for Wave 2 work
    Then the agent dispatch is blocked
    And Phil sees "writer is not authorized for Wave 2" in the block reason

  @skip
  Scenario: Unknown agent name is blocked from any wave
    Given Phil's proposal "AF243-001" is in Wave 4 drafting
    When an unrecognized agent "rogue-agent" is dispatched
    Then the agent dispatch is blocked
    And Phil sees "rogue-agent is not a recognized agent" in the block reason

  @skip
  Scenario: Agent dispatch is blocked when no proposal is active
    Given no proposal session is active
    When the writer agent is dispatched
    Then the agent dispatch is blocked
    And Phil sees "no active proposal for agent dispatch" in the block reason

  # --- Boundary Scenarios ---

  @skip
  Scenario: Agent authorized for multiple waves is allowed in each
    Given Phil's proposal "AF243-001" is in Wave 3 outline
    When the writer agent is dispatched for Wave 3 work
    Then the agent dispatch is allowed

  @skip
  Scenario: Compliance sheriff is allowed in both Wave 1 and Wave 6
    Given Phil's proposal "AF243-001" is in Wave 6 formatting
    When the compliance-sheriff agent is dispatched for Wave 6 work
    Then the agent dispatch is allowed
    And the agent activation is recorded in the audit trail
