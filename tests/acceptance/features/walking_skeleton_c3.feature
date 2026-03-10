Feature: C3 Walking Skeletons -- Production, Submission, and Learning
  As an engineer completing proposal production and submission
  I want a structured workflow from figures through submission and learning
  So I can submit a polished proposal and improve with every cycle

  Background:
    Given the proposal plugin is active

  # Walking Skeleton 6: Engineer produces visual assets and formats proposal
  # Validates: figure inventory -> generation -> cross-ref validation -> formatting -> assembly -> compliance check
  @walking_skeleton
  @skip
  Scenario: Engineer produces figures, formats document, and assembles volumes
    Given Phil has an active proposal with all sections approved and PDCs GREEN
    And the approved outline contains 5 figure placeholders
    When Phil generates the figure inventory
    Then Phil sees 5 figures classified by type and generation method
    When Phil generates and approves all figures
    Then Phil sees a cross-reference log with all references valid
    When Phil formats the proposal selecting "Microsoft Word (.docx)"
    Then Phil sees formatting applied with page count within limits
    And Phil sees a jargon audit with any undefined acronyms flagged
    When the tool assembles volumes
    Then Phil sees Volume 1 (Technical), Volume 2 (Cost), and Volume 3 (Company Info)
    And Phil reviews the assembled package at the human checkpoint

  # Walking Skeleton 7: Engineer reviews, submits, and learns from outcome
  # Validates: final review -> sign-off -> portal packaging -> submission -> outcome recording -> debrief
  @walking_skeleton
  @skip
  Scenario: Engineer reviews proposal, submits, and captures lessons learned
    Given Phil has an active proposal with assembled volumes ready for review
    When Phil requests the final review
    Then Phil sees evaluation scores with rationales
    And Phil sees red team objections tagged by severity
    When Phil addresses HIGH issues and signs off
    Then Wave 8 is unlocked
    When Phil prepares the submission package
    Then Phil sees all files correctly named and sized for the portal
    When Phil confirms submission and enters the confirmation number
    Then an immutable archive is created and artifacts are read-only
    When Phil records the outcome and ingests the debrief
    Then Phil sees critiques mapped to proposal sections
    And Phil sees pattern analysis across the corpus

  # Walking Skeleton 8: PES enforcement prevents production process violations
  # Validates: PDC gate -> deadline blocking -> submission immutability -> corpus integrity
  @walking_skeleton
  Scenario: Enforcement system prevents production and submission violations
    Given Phil has an active proposal with section 3.2 having a RED Tier 2 PDC item
    When Phil attempts to start Wave 5 visual asset work
    Then the enforcement system blocks the action
    And Phil sees the specific section and PDC items that remain RED
    And Phil sees guidance to resolve the RED items before proceeding
