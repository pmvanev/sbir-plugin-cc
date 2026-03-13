# ADR-015: JSON Schema as Single Source of Truth for Profile Structure

## Status

Accepted

## Context

The company profile is written by the profile builder agent and read by the topic scout agent. Both must agree on structure. Currently the schema is defined only as a code example in `skills/topic-scout/fit-scoring-methodology.md`. There is no machine-readable contract. Schema drift between writer and reader would cause silent scoring failures.

Quality attributes: **reliability** (schema contract must be exact), **maintainability** (single place to update when schema evolves).

## Decision

Create a JSON Schema file at `templates/company-profile-schema.json` as the single source of truth for profile structure. The profile validation service validates against this schema. The skill file references this schema rather than embedding a duplicate definition. When the schema evolves, only the template needs updating -- validation and documentation derive from it.

## Alternatives Considered

### Alternative 1: Schema defined only in skill markdown

- **Pros**: Simple. No additional file. Human-readable.
- **Cons**: Not machine-readable. Validation service cannot use it directly. Schema duplication between skill and validation code. Drift risk between documentation and enforcement.
- **Rejected because**: Machine-readable schema enables automated validation via `jsonschema`. Skill-only definition requires manual synchronization between documentation and validation code.

### Alternative 2: Schema defined in Python dataclass

- **Pros**: Type-safe. Python tooling support. Could generate JSON Schema from dataclass.
- **Cons**: Ties schema definition to Python. Agents (markdown) cannot directly reference a Python dataclass. Schema generation adds a build step.
- **Rejected because**: The primary consumers are markdown agents that load skills. A JSON Schema file is directly referenceable from both Python (via `jsonschema`) and markdown (via human-readable documentation). No build step required.

## Consequences

- **Positive**: Single source of truth. Machine-readable. Used by both Python validation and agent skill documentation.
- **Positive**: Schema evolution requires updating one file. Validation automatically enforces new constraints.
- **Negative**: Maintaining a JSON Schema file requires JSON Schema syntax knowledge. Mitigated: JSON Schema Draft 2020-12 is well-documented and the schema is simple (no advanced features needed).
