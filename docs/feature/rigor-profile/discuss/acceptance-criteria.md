# Acceptance Criteria -- Rigor Profile

Feature: rigor-profile
Date: 2026-03-23
Phase: 3 -- Requirements Crafting

All scenarios use Given-When-Then format. Traced to user stories and JTBD jobs.
Organized by user story for traceability.

---

## RP-001: View and Compare Rigor Profiles

**Jobs**: J6 (Understand What Rigor Changes)

### Scenario 1: Summary comparison displays all profiles

```gherkin
Given Dr. Elena Vasquez has an active proposal "AF243-001" at "standard" rigor
When she runs "/proposal rigor show"
Then a comparison table displays four profiles:
  | profile    | quality  | cost_per_wave | review_passes | critique_iterations |
  | lean       | Basic    | $2-5          | 1             | 0                   |
  | standard   | Balanced | $8-15         | 2             | 2                   |
  | thorough   | Deep     | $20-35        | 2             | 3                   |
  | exhaustive | Maximum  | $40-60        | 3             | 4                   |
And the header shows "Active: standard"
And the output includes "Run /proposal rigor show <profile> for full detail."
```

### Scenario 2: Detail view shows model tier per agent role

```gherkin
Given Dr. Elena Vasquez has an active proposal "AF243-001"
When she runs "/proposal rigor show thorough"
Then the detail view displays:
  | agent_role    | model_tier |
  | Strategist    | strongest  |
  | Writer        | strongest  |
  | Reviewer      | strongest  |
  | Researcher    | standard   |
  | Compliance    | strongest  |
  | Visual Assets | strongest  |
  | Formatter     | standard   |
And review depth is shown as "2 passes (structural + evaluator scoring)"
And critique loops are shown as "Enabled, max 3 iterations"
And estimated cost is shown as "$20-35 per wave"
```

### Scenario 3: Profiles viewable without active proposal

```gherkin
Given Marcus Chen has no active proposal in the workspace
When he runs "/proposal rigor show"
Then the comparison table is displayed with all four profiles
And no "Active:" line appears in the header
```

---

## RP-002: Select Rigor Profile for a Proposal

**Jobs**: J1 (Right-Size Quality), J2 (Control Costs)

### Scenario 1: Set thorough profile with diff display

```gherkin
Given Dr. Elena Vasquez has an active proposal "AF243-001" at "standard" rigor
When she runs "/proposal rigor set thorough"
Then rigor-profile.json is updated with profile "thorough"
And the output displays a diff:
  | setting          | from     | to       |
  | Writer model     | standard | strongest |
  | Reviewer model   | standard | strongest |
  | Strategist model | standard | strongest |
  | Compliance model | standard | strongest |
  | Visual assets    | standard | strongest |
  | Critique loops   | 2 iter   | 3 iter   |
And the output states "Existing artifacts are preserved -- no re-run required."
And a history entry is appended with from "standard", to "thorough", timestamp, and wave number
```

### Scenario 2: Set lean profile for screening

```gherkin
Given Marcus Chen has an active proposal "N244-015" at "standard" rigor
When he runs "/proposal rigor set lean"
Then rigor-profile.json is updated with profile "lean"
And the output shows all agents at "basic" model tier
And review passes shown as "1 (structural only)"
And critique loops shown as "Skipped"
And estimated cost shown as "$2-5 per wave"
```

### Scenario 3: Invalid profile name

```gherkin
Given Dr. Elena Vasquez has an active proposal "AF243-001"
When she runs "/proposal rigor set ultra"
Then the output shows "Error: Unknown rigor profile 'ultra'."
And the output lists "Available profiles: lean, standard, thorough, exhaustive"
And the output suggests "Run /proposal rigor show to compare profiles."
And rigor-profile.json is not modified
```

### Scenario 4: No active proposal

```gherkin
Given no proposal is currently active in the workspace
When the user runs "/proposal rigor set thorough"
Then the output shows "Error: No active proposal."
And the output suggests "Start a proposal with /proposal new <solicitation-file>"
And the output suggests "or switch to an existing one with /proposal switch <topic-id>."
```

### Scenario 5: Same profile is no-op

```gherkin
Given Dr. Elena Vasquez has proposal "AF243-001" at "thorough" rigor
When she runs "/proposal rigor set thorough"
Then the output shows "Rigor is already set to 'thorough' for AF243-001."
And the output shows "No changes made."
And rigor-profile.json is not modified
And no history entry is appended
```

---

## RP-003: Contextual Rigor Suggestion at Proposal Creation

**Jobs**: J6 (Understand), J1 (Right-Size), J2 (Control Costs)

### Scenario 1: High-value proposal gets thorough suggestion

```gherkin
Given Dr. Elena Vasquez creates a new proposal from solicitation "AF243-001"
When the proposal is created with fit score 85 and contract value $1.7M Phase II
Then the output includes "Rigor Profile: standard (default)"
And the output includes a tip: "This proposal has a high fit score and Phase II value."
And the tip suggests "/proposal rigor set thorough for maximum quality"
And the tip includes "/proposal rigor show to compare profiles"
And rigor-profile.json is created with profile "standard" and empty history
```

### Scenario 2: Moderate-value proposal gets lean suggestion

```gherkin
Given Marcus Chen creates a new proposal from solicitation "N244-015"
When the proposal is created with fit score 64 and contract value $250K Phase I
Then the output includes "Rigor Profile: standard (default)"
And the output includes a tip suggesting "lean" for exploratory screening
And the tip includes cost range "$2-5/wave"
```

### Scenario 3: Mid-range proposal gets no suggestion

```gherkin
Given Phil Santos creates a new proposal from solicitation "DA244-007"
When the proposal is created with fit score 75 and contract value $250K Phase I
Then the output includes "Rigor Profile: standard (default)"
And no rigor upgrade or downgrade tip is shown
```

### Scenario 4: Default rigor always standard regardless of metadata

```gherkin
Given Dr. Elena Vasquez creates a new proposal from solicitation "AF243-001"
When the proposal is created with fit score 95 and contract value $2.5M Phase II
Then rigor-profile.json is created with profile "standard"
And the actual rigor is "standard" despite the thorough suggestion
And the suggestion does not auto-apply "thorough"
```

---

## RP-004: Agent Model Resolution from Rigor Profile

**Jobs**: J1 (Right-Size Quality), J2 (Control Costs)
**Highest-priority outcome**: #12 (score 16.5)

### Scenario 1: Writer resolves model from thorough profile

```gherkin
Given Dr. Elena Vasquez has proposal "AF243-001" at "thorough" rigor
And the "thorough" profile defines writer role as "strongest" model tier
When the writer agent is invoked during Wave 4 drafting
Then the writer uses the "strongest" model tier
And the writer does not use any hardcoded model from its own frontmatter
```

### Scenario 2: Reviewer uses configured review pass count

```gherkin
Given Dr. Elena Vasquez has proposal "AF243-001" at "thorough" rigor
And the "thorough" profile defines 2 review passes
When the reviewer agent is invoked during Wave 4
Then the reviewer executes 2 review passes
And the first pass is structural review
And the second pass is evaluator scoring
```

### Scenario 3: Lean rigor reduces all agents to basic

```gherkin
Given Marcus Chen has proposal "N244-015" at "lean" rigor
And the "lean" profile defines all agent roles as "basic" model tier
When any agent is invoked during Wave 0
Then the agent uses "basic" model tier
And review is limited to 1 structural pass
And critique loops are skipped (0 iterations)
```

### Scenario 4: Visual assets agent respects critique iteration cap

```gherkin
Given Dr. Elena Vasquez has proposal "AF243-001" at "thorough" rigor
And the "thorough" profile defines critique_max_iterations as 3
When the visual-assets agent runs a critique-refine loop on Figure 3
Then the critique loop runs at most 3 iterations
And if the figure passes critique before iteration 3, the loop exits early
```

### Scenario 5: Missing rigor-profile.json defaults to standard

```gherkin
Given Phil Santos opens a proposal created before the rigor feature existed
And no rigor-profile.json exists in ".sbir/proposals/da244-007/"
When any agent is invoked
Then the agent resolves model tier as if "standard" profile is active
And no error message is displayed to Phil
And the wave executes normally
```

### @property Scenario: Rigor enforcement consistency

```gherkin
@property
Given any proposal has a rigor profile set
Then every agent invocation for that proposal resolves its model tier from rigor-profile.json
And no agent invocation uses a hardcoded model that contradicts the active profile
And the resolution chain is: active proposal -> rigor-profile.json -> rigor-profiles.json -> model tier
```

---

## RP-005: Rigor Display in Wave Execution

**Jobs**: J1 (Right-Size Quality)

### Scenario 1: Wave header shows rigor level

```gherkin
Given Dr. Elena Vasquez has proposal "AF243-001" at "thorough" rigor
When she runs Wave 1 strategy
Then the wave header line includes "Rigor: thorough"
```

### Scenario 2: Per-step output shows model tier

```gherkin
Given Dr. Elena Vasquez has proposal "AF243-001" at "thorough" rigor
When she runs Wave 1 strategy with 3 steps
Then step 1 (Topic analysis) shows "Model: strongest"
And step 2 (Strategy brief) shows "Model: strongest"
And step 3 (Compliance pre-check) shows "Model: strongest"
And no step shows a specific model name like "Opus" or "Sonnet"
```

### Scenario 3: Lean rigor visibly lighter

```gherkin
Given Marcus Chen has proposal "N244-015" at "lean" rigor
When he runs Wave 0 topic analysis
Then the wave header shows "Rigor: lean"
And steps show "Model: basic"
And review depth shows "1 pass (structural)"
```

---

## RP-006: Rigor in Proposal Status and Portfolio View

**Jobs**: J4 (Multi-Proposal Management)

### Scenario 1: Portfolio shows rigor per proposal

```gherkin
Given the workspace contains three proposals:
  | topic_id  | name                    | rigor    | fit_score | contract |
  | AF243-001 | Compact Directed Energy | thorough | 85        | $1.7M    |
  | N244-012  | AUV Navigation          | standard | 72        | $250K    |
  | DA244-003 | Sensor Fusion           | lean     | 58        | $250K    |
And "AF243-001" is the active proposal
When Dr. Elena Vasquez runs "/proposal status"
Then the active proposal line shows "Rigor: thorough" alongside "Fit: 85" and "$1.7M"
And "N244-012" in the other proposals list shows "standard"
And "DA244-003" in the other proposals list shows "lean"
```

### Scenario 2: Switch loads target proposal rigor

```gherkin
Given Dr. Elena Vasquez has "AF243-001" active at "thorough" rigor
And proposal "N244-012" exists at "standard" rigor
When she runs "/proposal switch n244-012"
Then the active proposal becomes "N244-012"
And the displayed rigor is "standard"
And subsequent wave commands use "standard" rigor settings
And "AF243-001" retains "thorough" rigor in its rigor-profile.json
```

### Scenario 3: Single proposal omits portfolio section

```gherkin
Given Phil Santos has only one proposal "DA244-007" at "standard" rigor
When he runs "/proposal status"
Then the status shows "Rigor: standard" for the active proposal
And no "Other proposals" section is displayed
```

---

## RP-007: Adjust Rigor Mid-Proposal

**Jobs**: J4 (Multi-Proposal), J2 (Control Costs)

### Scenario 1: Mid-proposal upgrade preserves existing artifacts

```gherkin
Given Dr. Elena Vasquez has proposal "DA244-003" at "lean" rigor
And Waves 0, 1, and 2 have been completed at "lean" rigor
And the proposal is currently on Wave 3
When she runs "/proposal rigor set standard"
Then the rigor is updated to "standard"
And the output states "Waves 0-2 retain their existing artifacts (produced at lean)."
And the output states "Wave 3+ will use standard settings."
And no automatic re-run of Waves 0-2 occurs
```

### Scenario 2: History entry records wave number

```gherkin
Given Dr. Elena Vasquez has proposal "DA244-003" at "lean" rigor
And the proposal is currently on Wave 3
When she runs "/proposal rigor set standard"
Then rigor-profile.json history contains an entry with:
  | field    | value    |
  | from     | lean     |
  | to       | standard |
  | wave     | 3        |
And the entry includes a timestamp
```

### Scenario 3: Re-processing guidance offered

```gherkin
Given Dr. Elena Vasquez has proposal "DA244-003" at "lean" rigor
And Waves 0-2 have been completed
When she runs "/proposal rigor set standard"
Then the output includes "Note: Earlier waves were produced at lean rigor."
And the output suggests "/proposal iterate <section> to re-process specific sections at the new rigor level if needed."
```

---

## RP-008: Rigor Summary in Proposal Debrief

**Jobs**: J1 (Right-Size Quality)

### Scenario 1: Debrief with consistent profile

```gherkin
Given Dr. Elena Vasquez has completed all 10 waves for "AF243-001" at "thorough" rigor
And the proposal had 24 total review cycles across 10 sections
And 8 figures went through critique loops averaging 3 iterations each
When she runs "/proposal debrief"
Then the debrief includes a "Rigor Summary" section
And the summary shows "Profile: thorough (used throughout)"
And the summary shows "Review cycles: 24 total (avg 2.4/section)"
And the summary shows "Critique loops: 8 figures, 3 iterations avg"
And the summary shows "Profile changes: None"
```

### Scenario 2: Debrief with mid-proposal rigor change

```gherkin
Given Dr. Elena Vasquez has completed proposal "DA244-003"
And the rigor was changed from "lean" to "standard" at Wave 3 on 2026-04-15
When she runs "/proposal debrief"
Then the rigor summary shows "Profile: standard (changed from lean at Wave 3)"
And the change is listed as "lean -> standard at Wave 3 (2026-04-15)"
```

### Scenario 3: Debrief for lean-only screening

```gherkin
Given Marcus Chen has completed proposal "N244-015" at "lean" rigor throughout
And the proposal had 6 review cycles across 6 sections (1 each)
And no critique loops were executed
When he runs "/proposal debrief"
Then the rigor summary shows "Profile: lean (used throughout)"
And the summary shows "Review cycles: 6 total (avg 1.0/section)"
And the summary shows "Critique loops: 0 (skipped at lean)"
```
