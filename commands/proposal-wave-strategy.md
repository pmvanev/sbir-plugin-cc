---
description: "Generate strategy brief and manage Wave 1 strategy checkpoint"
argument-hint: "[approve|revise|skip] - Optional subcommand for checkpoint action"
---

# /proposal wave strategy

Generate strategy brief and manage Wave 1 strategy checkpoint.

## Usage

```
/proposal wave strategy              # Generate strategy brief
/proposal wave strategy approve      # Approve and unlock Wave 2
/proposal wave strategy revise       # Revise with feedback
/proposal wave strategy skip         # Skip checkpoint (records skip)
```

## Prerequisites

- Compliance matrix generated (run `/proposal compliance` first)
- Go/No-Go decision is "go"
- Current wave is 1 (Wave 1 active)

## Strategy Brief Sections

The generated brief covers:

1. **Technical Approach** -- Approach addressing solicitation requirements
2. **TRL** -- Technology Readiness Level assessment and progression plan
3. **Teaming** -- Teaming strategy to address capability gaps
4. **Phase III** -- Commercialization pathway and transition plan
5. **Budget** -- Budget allocation across requirements
6. **Risks** -- Risk assessment from compliance items and gaps

## TPOC Integration

If TPOC answers have been ingested, the brief integrates TPOC insights into relevant sections. If TPOC answers are not yet available, the brief notes their absence and proceeds with solicitation and corpus data alone.

## Strategy Checkpoint

Strategy alignment is a human checkpoint with three options:

- **approve** -- Records approval in proposal state and unlocks Wave 2 (PES-enforced)
- **revise** -- Accepts feedback, regenerates the brief incorporating changes, and presents for re-review
- **skip** -- Records skip decision and allows proceeding (with PES audit)

## Implementation

This command invokes `StrategyService` (driving port):
- `generate_brief()` -- Builds brief from compliance matrix and optional TPOC data
- `approve_brief()` -- Records approval and unlocks Wave 2
- `revise_brief()` -- Regenerates brief with user feedback

## Agent Invocation

@sbir-strategist

Generate or update the strategy brief from compliance matrix and TPOC data, and manage the strategy checkpoint.
