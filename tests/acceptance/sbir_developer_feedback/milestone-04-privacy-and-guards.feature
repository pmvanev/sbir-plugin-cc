Feature: Privacy Boundary and Empty Submission Guard
  As a plugin user at a defense company
  I want feedback files to exclude sensitive company content
  And I want protection against accidentally empty submissions

  # Story 6 (privacy), Story 7 (empty submission guard)
  # Privacy is enforced at the domain layer (FeedbackSnapshotService)
  # The empty submission guard is handled by the agent (not testable at Python level)

  @skip
  Scenario: Snapshot excludes company capability text
    Given a company profile with capabilities list ["radar signal processing", "FPGA design"]
    When FeedbackSnapshotService builds a snapshot from this profile
    Then the snapshot does not contain a "capabilities" key anywhere in its dict
    And the snapshot company_name matches the profile company_name

  @skip
  Scenario: Snapshot excludes past performance narrative text
    Given a company profile with past_performance entries containing description text
    When FeedbackSnapshotService builds a snapshot from this profile
    Then the snapshot does not contain "past_performance" key
    And the snapshot does not contain any string longer than 200 characters from the profile

  @skip
  Scenario: Snapshot excludes key personnel details
    Given a company profile with key_personnel entries containing names and expertise
    When FeedbackSnapshotService builds a snapshot from this profile
    Then the snapshot does not contain "key_personnel" key

  @skip
  Scenario: Snapshot includes only top_scored_topics metadata not full descriptions
    Given finder results with scored topics containing composite_score, recommendation, and description text
    When FeedbackSnapshotService builds a snapshot from the finder results
    Then each top_scored_topics entry has only topic_id, composite_score, recommendation
    And no topic description text appears in the snapshot

  @skip
  Scenario: Snapshot limits top_scored_topics to 5 entries
    Given finder results with 12 scored topics
    When FeedbackSnapshotService builds a snapshot from the finder results
    Then the snapshot has at most 5 top_scored_topics entries
