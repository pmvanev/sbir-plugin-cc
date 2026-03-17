# ADR-023: Format Selection as State-Driven Orchestrator Prompt

## Status

Accepted

## Context

The SBIR Proposal Plugin defers output format selection (LaTeX vs DOCX) to Wave 6 formatting. By that point, the writer has produced content across Waves 3-4 without knowing the target format. LaTeX proposals need different figure handling, cross-reference patterns, and section structure than DOCX. Late discovery causes rework.

The feature adds an explicit format selection step during `/proposal new` (after fit scoring, before Go/No-Go) and a `/proposal config format` command for mid-proposal changes. The choice must persist and be readable by all downstream agents.

Constraints: solo developer, existing ports-and-adapters architecture, additive state schema changes per ADR-012, interactive prompts are agent (markdown) responsibility.

## Decision

**Format selection is a state field (`output_format`) set by the orchestrator agent during the `/proposal new` interactive flow.** A `FormatConfigService` domain service handles mid-proposal changes with rework-risk validation.

Specifics:
- `output_format` added to `proposal-state.json` (enum: `"latex"`, `"docx"`, default: `"docx"`)
- The orchestrator agent (markdown) owns the interactive prompt -- not PES Python
- `FormatConfigService` (PES domain) validates format values and determines rework risk
- Existing `StateReader`/`StateWriter` ports used -- no new ports
- Solicitation PDF-submission hints are LLM reasoning (agent behavior), not domain logic
- Schema change is additive per ADR-012: missing field defaults to `"docx"`

## Alternatives Considered

### Alternative 1: PES hook-enforced format gate

- **What**: Add a PES enforcement rule that blocks Wave 1 if `output_format` is missing. PES Python handles format validation and prompting.
- **Expected impact**: Guaranteed format selection before Wave 1 starts
- **Why rejected**: Format selection is a user preference, not a compliance invariant. PES enforces business rules (wave ordering, compliance gates), not user preferences. Adding a hook for this conflates enforcement with configuration. The orchestrator already manages the `/proposal new` flow and is the natural owner of interactive prompts.

### Alternative 2: Format as a configuration file separate from state

- **What**: Store format preference in `.sbir/config.json` rather than `proposal-state.json`. Keep state for lifecycle tracking, config for user preferences.
- **Expected impact**: Clean separation of lifecycle state from user preferences
- **Why rejected**: Introduces a new file that all agents must discover and read. Current agents already read `proposal-state.json` for all proposal context. Adding a second file increases integration surface and inconsistency risk. One field does not justify a new persistence abstraction. If more configuration accumulates in future, this can be revisited.

### Alternative 3: Default to DOCX, never ask

- **What**: Hard-default to DOCX. Users who want LaTeX edit state manually.
- **Expected impact**: Zero added friction in setup flow
- **Why rejected**: Phil alternates between LaTeX and DOCX depending on proposal. Manual state editing is error-prone and undiscoverable. One additional prompt (with Enter-for-default) is minimal friction. The user story explicitly calls for this selection step.

## Consequences

- **Positive**: Single source of truth in `proposal-state.json` -- all downstream agents read one field
- **Positive**: No new ports, no new adapters, no new dependencies -- minimal architecture surface change
- **Positive**: Additive schema change -- existing proposals unaffected
- **Positive**: FormatConfigService is a pure domain object, fully testable through existing ports
- **Negative**: Format prompt adds one interaction step to `/proposal new` flow (mitigated by Enter-for-default)
- **Negative**: Mid-proposal format change does not auto-migrate content -- rework is manual (acceptable: rework is inherently content-specific and rare)
- **Trade-off**: Solicitation format hints depend on LLM reasoning quality. If the LLM misses a PDF requirement, the user still sees the prompt and can choose LaTeX. No silent failure.
