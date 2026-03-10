# ADR-012: State Schema Evolution for C3

## Status

Accepted

## Context

C3 adds Waves 5-9 to the proposal lifecycle. The proposal-state.json schema (v1.0.0 from C1) needs new fields for visual assets, formatting, assembly, final review, submission, and learning. Existing proposals created under v1.0.0 must continue to work.

## Decision

Bump schema_version to `2.0.0`. New C3 fields are additive top-level sections with default values. No migration script -- domain services handle missing fields gracefully by defaulting to null/empty. Schema version check at load time: v1.0.0 state is valid in v2.0.0 context (all new fields optional).

New sections: `visuals`, `formatting`, `assembly`, `final_review`, `submission`, `learning`. Existing waves dict extended with keys `"5"` through `"9"`.

## Alternatives Considered

### Alternative 1: Separate state file per wave
- **What**: Each wave writes its own state file (wave-5-state.json, wave-6-state.json, etc.)
- **Expected impact**: Avoids schema evolution; each wave owns its data
- **Why rejected**: Breaks the single-source-of-truth principle. PES enforcement needs cross-wave state (e.g., submission immutability affects all waves). Atomic consistency across waves becomes harder. Status command would need to read 10 files.

### Alternative 2: Schema migration script
- **What**: Python script that upgrades v1.0.0 files to v2.0.0 by adding missing fields
- **Expected impact**: Guarantees all fields present after migration
- **Why rejected**: Over-engineered for additive-only changes. No fields are renamed, moved, or removed. Default-on-missing is simpler and equally correct. Migration script adds a step to plugin update that could fail.

## Consequences

- **Positive**: Zero-friction upgrade. Existing proposals work immediately after plugin update.
- **Positive**: Single state file maintains atomic consistency.
- **Negative**: Domain services must handle None/missing for all C3 fields. Small additional null-checking code.
- **Negative**: Schema file grows larger. Acceptable -- JSON is still human-readable at this size.
