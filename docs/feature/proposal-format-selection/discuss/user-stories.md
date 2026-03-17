<!-- markdownlint-disable MD024 -->

# User Stories: Proposal Format Selection

All stories trace to the job story in `jtbd-analysis.md`:
"When I am setting up a new SBIR proposal, I want to declare whether I will produce my final proposal in LaTeX or DOCX, so I can ensure the downstream pipeline is tailored to my chosen output medium."

---

## US-PFS-001: Select Output Format During Proposal Setup

### Problem

Phil Santos is an engineer who writes 2-3 SBIR proposals per year, alternating between LaTeX (for proposals with heavy equations) and DOCX (for collaborative proposals with non-technical partners). He finds it frustrating that the current `/proposal new` flow does not ask about output format, causing the formatter agent at Wave 6 to ask belatedly -- by which point the writer has already produced content structured for an unknown medium. Phil has had to rework cross-references and figure formats after discovering the mismatch.

### Who

- Engineer | Setting up a new SBIR proposal | Wants the system configured for their preferred output tooling from the start

### Solution

During the `/proposal new` guided setup, after fit scoring and before the Go/No-Go checkpoint, the system prompts the user to select LaTeX or DOCX. The choice is persisted in `proposal-state.json` as `output_format` and consumed by all downstream agents.

### Domain Examples

#### 1: Happy Path -- Phil selects LaTeX for a directed-energy proposal

Phil Santos runs `/proposal new ./solicitations/AF243-001.pdf` for topic AF243-001 ("Compact Directed Energy for Maritime UAS Defense"). The solicitation is parsed, corpus is searched, fit is scored. The system then asks: "Choose output format: (1) LaTeX (2) DOCX. Default: docx." Phil selects 1. The state records `output_format: "latex"`. The Go/No-Go checkpoint follows immediately. When Phil reaches Wave 4 drafting, the writer agent knows to produce LaTeX-friendly content structures.

#### 2: Happy Path -- Elena accepts DOCX default for a collaborative proposal

Elena Rodriguez runs `/proposal new ./solicitations/N244-012.pdf` for topic N244-012 ("Autonomous Underwater Vehicle Navigation"). She is collaborating with a university partner who uses Word. When prompted for output format, Elena presses Enter to accept the default DOCX. The state records `output_format: "docx"`. The formatter at Wave 6 generates a .docx file without asking again.

#### 3: Edge Case -- Solicitation requires PDF submission

Phil Santos runs `/proposal new ./solicitations/DA245-003.pdf` for topic DA245-003 ("Portable Battlefield Communications Relay"). The solicitation contains the requirement "Technical volume must be submitted as PDF." The format selection prompt includes a note: "Solicitation requires PDF submission. LaTeX recommended for PDF-native output." Phil sees LaTeX marked as "(recommended)" and selects it.

#### 4: Error/Boundary -- Invalid input at format prompt

Phil Santos accidentally types "3" at the format selection prompt. The system re-prompts: "Invalid selection. Please enter 1 for LaTeX, 2 for DOCX, or press Enter for default (DOCX)." No state is written until a valid selection is made.

### UAT Scenarios (BDD)

#### Scenario: Select LaTeX during proposal setup

Given Phil Santos runs "/proposal new ./solicitations/AF243-001.pdf"
And the solicitation for topic AF243-001 has been parsed successfully
And fit scoring is complete
When the system prompts for output format selection
And Phil Santos selects "1" for LaTeX
Then the proposal state field "output_format" is set to "latex"
And the confirmation message shows "Output format set to: LaTeX"
And the setup continues to the Go/No-Go checkpoint

#### Scenario: Accept default DOCX by pressing Enter

Given Elena Rodriguez runs "/proposal new ./solicitations/N244-012.pdf"
And the solicitation for topic N244-012 has been parsed successfully
And fit scoring is complete
When the system prompts for output format selection
And Elena presses Enter without typing a selection
Then the proposal state field "output_format" is set to "docx"
And the confirmation message shows "Output format set to: DOCX (default)"

#### Scenario: Solicitation hints at PDF and system recommends LaTeX

Given the solicitation for topic DA245-003 contains the text "submit as PDF"
And Phil Santos runs "/proposal new ./solicitations/DA245-003.pdf"
When the system prompts for output format selection
Then the prompt includes "Solicitation requires PDF submission. LaTeX recommended."
And "LaTeX" is marked as "(recommended)"

#### Scenario: Invalid input re-prompts without error

Given Phil Santos is at the output format selection prompt
When Phil Santos types "3"
Then the system displays "Invalid selection. Please enter 1 for LaTeX, 2 for DOCX, or press Enter for default."
And the system re-prompts for output format selection
And no value is written to proposal state

#### Scenario: Output format visible in proposal status

Given Phil Santos has an active proposal for AF243-001 with output_format "latex"
When Phil Santos runs "/proposal status"
Then the status dashboard includes a line "Format: LaTeX"

### Acceptance Criteria

- [ ] Format selection prompt appears during `/proposal new` after fit scoring and before Go/No-Go
- [ ] User can select LaTeX (1) or DOCX (2), or press Enter for default (DOCX)
- [ ] Selected format is persisted as `output_format` in `.sbir/proposal-state.json`
- [ ] Invalid input re-prompts without writing partial state
- [ ] Solicitation PDF-submission hints surface a LaTeX recommendation
- [ ] `/proposal status` displays the chosen output format

### Technical Notes

- New `output_format` field in `proposal-state-schema.json` (enum: `"latex"`, `"docx"`, default: `"docx"`)
- `ProposalCreationService._build_initial_state()` must include `output_format` in the state dict
- The format selection is an interactive prompt managed by the orchestrator agent, not PES Python code
- Solicitation format hints depend on compliance-sheriff extraction of FORMAT requirements (may not always be available at parse time)

### Dependencies

- Depends on existing `/proposal new` flow (complete, working)
- Depends on `proposal-state-schema.json` accepting the new field
- No dependency on downstream agent changes (those are separate stories)

---

## US-PFS-002: Change Output Format Mid-Proposal

### Problem

Phil Santos is an engineer who initially chose DOCX for proposal AF243-001 but realized after reviewing the solicitation's equation-heavy requirements in Wave 1 that LaTeX would be a better fit. He finds it concerning that there is no way to change the format choice without manually editing the state file. He wants a supported command that changes the format with appropriate warnings about potential rework.

### Who

- Engineer | Mid-proposal, reconsidering format choice | Wants to correct an early decision without losing work

### Solution

A `/proposal config format <latex|docx>` command that updates the `output_format` field in proposal state. If drafting has begun (Wave 3+), the command warns about potential rework and requires explicit confirmation.

### Domain Examples

#### 1: Happy Path -- Phil changes format in Wave 1 (no rework risk)

Phil Santos has an active proposal for AF243-001 in Wave 1. He runs `/proposal config format latex`. The system updates `output_format` to `"latex"` and confirms: "Output format changed to: LaTeX." No warning needed because no draft content exists yet.

#### 2: Edge Case -- Phil changes format in Wave 4 (rework risk)

Phil Santos has an active proposal for AF243-001 in Wave 4 with the technical volume in "drafting" status. He runs `/proposal config format latex`. The system warns: "Changing format after drafting has begun may require rework. Section structures may need adjustment. Proceed? [y/N]." Phil types "y" and the format is updated. The system notes: "Format changed. Re-validate content structure at Wave 6."

#### 3: Error -- Phil tries to set format to an invalid value

Phil Santos runs `/proposal config format pdf`. The system responds: "Invalid format 'pdf'. Valid options: latex, docx." No state change occurs.

### UAT Scenarios (BDD)

#### Scenario: Change format before drafting begins

Given Phil Santos has an active proposal for AF243-001 with output_format "docx"
And the current wave is 1
When Phil Santos runs "/proposal config format latex"
Then the proposal state field "output_format" is updated to "latex"
And the confirmation message shows "Output format changed to: LaTeX"
And no rework warning is displayed

#### Scenario: Change format after drafting with rework warning

Given Phil Santos has an active proposal for AF243-001 with output_format "docx"
And the current wave is 4
And the technical volume status is "drafting"
When Phil Santos runs "/proposal config format latex"
Then the system displays a warning about potential rework
And the system asks "Proceed? [y/N]"
When Phil Santos confirms with "y"
Then the proposal state field "output_format" is updated to "latex"

#### Scenario: Decline format change after seeing rework warning

Given Phil Santos has an active proposal for AF243-001 with output_format "docx"
And the current wave is 4
When Phil Santos runs "/proposal config format latex"
And the system displays a rework warning
When Phil Santos declines with "N"
Then the proposal state field "output_format" remains "docx"

#### Scenario: Invalid format value rejected

Given Phil Santos has an active proposal for AF243-001
When Phil Santos runs "/proposal config format pdf"
Then the system displays "Invalid format 'pdf'. Valid options: latex, docx"
And the proposal state is not modified

### Acceptance Criteria

- [ ] `/proposal config format <latex|docx>` updates `output_format` in proposal state
- [ ] Changes before Wave 3 proceed without warning
- [ ] Changes at Wave 3+ display rework warning and require confirmation
- [ ] Invalid format values are rejected with helpful error message
- [ ] Declining confirmation leaves state unchanged

### Technical Notes

- New command: `/proposal config format` -- routed by orchestrator
- Rework warning threshold: Wave 3 (Outline) and above
- The orchestrator checks `current_wave` to determine whether to warn
- No automatic content migration -- rework is manual, flagged at Wave 6 formatting

### Dependencies

- Depends on US-PFS-001 (output_format field exists in state)
- No dependency on downstream agent changes

---

## Definition of Ready Validation

### US-PFS-001: Select Output Format During Proposal Setup

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | Phil Santos persona, specific pain (late format discovery at Wave 6), domain language (output format, LaTeX, DOCX) |
| User/persona identified | PASS | Engineer writing 2-3 SBIR proposals/year, alternating LaTeX and DOCX |
| 3+ domain examples | PASS | 4 examples: LaTeX selection, DOCX default, solicitation hint, invalid input |
| UAT scenarios (3-7) | PASS | 5 scenarios covering happy path, default, hint, error, and status display |
| AC derived from UAT | PASS | 6 AC items, each traceable to a scenario |
| Right-sized | PASS | ~2 days effort, 5 scenarios, single demo-able feature |
| Technical notes | PASS | Schema change, state builder change, interactive prompt ownership noted |
| Dependencies tracked | PASS | Existing `/proposal new` flow (complete), schema change (internal) |

### DoR Status: PASSED

### US-PFS-002: Change Output Format Mid-Proposal

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | Phil Santos persona, specific pain (no supported way to change format choice), domain language |
| User/persona identified | PASS | Engineer mid-proposal reconsidering format choice |
| 3+ domain examples | PASS | 3 examples: pre-draft change, post-draft change with warning, invalid value |
| UAT scenarios (3-7) | PASS | 4 scenarios covering clean change, warned change, declined change, invalid value |
| AC derived from UAT | PASS | 5 AC items, each traceable to a scenario |
| Right-sized | PASS | ~1 day effort, 4 scenarios, single command |
| Technical notes | PASS | New command routing, wave threshold for warning, manual rework noted |
| Dependencies tracked | PASS | Depends on US-PFS-001 (tracked) |

### DoR Status: PASSED
