# ADR-032: Legacy Migration Approach

## Status

Proposed

## Context

Existing single-proposal workspaces store state at `.sbir/proposal-state.json` (root) and artifacts at `artifacts/wave-N-name/` (root). Multi-proposal support namespaces these under `{topic-id}/` subdirectories. Existing workspaces must continue working. Migration to multi-proposal layout must be opt-in, safe, and reversible.

## Decision

Opt-in migration triggered only when user runs `/proposal new` in a legacy workspace. The plugin prompts: "Single-proposal layout detected. Enable multi-proposal support?" Migration moves existing state and artifacts into a namespaced subdirectory, preserving originals with `.migrated` suffix. Legacy workspaces that never add a second proposal continue working unchanged indefinitely.

Migration steps:
1. Read topic ID from existing `proposal-state.json`
2. Create `.sbir/proposals/{topic-id}/`
3. Copy `proposal-state.json` to `.sbir/proposals/{topic-id}/proposal-state.json`
4. Copy `audit/` to `.sbir/proposals/{topic-id}/audit/`
5. Move `artifacts/wave-*` to `artifacts/{topic-id}/wave-*`
6. Create `.sbir/active-proposal` with topic ID
7. Rename originals: `.sbir/proposal-state.json` -> `.sbir/proposal-state.json.migrated`

## Alternatives Considered

### Alternative 1: Automatic migration on plugin update

- **What**: Plugin update detects legacy layout and migrates automatically on first command.
- **Evaluation**: Zero user friction. Seamless upgrade path.
- **Why rejected**: Silent file moves are dangerous. If migration has a bug, in-progress proposals are disrupted with no user awareness. Phil could lose work mid-deadline. Opt-in with confirmation is safer for a solo engineer with no backup system.

### Alternative 2: Dual-write during transition period

- **What**: Write state to both legacy and multi-proposal locations simultaneously for N sessions. Then remove legacy.
- **Evaluation**: Gradual transition. Rollback is trivial.
- **Why rejected**: Dual-write adds complexity to every state write. Risk of divergence if one write succeeds and the other fails. Over-engineered for a one-time migration.

### Alternative 3: No migration -- require fresh workspace for multi-proposal

- **What**: Legacy workspaces stay legacy. Multi-proposal requires `mkdir new-workspace && cd new-workspace && /proposal new`.
- **Evaluation**: Simplest implementation. Zero risk to existing proposals.
- **Why rejected**: Forces corpus re-ingestion and partner re-configuration in new workspace. The whole point of multi-proposal is to share these resources. Defeats the primary user need.

## Consequences

### Positive
- Zero risk to users who never need multi-proposal (legacy works unchanged forever)
- Migration is explicit user action with confirmation
- `.migrated` suffix provides manual rollback path
- Copy-then-rename avoids data loss on interruption

### Negative
- Migration code path is used infrequently (once per workspace lifetime), making it harder to validate in production
- Artifact directory moves could be slow for large proposal outputs (mitigated: typical proposal artifacts are <100 files)
