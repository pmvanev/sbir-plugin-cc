Feature: Topic Selection and Proposal Transition
  As a solo SBIR proposal writer
  I want to select a scored topic and transition directly into proposal creation
  So that I can start writing without re-entering topic metadata

  # --- US-SF-004: Select Topic and Transition ---
  # Note: These scenarios describe agent/command behavior (LLM-mediated).
  # They are documented for stakeholder alignment but not executable as
  # automated Python tests. The agent and command are Markdown artifacts.

  # Happy path: select and see confirmation
  @skip @agent_behavior
  Scenario: Proposal writer sees confirmation before starting proposal
    Given Phil is viewing finder results
    And topic "AF263-042" has recommendation GO with score 0.82
    When Phil types "pursue AF263-042"
    Then the tool displays topic ID, title, agency, phase, deadline, and score
    And the tool prompts "Proceed to create proposal? (y/n)"

  # Happy path: confirm transitions to proposal workflow
  @skip @agent_behavior
  Scenario: Confirmed selection transitions to proposal creation
    Given Phil has typed "pursue AF263-042" and the confirmation is displayed
    When Phil confirms with "y"
    Then the proposal workflow begins with topic "AF263-042" pre-loaded
    And the proposal has topic "Compact Directed Energy for C-UAS", agency "Air Force", phase "I", deadline "2026-05-15"
    And Phil does not re-enter any topic metadata

  # Error: cancel returns to results
  @skip @agent_behavior
  Scenario: Cancelled selection returns to results without side effects
    Given Phil has typed "pursue N263-044" and the confirmation is displayed
    When Phil declines with "n"
    Then the tool returns to the results list
    And no proposal is created

  # Error: pursue expired topic blocked
  @skip @agent_behavior
  Scenario: Expired topic cannot be pursued
    Given topic "AF263-042" has a deadline of "2026-03-01" which has passed
    When Phil types "pursue AF263-042"
    Then the tool displays "Topic deadline has expired (2026-03-01)"
    And the tool does not offer the confirmation prompt
    And the tool returns to the results list
