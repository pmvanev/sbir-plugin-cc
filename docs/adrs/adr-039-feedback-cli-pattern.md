# ADR-039: Feedback Snapshot Assembly via Standalone CLI Script

## Status
Accepted

## Context

The `/sbir:developer-feedback` command requires reading state from 5 existing adapters (proposal-state, rigor-profile, company-profile, finder-results, workspace-resolver) and assembling a context snapshot before persisting the feedback entry.

Two implementation options were considered for where this assembly happens:

**Option A**: Inline in the `sbir-feedback-collector` agent using `Read` tool calls directly from the markdown agent.

**Option B**: Standalone Python CLI script (`scripts/sbir_feedback_cli.py`) that the agent calls via Bash, following the pattern established by `dsip_cli.py`.

## Decision

**Option B**: Standalone CLI script (`scripts/sbir_feedback_cli.py`).

## Rationale

1. **Testability**: Python logic in a CLI is unit-testable with pytest. Agent `Read` tool calls are not unit-testable — they require running Claude Code.

2. **Consistency**: `dsip_cli.py` establishes the pattern of "agent calls Bash → Python CLI wires adapters → returns JSON to stdout." Deviating from this for feedback would create two conventions in the same codebase.

3. **Separation of concerns**: The agent handles interactive UX (type selection, ratings, free text). The CLI handles data assembly and persistence. Neither layer reaches into the other's domain.

4. **Mutation testing**: PES Python code undergoes mutation testing at ≥80% kill rate. This is impossible for inline agent logic. Separating into Python enables the kill rate gate to apply.

5. **Privacy boundary enforcement**: The privacy boundary (exclude capability text, draft content) is enforced at the Python domain layer in `FeedbackSnapshotService.build_snapshot()`. This is verifiable in code review and testable in isolation.

## Alternatives Considered

**Option A (inline agent)**:
- Pro: Fewer files, simpler dispatch
- Con: No unit tests, no mutation testing, privacy boundary only in markdown prose (not enforceable)
- Con: Adds file-reading responsibility to the agent, conflating UX and data assembly

## Consequences

- New files: `scripts/sbir_feedback_cli.py`, `scripts/pes/domain/feedback.py`, `scripts/pes/domain/feedback_service.py`, `scripts/pes/ports/feedback_port.py`, `scripts/pes/adapters/filesystem_feedback_adapter.py`
- The agent remains a thin UX layer (~100 lines), delegating all state work to the CLI
- CLI follows `argparse` convention matching `dsip_cli.py`
