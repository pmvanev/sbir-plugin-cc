---
description: "Switch active proposal context to a different proposal in the workspace"
argument-hint: "<topic-id> - The topic ID or namespace of the proposal to switch to"
---

# /proposal switch

Switch the active proposal context so all subsequent commands operate on the target proposal.

## Usage

```
/proposal switch <topic-id>
```

## Arguments

- `<topic-id>` -- The topic ID or namespace of the target proposal (e.g., `af263-042`, `n244-012`). Case-insensitive; internally lowercased.

## Behavior

1. Read current active proposal from `.sbir/active-proposal`
2. Validate target `<topic-id>` exists at `.sbir/proposals/{topic-id}/`
3. If target does not exist, fail with error listing available proposals
4. If target is already active, display "already active" message with status summary (no state change)
5. Write `<topic-id>` to `.sbir/active-proposal`
6. Display switch confirmation with from/to proposals
7. Display target proposal status summary (wave, deadline, next action)

## Output

Successful switch:
```
Switched from: N244-012 (AUV Navigation)
Switched to: AF263-042 (Compact Directed Energy)

Wave 3: Discrimination & Outline
27 days to deadline
Next: /sbir:proposal wave outline
```

Already active:
```
AF263-042 is already the active proposal.

Wave 3: Discrimination & Outline
27 days to deadline
Next: /sbir:proposal wave outline
```

Nonexistent topic ID:
```
No proposal found with topic ID 'xyz-999'.
Available proposals: af263-042, n244-012
```

## Notes

- Completed proposals (Wave 8+) are switchable for Wave 9 debrief access
- The switch command does not modify any proposal state -- only the active pointer changes
- Requires multi-proposal workspace layout (`.sbir/proposals/` must exist)

## Agent Invocation

@sbir-orchestrator

Validate target proposal exists, update `.sbir/active-proposal`, and display switch confirmation with target proposal status summary.
