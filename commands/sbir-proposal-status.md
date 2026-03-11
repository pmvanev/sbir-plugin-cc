---
description: "Display current proposal status, progress, and suggested next actions"
argument-hint: "- No arguments required"
---

# /proposal status

Display current proposal status, progress, and suggested next actions.

## Usage

```
/proposal status
```

## Output

1. **Current wave** -- Name and number of the active wave
2. **Progress** -- Completed vs total waves
3. **Deadline countdown** -- Days remaining until submission deadline
4. **Pending events** -- Async events awaiting user action (e.g., TPOC call)
5. **Next action** -- Concrete suggestion for what to do next
6. **Warnings** -- Critical deadline warnings when days remaining <= 5

## Examples

```
Wave 1: Requirements & Strategy
1/5 waves completed
18 days to deadline
Next: Start strategy brief with /proposal strategy
```

When TPOC questions are pending:
```
TPOC questions generated -- PENDING CALL
Next: Have TPOC call, then /proposal tpoc ingest
```

When no proposal exists:
```
No active proposal found
Start with /proposal new
```

## Implementation

This command invokes `StatusService.get_status()` (driving port) which reads proposal state via `StateReader` (driven port) and produces a `StatusReport` domain model.

## Agent Invocation

@sbir-orchestrator

Read proposal state and present current status, progress, deadline countdown, and suggested next action.
