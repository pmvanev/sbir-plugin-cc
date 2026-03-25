Feature: /sbir:developer-feedback slash command
  As a plugin user writing an SBIR proposal
  I want to submit structured feedback with automatic context capture
  So that the developer can understand and act on issues without reconstructing what happened

  Background:
    Given the sbir-plugin-cc plugin is installed and active
    And the user is in a Claude Code session

  # ============================================================
  # Happy path: quality issue with ratings
  # ============================================================

  Scenario: User reports a quality issue with ratings and free text
    Given an active proposal for topic "A254-049" in wave 3 (Strategy)
    And the rigor profile is "standard"
    And the company profile was last updated 14 days ago
    And finder results are 3 days old
    When the user invokes "/sbir:developer-feedback"
    Then the agent asks the user to select a feedback type
    When the user selects "Quality issue"
    Then the agent presents quality rating dimensions: past_performance, images, writing, topic_scoring
    When the user rates past_performance as 2 and skips the others
    And the user enters free text "Past performance selection missed the mark — radar topic got GPS project"
    Then the agent captures a context snapshot containing:
      | field                    | value                  |
      | proposal_id              | proposal-a254-049      |
      | current_wave             | 3                      |
      | completed_waves          | [0, 1, 2]              |
      | skipped_waves            | []                     |
      | rigor_profile            | standard               |
      | company_profile_age_days | 14                     |
      | finder_results_age_days  | 3                      |
    And the feedback entry is written to ".sbir/feedback/feedback-{timestamp}.json"
    And the agent confirms with the feedback ID and file path

  # ============================================================
  # Happy path: bug report, no ratings
  # ============================================================

  Scenario: User reports a bug without quality ratings
    Given any proposal state (or no active proposal)
    When the user invokes "/sbir:developer-feedback"
    And the user selects "Bug"
    And the user enters free text "The enrich command crashed with a 404 for topic 7051b2da"
    Then the quality ratings step is skipped
    And the agent captures the context snapshot
    And the feedback entry is written with type "bug"
    And the agent confirms with the feedback ID and file path

  # ============================================================
  # Happy path: suggestion, text only
  # ============================================================

  Scenario: User submits a suggestion with free text only
    Given any proposal state
    When the user invokes "/sbir:developer-feedback"
    And the user selects "Suggestion"
    And the user enters free text "Would be great if the rigor dial showed an estimate of token cost"
    Then the feedback entry is written with type "suggestion"
    And the ratings field is null

  # ============================================================
  # Context snapshot: no active proposal
  # ============================================================

  Scenario: User submits feedback with no active proposal
    Given no ".sbir/proposals/" directory exists
    When the user invokes "/sbir:developer-feedback"
    And the user completes the feedback form
    Then the context snapshot has proposal_id null
    And the feedback is still saved successfully

  # ============================================================
  # Context snapshot: graceful degradation on missing state files
  # ============================================================

  Scenario: Feedback captured even when company profile and finder results are absent
    Given an active proposal
    And no company profile exists at "~/.sbir/company-profile.json"
    And no finder results exist at ".sbir/finder-results.json"
    When the user submits feedback
    Then the context snapshot has company_profile_age_days null
    And the context snapshot has finder_results_age_days null
    And the feedback is written without error

  # ============================================================
  # Empty submission guard
  # ============================================================

  Scenario: User tries to submit with no ratings and no free text
    Given any proposal state
    When the user invokes "/sbir:developer-feedback"
    And the user selects a feedback type
    And the user skips the ratings
    And the user skips the free text field
    Then the agent prompts once: "Are you sure you want to submit with no details?"
    When the user confirms
    Then the feedback is saved with empty ratings and null free_text

  # ============================================================
  # Output schema
  # ============================================================

  Scenario: Feedback file has correct schema
    Given a submitted feedback entry
    Then the JSON file at ".sbir/feedback/feedback-{timestamp}.json" contains:
      | field                  | type     | nullable |
      | feedback_id            | string   | false    |
      | timestamp              | ISO-8601 | false    |
      | type                   | enum     | false    |
      | ratings                | object   | false    |
      | free_text              | string   | true     |
      | context_snapshot       | object   | false    |
    And the context_snapshot contains:
      | field                    | type       | nullable |
      | plugin_version           | string     | false    |
      | proposal_id              | string     | true     |
      | topic                    | object     | true     |
      | current_wave             | int        | true     |
      | completed_waves          | list[int]  | false    |
      | skipped_waves            | list[int]  | false    |
      | rigor_profile            | string     | true     |
      | company_profile_age_days | int        | true     |
      | company_name             | string     | true     |
      | finder_results_age_days  | int        | true     |
      | top_scored_topics        | list       | false    |
      | generated_artifacts      | list[str]  | false    |
