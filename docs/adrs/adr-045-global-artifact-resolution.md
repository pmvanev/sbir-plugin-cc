# ADR-045: Global Artifact Resolution in Hook Adapter

## Status

Accepted

## Context

Existing PES evaluators check artifacts in the proposal artifact directory (e.g., `artifacts/{topic-id}/wave-5-visuals/figure-specs.md`). The hook adapter resolves these local paths and passes existence info via `tool_context["artifacts_present"]` (ADR-044).

The new WritingStyleGateEvaluator needs to check `~/.sbir/quality-preferences.json` -- a global artifact outside the proposal directory. The evaluator is a pure domain object with no filesystem imports. The hook adapter must resolve global artifact existence and pass it to the evaluator as data.

Three design questions:
1. How to represent global artifacts in tool_context
2. When to trigger global artifact resolution
3. How to resolve the global path

## Decision

**Part 1 -- Separate field**: Add `global_artifacts_present` list to `tool_context` alongside `artifacts_present`. This keeps the two scopes semantically distinct. The evaluator checks `tool_context.get("global_artifacts_present", [])` for `"quality-preferences.json"`.

**Part 2 -- Path-based trigger**: Resolve global artifacts when `file_path` contains `wave-4-drafting/`. This mirrors the existing pattern where `wave-5-visuals/` triggers local artifact resolution. New wave directories requiring global checks will need additional path segments -- acceptable for the low rate of new gates.

**Part 3 -- Home directory resolution**: The hook adapter resolves `Path.home() / ".sbir"` and checks for configured global prerequisite files. This uses the same `os.path.isfile` pattern as existing local artifact resolution.

## Alternatives Considered

### Alternative 1: Extend artifacts_present with prefixed names

- **What**: Add entries like `"global:quality-preferences.json"` to the existing `artifacts_present` list.
- **Expected Impact**: No new field, evaluators parse prefix to distinguish scope.
- **Why Insufficient**: Conflates local and global artifacts in a single list. Evaluators must parse prefixes (string convention coupling). Existing evaluators (figure pipeline, style profile) would need to filter out `global:` prefixed entries to avoid false positives. Breaks the semantic contract of `artifacts_present` = "files in the artifact directory."

### Alternative 2: Pass home directory path, let evaluator check filesystem

- **What**: Add `home_dir` to tool_context. Evaluator calls `os.path.isfile(home_dir + "/.sbir/quality-preferences.json")`.
- **Expected Impact**: Simplest adapter change -- just pass a string.
- **Why Insufficient**: Violates domain purity. Evaluators are pure domain objects with no infrastructure imports (established in ADR-044). Filesystem access belongs in the adapter layer. This would make WritingStyleGateEvaluator the only evaluator with `os` imports.

### Alternative 3: Always resolve global artifacts regardless of target path

- **What**: Check `~/.sbir/` for global artifacts on every PreToolUse event, not just wave-4-drafting/ targets.
- **Expected Impact**: Simpler conditional logic in adapter.
- **Why Insufficient**: Every Write/Edit event would hit the filesystem to check `~/.sbir/quality-preferences.json`, even for wave-1 through wave-3 writes and wave-5 writes where the gate is irrelevant. Unnecessary I/O for ~80% of tool invocations.

## Consequences

- Positive: Clean semantic separation between local and global artifact scopes
- Positive: Evaluator remains pure domain object -- no filesystem imports
- Positive: Existing `artifacts_present` behavior unchanged -- no impact on figure pipeline or style profile gates
- Positive: Pattern is extensible -- future global artifact checks add to `global_artifacts_present` list
- Negative: Hook adapter grows in complexity (two resolution paths for two wave directories)
- Negative: New wave directories requiring global checks need adapter code changes (acceptable at current rate of new gates)
