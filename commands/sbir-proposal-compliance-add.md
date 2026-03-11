---
description: "Manually add a missed compliance item to the compliance matrix"
argument-hint: "<requirement-text> - Quoted text of the compliance requirement to add"
---

# /proposal compliance add

Manually add a missed compliance item to the compliance matrix.

## Usage

```
/proposal compliance add "Section 3 shall include risk mitigation table"
```

## Behavior

1. Loads the existing compliance matrix from the artifacts directory
2. Adds the new item with type `manual` and auto-incremented ID
3. Infers the proposal section from the text (e.g., "Section 3" references)
4. Writes the updated matrix back to markdown

## Output

```
Added item #48: "Section 3 shall include risk mitigation table"
Type: manual | Section: Section 3
Matrix updated: 48 items total
```

## Error Cases

When no compliance matrix exists:
```
No compliance matrix found
Generate one first with the strategy wave command
```

## Implementation

This command invokes `ComplianceService.add_item()` (driving port) which adds a `ComplianceItem` with `RequirementType.MANUAL` to an existing `ComplianceMatrix`. The `MarkdownComplianceAdapter` persists the updated matrix.

## Agent Invocation

@sbir-compliance-sheriff

Add the user-provided requirement text as a manual compliance item and update the matrix.
