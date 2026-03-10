Feature: Visual Asset Generation from Outline Placeholders (US-010)
  As an engineer with approved proposal sections
  I want professional figures generated from outline placeholders
  So I can submit a proposal with visuals that strengthen the technical argument

  Background:
    Given the proposal plugin is active
    And Phil has an active proposal with all sections approved

  # --- Happy Path ---

  @skip
  Scenario: Generate figure inventory from approved outline
    Given the approved outline contains 5 figure placeholders across 4 sections
    When Phil generates the figure inventory
    Then the inventory lists 5 entries
    And each entry has a type classification and recommended generation method
    And each entry has its target section identified
    And the inventory is written to the visuals artifacts directory

  @skip
  Scenario: Generate Mermaid diagram and present for review
    Given Figure 1 is classified as a block diagram with method "Mermaid"
    When the tool generates Figure 1 from the Section 3.1 content
    Then an SVG file is produced in the figures directory
    And the figure is presented to Phil for review
    And Phil can approve, request revision, or replace with a manual file

  @skip
  Scenario: Create external brief for non-generatable figure
    Given Figure 5 requires a photograph that cannot be generated
    When the tool classifies Figure 5
    Then an external brief is generated with content description, dimensions, and resolution
    And Phil can provide a manual file to replace the brief

  # --- Edge Cases ---

  @skip
  Scenario: Cross-reference validation catches orphaned reference
    Given 5 figures are generated and Section 3.3 references "Figure 6"
    When the tool runs cross-reference validation
    Then it flags "Figure 6 referenced in Section 3.3 does not exist"
    And the cross-reference log records the mismatch

  @skip
  Scenario: Cross-reference validation passes with consistent references
    Given 5 figures are generated and all text references resolve to existing figures
    When the tool runs cross-reference validation
    Then the cross-reference log shows all references valid
    And no orphaned references are flagged

  # --- Error Path ---

  @skip
  Scenario: PES blocks Wave 5 when sections have RED PDCs
    Given section 3.2 still has a RED Tier 2 PDC item
    When Phil attempts to generate the figure inventory
    Then the enforcement system blocks the action
    And Phil sees "Wave 5 requires all sections to have Tier 1+2 PDCs GREEN"
