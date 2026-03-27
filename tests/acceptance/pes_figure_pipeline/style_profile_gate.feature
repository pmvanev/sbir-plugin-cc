Feature: Style Profile Gate
  As a proposal author using Wave 5 visual assets,
  I want PES to block figure generation when no style analysis has been completed
  So that figures match agency visual expectations

  Background:
    Given an active proposal for topic "SF25D-T1201" at Wave 5
    And the enforcement rules are loaded from the standard configuration

  # --- Blocking without style ---

  @skip
  Scenario: Block figure generation when style-profile.yaml missing and no skip marker
    Given the visual assets directory contains a figure specification plan
    And the visual assets directory does not contain a style profile
    And the proposal state does not contain a style analysis skip marker
    When the formatter agent attempts to Write "artifacts/sf25d-t1201/wave-5-visuals/figure-1-system-arch.svg"
    Then PES returns decision BLOCK
    And the block message includes "style analysis"

  # --- Allowing with style profile ---

  @skip
  Scenario: Allow figure generation when style-profile.yaml exists
    Given the visual assets directory contains a figure specification plan
    And the visual assets directory contains a style profile
    When the formatter agent attempts to Write "artifacts/sf25d-t1201/wave-5-visuals/figure-2-data-flow.svg"
    Then PES returns decision ALLOW

  # --- Allowing with explicit skip ---

  @skip
  Scenario: Allow figure generation when user explicitly skipped style analysis
    Given the visual assets directory contains a figure specification plan
    And the visual assets directory does not contain a style profile
    And the proposal state contains a style analysis skip marker
    When the formatter agent attempts to Write "artifacts/sf25d-t1201/wave-5-visuals/figure-2-data-flow.svg"
    Then PES returns decision ALLOW

  # --- Allowing prerequisite creation ---

  @skip
  Scenario: Allow writing style-profile.yaml itself (prerequisite creation)
    Given the visual assets directory contains a figure specification plan
    And the visual assets directory does not contain a style profile
    When the formatter agent attempts to Write "artifacts/sf25d-t1201/wave-5-visuals/style-profile.yaml"
    Then PES returns decision ALLOW
