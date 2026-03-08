Feature: SBIR Proposal Walking Skeleton
  As an engineer writing SBIR proposals
  I want a structured proposal workflow with enforcement guardrails
  So I can write winning proposals faster with confidence the process is sound

  Background:
    Given the proposal plugin is active

  # Walking Skeleton 1: New proposal through Go decision
  # Validates: solicitation parsing -> corpus search -> fit scoring -> Go/No-Go -> state persistence
  @walking_skeleton
  Scenario: Engineer starts a new proposal and decides to proceed
    Given Phil has ingested past proposals from "./past-proposals/"
    And Phil has a solicitation PDF for topic AF243-001
    When Phil starts a new proposal from the solicitation
    Then Phil sees topic "AF243-001" with agency "Air Force" and deadline "2026-04-15"
    And Phil sees related past work from the corpus with relevance scores
    And Phil sees a Go/No-Go recommendation
    When Phil approves the Go decision
    Then the proposal records the Go decision
    And Wave 1 is unlocked for work

  # Walking Skeleton 2: Status reorientation after returning
  # Validates: state read -> wave progress -> deadline countdown -> next action suggestion
  @walking_skeleton
  Scenario: Engineer returns to proposal after days away and regains context
    Given Phil has an active proposal for topic AF243-001 in Wave 1
    And the compliance matrix has 47 items
    And TPOC questions were generated 5 days ago with status "pending"
    And 18 days remain until the deadline
    When Phil checks proposal status
    Then Phil sees the current wave is "Wave 1: Requirements & Strategy"
    And Phil sees "Compliance matrix generated (47 items)"
    And Phil sees "TPOC questions generated -- PENDING CALL"
    And Phil sees "18 days to deadline"
    And Phil sees the suggested next action "Have TPOC call, then /proposal tpoc ingest"

  # Walking Skeleton 3: PES enforcement prevents process violations
  # Validates: hook event -> rule evaluation -> block decision -> user guidance
  @walking_skeleton
  Scenario: Enforcement system prevents skipping required steps
    Given Phil has an active proposal with Go/No-Go decision "pending"
    When Phil attempts to start Wave 1 strategy work
    Then the enforcement system blocks the action
    And Phil sees "Wave 1 requires Go decision in Wave 0"
    And Phil sees guidance to complete the Go/No-Go step first
