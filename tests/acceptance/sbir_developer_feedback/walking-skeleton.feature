Feature: /sbir:developer-feedback Walking Skeleton
  As a plugin user writing an SBIR proposal
  I want to submit feedback with automatic context capture
  So that the developer can act on issues without reconstructing what happened

  # Walking Skeleton 1: Submit a quality issue with full context snapshot
  # Validates: FeedbackSnapshotService -> FeedbackEntry -> FilesystemFeedbackAdapter -> JSON file
  @walking_skeleton
  Scenario: Proposal writer submits a quality issue and feedback is persisted with context snapshot
    Given Maya has an active proposal for topic "A254-049" in wave 3 with rigor profile "standard"
    And the company profile is 14 days old for "Acme Defense Systems"
    And finder results are 3 days old with 2 scored topics
    When Maya submits a quality issue rating past_performance 2 with text "Wrong past project selected"
    Then a feedback entry is written to the feedback directory
    And the feedback entry has type "quality"
    And the feedback entry has past_performance_rating 2
    And the feedback entry has free_text "Wrong past project selected"
    And the context snapshot captures proposal_id "proposal-a254-049"
    And the context snapshot captures current_wave 3
    And the context snapshot captures completed_waves [0, 1, 2]
    And the context snapshot captures rigor_profile "standard"
    And the context snapshot captures company_name "Acme Defense Systems"
    And the context snapshot captures company_profile_age_days 14
    And the context snapshot captures finder_results_age_days 3

  # Walking Skeleton 2: Submit feedback with no active proposal
  # Validates: graceful degradation path — all proposal fields null, feedback still written
  @walking_skeleton @skip
  Scenario: User submits feedback with no active proposal and feedback is still saved
    Given no active proposal exists
    And the company profile is 7 days old for "Test Company"
    When Maya submits a bug with text "First-time setup was confusing"
    Then a feedback entry is written to the feedback directory
    And the feedback entry has type "bug"
    And the context snapshot captures proposal_id null
    And the context snapshot captures current_wave null
    And the context snapshot captures completed_waves []
