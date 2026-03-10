Feature: Final Review with Simulated Government Evaluator (US-012)
  As an engineer who is the sole reviewer of proposals
  I want a simulated adversarial review to catch fatal flaws
  So I can fix critical issues while there is still time before submission

  Background:
    Given the proposal plugin is active
    And Phil has an active proposal with assembled volumes ready for review

  # --- Happy Path ---

  Scenario: Reviewer persona simulation scores proposal
    Given the assembled proposal for AF243-001 is ready for final review
    When Phil requests the final review
    Then the tool scores the proposal against 5 evaluation criteria
    And each score includes a brief rationale
    And the scorecard is written to the review artifacts directory

  Scenario: Red team review identifies strongest objections
    Given the reviewer simulation has completed
    When the tool runs a red team review
    Then it identifies objections tagged by severity (HIGH, MEDIUM, LOW)
    And each objection references a specific section and page
    And the findings are written to the review artifacts directory

  Scenario: Debrief-informed review flags known weaknesses
    Given past debrief feedback for AF241-087 exists in the corpus
    And that debrief said "transition pathway lacked specificity"
    When the tool checks against known weaknesses
    Then it flags "transition pathway specificity" as a known weakness
    And reports whether the current proposal addresses it

  Scenario: Issue resolution and re-review
    Given the red team found 1 HIGH issue in Section 3.2
    When Phil fixes the issue and requests re-review
    Then the tool re-reviews and confirms the HIGH issue is resolved
    And the iteration count is logged

  # --- Edge Cases ---

  Scenario: No past debriefs available
    Given no debrief feedback exists in the corpus
    When the tool runs the debrief cross-check
    Then it reports "No past debrief data available"
    And notes this check improves as debriefs are ingested

  Scenario: Forced sign-off after 2 review iterations
    Given 2 review iterations have been completed
    And 1 MEDIUM issue remains unresolved
    When Phil requests a third review cycle
    Then Phil sees that sign-off is required after 2 iterations
    And unresolved issues are documented in the sign-off record

  # --- Sign-Off Gate ---

  Scenario: Human sign-off unlocks Wave 8
    Given all HIGH issues are addressed
    When Phil signs off on the final review
    Then the sign-off is recorded with timestamp
    And the sign-off is written to the review artifacts directory
    And Wave 8 is unlocked
