Feature: Proposal Format Selection
  As part of the guided proposal setup, the user selects LaTeX or DOCX
  as the output format for their proposal. This choice persists in
  proposal state and is consumed by downstream agents (writer, formatter,
  submission agent).

  Background:
    Given Phil Santos has a solicitation file for topic AF243-001

  # --- Happy Path: Explicit Selection ---

  Scenario: User selects LaTeX during proposal setup
    Given Phil Santos runs "/proposal new ./solicitations/AF243-001.pdf"
    And the solicitation has been parsed successfully
    And fit scoring is complete
    When the system prompts for output format selection
    And Phil Santos selects "latex"
    Then the proposal state field "output_format" is set to "latex"
    And the setup continues to the Go/No-Go checkpoint

  Scenario: User selects DOCX during proposal setup
    Given Phil Santos runs "/proposal new ./solicitations/N244-012.pdf"
    And the solicitation has been parsed successfully
    And fit scoring is complete
    When the system prompts for output format selection
    And Phil Santos selects "docx"
    Then the proposal state field "output_format" is set to "docx"
    And the setup continues to the Go/No-Go checkpoint

  # --- Default Behavior ---

  Scenario: User accepts default format by pressing Enter
    Given Phil Santos runs "/proposal new ./solicitations/AF243-001.pdf"
    And the solicitation has been parsed successfully
    And fit scoring is complete
    When the system prompts for output format selection
    And Phil Santos presses Enter without typing a selection
    Then the proposal state field "output_format" is set to "docx"
    And the confirmation message shows "Output format set to: DOCX (default)"

  # --- Solicitation Hint ---

  Scenario: Solicitation specifies PDF submission and system recommends LaTeX
    Given the solicitation for topic AF243-001 contains a requirement "Submit as PDF"
    And Phil Santos runs "/proposal new ./solicitations/AF243-001.pdf"
    And the solicitation has been parsed successfully
    When the system prompts for output format selection
    Then the prompt includes a note "Solicitation requires PDF submission. LaTeX recommended."
    And "latex" is marked as "(recommended)" in the choices

  # --- Mid-Proposal Format Change ---

  Scenario: User changes format from DOCX to LaTeX before drafting
    Given Phil Santos has an active proposal for AF243-001 with output_format "docx"
    And the current wave is 1 (Requirements and Strategy)
    When Phil Santos runs "/proposal config format latex"
    Then the proposal state field "output_format" is updated to "latex"
    And the confirmation message shows "Output format changed to: LaTeX"

  Scenario: User changes format after drafting has begun and receives warning
    Given Phil Santos has an active proposal for AF243-001 with output_format "docx"
    And the current wave is 4 (Drafting)
    And the technical volume has status "drafting"
    When Phil Santos runs "/proposal config format latex"
    Then the system displays a warning about potential rework
    And the warning mentions "Section structures may need adjustment"
    And the system asks for confirmation before proceeding

  # --- Status Display ---

  Scenario: Proposal status dashboard shows output format
    Given Phil Santos has an active proposal for AF243-001 with output_format "latex"
    When Phil Santos runs "/proposal status"
    Then the status dashboard displays "Format: LaTeX"
