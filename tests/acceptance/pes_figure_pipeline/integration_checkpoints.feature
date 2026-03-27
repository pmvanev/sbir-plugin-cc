Feature: Figure Pipeline Integration Checkpoints
  As a plugin maintainer,
  I want the figure pipeline gates to work across workspace layouts and record decisions
  So that enforcement is reliable regardless of project structure

  # --- Path Resolution ---

  Scenario: Gate works with multi-proposal workspace path layout
    Given an active proposal for topic "af263-042" at Wave 5 with multi-proposal workspace
    And the enforcement rules are loaded from the standard configuration
    And the visual assets directory does not contain a figure specification plan
    When the formatter agent attempts to Write "artifacts/af263-042/wave-5-visuals/figure-1.svg"
    Then PES returns decision BLOCK

  Scenario: Gate works with legacy single-proposal path layout
    Given an active proposal at Wave 5 with legacy single-proposal workspace
    And the enforcement rules are loaded from the standard configuration
    And the visual assets directory does not contain a figure specification plan
    When the formatter agent attempts to Write "artifacts/wave-5-visuals/figure-1.svg"
    Then PES returns decision BLOCK

  # --- Non-interference ---

  Scenario: Gate does not affect writes outside visual assets directory
    Given an active proposal for topic "SF25D-T1201" at Wave 4
    And the enforcement rules are loaded from the standard configuration
    When the formatter agent attempts to Write "artifacts/sf25d-t1201/wave-4-drafting/section-1.md"
    Then PES returns decision ALLOW
    And the figure pipeline gate is not evaluated

  Scenario: Gate does not affect Read operations
    Given an active proposal for topic "SF25D-T1201" at Wave 5
    And the enforcement rules are loaded from the standard configuration
    And the visual assets directory does not contain a figure specification plan
    When the formatter agent uses Read on "artifacts/sf25d-t1201/wave-5-visuals/figure-1.svg"
    Then PES returns decision ALLOW

  # --- Audit Trail ---

  Scenario: Blocked figure write is recorded in audit log
    Given an active proposal for topic "SF25D-T1201" at Wave 5
    And the enforcement rules are loaded from the standard configuration
    And the visual assets directory does not contain a figure specification plan
    When the formatter agent attempts to Write "artifacts/sf25d-t1201/wave-5-visuals/figure-1.svg"
    Then PES returns decision BLOCK
    And an audit entry is recorded with event "evaluate" and decision "block"
    And the audit entry includes the rule_id "figure-pipeline-requires-specs"

  Scenario: Allowed figure write after gates pass is recorded in audit log
    Given an active proposal for topic "SF25D-T1201" at Wave 5
    And the enforcement rules are loaded from the standard configuration
    And the visual assets directory contains a figure specification plan
    And the visual assets directory contains a style profile
    When the formatter agent attempts to Write "artifacts/sf25d-t1201/wave-5-visuals/figure-1.svg"
    Then PES returns decision ALLOW
    And an audit entry is recorded with event "evaluate" and decision "allow"
