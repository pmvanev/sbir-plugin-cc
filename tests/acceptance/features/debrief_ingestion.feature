Feature: Debrief Ingestion and Critique-to-Section Mapping (US-015)
  As an engineer who receives debrief feedback after proposal decisions
  I want critiques structured and mapped to sections for lasting learning
  So I can improve my win rate instead of repeating the same mistakes

  Background:
    Given the proposal plugin is active
    And Phil has a submitted proposal for AF243-001

  # --- Happy Path ---

  @skip
  Scenario: Ingest debrief and map critiques to sections
    Given AF243-001 was not selected and Phil has a debrief letter
    When Phil ingests the debrief from a PDF file
    Then the tool parses reviewer scores and critique comments
    And maps each critique to a specific proposal section and page
    And flags critiques matching known weaknesses from past debriefs
    And writes the structured debrief to the learning artifacts directory

  @skip
  Scenario: Win/loss pattern analysis updates across corpus
    Given the corpus contains 7 proposals with 3 awarded and 4 not selected
    When the tool updates pattern analysis
    Then it identifies recurring weaknesses across losses
    And identifies recurring strengths across wins
    And writes pattern analysis to the learning artifacts directory

  Scenario: Record awarded outcome and archive winner
    Given AF243-001 was awarded
    When Phil records the outcome as "awarded"
    Then the winning proposal is archived with outcome tag
    And winning discriminators are extracted for pattern analysis
    And the tool suggests Phase II pre-planning

  # --- Edge Cases ---

  Scenario: Record outcome without debrief
    Given AF243-001 was not selected
    And no debrief letter is available
    When Phil records the outcome
    Then the outcome tag is appended to the proposal state
    And no debrief artifacts are created
    And the tool notes "Debrief can be ingested later if received"

  @skip
  Scenario: Ingest unstructured debrief with minimal content
    Given the debrief letter is a single paragraph with no scores
    When Phil ingests the debrief from a PDF file
    Then the tool preserves the full text as freeform feedback
    And notes "Structured scores could not be extracted from this debrief"
    And the freeform text is available for keyword-based pattern matching

  @skip
  Scenario: Lessons learned human checkpoint
    Given debrief ingestion and pattern analysis are complete
    When the tool presents lessons learned
    Then Phil can review, edit, and acknowledge before corpus update completes

  # --- Error Path ---

  @skip
  @property
  Scenario: Win/loss tags are append-only regardless of outcome changes
    Given any proposal with an existing outcome tag
    When any process attempts to overwrite the tag
    Then the modification is blocked
    And the original tag is preserved
