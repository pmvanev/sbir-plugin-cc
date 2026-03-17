# ADR-026: Company-Level Quality Artifacts at ~/.sbir/

## Status

Accepted

## Context

Quality discovery produces three JSON artifacts: quality-preferences.json (writing style), winning-patterns.json (past proposal quality ratings), writing-quality-profile.json (evaluator meta-writing feedback). These artifacts need a persistence location.

Two options: company-level at `~/.sbir/` (alongside company-profile.json) or project-level at `.sbir/` (alongside proposal-state.json).

Quality attributes: reliability (artifacts survive across proposals), usability (available without per-project setup), maintainability (consistent with existing patterns).

## Decision

Persist all three quality artifacts at `~/.sbir/` (company-level), consistent with company-profile.json.

## Alternatives Considered

### Alternative 1: Project-level at .sbir/ (per-proposal)

- **Evaluation**: Each proposal would have its own quality artifacts. Aligns with proposal-state.json location. Could support per-proposal style overrides.
- **Rejection**: Quality preferences are company-wide ("how Pacific Systems Engineering writes proposals"), not per-proposal. Winning patterns compound across all proposals. Per-proposal storage would require copying artifacts on each `/proposal new` and would lose compounding benefit. The user stories explicitly describe company-level institutional knowledge (JS-4).

### Alternative 2: Hybrid -- preferences at ~/.sbir/, patterns at .sbir/

- **Evaluation**: Style preferences are company-wide; winning patterns could be per-proposal for proposal-specific overrides.
- **Rejection**: Adds complexity for no clear benefit. Winning patterns are inherently cross-proposal (patterns from AF243-001 inform AF244-015). The pattern frequency and confidence model requires a single aggregated view across all outcomes.

## Consequences

### Positive

- Quality artifacts compound with every proposal cycle (JS-4 requirement)
- Available immediately when starting new proposals without per-project copy
- Consistent with company-profile.json location pattern
- Single source of truth for company writing intelligence
- Incremental update command (`quality update`) has one location to read/write

### Negative

- Cannot have per-proposal style overrides without additional mechanism
- Company-level artifacts are shared -- concurrent proposals using different styles would need manual coordination
- Quality artifacts are not backed up with project-level git commits (same as company-profile.json)

### Mitigation

- Per-proposal style overrides: the `writing_style` field in `.sbir/proposal-state.json` already supports per-proposal override. Quality preferences supplement but do not replace this mechanism.
- Concurrent updates: last-writer-wins with .bak backup (same pattern as company-profile.json, documented in US-QD-002 technical notes).
