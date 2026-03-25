# Evolution: sbir-developer-feedback

**Date**: 2026-03-25
**Feature**: sbir-developer-feedback
**Status**: Complete

---

## Problem Solved

Plugin users had no in-context way to report friction or quality issues. Feedback required leaving the tool entirely — writing an email or opening a GitHub issue with no session context attached. The developer received vague reports ("it didn't work") with no information about what wave the user was in, which rigor profile was active, or what artifacts had been generated.

This feature delivers a `/sbir:developer-feedback` slash command that captures a structured context snapshot automatically at the moment of feedback submission.

---

## User Stories Addressed

All 7 user stories from `docs/feature/sbir-developer-feedback/discuss/user-stories.md`:

| Story | Description | Priority |
|-------|-------------|----------|
| 1 | Submit feedback with automatic context snapshot | Must-have |
| 2 | Rate specific AI output quality dimensions (1-5 scale) | Must-have |
| 3 | Feedback works without an active proposal (graceful null handling) | Must-have |
| 4 | Developer reads structured feedback entries from `.sbir/feedback/` | Must-have |
| 5 | Feedback accumulates across sessions with timestamped filenames | Must-have |
| 6 | Privacy: no company IP captured in snapshot | Must-have |
| 7 | Empty submission guard (confirmation prompt before submitting with no details) | Should-have |

---

## Architecture

### Pattern

Ports-and-Adapters (OOP) — consistent with the rest of `scripts/pes/`. The feature introduces 5 new Python components and 2 markdown files. All 5 existing PES adapters are consumed read-only; no existing adapter is modified.

### Two Delivery Surfaces

The project uses two distinct delivery surfaces, and this feature exercises both:

- **Python TDD** (Steps 01-01 through 01-04): Domain model, domain service, port, adapter, CLI — all delivered via DES RED/GREEN/COMMIT cycle with pytest unit and acceptance tests.
- **Markdown Forge** (Step 02-01): Slash command and agent delivered via nWave forge checklist. No pytest — markdown validation is structural and behavioral.

### Data Flow

```
User invokes /sbir:developer-feedback
    |
    v
sbir-feedback-collector agent
  1. AskUserQuestion: type (Bug/Suggestion/Quality)
  2. If Quality: AskUserQuestion: ratings (1-5 or skip per dimension)
  3. AskUserQuestion: free text (optional)
  4. Bash: python scripts/sbir_feedback_cli.py save ...
    |
    v
sbir_feedback_cli.py
  1. WorkspaceResolver -> active proposal dir
  2. Read proposal-state, rigor-profile, company-profile, finder-results (all graceful on missing)
  3. git rev-parse --short HEAD -> plugin_version
  4. FeedbackSnapshotService.build_snapshot() -> FeedbackSnapshot (pure function)
  5. FeedbackEntry(uuid, timestamp, type, ratings, free_text, snapshot)
  6. FilesystemFeedbackAdapter.write() -> .sbir/feedback/feedback-{ts}.json (atomic)
  7. print JSON: {feedback_id, file_path}
    |
    v
Agent confirms: "Feedback saved. ID: {uuid}."
```

### Privacy Boundary

The privacy boundary is enforced in Python at `FeedbackSnapshotService.build_snapshot()`, not in documentation. Fields excluded from the snapshot:

- Company capabilities, past performance descriptions, key personnel details
- Proposal draft content and corpus matches
- Full topic descriptions, objectives, Q&A entries from finder results

Fields included (metadata only): company name, profile age, proposal/topic IDs, current wave, rigor profile name, finder results age, top 5 scored topics (IDs + scores only), artifact filename list, plugin version (git SHA).

This ensures `.sbir/feedback/` files can be shared with the developer without the user reviewing them for sensitive content.

---

## Architecture Decision Records

### ADR-039: Feedback Snapshot Assembly via Standalone CLI Script

**Decision**: Standalone Python CLI (`scripts/sbir_feedback_cli.py`) rather than inline agent `Read` tool calls.

**Rationale**: CLI is unit-testable with pytest; agent tool calls are not. Maintains the `dsip_cli.py` convention of "agent calls Bash → Python wires adapters → JSON stdout." Enables mutation testing kill rate gate to apply. Privacy boundary is enforced in verifiable Python code, not markdown prose.

### ADR-040: Feedback Snapshot Privacy Boundary — Metadata Only

**Decision**: Snapshot includes metadata fields only; prose content (capabilities, drafts, descriptions) is excluded.

**Rationale**: Snapshots must be shareable without review. Developer needs to know what was happening (wave, topic, rigor, profile freshness), not what the content was. Defense in depth: even if `.sbir/feedback/` is accidentally committed to git, it contains no company IP.

---

## Files Created

### Python PES (5 files)

| File | Role |
|------|------|
| `scripts/pes/domain/feedback.py` | Domain model: `FeedbackType` enum, `QualityRatings`, `FeedbackSnapshot` (14 fields), `FeedbackEntry`. All dataclasses. `to_dict()` produces JSON-serializable output. |
| `scripts/pes/domain/feedback_service.py` | `FeedbackSnapshotService.build_snapshot()` — pure function, no IO. Receives pre-read dicts. Enforces privacy boundary. |
| `scripts/pes/ports/feedback_port.py` | `FeedbackWriterPort` ABC — single `write(entry, output_dir) -> Path` method. Dependency inversion boundary. |
| `scripts/pes/adapters/filesystem_feedback_adapter.py` | `FilesystemFeedbackAdapter` — implements port. Atomic write (.tmp -> .bak -> rename). Creates output directory if absent. Filename: `feedback-{timestamp}.json`. |
| `scripts/sbir_feedback_cli.py` | CLI entry point with `save` subcommand. Wires all 5 existing adapters. Graceful degradation on missing files. Prints `{feedback_id, file_path}` JSON on success. |

### Markdown (2 files)

| File | Role |
|------|------|
| `commands/proposal-developer-feedback.md` | `/sbir:developer-feedback` slash command. Requires no context files — works without any active proposal state. Dispatches to `sbir-feedback-collector`. |
| `agents/sbir-feedback-collector.md` | Interactive agent. AskUserQuestion flow: type → ratings (if Quality) → free text. Calls CLI via Bash. Confirms with feedback_id and file path on success. |

### Tests (3 files)

| File | Role |
|------|------|
| `tests/unit/test_feedback_domain.py` | Unit tests for `feedback.py` domain model |
| `tests/unit/test_feedback_service.py` | Unit tests for `FeedbackSnapshotService` |
| `tests/unit/test_filesystem_feedback_adapter.py` | Unit tests for `FilesystemFeedbackAdapter` |
| `tests/acceptance/sbir_developer_feedback/` | BDD acceptance tests including walking skeleton and CLI milestone features |

---

## Quality Metrics

### DES TDD Execution (5 Steps, all PASS)

| Step | Name | PREPARE | RED | GREEN | COMMIT |
|------|------|---------|-----|-------|--------|
| 01-01 | Feedback domain model | PASS | PASS (unit) | PASS | PASS |
| 01-02 | FeedbackSnapshotService | PASS | PASS (unit) | PASS | PASS |
| 01-03 | Port and adapter | PASS | PASS (unit) | PASS | PASS |
| 01-04 | CLI entry point | PASS | PASS (acceptance) | PASS | PASS |
| 02-01 | Command and agent | PASS | N/A (forge) | PASS | PASS |

### Test Coverage

- Walking skeleton acceptance test: passing
- L1-L4 refactoring: complete
- Adversarial review: PASS (no defects)

### Mutation Testing (per-feature, scoped to modified Python files)

| File | Kill Rate |
|------|-----------|
| `scripts/pes/domain/feedback.py` | 100% |
| `scripts/pes/domain/feedback_service.py` | 88.2% |
| `scripts/pes/adapters/filesystem_feedback_adapter.py` | 90.5% |

All files exceed the 80% kill rate gate defined in CLAUDE.md.

---

## Integration Notes

- No existing PES adapter was modified. All 5 (`WorkspaceResolver`, `JsonStateAdapter`, `FilesystemRigorAdapter`, `JsonProfileAdapter`, `JsonFinderResultsAdapter`) are consumed read-only.
- Feedback output directory `.sbir/feedback/` follows the `.sbir/` state convention established in earlier waves.
- CLI pattern matches `dsip_cli.py` (argparse, JSON stdout, subprocess entry point).
- Feature is portable: no network calls, no external services. Works air-gapped and on first-time setup.
