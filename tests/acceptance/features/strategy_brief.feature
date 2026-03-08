Feature: Strategy Brief and Wave 1 Checkpoint (US-009)
  As an engineer completing Wave 1
  I want a documented strategy that all downstream work builds on
  So I avoid mid-course corrections during drafting

  Background:
    Given the proposal plugin is active
    And Phil has an active proposal for AF243-001 with Go/No-Go "go"

  # --- Happy Path ---

  Scenario: Strategy brief generated from full Wave 1 context
    Given a compliance matrix exists for AF243-001
    And TPOC answers have been ingested
    And the corpus has relevant past proposals
    When the strategy brief is generated
    Then Phil sees the brief covering technical approach, TRL, teaming, Phase III, budget, and risks
    And the brief references TPOC insights where applicable
    And the brief is written to the Wave 1 strategy artifacts

  Scenario: Strategy checkpoint -- approve unlocks Wave 2
    Given a strategy brief exists for AF243-001
    When Phil approves the strategy brief
    Then the approval is recorded in the proposal state
    And Wave 2 is unlocked

  # --- Edge Cases ---

  Scenario: Strategy brief generated without TPOC answers
    Given a compliance matrix exists for AF243-001
    And TPOC questions are in "pending" state
    When the strategy brief is generated
    Then the brief is generated from solicitation and corpus data alone
    And the brief notes "TPOC insights: not available"

  Scenario: Strategy revision with feedback
    Given a strategy brief exists for AF243-001
    When Phil provides revision feedback "Change approach from solid-state laser to fiber laser"
    Then the strategy brief is regenerated incorporating the feedback
    And Phil reviews the revised brief

  # --- Error Paths ---

  Scenario: Cannot generate strategy brief without compliance matrix
    Given no compliance matrix exists
    When Phil attempts to generate the strategy brief
    Then Phil sees "Compliance matrix required before strategy brief"
    And Phil sees guidance to run the strategy wave command first

  Scenario: Cannot approve strategy brief that does not exist
    Given no strategy brief has been generated
    When Phil attempts to approve the strategy brief
    Then Phil sees "No strategy brief to approve"
    And Phil sees guidance to generate one first
