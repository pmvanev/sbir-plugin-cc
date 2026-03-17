Feature: Quality Artifact Schema Validation
  As a quality discoverer agent producing quality artifacts
  I want artifacts to conform to their defined schemas
  So that downstream agents can reliably consume quality intelligence

  Background:
    Given the quality artifact schemas are available

  # --- Walking Skeleton: quality-preferences.json ---

  @walking_skeleton
  Scenario: Complete quality preferences artifact passes validation
    Given quality preferences captured with tone "direct_data_driven" and detail "deep_technical"
    And evidence style is "inline_quantitative" and organization is "short_paragraphs"
    And practices to replicate include "Lead with quantitative results"
    And practices to avoid include "Vague experience claims without specifics"
    When the quality preferences artifact is assembled
    Then the artifact passes schema validation
    And the artifact contains schema version and updated timestamp

  # --- Walking Skeleton: winning-patterns.json ---

  @walking_skeleton
  Scenario: Complete winning patterns artifact passes validation
    Given proposal AF243-001 rated as "strong" for "Air Force" with outcome "WIN"
    And winning practice "Led with quantitative results in every section" is recorded
    And evaluator praise "Clearly organized approach with measurable milestones" is recorded
    When the winning patterns artifact is assembled with 3 wins analyzed
    Then the artifact passes schema validation
    And confidence level is "low" because fewer than 10 wins are analyzed
    And the artifact contains schema version and updated timestamp

  # --- Walking Skeleton: writing-quality-profile.json ---

  @walking_skeleton
  Scenario: Complete writing quality profile artifact passes validation
    Given evaluator comment "Technical approach was difficult to follow" for proposal AF243-002 by "Air Force" with outcome "LOSS"
    And the comment is categorized as "organization_clarity" with sentiment "negative"
    When the writing quality profile artifact is assembled
    Then the artifact passes schema validation
    And the artifact contains schema version and updated timestamp

  # --- Quality Preferences: Happy Path Variations ---

  Scenario: Quality preferences with custom tone description
    Given quality preferences captured with custom tone "Technical but accessible to non-specialists"
    And detail level is "moderate"
    And evidence style is "narrative_supporting" and organization is "medium_paragraphs"
    When the quality preferences artifact is assembled
    Then the artifact passes schema validation
    And the tone field is "custom"
    And the custom tone description is stored

  Scenario: Quality preferences with multiple practices
    Given quality preferences with 3 practices to replicate and 2 practices to avoid
    When the quality preferences artifact is assembled
    Then practices to replicate contains 3 items
    And practices to avoid contains 2 items

  Scenario: Quality preferences with empty practice lists
    Given quality preferences with no practices to replicate or avoid
    When the quality preferences artifact is assembled
    Then the artifact passes schema validation
    And practices to replicate is an empty list
    And practices to avoid is an empty list

  # --- Quality Preferences: Error Paths ---

  Scenario: Quality preferences with invalid tone value is rejected
    Given quality preferences with tone "casual_slangy"
    When the quality preferences artifact is validated
    Then validation fails because tone is not an allowed value

  Scenario: Quality preferences missing required tone field is rejected
    Given quality preferences with no tone specified
    When the quality preferences artifact is validated
    Then validation fails because tone is required

  Scenario: Custom tone without description is rejected
    Given quality preferences with tone "custom" but no description
    When the quality preferences artifact is validated
    Then validation fails because custom tone requires a description

  Scenario: Quality preferences with invalid detail level is rejected
    Given quality preferences with detail level "extreme_detail"
    When the quality preferences artifact is validated
    Then validation fails because detail level is not an allowed value

  # --- Winning Patterns: Happy Path Variations ---

  Scenario: Winning patterns with multiple agencies
    Given pattern "Explicit TRL entry/exit criteria" seen in Air Force and Navy proposals
    When the winning patterns artifact is assembled
    Then the pattern lists both agencies
    And source proposals are recorded

  Scenario: Winning patterns with adequate rating for losing proposal
    Given proposal AF243-002 rated as "adequate" for "Air Force" with outcome "LOSS"
    When the winning patterns artifact is assembled
    Then the proposal rating is recorded with outcome LOSS
    And no winning practices are expected for a losing proposal

  # --- Winning Patterns: Error Paths ---

  Scenario: Winning patterns with invalid quality rating is rejected
    Given a proposal rating with quality rating "excellent"
    When the winning patterns artifact is validated
    Then validation fails because quality rating is not an allowed value

  Scenario: Winning patterns with invalid outcome is rejected
    Given a proposal rating with outcome "PENDING"
    When the winning patterns artifact is validated
    Then validation fails because outcome must be WIN or LOSS

  Scenario: Winning patterns with empty topic ID is rejected
    Given a proposal rating with an empty topic ID
    When the winning patterns artifact is validated
    Then validation fails because topic ID must not be empty

  # --- Writing Quality Profile: Happy Path Variations ---

  Scenario: Writing quality profile with positive feedback
    Given evaluator comment "Well-organized approach with clear milestones" for proposal AF243-001 by "Air Force" with outcome "WIN"
    And the comment is categorized as "organization_clarity" with sentiment "positive"
    When the writing quality profile artifact is assembled
    Then the entry has sentiment "positive"
    And the entry is linked to proposal AF243-001

  Scenario: Writing quality profile with section-specific feedback
    Given evaluator comment "Technical approach was difficult to follow" for proposal AF243-002 by "Air Force" with outcome "LOSS"
    And the comment targets the "technical_approach" section
    And the comment is categorized as "organization_clarity" with sentiment "negative"
    When the writing quality profile artifact is assembled
    Then the entry specifies section "technical_approach"

  Scenario: Writing quality profile with agency patterns
    Given writing quality entries for Air Force with 1 positive and 2 negative organization clarity comments
    When the writing quality profile includes agency patterns
    Then Air Force has "organization_clarity" listed as a discriminator
    And positive count is 1 and negative count is 2

  # --- Writing Quality Profile: Error Paths ---

  Scenario: Writing quality profile with invalid category is rejected
    Given an evaluator feedback entry with category "grammar_spelling"
    When the writing quality profile artifact is validated
    Then validation fails because category is not in the allowed taxonomy

  Scenario: Writing quality profile with invalid sentiment is rejected
    Given an evaluator feedback entry with sentiment "neutral"
    When the writing quality profile artifact is validated
    Then validation fails because sentiment must be positive or negative

  Scenario: Writing quality profile entry missing required comment is rejected
    Given an evaluator feedback entry with an empty comment
    When the writing quality profile artifact is validated
    Then validation fails because comment must not be empty
