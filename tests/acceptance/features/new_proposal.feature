Feature: Start New Proposal from Solicitation (US-002)
  As an engineer evaluating a new solicitation
  I want data-driven Go/No-Go analysis
  So I invest time only in proposals worth pursuing

  Background:
    Given the proposal plugin is active

  # --- Happy Path ---

  Scenario: Start new proposal from local PDF file
    Given Phil has a solicitation PDF for topic AF243-001
    When Phil starts a new proposal from the PDF file
    Then Phil sees topic ID "AF243-001"
    And Phil sees agency "Air Force", phase "I", and deadline "2026-04-15"
    And Phil sees title "Compact Directed Energy for Maritime UAS Defense"
    And a new proposal state is created with the parsed metadata

  Scenario: Corpus search finds related past work during proposal creation
    Given Phil has ingested 5 past proposals into the corpus
    And 2 proposals relate to directed energy topics
    When Phil starts a new proposal for topic AF243-001
    Then Phil sees 2 related proposals with relevance scores
    And Phil sees fit scoring across subject matter, past performance, and certifications
    And Phil sees a Go/No-Go recommendation

  Scenario: Go decision recorded and unlocks Wave 1
    Given Phil sees a Go/No-Go recommendation for AF243-001
    When Phil selects "go" at the Go/No-Go checkpoint
    Then the proposal records Go/No-Go as "go"
    And Wave 1 is unlocked

  Scenario: No-Go decision archives the proposal
    Given Phil sees a Go/No-Go recommendation for AF243-001
    When Phil selects "no-go" at the Go/No-Go checkpoint
    Then the proposal records Go/No-Go as "no-go"
    And the proposal is archived
    And Phil sees "AF243-001 archived as no-go"

  # --- Edge Cases ---

  Scenario: Empty corpus does not block new proposal
    Given Phil has never ingested any documents into the corpus
    When Phil starts a new proposal for topic AF243-001
    Then Phil sees "No corpus documents found"
    And Phil sees the suggestion to add past proposals
    And fit scoring proceeds with solicitation data alone

  # --- Error Paths ---

  Scenario: Solicitation file cannot be parsed
    Given Phil provides a PDF that contains only scanned images with no extractable text
    When Phil starts a new proposal from the file
    Then Phil sees "Could not parse solicitation"
    And Phil sees guidance on acceptable file formats

  Scenario: Solicitation missing required metadata fields
    Given Phil provides a solicitation with no identifiable deadline
    When Phil starts a new proposal from the file
    Then Phil sees a warning that the deadline could not be extracted
    And Phil is prompted to enter the deadline manually
