Feature: Solution Shaper Agent Workflow
  As a solo SBIR proposal writer
  I want to shape my proposal approach through a guided agent workflow
  So that I make an evidence-backed approach decision before investing in proposal writing

  # --- US-SS-001: Approach Generation, Scoring, and Selection ---

  # Happy path: agent generates distinct approaches from solicitation and profile
  @skip @agent_behavior
  Scenario: Agent generates technically distinct candidate approaches
    Given Phil has an active proposal for topic AF243-001 with a Go decision
    And a company profile exists with Dr. Sarah Chen (fiber laser, 12 years) and past performance AF241-087
    When Phil runs the approach shaping workflow
    Then the agent extracts solicitation objectives, evaluation criteria, and constraints
    And generates 3-5 technically distinct candidate approaches
    And each approach includes a name, description, key technical elements, and required capabilities

  # Happy path: scoring references specific company data
  @skip @agent_behavior
  Scenario: Approach scoring references specific personnel and past performance
    Given the agent has generated 4 candidate approaches for AF243-001
    And the company profile lists Dr. Sarah Chen with fiber laser expertise
    And the company has past performance on contract AF241-087
    When the agent scores the approaches
    Then the scoring rationale for the fiber laser approach references Dr. Sarah Chen
    And the scoring rationale references contract AF241-087
    And each dimension score cites specific evidence from the company profile

  # Happy path: convergence produces recommendation with runner-up
  @skip @agent_behavior
  Scenario: Agent converges on recommendation with runner-up analysis
    Given the agent has scored 4 approaches with "Fiber Laser Array" at 0.79 and "Hybrid RF-Optical" at 0.68
    When the agent presents the recommendation
    Then "Fiber Laser Array" is recommended as the top approach
    And "Hybrid RF-Optical" is documented as the runner-up
    And the runner-up has conditions for reconsideration
    And at least 3 discrimination angles are identified
    And risks are assigned to Wave 1 or Wave 2 for validation

  # Happy path: user approves and brief is written
  @skip @agent_behavior
  Scenario: Approved approach writes brief and updates proposal state
    Given the agent has recommended "High-Power Fiber Laser Array" with composite score 0.79
    When Phil selects "approve" at the checkpoint
    Then the approach brief is written to wave-0-intelligence artifacts
    And the proposal records approach selection status as "approved"
    And the proposal records approach name as "High-Power Fiber Laser Array"

  # Error: user overrides recommendation with own preferred approach
  @skip @agent_behavior
  Scenario: User overrides recommendation with preferred approach and documented rationale
    Given the agent has recommended "Inertial-Acoustic Fusion" for N244-012
    When Phil selects "revise" at the checkpoint
    And Phil provides feedback "Use quantum magnetometry -- TPOC indicated Navy interest in quantum sensing"
    Then the agent regenerates the approach brief with quantum magnetometry as selected approach
    And Phil's override rationale is documented in the brief
    And the revised brief is presented for another review round

  # Happy path: explore option provides deep-dive on specific approach
  @skip @agent_behavior
  Scenario: User explores a specific approach before deciding
    Given the agent has presented 4 scored approaches
    When Phil selects "explore" for approach "Hybrid RF-Optical"
    Then the agent provides additional detail on the hybrid approach
    And the detail includes technical risks, implementation complexity, and trade-offs
    And Phil returns to the checkpoint to make a final decision

  # Happy path: restart regenerates candidates from scratch
  @skip @agent_behavior
  Scenario: User restarts approach generation for fresh candidates
    Given the agent has presented scored approaches that Phil finds unsatisfactory
    When Phil selects "restart" at the checkpoint
    Then the agent regenerates candidate approaches from scratch
    And the new candidates may differ from the original set
    And scoring proceeds on the new candidates

  # Error: quit saves pending state without finalizing
  @skip @agent_behavior
  Scenario: User quits and state is preserved for later
    Given the agent has presented scored approaches
    When Phil selects "quit" at the checkpoint
    Then the proposal records approach selection status as "pending"
    And Phil can resume approach selection later

  # --- US-SS-001: Error Paths ---

  # Error: missing company profile blocks the workflow
  @skip @agent_behavior
  Scenario: Missing company profile blocks approach scoring with guidance
    Given no company profile exists
    When Phil runs the approach shaping workflow
    Then the tool displays "Company profile required for approach scoring"
    And the tool suggests running the company profile setup
    And the workflow does not proceed to approach generation

  # Error: missing Go decision blocks the workflow
  @skip @agent_behavior
  Scenario: Missing Go decision blocks approach shaping
    Given Phil has an active proposal with go_no_go "pending"
    When Phil runs the approach shaping workflow
    Then the tool displays "Wave 0 Go decision required"
    And the tool suggests reviewing the Go/No-Go decision
    And the workflow does not proceed

  # Error: solicitation file not found
  @skip @agent_behavior
  Scenario: Missing solicitation file blocks deep read
    Given Phil has an active proposal for topic AF243-001 with a Go decision
    And the solicitation file path does not point to an existing file
    When Phil runs the approach shaping workflow
    Then the tool displays "Solicitation file not found"
    And the tool suggests updating the proposal state or providing the file

  # --- US-SS-002: Approach Revision After New Information ---

  # Happy path: revise after TPOC call with new insights
  @skip @agent_behavior
  Scenario: Revision re-scores approaches with new TPOC insights
    Given Phil approved "High-Power Fiber Laser Array" for AF243-001
    And Phil has new TPOC insights about GPS-denied operation requirements
    When Phil runs the approach revision with note "TPOC emphasized GPS-denied operation"
    Then the agent re-scores all approaches with the new constraint
    And the updated scoring matrix is presented
    And the original selection is preserved in the approach brief revision history

  # Happy path: revise after teaming partner joins
  @skip @agent_behavior
  Scenario: Revision reflects updated company profile after teaming partner joins
    Given Phil approved "Inertial-Acoustic Fusion" for N244-012
    And Phil has updated the company profile with NavTech Corp teaming partner capabilities
    When Phil runs the approach revision
    Then the agent re-scores approaches using the updated company profile
    And the quantum magnetometry approach reflects the new personnel and capabilities
    And Phil can approve a different top-ranked approach

  # Error: revision without prior selection
  @skip @agent_behavior
  Scenario: Revision without prior approach selection shows guidance
    Given no approach brief exists for the active proposal
    When Phil runs the approach revision
    Then the tool displays "No prior approach selection found"
    And the tool suggests running the initial approach shaping workflow

  # --- Integration: Strategist Reads Approach Brief ---

  # Happy path: strategist consumes approach brief as input
  @skip @agent_behavior
  Scenario: Strategist reads approach brief during strategy planning
    Given Phil approved "High-Power Fiber Laser Array" for AF243-001
    And the approach brief exists in wave-0-intelligence artifacts
    When the strategist agent begins Wave 1 strategy planning
    Then the strategist reads the approach brief as input
    And the strategy brief references the selected technical approach
    And the strategy brief incorporates discrimination angles from the approach brief

  # Edge: strategist proceeds without approach brief for backward compatibility
  @skip @agent_behavior
  Scenario: Strategist proceeds normally when no approach brief exists
    Given Phil has an active proposal with a Go decision
    And no approach brief exists in wave-0-intelligence artifacts
    When the strategist agent begins Wave 1 strategy planning
    Then the strategist proceeds with its standard workflow
    And the strategist does not produce errors about the missing brief
