Feature: Directory-Based Corpus Ingestion (US-003)
  As an engineer with directories of past proposals
  I want batch ingestion with near-zero effort
  So my past work is searchable when starting new proposals

  Background:
    Given the proposal plugin is active

  # --- Happy Path ---

  Scenario: Ingest a directory of past proposals and debriefs
    Given Phil has a directory with 5 PDF proposals and 2 Word debrief letters
    When Phil adds the directory to the corpus
    Then 7 documents are ingested
    And Phil sees "Ingested 7 documents (5 proposals, 2 debriefs)"
    And the corpus is ready for search

  Scenario: Re-ingestion adds only new files
    Given Phil previously ingested a directory with 7 documents
    And Phil has added 1 new PDF to the directory
    When Phil adds the same directory to the corpus again
    Then only the 1 new document is ingested
    And Phil sees "1 new document ingested. 7 already in corpus."

  # --- Edge Cases ---

  Scenario: Skip unsupported file types in directory
    Given a directory contains 3 PDFs, 2 Word docs, and 15 Python source files
    When Phil adds the directory to the corpus
    Then 5 supported documents are ingested
    And 15 unsupported files are skipped
    And Phil sees "Ingested 5 documents. Skipped 15 unsupported files."

  # --- Error Paths ---

  Scenario: Empty directory handled gracefully
    Given Phil provides a path to an empty directory
    When Phil adds the directory to the corpus
    Then Phil sees "No supported documents found"
    And Phil sees the list of supported file types

  Scenario: Corrupted or protected document skipped with warning
    Given a directory contains 4 PDFs, one of which is password-protected
    When Phil adds the directory to the corpus
    Then 3 readable PDFs are ingested
    And the password-protected PDF is skipped
    And Phil sees a warning naming the skipped file with the reason

  Scenario: Non-existent directory path rejected
    Given Phil provides a path that does not exist
    When Phil adds the directory to the corpus
    Then Phil sees "Directory not found"
    And Phil sees guidance to verify the path
