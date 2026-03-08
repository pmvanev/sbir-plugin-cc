Feature: TPOC Question Generation and Answer Ingestion (US-005)
  As an engineer preparing for a TPOC call
  I want strategically prioritized questions from solicitation gaps
  So I surface the real requirements in my one chance to talk to the TPOC

  Background:
    Given the proposal plugin is active
    And Phil has an active proposal for AF243-001 with Go/No-Go "go"

  # --- Happy Path ---

  Scenario: Generate TPOC questions from solicitation gaps
    Given a compliance matrix exists with 3 flagged ambiguities
    When Phil generates TPOC questions
    Then questions are generated tagged by category
    And questions are ordered by strategic priority
    And questions are written to the Wave 1 strategy artifacts
    And the TPOC status changes to "questions generated"

  Scenario: Ingest TPOC answers from call notes
    Given TPOC questions were generated for AF243-001
    And Phil has a notes file from the TPOC call
    When Phil ingests the TPOC call notes
    Then answers are matched to original questions
    And unanswered questions are marked
    And a solicitation delta analysis is generated
    And the compliance matrix is updated with TPOC clarifications
    And the TPOC status changes to "answers ingested"

  # --- Edge Cases ---

  Scenario: TPOC call never happens -- pending state does not block progress
    Given TPOC questions were generated 14 days ago
    And no answers have been ingested
    When Phil checks proposal status
    Then Phil sees "TPOC questions generated -- PENDING CALL"
    And no wave is blocked by the pending TPOC state

  Scenario: Partial answer ingestion from short call
    Given 23 TPOC questions were generated
    And Phil's notes cover only 8 questions
    When Phil ingests the partial notes
    Then 8 answers are matched
    And 15 questions are marked as unanswered
    And delta analysis is generated from the 8 answered questions

  # --- Error Paths ---

  Scenario: Cannot generate questions without compliance matrix
    Given no compliance matrix exists
    When Phil attempts to generate TPOC questions
    Then Phil sees "Compliance matrix required before generating TPOC questions"
    And Phil sees guidance to run the strategy wave command first

  Scenario: Notes file not found during ingestion
    Given TPOC questions were generated
    When Phil attempts to ingest notes from a non-existent file path
    Then Phil sees "Notes file not found"
    And Phil sees guidance to verify the file path
