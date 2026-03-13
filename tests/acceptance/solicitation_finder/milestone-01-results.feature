Feature: Finder Results Display and Persistence
  As a solo SBIR proposal writer
  I want to review scored results with transparent breakdowns
  So that I can make informed Go/No-Go pursuit decisions

  Background:
    Given the solicitation finder system is available

  # --- US-SF-003: Review Results and Drill Into Details ---

  # Happy path: ranked results table
  Scenario: Scored topics displayed as ranked table
    Given scoring has completed for 42 candidate topics
    And 5 topics scored GO, 4 scored EVALUATE, and 3 were disqualified
    When the results are displayed
    Then the ranked table shows 9 scored topics in descending score order
    And disqualified topics appear in a separate section below
    And each entry shows topic ID, agency, title, score, recommendation, and deadline

  # Happy path: drill into topic detail
  Scenario: Detail view shows five-dimension breakdown and rationale
    Given finder results include topic "AF263-042" with composite 0.82
    And "AF263-042" scored subject matter 0.95, past performance 0.80, certifications 1.00, eligibility 1.00, partnership 1.00
    When Phil views details for topic "AF263-042"
    Then all five dimension scores are displayed with rationale
    And matching key personnel from the company profile are shown
    And the deadline shows "61 days remaining"
    And the tool offers "pursue" and "back" actions

  # Edge: drill into disqualified topic
  Scenario: Disqualified topic detail shows reason without pursue option
    Given finder results include topic "AF263-099" disqualified for TS clearance
    When Phil views details for topic "AF263-099"
    Then the disqualification reason is displayed prominently
    And the tool shows which profile field triggered the disqualification
    And the tool does not offer "pursue" as an action

  # Edge: deadline urgency flags
  Scenario: Topics with imminent deadlines flagged as urgent
    Given topic "HR001126-01" has a deadline within 3 days
    And topic "AF263-042" has a deadline in 61 days
    When the results table is displayed
    Then "HR001126-01" shows an URGENT flag
    And "AF263-042" shows the deadline without a flag

  # Happy path: results persisted for later reference
  Scenario: Finder results saved for later reference
    Given scoring has completed for all candidate topics
    When the results are persisted
    Then results are saved to the finder results file
    And the file includes all scored topics with dimension breakdowns
    And the file includes run metadata with date, source, and company name

  # Error: results file missing when viewing details
  Scenario: Viewing details without prior results shows guidance
    Given no finder results exist
    When Phil attempts to view topic details
    Then the tool displays "No finder results found"
    And the tool suggests running the solicitation finder first

  @property
  Scenario: Persisted results roundtrip preserves all scoring data
    Given any set of scored finder results
    When the results are saved and then loaded
    Then the loaded results match the original scores exactly
