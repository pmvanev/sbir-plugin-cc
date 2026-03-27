Feature: Outline Gate
  As a proposal author using Wave 4 drafting,
  I want PES to block draft writes when no proposal outline exists in wave-3-outline
  So that the writer agent cannot bypass the outline planning phase

  Background:
    Given an active proposal for topic "SF25D-T1201" at Wave 4
    And the enforcement rules are loaded from the standard configuration

  # --- Blocking without outline ---

  @skip
  Scenario: Block draft section write when proposal-outline.md does not exist
    Given the outline directory does not contain a proposal outline
    When the writer agent attempts to Write "artifacts/sf25d-t1201/wave-4-drafting/section-1-technical-approach.md"
    Then PES returns decision BLOCK
    And the block message includes "proposal outline"
    And the block message includes "proposal-outline.md"
    And the block message includes "wave-3-outline"

  @skip
  Scenario: Block Edit to existing draft when proposal-outline.md does not exist
    Given the outline directory does not contain a proposal outline
    And "artifacts/sf25d-t1201/wave-4-drafting/section-1-technical-approach.md" exists from a previous session
    When the writer agent attempts to Edit "artifacts/sf25d-t1201/wave-4-drafting/section-1-technical-approach.md"
    Then PES returns decision BLOCK
    And the block message includes "proposal outline"

  # --- Allowing after outline exists ---

  @skip
  Scenario: Allow draft section write when proposal-outline.md exists
    Given the outline directory contains a proposal outline
    When the writer agent attempts to Write "artifacts/sf25d-t1201/wave-4-drafting/section-1-technical-approach.md"
    Then PES returns decision ALLOW

  @skip
  Scenario: Allow writing any file type to wave-4-drafting when outline exists
    Given the outline directory contains a proposal outline
    When the writer agent attempts to Write "artifacts/sf25d-t1201/wave-4-drafting/section-2-schedule.md"
    Then PES returns decision ALLOW
