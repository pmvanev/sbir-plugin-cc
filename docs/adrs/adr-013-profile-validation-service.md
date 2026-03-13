# ADR-013: Profile Validation as Python Domain Service

## Status

Accepted

## Context

The Company Profile Builder must validate user-entered profile data before saving to `~/.sbir/company-profile.json`. Validation includes structural checks (required fields, correct types), format checks (CAGE code = 5 alphanumeric, clearance in enum), and business rules (employee_count > 0). The profile feeds into fit scoring that drives Go/No-Go decisions -- invalid data causes silent scoring degradation.

Quality attributes driving this decision: **reliability** (validation must be deterministic), **maintainability** (validation rules must be auditable and testable).

## Decision

Implement profile validation as a pure Python domain service in `scripts/pes/domain/profile_validation.py`. The service receives a profile dict and returns a structured result with field-level errors. It uses `jsonschema` for structural validation and custom Python functions for business rules.

## Alternatives Considered

### Alternative 1: Agent-only validation (LLM validates during conversation)

The agent could validate fields as the user enters them, relying on LLM reasoning.

- **Pros**: Zero Python code. Simpler architecture. Immediate conversational feedback.
- **Cons**: Probabilistic -- LLM may accept "7X2K" as valid CAGE in edge cases. Not testable with unit tests. No deterministic guarantee. Validation behavior may vary across model versions.
- **Rejected because**: Profile data directly impacts scoring accuracy. A wrong CAGE code or invalid clearance enum silently degrades every future fit score. The cost of a probabilistic validation miss (wrong Go/No-Go on a $150K proposal) outweighs the simplicity benefit.

### Alternative 2: Pydantic model with built-in validation

Define a `CompanyProfile` Pydantic model with field validators.

- **Pros**: Rich validation DSL. Type-safe. Self-documenting. Popular in Python ecosystem.
- **Cons**: Adds `pydantic` as a new dependency (not currently in project). Heavier than needed for a single JSON schema. Schema definition split between Pydantic model and JSON Schema template.
- **Rejected because**: `jsonschema` is already a project dependency. Adding `pydantic` for one feature increases dependency surface. `jsonschema` + custom validation functions are sufficient.

### Alternative 3: JSON Schema validation only (no custom business rules)

Use `jsonschema` alone with a comprehensive JSON Schema that includes pattern/format constraints.

- **Pros**: Single validation mechanism. Schema is the complete truth.
- **Cons**: JSON Schema `pattern` for CAGE code is possible but error messages are cryptic. Conditional validation (CAGE required only when sam_gov.active=true) is complex in JSON Schema. Business rule evolution harder to express.
- **Rejected because**: Conditional business rules (CAGE required when active) and human-readable error messages require custom logic beyond JSON Schema capabilities.

## Consequences

- **Positive**: Deterministic validation. Testable with unit tests. Human-readable error messages. Consistent with existing PES domain pattern.
- **Positive**: Pure domain -- no infrastructure imports. Easy to test in isolation.
- **Negative**: Requires Python subprocess invocation from agent. Adds ~1 Python file to maintain.
- **Trade-off**: Slightly more complex than agent-only, but reliability is non-negotiable for scoring-critical data.
