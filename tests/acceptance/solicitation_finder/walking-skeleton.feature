Feature: Solicitation Finder Walking Skeleton
  As a solo SBIR proposal writer
  I want to discover and score solicitation topics against my company profile
  So that I can focus on the highest-probability topics without manual browsing

  # Walking Skeleton 1: Fetch topics, pre-filter, and see candidate count
  # Validates: topic source -> keyword pre-filter -> candidate list with count
  @walking_skeleton @skip
  Scenario: Proposal writer discovers candidate topics from open solicitations
    Given Phil has a company profile for "Radiant Defense Systems, LLC" with capabilities "directed energy", "RF power systems", "thermal management"
    And the topic source has 347 open topics for the current solicitation cycle
    When Phil searches for matching solicitation topics
    Then the tool displays "Radiant Defense Systems, LLC" as the active company
    And 42 candidate topics are identified from 347 total
    And Phil sees "42 candidate topics (305 eliminated)"

  # Walking Skeleton 2: Score candidates and see ranked results with recommendations
  # Validates: candidates -> five-dimension scoring -> ranked table with GO/EVALUATE/NO-GO
  @walking_skeleton @skip
  Scenario: Proposal writer sees scored and ranked topics with pursuit recommendations
    Given Phil has a company profile with capabilities, certifications, and past performance
    And 42 candidate topics have been scored with five-dimension fit analysis
    And topic "AF263-042" scored 0.82 composite with recommendation GO
    And topic "N263-044" scored 0.34 composite with recommendation EVALUATE
    And topic "AF263-099" was disqualified for requiring TS clearance
    When Phil views the finder results
    Then the ranked table shows scored topics in descending score order
    And topic "AF263-042" appears first with recommendation GO
    And disqualified topic "AF263-099" appears in a separate section with reason "Requires TS clearance"

  # Walking Skeleton 3: Select a topic and transition to proposal creation
  # Validates: results -> pursue selection -> confirmation -> TopicInfo handoff
  @walking_skeleton @skip
  Scenario: Proposal writer selects a top-scored topic and begins proposal creation
    Given Phil has finder results with topic "AF263-042" scored GO at 0.82
    And topic "AF263-042" is "Compact Directed Energy for C-UAS" by "Air Force" Phase "I" with deadline "2026-05-15"
    When Phil chooses to pursue topic "AF263-042"
    And Phil confirms the selection
    Then the proposal workflow begins with topic "AF263-042" pre-loaded
    And the proposal has agency "Air Force", phase "I", and deadline "2026-05-15"
    And Phil does not need to re-enter any topic metadata
