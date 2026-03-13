Feature: Solution Shaper Walking Skeleton
  As a solo SBIR proposal writer
  I want to evaluate candidate technical approaches against my company strengths
  So that I select the highest-probability approach before investing weeks in proposal writing

  # Walking Skeleton 1: Generate approaches, score them, and see a recommendation
  # Validates: solicitation + company profile -> candidate approaches -> scored matrix -> recommendation
  @walking_skeleton @skip @agent_behavior
  Scenario: Proposal writer sees scored candidate approaches with a recommendation
    Given Phil has an active proposal for topic AF243-001 with a Go decision
    And a company profile exists with Dr. Sarah Chen (fiber laser, 12 years) and past performance AF241-087
    When Phil runs the approach shaping workflow
    Then 3-5 candidate technical approaches are generated
    And each approach is scored across personnel alignment, past performance, technical readiness, solicitation fit, and commercialization
    And a ranked scoring matrix shows composite scores
    And the highest-scoring approach is recommended with rationale

  # Walking Skeleton 2: Approve recommendation and receive approach brief
  # Validates: recommendation -> human approval -> approach-brief.md artifact -> state updated
  @walking_skeleton @skip @agent_behavior
  Scenario: Proposal writer approves approach and receives approach brief for strategy planning
    Given the agent has recommended "High-Power Fiber Laser Array" with composite score 0.79
    And Phil reviews the scoring matrix and recommendation
    When Phil approves the recommended approach
    Then an approach brief is written to the wave-0-intelligence artifacts
    And the brief contains solicitation summary, selected approach, scoring matrix, runner-up analysis, discrimination angles, risks, and Phase III assessment
    And the proposal records the approved approach as "High-Power Fiber Laser Array"

  # Walking Skeleton 3: Low scores trigger reconsideration warning
  # Validates: all approaches below threshold -> warning -> user can archive as No-Go
  @walking_skeleton @skip @agent_behavior
  Scenario: Proposal writer warned when no approach fits company strengths
    Given Phil has an active proposal for topic AF243-099 with a Go decision
    And the company profile has no expertise in thermal protection systems
    When Phil runs the approach shaping workflow
    Then all generated approaches score below 0.40 composite
    And the tool warns "All approaches scored below 0.40. Reconsider the Go decision."
    And Phil can archive the proposal as No-Go
