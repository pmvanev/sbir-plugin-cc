# Journey: Proposal Format Selection

## Journey Flow

```
[Trigger: /proposal new]
    |
    v
[Step 1: Parse Solicitation]
    |  Feels: Expectant -- "Let's see if this topic fits"
    |  Artifacts: ${topic_id}, ${agency}, ${deadline}
    v
[Step 2: Corpus Search + Fit Scoring]
    |  Feels: Curious -- "How well do we match?"
    |  Artifacts: ${fit_scores}, ${corpus_matches}
    v
[Step 3: Format Selection]  <-- NEW STEP
    |  Feels: Decisive -- "I know my tooling"
    |  Artifacts: ${output_format}
    v
[Step 4: Go/No-Go Checkpoint]
    |  Feels: Deliberate -- "Is this worth pursuing?"
    |  Artifacts: ${go_no_go_decision}
    v
[Done: Wave 0 complete, format persisted]
    Feels: Confident -- "Pipeline knows my preferences"
```

## Emotional Arc

- **Start** (Parse): Expectant, slightly anxious about topic fit
- **Middle** (Format Selection): Brief, decisive -- this is a quick, confident choice
- **End** (Go/No-Go): Confident that the system is configured correctly for the full lifecycle

### Transition Design

The format selection step must feel lightweight -- it should not interrupt the flow's momentum between fit scoring and the Go/No-Go decision. One question, two clear options, sensible default. The user should spend less than 10 seconds on this step.

## TUI Mockup: Format Selection Step

### Happy Path -- User Selects LaTeX

```
+-- Step 3: Output Format Selection -----------------------------------+
|                                                                       |
|  Proposal output format                                               |
|                                                                       |
|  Choose how the final proposal will be produced:                      |
|                                                                       |
|    (1) LaTeX  -- Compile to PDF via LaTeX. Best for complex           |
|                  equations, precise formatting control, and            |
|                  agencies that accept PDF uploads.                     |
|                                                                       |
|    (2) DOCX   -- Microsoft Word format. Best for agencies             |
|                  requiring .docx uploads or collaborative              |
|                  editing with non-technical team members.              |
|                                                                       |
|  Default: docx                                                        |
|                                                                       |
|  Your choice [1/2]: 1                                                 |
|                                                                       |
|  Output format set to: LaTeX                                          |
|  (Change later with /proposal config format <latex|docx>)             |
|                                                                       |
+-----------------------------------------------------------------------+
```

### Happy Path -- User Accepts Default (DOCX)

```
+-- Step 3: Output Format Selection -----------------------------------+
|                                                                       |
|  Proposal output format                                               |
|                                                                       |
|  Choose how the final proposal will be produced:                      |
|                                                                       |
|    (1) LaTeX  -- Compile to PDF via LaTeX.                            |
|    (2) DOCX   -- Microsoft Word format.                               |
|                                                                       |
|  Default: docx                                                        |
|                                                                       |
|  Your choice [1/2]: <Enter>                                           |
|                                                                       |
|  Output format set to: DOCX (default)                                 |
|  (Change later with /proposal config format <latex|docx>)             |
|                                                                       |
+-----------------------------------------------------------------------+
```

### Edge Case -- Solicitation Specifies Format

```
+-- Step 3: Output Format Selection -----------------------------------+
|                                                                       |
|  Proposal output format                                               |
|                                                                       |
|  NOTE: Solicitation AF243-001 requires submission as PDF.             |
|  LaTeX is recommended for PDF-native output.                          |
|                                                                       |
|    (1) LaTeX  -- Compile to PDF via LaTeX. (recommended)              |
|    (2) DOCX   -- Microsoft Word, export to PDF.                       |
|                                                                       |
|  Your choice [1/2]: _                                                 |
|                                                                       |
+-----------------------------------------------------------------------+
```

## TUI Mockup: Mid-Proposal Format Change

```
+-- /proposal config format latex -------------------------------------+
|                                                                       |
|  WARNING: Changing output format mid-proposal                         |
|                                                                       |
|  Current format: DOCX                                                 |
|  Requested format: LaTeX                                              |
|  Current wave: 4 (Drafting)                                           |
|                                                                       |
|  Changing format after drafting has begun may require rework:          |
|  - Section structures may need adjustment                             |
|  - Figure references may need updating                                |
|  - Cross-references will be re-validated at Wave 6                    |
|                                                                       |
|  Proceed? [y/N]: _                                                    |
|                                                                       |
+-----------------------------------------------------------------------+
```

## TUI Mockup: Status Dashboard Shows Format

```
SBIR Proposal Status
====================
Topic:    AF243-001 -- Compact Directed Energy for Maritime UAS Defense
Agency:   Air Force
Phase:    I
Deadline: 2026-04-15 (29 days)
Format:   LaTeX                          <-- NEW FIELD
Go/No-Go: go

Wave Progress:
  [x] Wave 0 -- Intelligence & Fit (completed 2026-03-17)
  [>] Wave 1 -- Requirements & Strategy (active)
  ...
```
