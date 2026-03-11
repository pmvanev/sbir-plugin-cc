---
description: "Ingest TPOC call notes and match answers to original questions with delta analysis"
argument-hint: "<notes-file-path> - Path to TPOC call notes file"
---

# /proposal tpoc ingest

Ingest TPOC call notes, match answers to original questions, and generate delta analysis.

## Usage

```
/proposal tpoc ingest <notes-file-path>
```

## Prerequisites

- TPOC questions generated (run `/proposal tpoc questions` first)
- Notes file exists at the specified path (text, markdown, or Word)

## Input Format

Structured notes with answers keyed by question number:

```
TPOC Call Notes

Q1 Answer: Compact means less than 50 lbs.
Q2 Answer: Phase III target is PMS 501.
```

## Output

1. **Answer matching** -- Each answer matched to its original question by number
2. **Unanswered marking** -- Questions without answers marked as unanswered
3. **Delta analysis** -- Comparison of TPOC answers against solicitation requirements
4. **Compliance updates** -- Clarifications applied to the compliance matrix

## Partial Notes

If the call was short and not all questions were covered, the ingestion handles partial notes. Answered questions get matched; unanswered questions are marked. Delta analysis covers only answered questions.

## Implementation

This command invokes `TpocIngestionService.ingest_notes()` (driving port) which parses structured notes, matches answers to the `TpocQuestionSet`, builds a `DeltaAnalysis` comparing answers to `ComplianceMatrix` requirements, and generates compliance update notes.

## Agent Invocation

@sbir-tpoc-analyst

Parse the TPOC call notes, match answers to questions, generate delta analysis, and update compliance matrix.
