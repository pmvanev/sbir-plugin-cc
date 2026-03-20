# ADR-035: Style Profile as YAML Artifact, Not Python Domain Object

## Status

Accepted

## Context

Domain-aware visual style intelligence requires persisting a style profile (palette, tone, detail level, avoid list) that applies across all Nano Banana prompts in a proposal. The question is whether the style profile should be a Python domain object in PES or a YAML artifact managed by the agent.

## Decision

Style profile is a YAML file at `{artifact_base}/wave-5-visuals/style-profile.yaml`, created and consumed entirely by the formatter agent. No Python domain object. No PES enforcement of style.

## Alternatives Considered

### Alternative 1: Python domain object with port/adapter
- **What**: `StyleProfile` dataclass in `visual_asset.py`, `StyleProfilePort` for persistence, `FileStyleProfileAdapter` for YAML serialization.
- **Expected impact**: Type-safe, testable via pytest, consistent with existing PES patterns.
- **Why rejected**: Style profile is not a domain invariant that PES needs to enforce. PES enforces lifecycle rules (PDC gates, cross-reference validity). Style is aesthetic preference, not a correctness constraint. Adding a Python domain object for non-enforced data creates unnecessary code/test maintenance. The agent reads and writes YAML directly -- no Python intermediary needed.

### Alternative 2: Style embedded in proposal-state.json
- **What**: Add style fields to the proposal state JSON managed by the state service.
- **Expected impact**: Style accessible to all agents and PES hooks.
- **Why rejected**: Style is scoped to Wave 5 figure generation only. No other agent or PES hook needs it. Polluting proposal state with per-wave aesthetic preferences violates the state schema's purpose (lifecycle tracking, not aesthetic preferences). Also, state changes require schema evolution (ADR-012 process).

### Alternative 3: Style in figure-specs.md (per-figure, not per-proposal)
- **What**: Add style fields to each figure specification in figure-specs.md.
- **Expected impact**: Per-figure style control.
- **Why rejected**: The primary requirement is cross-figure consistency. Per-figure styles defeat the purpose. A single shared profile ensures all Nano Banana figures use the same palette/tone.

## Consequences

- **Positive**: Simple -- agent writes YAML text, reads it back when constructing prompts.
- **Positive**: No Python code changes for style profile feature.
- **Positive**: User can manually edit style-profile.yaml between figure generations.
- **Negative**: No type-safety or schema validation in Python. Mitigated by agent validating structure when reading.
- **Negative**: Style profile format changes require skill and agent updates, not schema migration. Acceptable for a single-consumer artifact.
