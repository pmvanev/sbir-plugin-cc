Feature: Writing Style Gate
  As a proposal author using Wave 4 drafting,
  I want PES to block draft writes when no writing style selection has been made
  So that all sections are drafted with a consistent writing voice

  Background:
    Given an active proposal for topic "SF25D-T1201" at Wave 4
    And the enforcement rules are loaded from the standard configuration

  # --- Blocking without quality preferences ---

  @skip
  Scenario: Block draft write when quality-preferences.json missing and no skip marker
    Given no quality preferences file exists at the global configuration location
    And the proposal does not have a writing style selection skip marker
    When the writer agent attempts to Write "artifacts/sf25d-t1201/wave-4-drafting/sections/technical-approach.md"
    Then PES returns decision BLOCK
    And the block message includes "writing style selection"
    And the block message includes "quality-preferences.json"

  @skip
  Scenario: Block Edit to existing draft when no style selection
    Given no quality preferences file exists at the global configuration location
    And the proposal does not have a writing style selection skip marker
    And "artifacts/sf25d-t1201/wave-4-drafting/sections/technical-approach.md" exists from a previous session
    When the writer agent attempts to Edit "artifacts/sf25d-t1201/wave-4-drafting/sections/technical-approach.md"
    Then PES returns decision BLOCK
    And the block message includes "writing style selection"

  @skip
  Scenario: Block message includes both resolution paths
    Given no quality preferences file exists at the global configuration location
    And the proposal does not have a writing style selection skip marker
    When the writer agent attempts to Write "artifacts/sf25d-t1201/wave-4-drafting/sections/technical-approach.md"
    Then PES returns decision BLOCK
    And the block message mentions "/proposal quality discover" as one resolution path
    And the block message mentions "skip" as an alternative resolution path

  # --- Allowing with quality preferences ---

  @skip
  Scenario: Allow draft write when quality-preferences.json exists
    Given the global configuration location contains quality preferences
    When the writer agent attempts to Write "artifacts/sf25d-t1201/wave-4-drafting/sections/technical-approach.md"
    Then PES returns decision ALLOW

  # --- Allowing with explicit skip ---

  @skip
  Scenario: Allow draft write when user explicitly skipped style selection
    Given no quality preferences file exists at the global configuration location
    And the proposal has a writing style selection skip marker
    When the writer agent attempts to Write "artifacts/sf25d-t1201/wave-4-drafting/sections/sow.md"
    Then PES returns decision ALLOW

  # --- Allowing prerequisite creation ---

  @skip
  Scenario: Allow writing quality-preferences.json itself
    Given no quality preferences file exists at the global configuration location
    When the writer agent attempts to Write "~/.sbir/quality-preferences.json"
    Then PES returns decision ALLOW
