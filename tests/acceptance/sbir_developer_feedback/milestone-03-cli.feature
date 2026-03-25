Feature: Feedback CLI — sbir_feedback_cli.py save command
  As an agent invoking the feedback command via Bash
  I want sbir_feedback_cli.py to assemble and persist a feedback entry
  So that the agent can capture feedback with a single Bash call

  # Story 1 (command invokable), Story 4 (developer reads structured feedback)

  @skip
  Scenario: CLI saves a quality issue entry with full context
    Given an active proposal workspace with proposal-state.json, rigor-profile.json, and finder-results.json
    And a company profile at the configured profile path
    When the CLI is called: sbir_feedback_cli.py save --type quality --ratings '{"past_performance": 2}' --free-text "Wrong project"
    Then the CLI exits with code 0
    And the CLI outputs JSON with feedback_id and file_path
    And the feedback file exists at the reported file_path
    And the feedback file has type "quality"
    And the context_snapshot has current_wave and completed_waves populated

  @skip
  Scenario: CLI saves a bug report with no ratings
    Given any workspace state
    When the CLI is called: sbir_feedback_cli.py save --type bug --free-text "CLI crashed"
    Then the CLI exits with code 0
    And the feedback file has type "bug"
    And the feedback file has ratings with all dimensions null

  @skip
  Scenario: CLI saves a suggestion with no free text
    Given any workspace state
    When the CLI is called: sbir_feedback_cli.py save --type suggestion
    Then the CLI exits with code 0
    And the feedback file has type "suggestion"
    And the feedback file has free_text null

  @skip
  Scenario: CLI works with no active proposal
    Given a workspace with no .sbir/proposals/ directory
    When the CLI is called: sbir_feedback_cli.py save --type bug --free-text "No proposal test"
    Then the CLI exits with code 0
    And the feedback file has context_snapshot.proposal_id null
    And the feedback file has context_snapshot.completed_waves as empty list

  @skip
  Scenario: CLI works with missing company profile
    Given an active proposal but no company profile at the profile path
    When the CLI is called: sbir_feedback_cli.py save --type suggestion
    Then the CLI exits with code 0
    And the feedback file has context_snapshot.company_name null
    And the feedback file has context_snapshot.company_profile_age_days null

  @skip
  Scenario: CLI captures plugin version from git
    Given a git repository is present in the workspace
    When the CLI is called: sbir_feedback_cli.py save --type bug
    Then the feedback file has context_snapshot.plugin_version as a non-empty string other than "unknown"

  @skip
  Scenario: CLI captures plugin_version as "unknown" when git is unavailable
    Given git is not available in the environment
    When the CLI is called: sbir_feedback_cli.py save --type suggestion
    Then the CLI exits with code 0
    And the feedback file has context_snapshot.plugin_version "unknown"

  @skip
  Scenario: CLI lists generated artifacts alphabetically
    Given an active proposal with artifacts: "strategy.md", "outline.md", "technical-approach.md"
    When the CLI is called: sbir_feedback_cli.py save --type quality
    Then the context_snapshot.generated_artifacts is ["outline.md", "strategy.md", "technical-approach.md"]
