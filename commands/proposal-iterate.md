---
description: "Submit a drafted section for writer-reviewer iteration loop (max 2 cycles)"
argument-hint: "<section>"
---

# /proposal iterate [section]

Submit a drafted section for the writer-reviewer iteration loop. The reviewer scores the section against evaluation criteria, produces findings, and the writer revises. Max 2 review cycles before escalating unresolved findings to human checkpoint.

## Usage

```
/proposal iterate technical-approach
/proposal iterate sow
/proposal iterate key-personnel
```

## Flow

1. **Review** -- @sbir-reviewer scores the section against solicitation evaluation criteria using the evaluator persona
2. **Findings** -- Reviewer writes scorecard to `./artifacts/wave-4-drafts/reviews/{section}-review.md`
3. **Revise** -- @sbir-writer addresses findings (preserves approved content, updates only flagged areas)
4. **Re-review** -- If issues remain, reviewer scores again (cycle 2)
5. **Escalate** -- After 2 cycles, unresolved findings go to human checkpoint for disposition

## Prerequisites

- Section drafted at `./artifacts/wave-4-drafts/sections/{section}.md`
- Compliance matrix at `.sbir/compliance-matrix.json`
- Solicitation evaluation criteria available

## Agent Invocation

@sbir-reviewer

Review the {section} section at `./artifacts/wave-4-drafts/sections/{section}.md`. Construct the evaluator persona from solicitation evaluation criteria. Score the section, identify strengths and weaknesses, check against debrief weakness profile, run jargon and cross-reference audits. Write scorecard to `./artifacts/wave-4-drafts/reviews/{section}-review.md`. If `writing_style` is set in `.sbir/proposal-state.json`, also evaluate prose against the loaded style skill.

After review, dispatch to @sbir-writer to revise based on findings. Writer preserves approved content and updates only flagged areas. Re-present for human review.

SKILL_LOADING: Load `skills/reviewer/reviewer-persona-simulator.md` and `skills/corpus-librarian/win-loss-analyzer.md`. If `writing_style` is set, also load `skills/writer/{writing_style}.md`.
