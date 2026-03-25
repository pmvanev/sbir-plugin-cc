Feature: Feedback Domain Model — FeedbackEntry and FeedbackSnapshot
  As a developer implementing the feedback feature
  I want FeedbackEntry and FeedbackSnapshot to correctly model all required fields
  So that the data contract is enforced by the domain layer, not just the CLI

  # Story 1 (capture friction in-context), Story 4 (developer reads structured feedback)

  @skip
  Scenario: FeedbackEntry serializes to valid JSON schema
    Given a complete FeedbackEntry with type "quality", all ratings set, and free text
    When the entry is serialized to a dict
    Then the dict contains feedback_id as a UUID v4 string
    And the dict contains timestamp as an ISO-8601 UTC string
    And the dict contains type "quality"
    And the dict contains ratings with all four dimensions
    And the dict contains context_snapshot with all 14 fields

  @skip
  Scenario Outline: QualityRatings accepts valid values and rejects invalid ones
    Given a QualityRatings with past_performance <pp>, image_quality <iq>, writing_quality <wq>, topic_scoring <ts>
    Then the ratings object is valid when all values are null or 1–5

    Examples:
      | pp   | iq   | wq   | ts   |
      | 1    | null | null | null |
      | 5    | 5    | 5    | 5    |
      | null | null | null | null |
      | 3    | 2    | 4    | 1    |

  @skip
  Scenario: FeedbackSnapshot enforces privacy boundary
    Given a company profile with capabilities "radar, sensor fusion" and past_performance entries
    When FeedbackSnapshotService builds a snapshot from this profile
    Then the snapshot company_name is "Acme Defense Systems"
    And the snapshot does not contain the capabilities field
    And the snapshot does not contain the past_performance field
    And the snapshot does not contain key_personnel details

  @skip
  Scenario: FeedbackSnapshotService extracts completed and skipped waves correctly
    Given a proposal state with waves 0 completed, 1 completed, 2 skipped, 3 active
    When FeedbackSnapshotService builds a snapshot from this state
    Then completed_waves is [0, 1]
    And skipped_waves is [2]
    And current_wave is 3

  @skip
  Scenario: FeedbackSnapshotService handles missing state files gracefully
    Given no proposal state file exists
    And no rigor profile file exists
    And no company profile file exists
    And no finder results file exists
    When FeedbackSnapshotService builds a snapshot with all-None inputs
    Then the snapshot has proposal_id null
    And the snapshot has current_wave null
    And the snapshot has completed_waves as empty list
    And the snapshot has rigor_profile null
    And the snapshot has company_name null
    And the snapshot has company_profile_age_days null
    And the snapshot has finder_results_age_days null
    And the snapshot has top_scored_topics as empty list
    And the snapshot has generated_artifacts as empty list
    And the snapshot has plugin_version as a non-empty string
