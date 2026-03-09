Feature: Wave 3 Discrimination Table and Proposal Outline
  As an engineer building the proposal's argumentative structure
  I want a discrimination table and proposal outline before drafting begins
  So I have a clear "why us" narrative and structural skeleton for the proposal

  Background:
    Given the proposal plugin is active
    And Phil has an active proposal with approved research review

  # --- Discrimination Table: Happy Path ---

  Scenario: Discrimination table generated from strategy and research context
    Given a strategy brief exists with key discriminators
    And research findings include competitor landscape and prior art
    When the discrimination table is generated
    Then Phil sees discriminators covering company strengths versus competitors
    And Phil sees discriminators covering technical approach versus prior art
    And Phil sees discriminators covering team qualifications and past performance
    And each discriminator cites supporting evidence

  Scenario: Discrimination table incorporates TPOC insights
    Given TPOC answers revealed the agency's failed prior approach
    When the discrimination table is generated
    Then the technical discriminators explicitly contrast with the failed prior approach
    And the TPOC insight is cited as evidence

  Scenario: Discrimination table iteration with feedback
    Given a discrimination table has been generated for AF243-001
    When Phil provides discrimination feedback "Add facility clearance as a company discriminator"
    Then the discrimination table is revised incorporating the feedback
    And Phil reviews the revised discrimination table

  # --- Proposal Outline: Happy Path ---

  @skip
  Scenario: Proposal outline maps compliance items to sections
    Given a compliance matrix exists with 47 items
    And a discrimination table has been approved
    When the proposal outline is generated
    Then every compliance item is mapped to a proposal section
    And Phil sees page budgets assigned to each section
    And Phil sees figure and table placeholders defined
    And Phil sees thesis statements for each section

  @skip
  Scenario: Outline page budgets total to solicitation page limit
    Given the solicitation allows 25 pages for the technical volume
    And a discrimination table has been approved
    When the proposal outline is generated
    Then the section page budgets total to 25 pages or fewer

  Scenario: Outline approval unlocks Wave 4
    Given a proposal outline has been generated for AF243-001
    When Phil approves the proposal outline
    Then the approval is recorded in the proposal state
    And Wave 4 is unlocked

  Scenario: Outline iteration with feedback
    Given a proposal outline has been generated for AF243-001
    When Phil provides outline feedback "Move risk table from appendix to main body"
    Then the proposal outline is revised incorporating the feedback
    And Phil reviews the revised outline

  # --- Error Paths ---

  Scenario: Discrimination table cannot start without research approval
    Given the research review has not been approved
    When Phil attempts to generate the discrimination table
    Then Phil sees "Research review required before discrimination table"
    And Phil sees guidance to complete Wave 2 research review first

  @skip
  Scenario: Outline cannot start without approved discrimination table
    Given no discrimination table has been approved
    When Phil attempts to generate the proposal outline
    Then Phil sees "Approved discrimination table required before outline"
    And Phil sees guidance to complete the discrimination review first

  Scenario: Cannot approve outline that does not exist
    Given no proposal outline has been generated
    When Phil attempts to approve the proposal outline
    Then Phil sees "No proposal outline to approve"
    And Phil sees guidance to generate one first

  @skip
  Scenario: Cannot approve discrimination table that does not exist
    Given no discrimination table has been generated
    When Phil attempts to approve the discrimination table
    Then Phil sees "No discrimination table to approve"
    And Phil sees guidance to generate one first

  # --- Edge Cases ---

  @skip
  Scenario: Outline with unmapped compliance items flags gaps
    Given a compliance matrix exists with 47 items
    And the outline covers only 44 of those items
    When the outline mapping is validated
    Then Phil sees a warning that 3 compliance items are not mapped to any section
    And the unmapped items are listed by ID

  @property
  @skip
  Scenario: Every compliance item appears in at least one outline section
    Given any valid compliance matrix and approved discrimination table
    When the proposal outline is generated
    Then every compliance item is mapped to at least one section

  @property
  @skip
  Scenario: Page budgets never exceed solicitation limit
    Given any valid solicitation page limit
    When the proposal outline is generated
    Then the sum of all section page budgets does not exceed the solicitation limit
