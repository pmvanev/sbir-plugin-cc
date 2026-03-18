---
description: "Generate and score candidate technical approaches for a solicitation, then select the best fit for your company"
argument-hint: "[--revise]"
---

# /proposal shape

Generate and evaluate candidate technical approaches for the active solicitation topic. Scores each approach against your company's personnel, past performance, TRL, solicitation fit, and commercialization potential. Produces an approach brief consumed by Wave 1.

## Usage

```
/proposal shape
/proposal shape --revise
```

## Flags

| Flag | Description |
|------|-------------|
| `--revise` | Re-evaluate approaches with updated inputs (new TPOC insights, revised company profile, or manual overrides). Requires a prior approach selection. |

## Flow

1. **Deep read** -- Read full solicitation text, extract objectives, evaluation criteria, constraints
2. **Generate** -- Produce 3-5 technically distinct candidate approaches (forward mapping, reverse mapping, prior art)
3. **Score** -- Five-dimension scoring: personnel alignment, past performance, technical readiness, solicitation fit, commercialization
4. **Converge** -- Recommend top approach with rationale, runner-up analysis, discrimination angles, risks, Phase III assessment
5. **Checkpoint** -- Present recommendation for human review: approve, revise, explore, restart, or quit
6. **Output** -- Write `approach-brief.md` to `./artifacts/wave-0-intelligence/`

## Revision Flow (--revise)

1. Read existing approach brief
2. Re-read company profile and proposal state for updates
3. Accept user's revision notes (TPOC insights, new constraints, teaming changes)
4. Re-score all approaches with updated inputs
5. Present updated matrix and recommendation
6. Append revision entry to approach-brief.md history

## Prerequisites

- Go decision required: proposal state must have `go_no_go: "go"` (run `/proposal new` first)
- Company profile required: `~/.sbir/company-profile.json` must exist (run `/company-profile setup` first)
- For `--revise`: a prior approach selection must exist (`approach-brief.md` on disk)

## Agent Invocation

@sbir-solution-shaper

Deep-read the solicitation for the active proposal topic. Generate 3-5 technically distinct candidate approaches using forward mapping, reverse mapping, and prior art awareness. Score each approach across 5 dimensions using the company profile. Converge on a recommendation with rationale, discrimination angles, risks, and Phase III assessment. Write approach-brief.md and present the checkpoint for human approval. If --revise flag is set, re-read inputs, accept user revision notes, re-score, and update the existing brief with revision history.
