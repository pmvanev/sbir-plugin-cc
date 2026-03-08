# ADR-008: Per-Feature Mutation Testing with mutmut

## Status

Accepted

## Context

PES is an enforcement system. Its correctness matters -- if a rule evaluation silently passes when it should block, the user gets no warning. Code coverage alone cannot detect tests that execute code without asserting meaningful behavior.

We need a mutation testing strategy proportional to the project.

## Decision

**Strategy**: Per-feature mutation testing using mutmut.

**When**: After each feature delivery, scoped to the Python files modified in that feature.

**Kill rate gate**: >= 80%.

**Tool**: mutmut (Python-native, configured in `pyproject.toml`).

**Execution**: Local developer responsibility. Not in CI pipeline (mutation testing is too slow for the commit stage; a full mutmut run could take 5-15 minutes).

## Rationale

Project sizing assessment:
- Under 50k LOC (currently ~12 Python files)
- Per-feature delivery cadence
- Solo developer velocity

Per nWave mutation testing guidelines: projects under 50k LOC with per-feature delivery should run mutation testing per-feature, targeting 5-15 minute feedback loops.

## Alternatives Considered

### No mutation testing
Rejected. PES enforces safety invariants. Tests must verify behavior, not just exercise code paths.

### Nightly mutation testing
Rejected. Feedback delay (~12 hours) is too long for a project this size. Per-feature is fast enough to run immediately.

### CI-integrated mutation testing
Rejected for now. Adds 5-15 minutes to every PR. Disproportionate for a project with < 50 PRs expected in Phase C1. Can be added later if the team grows.

## Consequences

- Developer runs `mutmut run --paths-to-mutate scripts/pes/` after completing PES features
- Surviving mutants indicate tests that cover code without asserting behavior
- Kill rate below 80% means tests need strengthening before the feature is considered complete
- Mutation testing results are not persisted in CI -- they are part of the developer's workflow
