Feature: Structured Critique and Refinement Loop
  As a solo SBIR proposal writer reviewing generated figures
  I want to critique figures using structured categories and have the system refine
  So that I can converge on high-quality figures through targeted feedback

  Background:
    Given the visual asset service is available

  # --- US-VAQ-2: Critique Rating Model ---

  # Happy path: all five categories present
  @us-vaq-2
  Scenario: Critique model accepts ratings for all five categories
    Given Phil provides ratings: composition 4, labels 3, accuracy 5, style match 4, scale 4
    When the critique ratings are validated
    Then the critique is valid with 5 rated categories
    And no categories are flagged for refinement

  # Happy path: categories below threshold flagged
  @us-vaq-2
  Scenario: Categories rated below 3 are flagged for refinement
    Given Phil provides ratings: composition 4, labels 2, accuracy 4, style match 5, scale 1
    When the critique ratings are evaluated
    Then "labels" and "scale_proportion" are flagged for refinement
    And "composition", "accuracy", and "style_match" are not flagged

  # Boundary: rating exactly 3 is not flagged
  @us-vaq-2
  Scenario: Category rated exactly 3 is not flagged
    Given Phil provides ratings: composition 3, labels 3, accuracy 3, style match 3, scale 3
    When the critique ratings are evaluated
    Then no categories are flagged for refinement

  # Boundary: rating exactly 2 is flagged
  @us-vaq-2
  Scenario: Category rated exactly 2 is flagged
    Given Phil provides ratings: composition 2, labels 4, accuracy 4, style match 4, scale 4
    When the critique ratings are evaluated
    Then "composition" is flagged for refinement

  # Happy path: all categories 4+ signals approval
  @us-vaq-2
  Scenario: All categories rated 4 or higher signals ready for approval
    Given Phil provides ratings: composition 4, labels 5, accuracy 4, style match 4, scale 5
    When the critique ratings are evaluated
    Then no categories are flagged for refinement
    And the critique signals ready for approval

  # Error: rating outside valid range rejected
  @us-vaq-2
  Scenario: Rating value of 0 is rejected
    Given Phil provides a rating of 0 for composition
    When the critique ratings are validated
    Then a validation error indicates rating must be between 1 and 5

  # Error: rating above maximum rejected
  @us-vaq-2
  Scenario: Rating value of 6 is rejected
    Given Phil provides a rating of 6 for accuracy
    When the critique ratings are validated
    Then a validation error indicates rating must be between 1 and 5

  # Error: missing category rating rejected
  @us-vaq-2
  Scenario: Critique with missing category is rejected
    Given Phil provides ratings for only 4 of 5 categories
    When the critique ratings are validated
    Then a validation error indicates all 5 categories must be rated

  # --- US-VAQ-2: Iteration Tracking ---

  # Happy path: iteration count increments
  @us-vaq-2
  Scenario: Each refinement round increments the iteration count
    Given Figure 3 has been through 0 refinement iterations
    When a refinement round is recorded
    Then the iteration count is 1

  # Boundary: maximum 3 iterations enforced
  @us-vaq-2
  Scenario: Fourth refinement round is blocked
    Given Figure 6 has been through 3 refinement iterations
    When a fourth refinement round is requested
    Then the refinement is blocked
    And the reason indicates maximum iterations reached

  # Edge: first review with no refinement records 0 iterations
  @us-vaq-2
  Scenario: Figure approved on first review has 0 iterations
    Given Figure 4 has not been refined
    When Figure 4 is approved
    Then the iteration count for Figure 4 is 0

  # --- US-VAQ-2: Average Rating Computation ---

  # Happy path: average computed correctly
  @us-vaq-2
  Scenario: Average rating computed from five categories
    Given Phil provides ratings: composition 4, labels 2, accuracy 4, style match 5, scale 3
    When the average rating is computed
    Then the average is 3.6

  @us-vaq-2 @property
  Scenario: Average rating is always between 1.0 and 5.0
    Given any valid set of critique ratings
    When the average rating is computed
    Then the average is between 1.0 and 5.0 inclusive
