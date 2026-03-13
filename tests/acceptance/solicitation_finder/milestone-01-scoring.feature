Feature: Topic Scoring and Ranking
  As a solo SBIR proposal writer
  I want topics scored against my company profile using five dimensions
  So that I can see quantitative fit analysis with clear pursuit recommendations

  Background:
    Given the solicitation finder system is available

  # --- US-SF-002: Score and Rank Topics ---

  # Happy path: five-dimension scoring with recommendations
  Scenario: Candidate topics scored with five-dimension fit analysis
    Given 42 candidate topics have full descriptions
    And the company profile has capabilities, certifications with SAM active and Secret clearance, 15 employees, and Air Force Phase I past performance in directed energy
    When the topics are scored
    Then topic "AF263-042" scores composite 0.82 with recommendation GO
    And topic "N263-044" scores composite 0.34 with recommendation EVALUATE
    And topics are ranked by composite score descending

  # Happy path: scoring dimension breakdown
  Scenario: Each scored topic shows all five dimension scores
    Given topic "AF263-042" has been scored
    When the dimension breakdown is retrieved
    Then the subject matter expertise score is 0.95
    And the past performance score is 0.80
    And the certifications score is 1.00
    And the eligibility score is 1.00
    And the partnership score is 1.00

  # Error: TS clearance disqualifier
  Scenario: Topic requiring higher clearance is disqualified
    Given topic "AF263-099" requires TS clearance
    And the company profile has security clearance "secret"
    When the topic is scored
    Then "AF263-099" receives recommendation NO-GO
    And the disqualification reason is "Requires TS clearance (profile: Secret)"

  # Error: STTR topic without research partner
  Scenario: STTR topic without research institution partner is disqualified
    Given topic "N263-S05" is an STTR solicitation
    And the company profile has no research institution partners
    When the topic is scored
    Then "N263-S05" receives recommendation NO-GO
    And the disqualification reason is "No research institution partner"

  # Error: incomplete profile degrades scoring
  Scenario: Missing past performance scores zero with warning
    Given the company profile has no past performance entries
    When scoring runs
    Then past performance dimension scores 0.0 for all topics
    And recommendations cap at EVALUATE rather than NO-GO from data absence
    And the tool warns "Profile incomplete: past_performance empty"

  # Boundary: recommendation thresholds
  Scenario: Recommendations follow threshold rules
    Given topic "HIGH-001" has composite score 0.60
    And topic "MID-001" has composite score 0.45
    And topic "LOW-001" has composite score 0.29
    When recommendations are applied
    Then "HIGH-001" receives recommendation GO
    And "MID-001" receives recommendation EVALUATE
    And "LOW-001" receives recommendation NO-GO

  @property
  Scenario: Composite score is never negative regardless of profile gaps
    Given any valid combination of topics and company profile gaps
    When the composite score is calculated
    Then the score is greater than or equal to zero

  @property
  Scenario: Composite score never exceeds 1.0 regardless of dimension scores
    Given any valid set of dimension scores
    When the composite score is calculated
    Then the score is less than or equal to 1.0
