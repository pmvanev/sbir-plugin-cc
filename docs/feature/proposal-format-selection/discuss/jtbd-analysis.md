# JTBD Analysis: Proposal Format Selection

## Job Classification

- **Job type**: Brownfield (extending existing guided proposal setup flow)
- **Entry point**: DISCUSS wave (requirements for a new decision point)
- **Complexity**: Lightweight -- single decision point added to existing `/proposal new` flow

## Job Story

**When** I am setting up a new SBIR proposal and the guided setup process is collecting my preferences,
**I want to** declare whether I will produce my final proposal in LaTeX or DOCX,
**so I can** ensure the entire downstream pipeline (outlining, drafting, formatting, assembly) is tailored to my chosen output medium from the start.

### Functional Job

Select the proposal output format (LaTeX or DOCX) during proposal initialization so that downstream agents operate consistently with that choice.

### Emotional Job

Feel confident that the system understands my tooling preference and will not surprise me with incompatible output at Wave 5/6. Avoid the anxiety of discovering late in the process that content was structured for the wrong medium.

### Social Job

Be seen as a prepared, tooling-savvy proposal author who made deliberate infrastructure choices early rather than scrambling at formatting time.

## Forces Analysis

### Demand-Generating

- **Push**: Currently, the formatter agent defers output medium selection to Wave 6. By that point, the writer has already drafted content across Waves 3-4 without knowing whether it targets LaTeX or DOCX. This creates rework risk -- LaTeX proposals need different figure handling, cross-reference patterns, and section structure than DOCX proposals. Users who prefer LaTeX discover this mismatch late.
- **Pull**: A single explicit choice during `/proposal new` means every downstream agent -- writer, reviewer, formatter -- knows the target format from day one. LaTeX users get LaTeX-aware outlining. DOCX users get DOCX-compatible structures. No rework at Wave 6.

### Demand-Reducing

- **Anxiety**: "What if I pick the wrong format early? Can I change it later?" Users may worry about being locked in. The system should allow changing format preference, though late changes may require rework.
- **Habit**: Current users have never been asked this question during setup. Adding a new prompt to the guided flow changes the muscle memory of `/proposal new`. Keep it minimal -- one question, sensible default.

### Assessment

- **Switch likelihood**: High -- this is a small addition to an existing flow, not a paradigm shift.
- **Key blocker**: Anxiety about lock-in. Mitigate by making the choice changeable (with a warning about rework).
- **Key enabler**: Push from late-stage formatting rework pain.
- **Design implication**: Add a single format selection step to the guided proposal setup. Persist choice in `proposal-state.json`. Make it changeable via a command, but warn about downstream impact.

## Outcome Statements

1. Minimize the likelihood that the chosen output format is incompatible with the user's tooling environment
2. Minimize the time spent reworking drafted content due to a late format decision
3. Minimize the number of steps added to the proposal setup flow for this choice

## 8-Step Job Map (Scoped to Format Selection)

| Step | In Context | Discovery Finding |
|------|-----------|-------------------|
| 1. Define | User decides to start a new proposal | Format preference already known by user before they start |
| 2. Locate | User has solicitation file ready | Some solicitations specify submission format (PDF from LaTeX, or .docx upload) |
| 3. Prepare | `/proposal new` parses solicitation | System could detect format hints from solicitation requirements |
| 4. Confirm | User reviews parsed metadata at Go/No-Go | Format selection should happen here -- after parsing, before Go/No-Go, so it is part of the proposal profile |
| 5. Execute | User selects LaTeX or DOCX | Simple choice with clear explanation of implications |
| 6. Monitor | Downstream agents reference the format | State field `output_format` consulted by writer, formatter |
| 7. Modify | User changes mind mid-proposal | Allow change via command, warn about rework |
| 8. Conclude | Formatter assembles in chosen format | Wave 6 uses the persisted format, no last-minute question |

## Integration Points

- **proposal-state.json**: New `output_format` field (values: `"latex"`, `"docx"`)
- **sbir-orchestrator.md**: Guided setup flow asks format question during `/proposal new`
- **sbir-formatter.md**: Reads `output_format` from state instead of asking at Wave 6
- **sbir-writer.md**: May adjust content structure hints based on target format
- **proposal-state-schema.json**: Schema extended with `output_format` property
