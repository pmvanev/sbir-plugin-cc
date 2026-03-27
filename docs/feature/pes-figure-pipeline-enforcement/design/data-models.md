# PES Figure Pipeline Enforcement -- Data Models

## Evaluator Interface (Updated)

```
triggers(rule: EnforcementRule, state: dict, tool_name: str, tool_context: dict = {}) -> bool
build_block_message(rule: EnforcementRule, state: dict) -> str  # optional, unchanged
```

`tool_context` is a new optional parameter with default empty dict. Existing evaluators continue to work unchanged.

## tool_context Structure

```json
{
  "file_path": "artifacts/sf25d-t1201/wave-5-visuals/figure-1-system-arch.svg",
  "artifacts_present": ["figure-specs.md", "style-profile.yaml"]
}
```

- `file_path`: Full path from hook input `tool.file_path`. Empty string if absent.
- `artifacts_present`: List of prerequisite filenames found in the resolved artifact directory. Empty list if file_path is not in `wave-5-visuals/` or directory does not exist.

## New Rule Configurations

### figure-pipeline-requires-specs

```json
{
  "rule_id": "figure-pipeline-requires-specs",
  "description": "Figure files in wave-5-visuals require figure-specs.md first",
  "rule_type": "figure_pipeline_gate",
  "condition": {
    "target_directory": "wave-5-visuals",
    "required_artifact": "figure-specs.md"
  },
  "message": "Cannot write figure files to wave-5-visuals/ before creating figure specifications"
}
```

### figure-generation-requires-style

```json
{
  "rule_id": "figure-generation-requires-style",
  "description": "Figure generation requires style profile or explicit skip",
  "rule_type": "style_profile_gate",
  "condition": {
    "target_directory": "wave-5-visuals",
    "required_artifact": "style-profile.yaml",
    "skip_state_field": "style_analysis_skipped"
  },
  "message": "Cannot generate figures before completing style analysis"
}
```

## State Fields Used

| Field | Type | Source | Consumer |
|---|---|---|---|
| `style_analysis_skipped` | boolean | Set by formatter agent when user skips style analysis | StyleProfileGateEvaluator |

## Prerequisite Files Checked

| File | Directory | Gate |
|---|---|---|
| `figure-specs.md` | `artifacts/{topic-id}/wave-5-visuals/` or `artifacts/wave-5-visuals/` | FigurePipelineGateEvaluator |
| `style-profile.yaml` | Same as above | StyleProfileGateEvaluator |

## Path Layout Support

Both multi-proposal and legacy layouts:
- Multi-proposal: `artifacts/{topic-id}/wave-5-visuals/`
- Legacy: `artifacts/wave-5-visuals/`

The artifact directory is resolved from the file_path by finding the `wave-5-visuals/` segment and using its parent.
