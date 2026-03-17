Feature: Downstream Agent Quality Artifact Consumption
  As a strategist, writer, or reviewer agent
  I want to load quality artifacts when they exist
  So that proposals benefit from institutional quality intelligence

  Background:
    Given the quality artifact directory exists at the company profile location

  # --- Graceful Degradation (all three agents) ---

  Scenario: Missing quality preferences file is handled gracefully
    Given no quality preferences file exists
    When a downstream agent attempts to load quality preferences
    Then the agent receives an indication that no preferences are available
    And no error occurs

  Scenario: Missing winning patterns file is handled gracefully
    Given no winning patterns file exists
    When a downstream agent attempts to load winning patterns
    Then the agent receives an indication that no patterns are available
    And no error occurs

  Scenario: Missing writing quality profile is handled gracefully
    Given no writing quality profile file exists
    When a downstream agent attempts to load the writing quality profile
    Then the agent receives an indication that no profile is available
    And no error occurs

  # --- Strategist: Agency Filtering ---

  Scenario: Winning patterns filtered by matching agency
    Given winning patterns with Air Force pattern "Lead with quantitative results"
    And winning patterns with Navy pattern "Emphasize past performance metrics"
    When patterns are filtered for an Air Force proposal
    Then the result includes "Lead with quantitative results"
    And the result does not include "Emphasize past performance metrics"

  Scenario: No matching patterns for target agency
    Given winning patterns with Air Force patterns only
    When patterns are filtered for a DARPA proposal
    Then the result is empty
    And no error occurs

  Scenario: Universal patterns included regardless of agency
    Given a winning pattern "Use evaluator language from solicitation" marked as universal
    And the current proposal is for DARPA
    When patterns are filtered for a DARPA proposal
    Then the result includes "Use evaluator language from solicitation"

  # --- Writer: Quality Alert Matching ---

  Scenario: Writing quality alert matches agency and section
    Given writing quality profile has negative "organization_clarity" for Air Force technical approach
    When quality alerts are checked for Air Force technical approach section
    Then an alert is returned referencing the past evaluator feedback

  Scenario: Writing quality alert does not match different agency
    Given writing quality profile has negative "organization_clarity" for Air Force technical approach
    When quality alerts are checked for Navy technical approach section
    Then no alert is returned

  Scenario: Writing quality alert does not match different section
    Given writing quality profile has negative "organization_clarity" for Air Force technical approach
    When quality alerts are checked for Air Force commercialization section
    Then no alert is returned

  # --- Reviewer: Practices-to-Avoid Matching ---

  Scenario: Practices to avoid detected in text
    Given quality preferences with practice to avoid "Our team has extensive experience without specifics"
    When a draft section contains "Our team brings extensive experience to this effort"
    Then the practice-to-avoid match is flagged

  # --- Error: Malformed Artifact ---

  Scenario: Malformed quality preferences file produces warning not crash
    Given a quality preferences file with invalid content
    When a downstream agent attempts to load quality preferences
    Then the agent receives a warning about the malformed file
    And the agent can proceed with defaults
