Feature: Partnership-Aware Topic Scoring (US-PM-002)
  As an SBIR proposal writer with partner profiles on file
  I want to see how topics score for the partnership versus my company alone
  So that I can identify topics where the combined team has a strong fit

  Background:
    Given the topic scoring service is available

  # --- Happy Path: Dual-Column Scoring ---

  @skip
  Scenario: Partnership SME score uses combined capability keywords
    Given Phil has a company profile with capabilities "directed energy, RF engineering, machine learning"
    And Phil has a partner profile for "CU Boulder" with capabilities "autonomous navigation, underwater acoustics, sensor fusion"
    And STTR topic "N244-012" title is "Autonomous UUV Navigation and Sensing"
    When the topic is scored for Phil's company alone
    Then the solo SME score reflects only Phil's capabilities
    When the topic is scored with CU Boulder as partner
    Then the partnership SME score is higher than the solo SME score
    And the partnership SME score reflects the combined capability set

  @skip
  Scenario: Partnership STTR dimension scores 1.0 for qualifying institution
    Given Phil has a partner profile for "CU Boulder" of type "university"
    And the topic is an STTR solicitation
    When the topic is scored with CU Boulder as partner
    Then the STTR dimension score is 1.0

  @skip
  Scenario: Partnership scoring shows delta between solo and combined
    Given Phil has solo scores for topic "N244-012" with composite 0.42
    And Phil has partnership scores for the same topic with composite 0.78
    When the score delta is computed
    Then the delta is 0.36
    And the delta indicates significant partnership impact

  @skip
  Scenario: Recommendation elevation from EVALUATE to GO is noted
    Given topic "N244-012" scores EVALUATE for Phil alone at composite 0.42
    And topic "N244-012" scores GO with CU Boulder at composite 0.78
    When the recommendations are compared
    Then the elevation from EVALUATE to GO is detected
    And the capabilities that drove the elevation are identified

  # --- Happy Path: No Impact ---

  @skip
  Scenario: Partnership has minimal impact when capabilities do not overlap
    Given Phil has a company profile with capabilities "directed energy, RF engineering, power systems"
    And Phil has a partner profile for "CU Boulder" with capabilities "autonomous navigation, underwater acoustics, sensor fusion"
    And SBIR topic "AF243-001" title is "Compact Directed Energy for C-UAS"
    When the topic is scored for Phil's company alone
    And the topic is scored with CU Boulder as partner
    Then the score delta is less than 0.05
    And the partnership is noted as having minimal impact on this topic

  # --- Error Path: Missing Partner ---

  @skip
  Scenario: No partner profiles defaults to solo scoring only
    Given Phil has a company profile but no partner profiles
    When scoring runs for STTR topic "N244-012"
    Then only solo scores are computed
    And the STTR dimension scores 0.0
    And the tool suggests setting up a partner profile

  @skip
  Scenario: STTR topic with no partner produces disqualification
    Given Phil has no partner profiles
    And no research institution partners listed in the company profile
    When STTR topic "N244-012" is scored
    Then the topic receives recommendation NO-GO
    And the disqualification reason is "No research institution partner"

  # --- Boundary: Score Integrity ---

  @skip
  Scenario: Partnership score never falls below solo score
    Given Phil has a company profile and a partner profile for "CU Boulder"
    And topic "N244-012" is scored both solo and with partnership
    When the scores are compared
    Then the partnership composite is greater than or equal to the solo composite

  @property @skip
  Scenario: Combined capability set is always a superset of company capabilities
    Given any company profile and any partner profile
    When the combined capability set is computed
    Then every company capability appears in the combined set
    And every partner capability appears in the combined set

  @property @skip
  Scenario: Partnership composite score stays within valid range
    Given any valid company profile and partner profile
    When partnership scoring is computed for any topic
    Then the composite score is between 0.0 and 1.0 inclusive
