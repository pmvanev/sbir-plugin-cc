Feature: Writing Style Gate Enforcement
  As a proposal author using the SBIR plugin
  I want PES to enforce writing style selection before drafting
  So that the writer agent cannot bypass the style conversation

  Background:
    Given an active proposal for topic "SF25D-T1201" owned by Dr. Rafael Moreno
    And the proposal is at Wave 4 (drafting)
    And the artifact directory is "artifacts/sf25d-t1201/wave-4-drafting/"

  # --- Writing Style Gate (PES Layer) ---

  Scenario: Block draft write when quality-preferences.json missing and no skip marker
    Given "~/.sbir/quality-preferences.json" does not exist
    And the proposal state does not contain "writing_style_selection_skipped"
    When the writer agent attempts to Write "artifacts/sf25d-t1201/wave-4-drafting/sections/technical-approach.md"
    Then PES returns decision BLOCK
    And the block message includes "writing style selection"
    And the block message includes "quality-preferences.json"

  Scenario: Allow draft write when quality-preferences.json exists
    Given "~/.sbir/quality-preferences.json" exists with tone "direct" and detail_level "high"
    When the writer agent attempts to Write "artifacts/sf25d-t1201/wave-4-drafting/sections/technical-approach.md"
    Then PES returns decision ALLOW

  Scenario: Allow draft write when user explicitly skipped style selection
    Given "~/.sbir/quality-preferences.json" does not exist
    And the proposal state contains "writing_style_selection_skipped" set to true
    When the writer agent attempts to Write "artifacts/sf25d-t1201/wave-4-drafting/sections/sow.md"
    Then PES returns decision ALLOW

  Scenario: Block Edit to existing draft when no style selection
    Given "~/.sbir/quality-preferences.json" does not exist
    And the proposal state does not contain "writing_style_selection_skipped"
    And "artifacts/sf25d-t1201/wave-4-drafting/sections/technical-approach.md" exists from a previous session
    When the writer agent attempts to Edit "artifacts/sf25d-t1201/wave-4-drafting/sections/technical-approach.md"
    Then PES returns decision BLOCK

  Scenario: Block message includes both resolution paths
    Given "~/.sbir/quality-preferences.json" does not exist
    And the proposal state does not contain "writing_style_selection_skipped"
    When the writer agent attempts to Write a section draft
    Then the block message mentions "/proposal quality discover" as one resolution path
    And the block message mentions "skip style selection" as an alternative resolution path

  # --- Path Resolution ---

  Scenario: Gate works with multi-proposal workspace path layout
    Given an active proposal for topic "af263-042" with multi-proposal workspace
    And the artifact directory is "artifacts/af263-042/wave-4-drafting/"
    And "~/.sbir/quality-preferences.json" does not exist
    And the proposal state does not contain "writing_style_selection_skipped"
    When the writer agent attempts to Write "artifacts/af263-042/wave-4-drafting/sections/technical-approach.md"
    Then PES returns decision BLOCK

  Scenario: Gate works with legacy single-proposal path layout
    Given an active proposal with legacy single-proposal workspace
    And the artifact directory is "artifacts/wave-4-drafting/"
    And "~/.sbir/quality-preferences.json" does not exist
    And the proposal state does not contain "writing_style_selection_skipped"
    When the writer agent attempts to Write "artifacts/wave-4-drafting/sections/technical-approach.md"
    Then PES returns decision BLOCK

  # --- Non-interference ---

  Scenario: Gate does not affect writes outside wave-4-drafting
    Given "~/.sbir/quality-preferences.json" does not exist
    When the writer agent attempts to Write "artifacts/sf25d-t1201/wave-3-outline/proposal-outline.md"
    Then PES returns decision ALLOW
    And the writing style gate is not evaluated

  Scenario: Gate does not affect Read operations
    Given "~/.sbir/quality-preferences.json" does not exist
    When the writer agent uses Read on "artifacts/sf25d-t1201/wave-4-drafting/sections/technical-approach.md"
    Then PES returns decision ALLOW

  Scenario: Gate does not affect writes to wave-5-visuals
    Given "~/.sbir/quality-preferences.json" does not exist
    When the formatter agent attempts to Write "artifacts/sf25d-t1201/wave-5-visuals/figure-1.svg"
    Then the writing style gate is not evaluated

  # --- Writer Agent Style Checkpoint ---

  Scenario: Style checkpoint presented on first section draft with quality profile
    Given Dr. Rafael Moreno's proposal "SF25D-T1201" is at Wave 4
    And "~/.sbir/quality-preferences.json" exists with tone "direct" and evidence_style "inline"
    And "~/.sbir/winning-patterns.json" exists with 3 Air Force winning patterns
    And the proposal state does not contain "writing_style"
    When the writer agent begins Phase 3 DRAFT for the first section
    Then the writer presents available writing styles
    And the recommendation references the quality profile tone "direct"
    And the recommendation mentions Air Force winning patterns

  Scenario: Style checkpoint presented to first-time user without quality profile
    Given Dr. Amara Okafor's proposal "navy-fy26-003" is at Wave 4
    And "~/.sbir/quality-preferences.json" does not exist
    And the proposal state does not contain "writing_style"
    When the writer agent begins Phase 3 DRAFT for the first section
    Then the writer presents available writing styles with default recommendations
    And the writer mentions "/proposal quality discover" as an option
    And "Standard" is recommended as the default style

  Scenario: Style checkpoint skipped when writing_style already in state
    Given Dr. Rafael Moreno's proposal "SF25D-T1201" is at Wave 4
    And the proposal state contains "writing_style" set to "elements"
    When the writer agent begins Phase 3 DRAFT for the next section
    Then the writer does not present the style checkpoint
    And drafting proceeds with the "elements" style skill loaded

  Scenario: User chooses skip at style checkpoint
    Given Dr. Amara Okafor's proposal "navy-fy26-003" is at Wave 4
    And the proposal state does not contain "writing_style"
    When the writer presents the style checkpoint
    And Dr. Okafor chooses "skip style selection"
    Then the proposal state is updated with "writing_style_selection_skipped" set to true
    And drafting proceeds with standard prose defaults

  # --- Audit Trail ---

  Scenario: Blocked draft write is recorded in audit log
    Given "~/.sbir/quality-preferences.json" does not exist
    And the proposal state does not contain "writing_style_selection_skipped"
    When the writer agent attempts to Write "artifacts/sf25d-t1201/wave-4-drafting/sections/technical-approach.md"
    Then PES returns decision BLOCK
    And an audit entry is recorded with event "evaluate" and decision "block"
    And the audit entry includes the rule_id "drafting-requires-style-selection"

  Scenario: Allowed draft write after style selection is recorded in audit log
    Given "~/.sbir/quality-preferences.json" exists
    When the writer agent attempts to Write "artifacts/sf25d-t1201/wave-4-drafting/sections/technical-approach.md"
    Then PES returns decision ALLOW
    And an audit entry is recorded with event "evaluate" and decision "allow"
