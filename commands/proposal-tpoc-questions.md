# /proposal tpoc questions

Generate prioritized TPOC questions from solicitation ambiguities and strategic probes.

## Usage

```
/proposal tpoc questions
```

## Prerequisites

- Active proposal with Go/No-Go decision "go"
- Compliance matrix generated (run `/proposal compliance` first)

## Output

1. **Ambiguity questions** -- One question per flagged ambiguity in the compliance matrix
2. **Strategic probes** -- Standard questions to surface evaluation priorities and TPOC expectations
3. **Editable markdown** -- Written to `artifacts/wave-1-strategy/tpoc-questions.md`

Questions are ordered by strategic priority: ambiguities first, then strategic probes.

## After Generation

1. Edit `tpoc-questions.md` to add, remove, or reorder questions
2. Conduct the TPOC call
3. Run `/proposal tpoc ingest <notes-file>` to match answers

If the TPOC call does not happen, the pending state does not block proposal progress.

## Implementation

This command invokes `TpocService.generate_questions()` (driving port) which reads the `ComplianceMatrix` and produces a `TpocQuestionSet` domain model. The `MarkdownTpocAdapter` renders questions to an editable markdown file.
