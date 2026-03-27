# Writing Style Gate Enforcement -- Data Models

## Evaluator Interface (Unchanged)

```
triggers(rule: EnforcementRule, state: dict, tool_name: str, tool_context: dict = {}) -> bool
build_block_message(rule: EnforcementRule, state: dict) -> str
```

Same interface as figure pipeline and style profile gates. No interface changes needed.

## tool_context Structure (Extended)

```json
{
  "file_path": "artifacts/sf25d-t1201/wave-4-drafting/sections/technical-approach.md",
  "artifacts_present": [],
  "global_artifacts_present": ["quality-preferences.json"]
}
```

- `file_path`: Full path from hook input `tool.file_path`. Empty string if absent.
- `artifacts_present`: List of local prerequisite filenames found in proposal artifact directory. Empty list unless file_path targets `wave-5-visuals/`. Unchanged from ADR-044.
- `global_artifacts_present`: **NEW**. List of global artifact filenames found at `~/.sbir/`. Populated when file_path targets `wave-4-drafting/`. Empty list otherwise.

## New Rule Configuration

### drafting-requires-style-selection

```json
{
  "rule_id": "drafting-requires-style-selection",
  "description": "Wave 4 draft writes require writing style selection or explicit skip",
  "rule_type": "writing_style_gate",
  "condition": {
    "target_directory": "wave-4-drafting",
    "required_global_artifact": "quality-preferences.json",
    "skip_state_field": "writing_style_selection_skipped"
  },
  "message": "Cannot write draft sections before writing style selection"
}
```

## State Fields Used

| Field | Type | Source | Consumer |
|---|---|---|---|
| `writing_style_selection_skipped` | boolean | Set by writer agent when user skips style selection at checkpoint | WritingStyleGateEvaluator |
| `writing_style` | string | Set by writer agent when user chooses a style at checkpoint | sbir-writer style skill loading |

## Global Artifacts Checked

| File | Location | Gate | Purpose |
|---|---|---|---|
| `quality-preferences.json` | `~/.sbir/` | WritingStyleGateEvaluator | Existence check -- if present, user has run quality discovery |

## Path Layout Support

Both multi-proposal and legacy layouts:
- Multi-proposal: `artifacts/{topic-id}/wave-4-drafting/`
- Legacy: `artifacts/wave-4-drafting/`

The evaluator detects `wave-4-drafting/` as a path segment, same pattern as existing evaluators detect `wave-5-visuals/`.
