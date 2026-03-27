Feature: PES Outline Gate Enforcement
  As a proposal author using the SBIR plugin
  I want PES to enforce that an approved outline exists before drafting begins
  So that the writer agent cannot fabricate section structure without the approved plan

  Background:
    Given an active proposal for topic "SF25D-T1201" owned by Dr. Rafael Moreno
    And the proposal is at Wave 4 (drafting)
    And the drafting artifact directory is "artifacts/sf25d-t1201/wave-4-drafting/"
    And the outline artifact directory is "artifacts/sf25d-t1201/wave-3-outline/"

  # --- Outline Gate ---

  Scenario: Block draft section write when proposal-outline.md does not exist
    Given the directory "artifacts/sf25d-t1201/wave-3-outline/" does not contain "proposal-outline.md"
    When the writer agent attempts to Write "artifacts/sf25d-t1201/wave-4-drafting/section-1-technical-approach.md"
    Then PES returns decision BLOCK
    And the block message includes "proposal outline"
    And the block message includes "proposal-outline.md"
    And the block message includes "wave-3-outline"

  Scenario: Allow draft section write when proposal-outline.md exists
    Given "artifacts/sf25d-t1201/wave-3-outline/proposal-outline.md" exists
    When the writer agent attempts to Write "artifacts/sf25d-t1201/wave-4-drafting/section-1-technical-approach.md"
    Then PES returns decision ALLOW

  Scenario: Block Edit to existing draft when proposal-outline.md does not exist
    Given the directory "artifacts/sf25d-t1201/wave-3-outline/" does not contain "proposal-outline.md"
    And "artifacts/sf25d-t1201/wave-4-drafting/section-1-technical-approach.md" exists from a previous session
    When the writer agent attempts to Edit "artifacts/sf25d-t1201/wave-4-drafting/section-1-technical-approach.md"
    Then PES returns decision BLOCK
    And the block message includes "proposal outline"

  Scenario: Allow writing any file type to wave-4-drafting when outline exists
    Given "artifacts/sf25d-t1201/wave-3-outline/proposal-outline.md" exists
    When the writer agent attempts to Write "artifacts/sf25d-t1201/wave-4-drafting/section-2-schedule.md"
    Then PES returns decision ALLOW

  # --- Path Resolution ---

  Scenario: Gate works with multi-proposal workspace path layout
    Given an active proposal for topic "af263-042" with multi-proposal workspace
    And the drafting artifact directory is "artifacts/af263-042/wave-4-drafting/"
    And "artifacts/af263-042/wave-3-outline/" does not contain "proposal-outline.md"
    When the writer agent attempts to Write "artifacts/af263-042/wave-4-drafting/section-1-approach.md"
    Then PES returns decision BLOCK

  Scenario: Gate works with legacy single-proposal path layout
    Given an active proposal with legacy single-proposal workspace
    And the drafting artifact directory is "artifacts/wave-4-drafting/"
    And "artifacts/wave-3-outline/" does not contain "proposal-outline.md"
    When the writer agent attempts to Write "artifacts/wave-4-drafting/section-1-approach.md"
    Then PES returns decision BLOCK

  Scenario: Cross-directory resolution derives wave-3-outline from wave-4-drafting
    Given an active proposal for topic "navy-fy26-001"
    And "artifacts/navy-fy26-001/wave-3-outline/proposal-outline.md" exists
    When the writer agent attempts to Write "artifacts/navy-fy26-001/wave-4-drafting/section-3-management.md"
    Then PES returns decision ALLOW

  # --- Non-interference ---

  Scenario: Gate does not affect writes outside wave-4-drafting
    Given "artifacts/sf25d-t1201/wave-3-outline/" does not contain "proposal-outline.md"
    When the writer agent attempts to Write "artifacts/sf25d-t1201/wave-3-outline/notes.md"
    Then PES returns decision ALLOW
    And the outline gate is not evaluated

  Scenario: Gate does not affect Read operations on wave-4-drafting
    Given "artifacts/sf25d-t1201/wave-3-outline/" does not contain "proposal-outline.md"
    When the writer agent uses Read on "artifacts/sf25d-t1201/wave-4-drafting/section-1-technical-approach.md"
    Then PES returns decision ALLOW

  # --- Audit Trail ---

  Scenario: Blocked draft write is recorded in audit log
    Given "artifacts/sf25d-t1201/wave-3-outline/" does not contain "proposal-outline.md"
    When the writer agent attempts to Write "artifacts/sf25d-t1201/wave-4-drafting/section-1-technical-approach.md"
    Then PES returns decision BLOCK
    And an audit entry is recorded with event "evaluate" and decision "block"
    And the audit entry includes the rule_id "drafting-requires-outline"

  Scenario: Allowed draft write after gate passes is recorded in audit log
    Given "artifacts/sf25d-t1201/wave-3-outline/proposal-outline.md" exists
    When the writer agent attempts to Write "artifacts/sf25d-t1201/wave-4-drafting/section-1-technical-approach.md"
    Then PES returns decision ALLOW
    And an audit entry is recorded with event "evaluate" and decision "allow"
