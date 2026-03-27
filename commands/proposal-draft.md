---
description: "Draft a proposal section from the approved outline, compliance-traced and page-budgeted"
argument-hint: "<section> [--iterate]"
---

# /proposal draft [section]

Draft a specific proposal section from the approved outline. Each section is compliance-traced to the matrix, stays within page budget, and enters a human review loop.

## Usage

```
/proposal draft technical-approach
/proposal draft sow
/proposal draft key-personnel
/proposal draft facilities
/proposal draft past-performance
/proposal draft management
/proposal draft commercialization
/proposal draft risks
/proposal draft --iterate technical-approach
```

## Sections

| Section | Wave 4 Order | Typical Pages |
|---------|-------------|---------------|
| `technical-approach` | 1st (draft first) | 6-10 |
| `sow` | 2nd | 2-4 |
| `key-personnel` | 3rd | 2-3 |
| `facilities` | 4th | 1-2 |
| `past-performance` | 5th | 2-3 |
| `management` | 6th | 1-2 |
| `commercialization` | 7th | 2-4 |
| `risks` | 8th | 1-2 |

## Flags

| Flag | Description |
|------|-------------|
| `--iterate` | Submit the section for writer + reviewer iteration. Writer revises based on reviewer findings. Max 2 review cycles before human checkpoint. |

## Flow

1. **Style checkpoint** -- If `writing_style` is not set in proposal state, present available styles (Elements of Style, Agency Default, Academic, Conversational, Standard, Custom) with recommendations from quality discovery artifacts. User selects or skips. Choice recorded in state.
2. **Load inputs** -- Read approved outline from `./artifacts/wave-3-outline/proposal-outline.md`, discrimination table from `./artifacts/wave-3-outline/discrimination-table.md`, compliance matrix from `.sbir/compliance-matrix.json`
3. **Load exemplars** -- Pull corpus exemplars for tone and structure calibration
4. **Draft** -- Write the section addressing all mapped compliance items, within page budget, reinforcing discriminators, applying selected writing style
5. **Self-check** -- Run acronym audit, cross-reference check, jargon scan
6. **Write** -- Save to `./artifacts/wave-4-drafts/sections/{section-name}.md`
7. **Checkpoint** -- Present for human review: approve, revise, skip

## Iterate Flow (--iterate)

1. Submit section to sbir-reviewer for evaluator simulation
2. Reviewer produces scorecard at `./artifacts/wave-4-drafts/reviews/{section-name}-review.md`
3. Writer revises based on findings (preserves approved content)
4. Re-submit for second review if needed
5. After 2 cycles, escalate unresolved findings to human checkpoint

## Prerequisites

- Wave 3 complete: outline and discrimination table approved
- Compliance matrix generated
- Strategy brief available at `./artifacts/wave-1-strategy/strategy-brief.md`
- Company profile at `~/.sbir/company-profile.json`
- **Writing style selected** (or explicitly skipped): The writer will present a style checkpoint before the first section draft. Run `/sbir:proposal quality discover` beforehand for best recommendations. PES blocks drafting until style selection is complete.

## Agent Invocation

@sbir-writer

Draft the {section} section of the proposal. Read the approved outline and discrimination table from `./artifacts/wave-3-outline/`. Map compliance matrix items to this section. Draft within the page budget allocated in the outline. Reinforce discriminators. Run acronym and cross-reference audits. Write to `./artifacts/wave-4-drafts/sections/{section}.md`. Present checkpoint for human review.

If --iterate flag is set, after the initial draft or revision, dispatch to @sbir-reviewer for evaluator simulation and scoring. The reviewer writes findings to `./artifacts/wave-4-drafts/reviews/{section}-review.md`. Then revise based on findings and re-present.

SKILL_LOADING: Load `skills/writer/discrimination-table.md` and `skills/corpus-librarian/proposal-archive-reader.md` before drafting. Load `skills/reviewer/reviewer-persona-simulator.md` for self-check. If `writing_style` is set in `.sbir/proposal-state.json`, also load `skills/writer/{writing_style}.md` for prose style guidance.
