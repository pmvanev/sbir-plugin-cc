# ADR-004: JSON Files for State Persistence

## Status

Accepted

## Context

Proposal state must persist across Claude Code sessions (days or weeks apart). State includes topic metadata, wave progress, TPOC status, compliance matrix references, and fit scores. The persistence mechanism must survive session crashes without data loss.

## Decision

Local JSON files on disk:

- `proposal-state.json` -- single source of truth for proposal metadata and progress
- `pes-config.json` -- PES enforcement configuration
- Audit log files in `.sbir/audit/`

Write pattern: atomic writes (write to `.tmp`, backup existing to `.bak`, rename `.tmp` to target).

Schema versioning via `schema_version` field for future migration support.

## Alternatives Considered

### SQLite database
- What: Single-file relational database for structured state queries.
- Expected Impact: Better querying, ACID transactions, concurrent access support.
- Why Rejected: Over-engineered for single-user, single-proposal state. JSON is human-readable and editable. SQLite adds a dependency and tooling requirement. Git diffs on JSON are readable; SQLite binary diffs are not.

### YAML files
- What: YAML instead of JSON for state files.
- Expected Impact: Slightly more human-readable (comments, no quotes on keys).
- Why Rejected: JSON is the standard for programmatic state in Claude Code plugins (nWave uses JSON). Python's `json` module is in the standard library; YAML requires `pyyaml` dependency. JSON schema validation is more mature.

## Consequences

- **Positive:** Human-readable. Users can inspect and manually fix state if needed.
- **Positive:** Zero dependencies -- Python's `json` module is built-in.
- **Positive:** Git-friendly -- diffs show exactly what changed.
- **Positive:** Atomic write pattern prevents corruption on crash.
- **Negative:** No query capability beyond reading the whole file. Acceptable for single-proposal state.
- **Negative:** Schema evolution requires manual migration code. Mitigated by `schema_version` field.
- **Negative:** No concurrent access protection. Acceptable for single-user tool.
