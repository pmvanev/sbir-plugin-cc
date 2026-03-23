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
3. **Rigor** -- Active rigor profile (read from `.sbir/proposals/{id}/rigor-profile.json`, default "standard" if missing)
4. **Deadline countdown** -- Days remaining until submission deadline
5. **Pending events** -- Async events awaiting user action (e.g., TPOC call)
6. **Next action** -- Concrete suggestion for what to do next
7. **Warnings** -- Critical deadline warnings when days remaining <= 5

## Examples

```
Wave 1: Requirements & Strategy
1/5 waves completed
Rigor: standard
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

Portfolio view (multiple proposals):
```
Proposals:
  af263-042  Wave 3  Rigor: thorough    12 days to deadline
  navy-0087  Wave 1  Rigor: standard    25 days to deadline
  doe-112    Wave 6  Rigor: lean         4 days to deadline  ⚠ DEADLINE
```

## Implementation

This command invokes `StatusService.get_status()` (driving port) which reads proposal state via `StateReader` (driven port) and produces a `StatusReport` domain model.

## Agent Invocation

@sbir-orchestrator

Read proposal state and present current status, progress, deadline countdown, and suggested next action.
