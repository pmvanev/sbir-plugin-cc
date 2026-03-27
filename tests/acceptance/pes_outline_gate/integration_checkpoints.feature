Feature: Outline Gate Integration Checkpoints
  As a plugin maintainer,
  I want the outline gate to work across workspace layouts and record decisions
  So that enforcement is reliable regardless of project structure

  # --- Path Resolution ---

  Scenario: Gate works with multi-proposal workspace path layout
    Given an active proposal for topic "af263-042" at Wave 4 with multi-proposal workspace
    And the enforcement rules are loaded from the standard configuration
    And the outline directory does not contain a proposal outline
    When the writer agent attempts to Write "artifacts/af263-042/wave-4-drafting/section-1-approach.md"
    Then PES returns decision BLOCK

  Scenario: Gate works with legacy single-proposal path layout
    Given an active proposal at Wave 4 with legacy single-proposal workspace
    And the enforcement rules are loaded from the standard configuration
    And the outline directory does not contain a proposal outline
    When the writer agent attempts to Write "artifacts/wave-4-drafting/section-1-approach.md"
    Then PES returns decision BLOCK

  Scenario: Cross-directory resolution derives wave-3-outline from wave-4-drafting
    Given an active proposal for topic "navy-fy26-001" at Wave 4
    And the enforcement rules are loaded from the standard configuration
    And the outline directory contains a proposal outline
    When the writer agent attempts to Write "artifacts/navy-fy26-001/wave-4-drafting/section-3-management.md"
    Then PES returns decision ALLOW

  # --- Non-interference ---

  Scenario: Gate does not affect writes outside wave-4-drafting
    Given an active proposal for topic "SF25D-T1201" at Wave 3
    And the enforcement rules are loaded from the standard configuration
    When the writer agent attempts to Write "artifacts/sf25d-t1201/wave-3-outline/notes.md"
    Then PES returns decision ALLOW
    And the outline gate is not evaluated

  Scenario: Gate does not affect Read operations on wave-4-drafting
    Given an active proposal for topic "SF25D-T1201" at Wave 4
    And the enforcement rules are loaded from the standard configuration
    And the outline directory does not contain a proposal outline
    When the writer agent uses Read on "artifacts/sf25d-t1201/wave-4-drafting/section-1-technical-approach.md"
    Then PES returns decision ALLOW

  Scenario: Gate does not affect wave-5 writes when outline is missing
    Given an active proposal for topic "SF25D-T1201" at Wave 5
    And the enforcement rules are loaded from the standard configuration
    And the outline directory does not contain a proposal outline
    When the writer agent attempts to Write "artifacts/sf25d-t1201/wave-5-visuals/figure-1.svg"
    Then PES returns decision ALLOW
    And the outline gate is not evaluated

  # --- Audit Trail ---

  Scenario: Blocked draft write is recorded in audit log
    Given an active proposal for topic "SF25D-T1201" at Wave 4
    And the enforcement rules are loaded from the standard configuration
    And the outline directory does not contain a proposal outline
    When the writer agent attempts to Write "artifacts/sf25d-t1201/wave-4-drafting/section-1-technical-approach.md"
    Then PES returns decision BLOCK
    And an audit entry is recorded with event "evaluate" and decision "block"
    And the audit entry includes the rule_id "drafting-requires-outline"

  Scenario: Allowed draft write after outline exists is recorded in audit log
    Given an active proposal for topic "SF25D-T1201" at Wave 4
    And the enforcement rules are loaded from the standard configuration
    And the outline directory contains a proposal outline
    When the writer agent attempts to Write "artifacts/sf25d-t1201/wave-4-drafting/section-1-technical-approach.md"
    Then PES returns decision ALLOW
    And an audit entry is recorded with event "evaluate" and decision "allow"
