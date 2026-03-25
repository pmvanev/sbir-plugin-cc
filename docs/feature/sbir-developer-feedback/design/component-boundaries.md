# Component Boundaries — sbir-developer-feedback

## New Components

### Domain Layer (`scripts/pes/domain/`)

#### `feedback.py`
**Responsibility**: Define the data model for feedback entries and snapshots.
**Public interface**:
- `FeedbackType` — enum: `BUG | SUGGESTION | QUALITY`
- `QualityRatings` — dataclass: `past_performance`, `image_quality`, `writing_quality`, `topic_scoring` (each `int | None`, 1–5)
- `FeedbackSnapshot` — dataclass: all 14 context fields (see shared-artifacts-registry)
- `FeedbackEntry` — dataclass: `feedback_id`, `timestamp`, `type`, `ratings`, `free_text`, `context_snapshot`
- `FeedbackEntry.to_dict()` — serialization for JSON output

**Must NOT import**: any adapter, any port, any IO library.
**May import**: `dataclasses`, `enum`, `datetime`, `uuid`.

#### `feedback_service.py`
**Responsibility**: Assemble a `FeedbackSnapshot` from pre-read state data.
**Public interface**:
- `FeedbackSnapshotService.build_snapshot(state, rigor, profile, profile_mtime, finder, finder_mtime, cwd, artifacts_dir) -> FeedbackSnapshot`

**Input contract**:
- All arguments are plain Python dicts or `Path | datetime | None`
- No adapter instances passed in — CLI pre-reads everything
- Privacy boundary enforced here: only metadata fields extracted, no capability text

**Must NOT import**: any adapter, any filesystem IO.
**May import**: `datetime`, `pathlib.Path`, `subprocess` (for git SHA only).

---

### Port Layer (`scripts/pes/ports/`)

#### `feedback_port.py`
**Responsibility**: Abstract interface for writing feedback entries.
**Public interface**:
- `FeedbackWriterPort` (ABC):
  - `write(entry: FeedbackEntry, output_dir: Path) -> Path` — writes entry, returns path of written file

---

### Adapter Layer (`scripts/pes/adapters/`)

#### `filesystem_feedback_adapter.py`
**Responsibility**: Persist feedback entries as atomic JSON files.
**Implements**: `FeedbackWriterPort`
**Public interface**:
- `FilesystemFeedbackAdapter.write(entry, output_dir) -> Path`
  - Creates `output_dir` if absent
  - Generates filename: `feedback-{UTC-ISO-timestamp}.json` (colons → hyphens)
  - Writes via tmp → rename atomic pattern
  - Returns final file path

**Must NOT import**: domain services, other adapters.
**May import**: `json`, `pathlib`, `shutil`.

---

### CLI Layer (`scripts/`)

#### `sbir_feedback_cli.py`
**Responsibility**: Wire adapters, read all state, orchestrate snapshot assembly and persistence.
**Commands**: `save`
**Arguments for `save`**:
- `--type` (required): `bug | suggestion | quality`
- `--ratings` (optional): JSON string `{"past_performance": N, "image_quality": N, ...}` — missing keys = null
- `--free-text` (optional): string
- `--state-dir` (optional, default `.sbir`): override for testing
- `--profile-path` (optional, default `~/.sbir/company-profile.json`): override for testing

**Output**: JSON to stdout: `{"feedback_id": "...", "file_path": "..."}`
**Exit codes**: 0 = success, 1 = error writing file

**Wiring order**:
1. `WorkspaceResolver.resolve_workspace(Path.cwd())`
2. Read state (try/except → None)
3. Read rigor profile (try/except → None)
4. Read company profile (try/except → None, stat mtime)
5. Read finder results (try/except → None, stat mtime)
6. `FeedbackSnapshotService.build_snapshot(...)`
7. `FeedbackEntry(...)` — generate UUID, timestamp
8. `FilesystemFeedbackAdapter.write(entry, output_dir)`
9. Print JSON confirmation

---

### Markdown Layer

#### `commands/proposal-developer-feedback.md`
**Responsibility**: Slash command entry point (`/sbir:developer-feedback`).
**Pattern**: Dispatches to `sbir-feedback-collector` agent. Passes no required context files (command works without any state).
**Size**: ~30 lines.

#### `agents/sbir-feedback-collector.md`
**Responsibility**: Interactive UX for feedback submission.
**Behavior**:
1. Ask feedback type (Bug / Suggestion / Quality Issue) via AskUserQuestion
2. If Quality Issue: ask ratings (1–5 per dimension, all optional)
3. Ask free text (optional)
4. If no ratings and no free text: ask confirmation once
5. Invoke CLI: `python scripts/sbir_feedback_cli.py save --type ... [--ratings ...] [--free-text ...]`
6. Parse CLI JSON output, confirm to user with feedback ID and file path
**Size**: ~100 lines. No skill loading needed (all logic delegated to CLI).

---

## Dependency Rules

```
agents/sbir-feedback-collector.md
    └── calls via Bash ──► scripts/sbir_feedback_cli.py
                               ├── reads ──► workspace_resolver
                               ├── reads ──► json_state_adapter (existing)
                               ├── reads ──► filesystem_rigor_adapter (existing)
                               ├── reads ──► json_profile_adapter (existing)
                               ├── reads ──► json_finder_results_adapter (existing)
                               ├── calls ──► feedback_service (new domain)
                               │                └── uses ──► feedback (new domain model)
                               └── calls ──► filesystem_feedback_adapter (new adapter)
                                                └── implements ──► feedback_port (new port)
```

All arrows point inward. Domain has no knowledge of adapters or CLI.

---

## File Manifest

| File | Type | Status |
|------|------|--------|
| `scripts/pes/domain/feedback.py` | New | Domain model |
| `scripts/pes/domain/feedback_service.py` | New | Domain service |
| `scripts/pes/ports/feedback_port.py` | New | Port interface |
| `scripts/pes/adapters/filesystem_feedback_adapter.py` | New | Filesystem adapter |
| `scripts/sbir_feedback_cli.py` | New | CLI entry point |
| `commands/proposal-developer-feedback.md` | New | Slash command |
| `agents/sbir-feedback-collector.md` | New | Interactive agent |
| `scripts/pes/adapters/json_state_adapter.py` | Existing | Read-only, no change |
| `scripts/pes/adapters/filesystem_rigor_adapter.py` | Existing | Read-only, no change |
| `scripts/pes/adapters/json_profile_adapter.py` | Existing | Read-only, no change |
| `scripts/pes/adapters/json_finder_results_adapter.py` | Existing | Read-only, no change |
| `scripts/pes/adapters/workspace_resolver.py` | Existing | Read-only, no change |
