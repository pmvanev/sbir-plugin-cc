# ADR-037: Rigor Profile Storage Strategy

## Status

Accepted

## Context

The rigor profile feature requires two categories of data:

1. **Profile definitions** -- what each named profile (lean/standard/thorough/exhaustive) configures: model tiers per agent role, review passes, critique iterations, iteration caps
2. **Per-proposal profile selection** -- which profile is active for a given proposal, with change history

The storage strategy must support: per-proposal isolation (multi-proposal workspace), atomic writes (crash safety), backward compatibility (proposals created before rigor), and extensibility (adding profiles without code changes).

### Option A: Single per-proposal file containing both definitions and selection

Each proposal stores a full copy of the profile definition alongside the selection.

- **Pros**: Self-contained per proposal.
- **Cons**: Profile definitions duplicated across proposals. Updating a profile definition (e.g., adjusting cost ranges) requires updating every proposal's file. Violates single source of truth.

### Option B: Plugin-level definitions + per-proposal selection (separate files)

Profile definitions in `config/rigor-profiles.json` (shipped with plugin, read-only). Per-proposal selection in `.sbir/proposals/{topic-id}/rigor-profile.json` (read-write, user-specific).

- **Pros**: Single source of truth for definitions. Per-proposal file is small (profile name + history). Plugin updates can improve profile definitions without touching user data. Consistent with existing pattern: `pes-config.json` is plugin-level, `proposal-state.json` is per-proposal.
- **Cons**: Two files to read during resolution (negligible cost -- both are small JSON).

### Option C: Embed rigor in proposal-state.json

Add `rigor_profile` and `rigor_history` fields to the existing proposal-state.json.

- **Pros**: No new file. Existing atomic write infrastructure reused.
- **Cons**: Increases proposal-state.json schema complexity. Rigor is conceptually separate from proposal state (it controls how agents work, not what the proposal contains). Schema version bump required. Existing features that write to proposal-state.json must not clobber rigor fields.

## Decision

**Option B: Plugin-level definitions in `config/rigor-profiles.json` + per-proposal selection in `.sbir/proposals/{topic-id}/rigor-profile.json`.**

This follows the existing pattern of plugin-level config (like `pes-config.json`) separate from per-proposal state. The per-proposal file uses the same atomic write protocol as proposal-state.json.

## Consequences

### Positive

- Profile definitions maintained once, applied everywhere
- Per-proposal file is minimal (profile name + history array)
- Plugin updates can adjust profile definitions without migrating user data
- Clean separation of concerns: definitions vs. selection

### Negative

- New file created per proposal (minimal overhead)
- Resolution requires reading two files (negligible -- both <1KB)
