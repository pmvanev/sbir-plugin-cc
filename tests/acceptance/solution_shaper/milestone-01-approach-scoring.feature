Feature: Approach Scoring Model
  As a solo SBIR proposal writer
  I want approach scoring to produce differentiated, traceable results
  So that the recommendation reflects my company's actual strengths

  Background:
    Given the approach scoring system is available

  # --- Scoring Model Validation ---

  # Happy path: composite score computed correctly from dimension scores and weights
  Scenario: Composite score reflects weighted sum of dimension scores
    Given an approach scored 0.85 on personnel alignment, 0.80 on past performance, 0.70 on technical readiness, 0.80 on solicitation fit, and 0.75 on commercialization
    And the scoring weights are personnel 0.25, past performance 0.20, technical readiness 0.20, solicitation fit 0.20, and commercialization 0.15
    When the composite score is calculated
    Then the composite score is 0.785

  # Happy path: multiple approaches produce differentiated scores
  Scenario: Scoring differentiates between approaches with different company alignment
    Given approach "Fiber Laser Array" scores 0.85 on personnel alignment and 0.80 on past performance
    And approach "Direct Semiconductor" scores 0.30 on personnel alignment and 0.20 on past performance
    And both approaches score 0.70 on technical readiness, 0.80 on solicitation fit, and 0.75 on commercialization
    When composite scores are calculated for both approaches
    Then "Fiber Laser Array" scores higher than "Direct Semiconductor"
    And the score spread is at least 15 percentage points

  # Edge: all dimensions score identically produces equal composites
  Scenario: Identical dimension scores produce equal composite scores
    Given approach "Alpha" and approach "Beta" both score 0.60 on all five dimensions
    When composite scores are calculated for both approaches
    Then "Alpha" and "Beta" have the same composite score of 0.60

  # Edge: narrow score spread triggers tiebreaker guidance
  @skip @agent_behavior
  Scenario: Narrow score spread triggers tiebreaker considerations
    Given 3 approaches have been scored for topic N244-012
    And the score spread is less than 10 percentage points with composites 0.62, 0.65, and 0.68
    When the scoring results are presented
    Then the tool notes "Multiple viable approaches -- no clear winner by composite score"
    And tiebreaker considerations are presented: strongest single discriminator, lowest technical risk, most compelling narrative

  # Error: dimension score outside valid range is rejected
  @property
  Scenario: Dimension scores are always between 0.00 and 1.00
    Given any combination of dimension scores for an approach
    When scores are validated
    Then each dimension score is between 0.00 and 1.00 inclusive

  # Error: composite score is never negative regardless of inputs
  @property
  Scenario: Composite score is never negative
    Given any valid set of dimension scores and weights
    When the composite is computed from those scores and weights
    Then the composite score is greater than or equal to 0.00

  # Happy path: weights sum to 1.00
  @property
  Scenario: Scoring weights always sum to 1.00
    Given the default scoring weights
    When the weights are validated
    Then the weights sum to 1.00
