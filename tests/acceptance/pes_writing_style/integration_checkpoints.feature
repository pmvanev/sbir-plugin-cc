Feature: Writing Style Gate Integration Checkpoints
  As a plugin maintainer,
  I want the writing style gate to work across workspace layouts and record decisions
  So that enforcement is reliable regardless of project structure

  # --- Path Resolution ---

  @skip
  Scenario: Gate works with multi-proposal workspace path layout
    Given an active proposal for topic "af263-042" at Wave 4 with multi-proposal workspace
    And the enforcement rules are loaded from the standard configuration
    And no quality preferences file exists at the global configuration location
    And the proposal does not have a writing style selection skip marker
    When the writer agent attempts to Write "artifacts/af263-042/wave-4-drafting/sections/technical-approach.md"
    Then PES returns decision BLOCK

  @skip
  Scenario: Gate works with legacy single-proposal path layout
    Given an active proposal at Wave 4 with legacy single-proposal workspace
    And the enforcement rules are loaded from the standard configuration
    And no quality preferences file exists at the global configuration location
    And the proposal does not have a writing style selection skip marker
    When the writer agent attempts to Write "artifacts/wave-4-drafting/sections/technical-approach.md"
    Then PES returns decision BLOCK

  # --- Non-interference ---

  @skip
  Scenario: Gate does not affect writes outside wave-4-drafting
    Given an active proposal for topic "SF25D-T1201" at Wave 3
    And the enforcement rules are loaded from the standard configuration
    And no quality preferences file exists at the global configuration location
    When the writer agent attempts to Write "artifacts/sf25d-t1201/wave-3-outline/proposal-outline.md"
    Then PES returns decision ALLOW
    And the writing style gate is not evaluated

  @skip
  Scenario: Gate does not affect Read operations
    Given an active proposal for topic "SF25D-T1201" at Wave 4
    And the enforcement rules are loaded from the standard configuration
    And no quality preferences file exists at the global configuration location
    When the writer agent uses Read on "artifacts/sf25d-t1201/wave-4-drafting/sections/technical-approach.md"
    Then PES returns decision ALLOW

  @skip
  Scenario: Gate does not affect writes to wave-5-visuals
    Given an active proposal for topic "SF25D-T1201" at Wave 5
    And the enforcement rules are loaded from the standard configuration
    And no quality preferences file exists at the global configuration location
    When the formatter agent attempts to Write "artifacts/sf25d-t1201/wave-5-visuals/figure-1.svg"
    Then the writing style gate is not evaluated

  # --- Audit Trail ---

  @skip
  Scenario: Blocked draft write is recorded in audit log
    Given an active proposal for topic "SF25D-T1201" at Wave 4
    And the enforcement rules are loaded from the standard configuration
    And no quality preferences file exists at the global configuration location
    And the proposal does not have a writing style selection skip marker
    When the writer agent attempts to Write "artifacts/sf25d-t1201/wave-4-drafting/sections/technical-approach.md"
    Then PES returns decision BLOCK
    And an audit entry is recorded with event "evaluate" and decision "block"
    And the audit entry includes the rule_id "drafting-requires-style-selection"

  @skip
  Scenario: Allowed draft write after style selection is recorded in audit log
    Given an active proposal for topic "SF25D-T1201" at Wave 4
    And the enforcement rules are loaded from the standard configuration
    And the global configuration location contains quality preferences
    When the writer agent attempts to Write "artifacts/sf25d-t1201/wave-4-drafting/sections/technical-approach.md"
    Then PES returns decision ALLOW
    And an audit entry is recorded with event "evaluate" and decision "allow"
