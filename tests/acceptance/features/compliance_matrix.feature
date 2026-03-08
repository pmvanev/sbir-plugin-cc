Feature: Automated Compliance Matrix from Solicitation (US-004)
  As an engineer tracking solicitation requirements
  I want every requirement surfaced and mapped to proposal sections
  So I avoid disqualification from missed compliance items

  Background:
    Given the proposal plugin is active
    And Phil has an active proposal for AF243-001 with Go/No-Go "go"

  # --- Happy Path ---

  Scenario: Generate compliance matrix from solicitation
    When Phil runs the strategy wave command
    Then the compliance matrix is generated with items mapped to proposal sections
    And explicit "shall" statements are extracted
    And format requirements are extracted
    And implicit requirements from evaluation criteria are extracted
    And ambiguous requirements are flagged with explanations
    And the matrix is written to the Wave 1 strategy artifacts

  Scenario: Manually add a missed compliance item
    Given a compliance matrix exists with 47 items
    When Phil adds a compliance item "Section 3 shall include risk mitigation table"
    Then the matrix updates to 48 items
    And the new item is marked as "manually added"
    And the item is mapped to Section 3

  # --- Edge Cases ---

  Scenario: Low extraction count triggers warning
    Given a solicitation with minimal structured requirements
    When the compliance matrix is generated
    Then Phil sees a warning about the low extraction count
    And Phil sees guidance to review manually for implicit requirements

  Scenario: Compliance matrix status shows coverage breakdown
    Given a compliance matrix exists with 47 items
    And 12 items have status "covered" and 35 have status "not started"
    When Phil checks compliance matrix status
    Then Phil sees "12/47 covered | 0 partial | 35 not started"

  # --- Error Paths ---

  Scenario: Cannot generate matrix before Go decision
    Given Phil has a proposal with Go/No-Go "pending"
    When Phil attempts to run the strategy wave command
    Then the enforcement system blocks the action
    And Phil sees "Wave 1 requires Go decision in Wave 0"

  Scenario: Cannot add compliance item without existing matrix
    Given no compliance matrix exists
    When Phil attempts to add a compliance item
    Then Phil sees "No compliance matrix found"
    And Phil sees guidance to generate one first
