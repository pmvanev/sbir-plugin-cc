Feature: Filesystem Feedback Adapter — Atomic Write and File Naming
  As a developer implementing the feedback feature
  I want FilesystemFeedbackAdapter to write entries atomically with correct naming
  So that feedback files are never corrupted and are easily identifiable

  # Story 5 (feedback persists across sessions), Story 1 (output file written correctly)

  @skip
  Scenario: Adapter writes entry to feedback directory with timestamped filename
    Given a FeedbackEntry with timestamp "2026-03-25T18:30:00Z"
    And the feedback directory does not yet exist
    When FilesystemFeedbackAdapter writes the entry
    Then the feedback directory is created
    And a file named "feedback-2026-03-25T18-30-00Z.json" exists in the feedback directory
    And the file contains valid JSON matching the FeedbackEntry schema

  @skip
  Scenario: Adapter creates feedback directory if absent
    Given a target feedback directory that does not exist
    When FilesystemFeedbackAdapter writes any entry
    Then the directory is created automatically
    And the entry file is present inside it

  @skip
  Scenario: Multiple entries accumulate without overwriting
    Given two FeedbackEntry objects with different timestamps
    When FilesystemFeedbackAdapter writes both entries
    Then two separate files exist in the feedback directory
    And each file contains its respective entry

  @skip
  Scenario: Written file is valid JSON and matches schema
    Given any FeedbackEntry
    When FilesystemFeedbackAdapter writes the entry
    Then the written file parses as valid JSON
    And the JSON contains feedback_id, timestamp, type, ratings, free_text, context_snapshot
    And context_snapshot contains plugin_version, proposal_id, current_wave, completed_waves, skipped_waves

  @skip
  Scenario: Colons in timestamp are replaced with hyphens in filename
    Given a FeedbackEntry with timestamp containing colons "2026-03-25T18:30:00Z"
    When FilesystemFeedbackAdapter writes the entry
    Then the filename uses hyphens instead of colons: "feedback-2026-03-25T18-30-00Z.json"
