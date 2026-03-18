---
description: "Change the proposal output format (latex or docx). Warns about rework impact at Wave 3+"
argument-hint: "<format> - Target format: latex or docx"
---

# /proposal config format

Change the proposal output format after initial selection.

## Usage

```
/proposal config format latex     # Switch to LaTeX output
/proposal config format docx      # Switch to DOCX output
```

## Flow

1. **Validate format** -- Reject invalid or empty values with helpful error listing valid options (latex, docx)
2. **Check current wave** -- If Wave 3 or later, display rework warning with wave context and require user confirmation before proceeding
3. **Update state** -- Write new `output_format` to proposal state via FormatConfigService
4. **Confirm** -- Display updated format to user

## Rework Warning

At Wave 3+, formatting and outline artifacts may already exist. Changing format triggers a warning:

```
WARNING: Changing output format at Wave {N} may require rework.
Outline and formatting artifacts created for the current format may need adjustment.

Confirm format change to {format}? (y/n)
```

The user must confirm before the state update proceeds.

## Prerequisites

- Active proposal exists (`.sbir/proposal-state.json` present)
- Valid format value: `latex` or `docx` (case-insensitive)

## Examples

Before Wave 3 (no warning):
```
/proposal config format latex
Output format updated to: latex
```

At Wave 3+ (rework warning):
```
/proposal config format docx
WARNING: Changing output format at Wave 4 may require rework.
Outline and formatting artifacts created for the current format may need adjustment.
Confirm format change to docx? (y/n)
> y
Output format updated to: docx
```

Invalid format:
```
/proposal config format pdf
Error: "pdf" is not a valid output format.
Valid options: latex, docx
```

## Implementation

This command invokes `FormatConfigService.change_format()` (driving port) which orchestrates:
- Format validation (rejects invalid/empty values)
- Wave-aware rework warning (Wave 3+ triggers confirmation requirement)
- `StateWriter.save()` (driven port) to persist updated output format

## Agent Invocation

@sbir-orchestrator

Read proposal state, validate the requested format, display rework warning if at Wave 3+, and update the output format on confirmation.
