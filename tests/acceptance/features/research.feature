Feature: Wave 2 Research Orchestration
  As an engineer building the intelligence foundation for a proposal
  I want structured research across technical landscape, market analysis, and prior awards
  So I have evidence-backed material for proposal drafting

  Background:
    Given the proposal plugin is active
    And Phil has an active proposal with an approved strategy brief

  # --- Happy Path ---

  @skip
  Scenario: Research findings produced from strategy brief context
    Given a strategy brief exists with technical approach and TRL positioning
    When the research orchestration generates findings
    Then Phil sees research findings covering technical landscape
    And Phil sees research findings covering patent landscape
    And Phil sees research findings covering prior award analysis
    And Phil sees research findings covering market research with TAM, SAM, and SOM
    And Phil sees research findings covering commercialization pathway
    And Phil sees research findings covering refined TRL positioning

  @skip
  Scenario: Research checkpoint presented for human review
    Given research findings have been generated for AF243-001
    When Phil reaches the research review checkpoint
    Then Phil sees the six research artifacts listed for review
    And Phil can approve, revise, or skip the research review

  Scenario: Research approval unlocks Wave 3
    Given research findings have been generated for AF243-001
    When Phil approves the research review
    Then the approval is recorded in the proposal state
    And Wave 3 is unlocked

  Scenario: Research revision incorporates feedback
    Given research findings have been generated for AF243-001
    When Phil provides research revision feedback "Deepen prior award analysis for Navy directed energy programs"
    Then the research findings are regenerated incorporating the feedback
    And Phil reviews the revised research findings

  # --- Error Paths ---

  @skip
  Scenario: Research cannot start without strategy brief
    Given the strategy brief does not exist
    When Phil attempts to generate research findings
    Then Phil sees "Strategy brief required before Wave 2 research"
    And Phil sees guidance to complete Wave 1 strategy alignment first

  Scenario: Research cannot be approved before generation
    Given no research findings have been generated
    When Phil attempts to approve the research review
    Then Phil sees "No research findings to approve"
    And Phil sees guidance to generate research first

  Scenario: Research revision without existing findings fails
    Given no research findings have been generated
    When Phil attempts to revise research findings
    Then Phil sees "No research findings to revise"
    And Phil sees guidance to generate research first

  # --- Edge Cases ---

  @skip
  Scenario: Research generated without TPOC data proceeds with caveat
    Given a strategy brief exists with technical approach and TRL positioning
    And TPOC data is not available
    When the research orchestration generates findings
    Then the research findings note "TPOC data not available"
    And the findings are generated from strategy brief and solicitation data alone

  @skip
  Scenario: Research with no prior awards found reports absence
    Given a strategy brief exists with technical approach and TRL positioning
    When the research orchestration generates findings
    And no prior SBIR awards are found for the topic
    Then the prior award analysis notes "No direct SBIR precedent for this topic"
    And the research continues with adjacent topic analysis

  @property
  @skip
  Scenario: Research approval always records timestamp
    Given any completed research review
    When the research review is approved
    Then the approval timestamp is always recorded in the state
