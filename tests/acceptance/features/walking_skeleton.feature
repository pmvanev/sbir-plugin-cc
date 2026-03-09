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

  # ===================================================================
  # C2 Walking Skeletons: Waves 2-4
  # ===================================================================

  # Walking Skeleton 4: Research through discrimination and outline
  # Validates: research generation -> research checkpoint -> discrimination table -> outline -> Wave 4 unlock
  @walking_skeleton
  @skip
  Scenario: Engineer completes research and builds proposal structure
    Given Phil has an active proposal with an approved strategy brief
    And a compliance matrix exists with 47 items
    When Phil generates research findings from the strategy brief
    Then Phil sees research covering technical landscape, market analysis, and prior awards
    When Phil approves the research review
    Then Wave 3 is unlocked
    When Phil generates the discrimination table
    Then Phil sees discriminators for company, technical approach, and team
    When Phil generates the proposal outline
    Then Phil sees every compliance item mapped to a section with page budgets
    When Phil approves the proposal outline
    Then Wave 4 is unlocked

  # Walking Skeleton 5: Section drafting through review iteration
  # Validates: draft generation -> review scorecard -> iteration -> compliance verification
  @walking_skeleton
  @skip
  Scenario: Engineer drafts a section and iterates through review
    Given Phil has an active proposal with an approved proposal outline
    And the outline includes a technical approach section with 8-page budget
    When Phil requests a draft of the technical approach section
    Then Phil sees a draft addressing compliance items with word count
    When the section is submitted for review
    Then Phil sees a scorecard with actionable findings
    When Phil requests iteration on the technical approach section
    Then the revised section preserves approved content and addresses findings
