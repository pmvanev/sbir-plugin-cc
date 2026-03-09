Feature: Wave 4 Drafting, Review, and Iteration
  As an engineer writing proposal sections
  I want section-by-section drafting with structured review loops
  So I produce a complete, compliance-checked, reviewer-scored draft

  Background:
    Given the proposal plugin is active
    And Phil has an active proposal with an approved proposal outline

  # --- Drafting: Happy Path ---

  @skip
  Scenario: Technical approach section drafted from outline
    Given an approved outline with a technical approach section and 8-page budget
    When Phil requests a draft of the technical approach section
    Then Phil sees a draft addressing the mapped compliance items
    And the draft references discriminators from the discrimination table
    And the draft word count is reported against the page budget

  @skip
  Scenario: Statement of work section drafted with contractual language
    Given an approved outline with a statement of work section
    When Phil requests a draft of the statement of work section
    Then Phil sees a draft with milestone-based deliverables
    And the draft uses active voice and future tense

  @skip
  Scenario: All nine sections can be drafted in sequence
    Given an approved outline covering all required proposal sections
    When Phil drafts each section in the recommended order
    Then Phil sees a draft for technical approach
    And Phil sees a draft for statement of work
    And Phil sees a draft for key personnel
    And Phil sees a draft for facilities and equipment
    And Phil sees a draft for past performance
    And Phil sees a draft for management plan
    And Phil sees a draft for commercialization plan
    And Phil sees a draft for risk identification and mitigation
    And Phil sees a draft for references

  # --- Review: Happy Path ---

  Scenario: Section review produces actionable scorecard
    Given a draft exists for the technical approach section
    When the section is submitted for review
    Then Phil sees a scorecard with strengths and weaknesses
    And each finding includes location, severity, and specific suggestion
    And the scorecard is written to the review artifacts

  @skip
  Scenario: Review checks section against debrief weakness patterns
    Given a draft exists for the technical approach section
    And debrief history includes "Insufficient TRL advancement methodology" as a known weakness
    When the section is submitted for review
    Then the review flags any matching weakness patterns from debrief history

  Scenario: Full draft review checkpoint verifies compliance coverage
    Given all proposal sections have been drafted
    When the full draft review is requested
    Then the compliance matrix shows all items addressed
    And a full scorecard is produced across all sections
    And Phil can approve the draft to proceed to formatting

  # --- Iteration: Happy Path ---

  @skip
  Scenario: Section iteration addresses reviewer findings
    Given the technical approach section has review findings
    When Phil requests iteration on the technical approach section
    Then the writer addresses the review findings
    And unchanged content is preserved
    And the revised section is submitted for re-review

  Scenario: Re-review tracks which findings were addressed
    Given the technical approach was revised after first review
    When the revised section is re-reviewed
    Then each prior finding shows whether it was addressed or remains open
    And updated ratings reflect the improvements

  Scenario: Maximum two review cycles then escalate
    Given the technical approach has completed 2 review cycles
    And unresolved findings remain
    When a third review cycle is requested
    Then Phil sees unresolved findings escalated for human decision
    And Phil can accept the section as-is or provide final revisions

  # --- Error Paths ---

  Scenario: Cannot draft section without approved outline
    Given no proposal outline has been approved
    When Phil attempts to draft a section
    Then Phil sees "Approved outline required before drafting"
    And Phil sees guidance to complete Wave 3 outline approval first

  Scenario: Cannot draft section not in the outline
    Given an approved outline that does not include an "executive summary" section
    When Phil attempts to draft an "executive summary" section
    Then Phil sees "Section 'executive summary' is not in the approved outline"
    And Phil sees guidance to update the outline first

  Scenario: Cannot review section that has no draft
    Given no draft exists for the past performance section
    When Phil requests review of the past performance section
    Then Phil sees "No draft exists for past performance"
    And Phil sees guidance to draft the section first

  Scenario: Section draft exceeding page budget is flagged
    Given the technical approach has an 8-page budget
    When Phil's draft reaches approximately 5200 words
    Then Phil sees a warning that the section exceeds its page budget
    And Phil sees suggestions to cut content or reallocate pages

  Scenario: Compliance matrix gap detected during drafting
    Given a draft exists for the technical approach section
    And 2 compliance items mapped to technical approach are not addressed in the draft
    When the compliance check runs against the section
    Then Phil sees "2 compliance items not addressed in technical approach"
    And the unaddressed items are listed by ID

  # --- Edge Cases ---

  @skip
  Scenario: Drafting with no debrief history proceeds without pattern matching
    Given no debrief history exists in the corpus
    When the technical approach section is submitted for review
    Then the review notes "No debrief history available for pattern matching"
    And the review proceeds using evaluation criteria alone

  @skip
  Scenario: Acronym audit flags undefined terms
    Given a draft uses "CONOPS" 7 times without definition
    When the section is submitted for review
    Then the review flags "Acronym CONOPS used without definition"
    And the finding suggests defining on first use

  @skip
  Scenario: Cross-reference check detects missing figures
    Given a draft references "Figure 3" but only Figures 1 and 2 exist
    When the section is submitted for review
    Then the review flags "Figure 3 referenced but does not exist"
    And the finding suggests creating the figure or updating the reference

  @property
  @skip
  Scenario: Draft section always traces to at least one compliance item
    Given any valid section draft produced from the approved outline
    When the draft is validated
    Then the section addresses at least one compliance item

  @property
  @skip
  Scenario: Review findings always include location and severity
    Given any section review
    When findings are produced
    Then every finding includes a location and severity level
