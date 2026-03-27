Feature: PES Figure Pipeline Enforcement
  As a proposal author using the SBIR plugin
  I want PES to enforce the figure generation pipeline
  So that the formatter agent cannot bypass planning or style analysis

  Background:
    Given an active proposal for topic "SF25D-T1201" owned by Dr. Rafael Moreno
    And the proposal is at Wave 5 (visual assets)
    And the artifact directory is "artifacts/sf25d-t1201/wave-5-visuals/"

  # --- Figure Pipeline Gate ---

  Scenario: Block figure file write when figure-specs.md does not exist
    Given the directory "artifacts/sf25d-t1201/wave-5-visuals/" does not contain "figure-specs.md"
    When the formatter agent attempts to Write "artifacts/sf25d-t1201/wave-5-visuals/figure-1-system-arch.svg"
    Then PES returns decision BLOCK
    And the block message includes "figure specifications"
    And the block message includes "figure-specs.md"

  Scenario: Allow writing figure-specs.md itself (prerequisite creation)
    Given the directory "artifacts/sf25d-t1201/wave-5-visuals/" does not contain "figure-specs.md"
    When the formatter agent attempts to Write "artifacts/sf25d-t1201/wave-5-visuals/figure-specs.md"
    Then PES returns decision ALLOW

  Scenario: Allow figure file write when figure-specs.md exists and style gate passes
    Given "artifacts/sf25d-t1201/wave-5-visuals/figure-specs.md" exists
    And "artifacts/sf25d-t1201/wave-5-visuals/style-profile.yaml" exists
    When the formatter agent attempts to Write "artifacts/sf25d-t1201/wave-5-visuals/figure-1-system-arch.svg"
    Then PES returns decision ALLOW

  Scenario: Block Edit to existing figure when figure-specs.md does not exist
    Given the directory "artifacts/sf25d-t1201/wave-5-visuals/" does not contain "figure-specs.md"
    And "artifacts/sf25d-t1201/wave-5-visuals/figure-1-system-arch.svg" exists from a previous session
    When the formatter agent attempts to Edit "artifacts/sf25d-t1201/wave-5-visuals/figure-1-system-arch.svg"
    Then PES returns decision BLOCK
    And the block message includes "figure specifications"

  Scenario: Allow writing figure-log.md when figure-specs.md exists and style gate passes
    Given "artifacts/sf25d-t1201/wave-5-visuals/figure-specs.md" exists
    And "artifacts/sf25d-t1201/wave-5-visuals/style-profile.yaml" exists
    When the formatter agent attempts to Write "artifacts/sf25d-t1201/wave-5-visuals/figure-log.md"
    Then PES returns decision ALLOW

  Scenario: Allow writing external brief when figure-specs.md exists and style gate passes
    Given "artifacts/sf25d-t1201/wave-5-visuals/figure-specs.md" exists
    And "artifacts/sf25d-t1201/wave-5-visuals/style-profile.yaml" exists
    When the formatter agent attempts to Write "artifacts/sf25d-t1201/wave-5-visuals/external-briefs/figure-3-brief.md"
    Then PES returns decision ALLOW

  # --- Style Profile Gate ---

  Scenario: Block figure generation when style-profile.yaml missing and no skip marker
    Given "artifacts/sf25d-t1201/wave-5-visuals/figure-specs.md" exists
    And the directory "artifacts/sf25d-t1201/wave-5-visuals/" does not contain "style-profile.yaml"
    And the proposal state does not contain "style_analysis_skipped"
    When the formatter agent attempts to Write "artifacts/sf25d-t1201/wave-5-visuals/figure-1-system-arch.svg"
    Then PES returns decision BLOCK
    And the block message includes "style analysis"

  Scenario: Allow figure generation when style-profile.yaml exists
    Given "artifacts/sf25d-t1201/wave-5-visuals/figure-specs.md" exists
    And "artifacts/sf25d-t1201/wave-5-visuals/style-profile.yaml" exists
    When the formatter agent attempts to Write "artifacts/sf25d-t1201/wave-5-visuals/figure-2-data-flow.svg"
    Then PES returns decision ALLOW

  Scenario: Allow figure generation when user explicitly skipped style analysis
    Given "artifacts/sf25d-t1201/wave-5-visuals/figure-specs.md" exists
    And the directory "artifacts/sf25d-t1201/wave-5-visuals/" does not contain "style-profile.yaml"
    And the proposal state contains "style_analysis_skipped" set to true
    When the formatter agent attempts to Write "artifacts/sf25d-t1201/wave-5-visuals/figure-2-data-flow.svg"
    Then PES returns decision ALLOW

  Scenario: Allow writing style-profile.yaml itself (prerequisite creation)
    Given "artifacts/sf25d-t1201/wave-5-visuals/figure-specs.md" exists
    And the directory "artifacts/sf25d-t1201/wave-5-visuals/" does not contain "style-profile.yaml"
    When the formatter agent attempts to Write "artifacts/sf25d-t1201/wave-5-visuals/style-profile.yaml"
    Then PES returns decision ALLOW

  # --- Path Resolution ---

  Scenario: Gate works with multi-proposal workspace path layout
    Given an active proposal for topic "af263-042" with multi-proposal workspace
    And the artifact directory is "artifacts/af263-042/wave-5-visuals/"
    And "artifacts/af263-042/wave-5-visuals/" does not contain "figure-specs.md"
    When the formatter agent attempts to Write "artifacts/af263-042/wave-5-visuals/figure-1.svg"
    Then PES returns decision BLOCK

  Scenario: Gate works with legacy single-proposal path layout
    Given an active proposal with legacy single-proposal workspace
    And the artifact directory is "artifacts/wave-5-visuals/"
    And "artifacts/wave-5-visuals/" does not contain "figure-specs.md"
    When the formatter agent attempts to Write "artifacts/wave-5-visuals/figure-1.svg"
    Then PES returns decision BLOCK

  # --- Non-interference ---

  Scenario: Gate does not affect writes outside wave-5-visuals
    Given the proposal is at Wave 4 (drafting)
    When the formatter agent attempts to Write "artifacts/sf25d-t1201/wave-4-drafting/section-1.md"
    Then PES returns decision ALLOW
    And the figure pipeline gate is not evaluated

  Scenario: Gate does not affect Read operations
    Given "artifacts/sf25d-t1201/wave-5-visuals/" does not contain "figure-specs.md"
    When the formatter agent uses Read on "artifacts/sf25d-t1201/wave-5-visuals/figure-1.svg"
    Then PES returns decision ALLOW

  # --- Audit Trail ---

  Scenario: Blocked figure write is recorded in audit log
    Given "artifacts/sf25d-t1201/wave-5-visuals/" does not contain "figure-specs.md"
    When the formatter agent attempts to Write "artifacts/sf25d-t1201/wave-5-visuals/figure-1.svg"
    Then PES returns decision BLOCK
    And an audit entry is recorded with event "evaluate" and decision "block"
    And the audit entry includes the rule_id "figure-pipeline-requires-specs"

  Scenario: Allowed figure write after gates pass is recorded in audit log
    Given "artifacts/sf25d-t1201/wave-5-visuals/figure-specs.md" exists
    And "artifacts/sf25d-t1201/wave-5-visuals/style-profile.yaml" exists
    When the formatter agent attempts to Write "artifacts/sf25d-t1201/wave-5-visuals/figure-1.svg"
    Then PES returns decision ALLOW
    And an audit entry is recorded with event "evaluate" and decision "allow"
