# Acceptance Test Design: Proposal Quality Discovery

## Scope Rationale

This feature is markdown-first: the primary deliverables are a new agent, skill, and commands, all as markdown files. The architecture explicitly states "no new Python code." Acceptance tests focus on the testable Python boundary:

1. **Artifact schema validation** -- JSON schemas for the three quality artifacts
2. **Artifact persistence** -- file read/write/merge, graceful missing-file handling
3. **Confidence calculation** -- pure domain logic (win count to confidence tier)
4. **Downstream consumption** -- artifact loading, agency filtering, quality alert matching, practices-to-avoid detection, graceful degradation

Agent Q&A behavior (guided interview flow, user interaction) is validated by the nWave forge checklist, not by pytest.

## Test Architecture

**Driving port**: File system interface for quality artifact CRUD. No new Python application services exist for this feature.

**Test strategy**: Acceptance tests validate artifact schema compliance and consumption patterns through direct JSON operations. This mirrors how the markdown agents will produce and consume these artifacts (via the Write/Read tools).

## Scenario Summary

| Feature File | Scenarios | Walking Skeletons | Error/Edge |
|---|---|---|---|
| artifact_schema_validation.feature | 21 | 3 | 9 |
| artifact_persistence.feature | 13 | 1 | 7 |
| confidence_calculation.feature | 8 | 0 | 2 |
| downstream_consumption.feature | 11 | 0 | 5 |
| **Total** | **53** | **4** | **23** |

**Error/edge ratio**: 23/53 = 43% (exceeds 40% target)

## Walking Skeletons (4)

1. Complete quality preferences artifact passes validation
2. Complete winning patterns artifact passes validation
3. Complete writing quality profile artifact passes validation
4. Full quality discovery persists all three artifacts

Each answers: "Can the quality discovery agent produce a valid artifact that downstream agents can consume?"

## Property-Tagged Scenarios (3)

- Quality preferences roundtrip preserves all data exactly
- Winning patterns roundtrip preserves all data exactly
- Writing quality profile roundtrip preserves all data exactly

These signal the DELIVER wave crafter to implement as property-based tests with generators.

## Implementation Sequence (One-at-a-Time)

1. artifact_schema_validation.feature -- walking skeleton: quality preferences (FIRST)
2. artifact_schema_validation.feature -- remaining scenarios
3. confidence_calculation.feature -- all scenarios
4. artifact_persistence.feature -- walking skeleton + persistence scenarios
5. downstream_consumption.feature -- all scenarios

## Mandate Compliance Evidence

**CM-A (Hexagonal boundary)**: Tests operate through file I/O (the artifact read/write interface). No internal component imports. The "driving port" for this markdown-first feature is the file system where artifacts are persisted.

**CM-B (Business language)**: Feature files use domain terms exclusively: quality preferences, winning patterns, confidence level, practices to replicate, evaluator feedback, agency filtering. Zero HTTP/REST/JSON/database/API/controller terms in Gherkin.

**CM-C (Walking skeleton + focused counts)**: 4 walking skeletons + 49 focused scenarios across 4 feature files.

## Schema Files Created

- `templates/quality-preferences-schema.json`
- `templates/winning-patterns-schema.json`
- `templates/writing-quality-profile-schema.json`

These schemas are derived from the architecture document artifact definitions and enforce all field constraints (enums, required fields, conditional requirements).
