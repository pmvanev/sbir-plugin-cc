Feature: Submission Preparation and Portal-Specific Packaging (US-013)
  As an engineer preparing to submit a reviewed proposal
  I want confidence that the submission package is complete and correctly formatted
  So I avoid the nightmare of a rejected submission due to a technicality

  Background:
    Given the proposal plugin is active
    And Phil has an active proposal with final review signed off

  # --- Happy Path ---

  Scenario: Identify submission portal and apply packaging rules
    Given AF243-001 is an Air Force topic
    When Phil prepares the submission package
    Then the tool identifies DSIP as the submission portal
    And applies DSIP file naming conventions to all package files
    And verifies file sizes against portal limits

  @skip
  Scenario: Pre-submission verification passes
    Given all required files are present and correctly named
    When the tool runs pre-submission verification
    Then it reports all checks passing
    And the checklist is written to the submission artifacts directory

  Scenario: Human confirms submission at point of no return
    Given all checks pass
    When the tool presents the submission confirmation
    Then Phil must explicitly confirm before any submission occurs
    And declining returns to preparation without any irreversible action

  Scenario: Manual submission with confirmation entry
    Given all checks pass and Phil has confirmed readiness
    When Phil enters the confirmation number "DSIP-2026-AF243-001-7842"
    Then the tool records the confirmation number and the current timestamp
    And creates an immutable archive in the submission archive directory
    And the enforcement system marks all proposal artifacts as read-only

  # --- Error Paths ---

  Scenario: Missing attachment blocks submission
    Given the Firm Certification file is missing
    When the tool runs pre-submission verification
    Then it reports the missing file and blocks submission
    And suggests where to obtain the required form

  @skip
  Scenario: PES blocks Wave 8 without Wave 7 sign-off
    Given Phil has not completed the final review sign-off
    When Phil attempts to prepare the submission package
    Then the enforcement system blocks the action
    And Phil sees "Wave 8 requires final review sign-off from Wave 7"

  Scenario: PES blocks modification after submission
    Given AF243-001 has been submitted with confirmation recorded
    When Phil attempts to edit any submitted artifact
    Then the enforcement system blocks the modification
    And Phil sees "Proposal AF243-001 is submitted. Artifacts are read-only."
