---
name: proposal-state-schema
description: Schema reference for proposal-state.json fields. Shared across all agents that read or write proposal state.
---

# Proposal State Schema

## output_format

| Attribute | Value |
|-----------|-------|
| Field path | `output_format` |
| Type | string |
| Valid values | `"latex"`, `"docx"` |
| Default | `"docx"` |
| Required | Yes (set during proposal setup) |
| Added in | proposal-format-selection feature |

### When it is set

The `output_format` field is set during `/proposal new`, after fit scoring and before the Go/No-Go checkpoint.

- **Default (Enter)**: Sets `output_format` to `"docx"`.
- **Explicit selection**: Sets `output_format` to the chosen value (`"latex"` or `"docx"`).
- **PDF-submission hint**: When the solicitation text contains PDF submission indicators (e.g. "submit as PDF", "PDF format required"), the prompt recommends LaTeX for higher-fidelity PDF output.

### Mid-proposal changes

Format can be changed later via `/proposal format change`. Changes at Wave 3 or later trigger a rework warning because outline and draft artifacts may need adjustment.

### Legacy states

States created before the format-selection feature may lack `output_format`. When reading state, treat a missing field as `"docx"` (the default). The `FormatConfigService.get_effective_format()` method handles this.

### Status dashboard

The `/proposal status` dashboard includes the current `output_format` value so the engineer always knows which pipeline is active.

### Validation

Invalid values (anything other than `"latex"` or `"docx"`) are rejected by schema validation. The `FormatConfigService.validate_format()` method performs this check.
