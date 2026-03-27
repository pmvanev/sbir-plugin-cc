# Outline Gate Enforcement -- Data Models

## Evaluator Interface (Unchanged)

```
triggers(rule: EnforcementRule, state: dict, tool_name: str, tool_context: dict = {}) -> bool
build_block_message(rule: EnforcementRule, state: dict) -> str
```

No interface changes. OutlineGateEvaluator uses the same signature established in ADR-044.

## tool_context Structure (Extended)

```json
{
  "file_path": "artifacts/sf25d-t1201/wave-4-drafting/section-1-technical-approach.md",
  "artifacts_present": [],
  "global_artifacts_present": ["quality-preferences.json"],
  "outline_artifacts_present": ["proposal-outline.md"]
}
```

- `outline_artifacts_present`: List containing `"proposal-outline.md"` if found in the derived wave-3-outline/ sibling directory. Empty list if absent or if file_path is not in `wave-4-drafting/`. **New field.**

## New Rule Configuration

### drafting-requires-outline

```json
{
  "rule_id": "drafting-requires-outline",
  "description": "Wave 4 drafting requires approved outline from Wave 3",
  "rule_type": "outline_gate",
  "condition": {
    "target_directory": "wave-4-drafting",
    "required_artifact": "proposal-outline.md",
    "required_artifact_directory": "wave-3-outline"
  },
  "message": "Cannot write draft sections before the proposal outline is approved. Complete the outline in Wave 3 first."
}
```

## Prerequisite File Checked

| File | Source Directory | Target Directory | Gate |
|---|---|---|---|
| `proposal-outline.md` | `wave-3-outline/` (sibling of target) | `wave-4-drafting/` | OutlineGateEvaluator |

## Cross-Directory Path Resolution

| Target Path | Derived Check Path |
|---|---|
| `artifacts/{topic-id}/wave-4-drafting/section-1.md` | `artifacts/{topic-id}/wave-3-outline/proposal-outline.md` |
| `artifacts/wave-4-drafting/section-1.md` | `artifacts/wave-3-outline/proposal-outline.md` |

## State Fields Used

None. OutlineGateEvaluator does not read proposal state beyond what the engine provides. No skip marker. No state-based bypass.
