Feature: Approach Brief Schema and File Structure
  As a solo SBIR proposal writer
  I want the approach brief and agent files to have correct structure
  So that downstream agents can consume the brief and the plugin works correctly

  Background:
    Given the approach scoring system is available

  # --- Approach Brief Schema Validation ---

  # Happy path: complete approach brief has all required sections
  Scenario: Approach brief contains all required sections
    Given an approach brief has been generated
    When the brief structure is validated
    Then the brief contains a solicitation summary section
    And the brief contains a selected approach section
    And the brief contains an approach scoring matrix section
    And the brief contains a runner-up section
    And the brief contains a discrimination angles section
    And the brief contains a risks and open questions section
    And the brief contains a Phase III quick assessment section

  # Happy path: scoring matrix includes all approaches and all dimensions
  Scenario: Scoring matrix covers all approaches and dimensions
    Given 4 candidate approaches have been scored
    When the scoring matrix is validated
    Then the matrix has 4 approach columns
    And the matrix has rows for personnel alignment, past performance, technical readiness, solicitation fit, and commercialization
    And each cell contains a score between 0.00 and 1.00
    And each approach has a composite score row

  # Error: brief without required section fails validation
  Scenario: Brief missing required section fails validation
    Given an approach brief is missing the discrimination angles section
    When the brief structure is validated
    Then the validation fails with "missing required section: discrimination angles"

  # --- Agent File Structure Validation ---

  # Happy path: agent file has correct structure
  Scenario: Agent markdown file has required frontmatter and sections
    Given the solution-shaper agent file exists
    When the agent file structure is validated
    Then the agent has YAML frontmatter with name, description, and skill references
    And the agent has a workflow section covering all five phases
    And the agent references the approach-evaluation skill

  # Happy path: skill file has correct structure
  Scenario: Approach-evaluation skill file has required content
    Given the approach-evaluation skill file exists
    When the skill file structure is validated
    Then the skill has YAML frontmatter with name and description
    And the skill defines the five scoring dimensions with weights
    And the skill documents the approach brief schema

  # Happy path: command file dispatches to agent
  Scenario: Shape command file has correct dispatch configuration
    Given the shape command file exists
    When the command file structure is validated
    Then the command has YAML frontmatter with description and argument-hint
    And the command dispatches to the solution-shaper agent
    And the command documents the revise flag
