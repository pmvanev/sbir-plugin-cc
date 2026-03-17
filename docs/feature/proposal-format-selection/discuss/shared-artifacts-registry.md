# Shared Artifacts Registry: Proposal Format Selection

## Artifacts

### output_format

- **Source of truth**: `.sbir/proposal-state.json` -> `output_format`
- **Values**: `"latex"` | `"docx"`
- **Default**: `"docx"`
- **Owner**: sbir-orchestrator (set during `/proposal new`, changeable via `/proposal config format`)
- **Consumers**:
  - Status dashboard: displays as "Format: LaTeX" or "Format: DOCX"
  - sbir-writer: may adjust content structure hints (e.g., LaTeX cross-reference style vs DOCX bookmark style)
  - sbir-formatter (Wave 5): selects figure output format (EPS/PDF for LaTeX, PNG/EMF for DOCX)
  - sbir-formatter (Wave 6): applies formatting rules and assembles in target medium
  - sbir-submission-agent (Wave 8): packages in correct submission format
- **Integration risk**: HIGH -- if agents hardcode format assumptions instead of reading state, the user gets inconsistent output requiring manual correction at Wave 6
- **Validation**: All downstream agents must read `output_format` from `.sbir/proposal-state.json`. No agent should assume a default or prompt the user again.

### topic_id (existing, no change)

- **Source of truth**: `.sbir/proposal-state.json` -> `topic.id`
- **Consumers**: All agents, all artifact paths, status dashboard
- **Integration risk**: LOW -- already well-established in the codebase

### go_no_go (existing, no change)

- **Source of truth**: `.sbir/proposal-state.json` -> `go_no_go`
- **Consumers**: Wave progression, status dashboard
- **Integration risk**: LOW -- already well-established

## Integration Checkpoints

| Checkpoint | Validates | Failure Mode |
|-----------|----------|-------------|
| After format selection (Step 3) | `output_format` is `"latex"` or `"docx"` in state file | Invalid or missing value blocks Go/No-Go |
| Writer reads format (Wave 3-4) | Writer references `output_format` from state | Writer produces format-agnostic content (acceptable fallback) |
| Formatter reads format (Wave 5-6) | Formatter reads `output_format` instead of prompting | Formatter prompts user again (bad UX, but not data loss) |
| Submission agent reads format (Wave 8) | Package matches declared format | Wrong submission format (compliance failure) |

## Schema Change Required

The `proposal-state-schema.json` needs a new property:

```json
"output_format": {
  "type": "string",
  "enum": ["latex", "docx"],
  "default": "docx",
  "description": "Proposal output format selected during setup. Consumed by writer, formatter, and submission agent."
}
```

This field should be added to the `required` array in the schema.
