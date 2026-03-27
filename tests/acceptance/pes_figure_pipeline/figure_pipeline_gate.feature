Feature: Figure Pipeline Gate
  As a proposal author using Wave 5 visual assets,
  I want PES to block figure file writes when no figure specification plan exists
  So that the formatter agent cannot bypass the planning phase

  Background:
    Given an active proposal for topic "SF25D-T1201" at Wave 5
    And the enforcement rules are loaded from the standard configuration

  # --- Blocking without specs ---

  Scenario: Block figure file write when figure-specs.md does not exist
    Given the visual assets directory does not contain a figure specification plan
    When the formatter agent attempts to Write "artifacts/sf25d-t1201/wave-5-visuals/figure-1-system-arch.svg"
    Then PES returns decision BLOCK
    And the block message includes "figure specifications"
    And the block message includes "figure-specs.md"

  Scenario: Block Edit to existing figure when figure-specs.md does not exist
    Given the visual assets directory does not contain a figure specification plan
    And "artifacts/sf25d-t1201/wave-5-visuals/figure-1-system-arch.svg" exists from a previous session
    When the formatter agent attempts to Edit "artifacts/sf25d-t1201/wave-5-visuals/figure-1-system-arch.svg"
    Then PES returns decision BLOCK
    And the block message includes "figure specifications"

  # --- Allowing prerequisite creation ---

  Scenario: Allow writing figure-specs.md itself (prerequisite creation)
    Given the visual assets directory does not contain a figure specification plan
    When the formatter agent attempts to Write "artifacts/sf25d-t1201/wave-5-visuals/figure-specs.md"
    Then PES returns decision ALLOW

  # --- Allowing after specs exist ---

  Scenario: Allow figure file write when figure-specs.md exists and style gate passes
    Given the visual assets directory contains a figure specification plan
    And the visual assets directory contains a style profile
    When the formatter agent attempts to Write "artifacts/sf25d-t1201/wave-5-visuals/figure-1-system-arch.svg"
    Then PES returns decision ALLOW

  Scenario: Allow writing figure-log.md when figure-specs.md exists and style gate passes
    Given the visual assets directory contains a figure specification plan
    And the visual assets directory contains a style profile
    When the formatter agent attempts to Write "artifacts/sf25d-t1201/wave-5-visuals/figure-log.md"
    Then PES returns decision ALLOW

  Scenario: Allow writing external brief when figure-specs.md exists and style gate passes
    Given the visual assets directory contains a figure specification plan
    And the visual assets directory contains a style profile
    When the formatter agent attempts to Write "artifacts/sf25d-t1201/wave-5-visuals/external-briefs/figure-3-brief.md"
    Then PES returns decision ALLOW
