<!-- markdownlint-disable MD024 -->

# User Stories -- Rigor Profile

Feature: rigor-profile
Date: 2026-03-23
Phase: 3 -- Requirements Crafting

All stories trace to JTBD job stories from `jtbd-job-stories.md`.
MVP vs Phase 2 scoping from `jtbd-opportunity-scores.md`.

---

## MVP Stories (Jobs 1 + 2 + 6)

---

## RP-001: View and Compare Rigor Profiles

### Problem

Dr. Elena Vasquez is a principal investigator at Meridian Defense who manages 2-3 simultaneous SBIR proposals of varying strategic importance. She finds it impossible to make an informed quality/cost tradeoff because the plugin treats every proposal identically -- all 18 agents use the same model regardless of whether the proposal is a $1.7M must-win or a $250K exploratory screening. She currently has no visibility into what "quality" even means in terms of model selection, review depth, or critique loops.

### Who

- Principal investigator | Managing multiple proposals of different strategic value | Wants to understand quality options before committing resources

### Solution

A rigor comparison command that displays named profiles with transparent configuration: model tier per agent role, review passes, critique loop settings, iteration caps, and cost ranges. Summary view for quick decisions, detail view on demand.

### Domain Examples

#### 1: Happy Path -- Elena compares profiles before her first must-win

Dr. Elena Vasquez has just created proposal AF243-001 (Compact Directed Energy for Maritime UAS Defense, Phase II, $1.7M, fit score 85). She runs `/proposal rigor show` and sees a four-row table: lean ($2-5/wave, 1 review pass, no critique loops), standard ($8-15/wave, 2 passes, 2 critique iterations), thorough ($20-35/wave, 2 passes, 3 iterations), exhaustive ($40-60/wave, 3 passes, 4 iterations). She immediately understands the tradeoff space.

#### 2: Detail Drill-Down -- Elena inspects thorough profile

Elena runs `/proposal rigor show thorough` and sees model tier per agent role: strategist=strongest, writer=strongest, reviewer=strongest, researcher=standard, compliance=strongest, visual-assets=strongest, formatter=standard. She sees review depth (2 passes with evaluator scoring), critique loops (3 max iterations), and iteration cap (3 writer-reviewer cycles). She understands exactly what she is paying for.

#### 3: Edge Case -- Marcus views profiles with no active proposal context

Marcus Chen at NovaTech Solutions runs `/proposal rigor show` before creating any proposal. The comparison table still displays (profile definitions are plugin-level, not proposal-specific) but no "Active:" line appears in the header. He can browse profiles before committing to a proposal.

### UAT Scenarios (BDD)

#### Scenario: View summary comparison of all rigor profiles

Given Dr. Elena Vasquez has an active proposal "AF243-001" at "standard" rigor
When she runs "/proposal rigor show"
Then a comparison table displays all four profiles: lean, standard, thorough, exhaustive
And each row shows quality label, cost range per wave, review passes, and critique iterations
And the header indicates "Active: standard"
And the output offers "/proposal rigor show <profile>" for detail

#### Scenario: View detailed configuration of a specific profile

Given Dr. Elena Vasquez has an active proposal "AF243-001"
When she runs "/proposal rigor show thorough"
Then the detail view shows model tier for each agent role
And roles include strategist, writer, reviewer, researcher, compliance, and visual-assets
And review depth, critique loop limits, and iteration caps are shown
And estimated cost per wave is displayed as a range

#### Scenario: View profiles without an active proposal

Given Marcus Chen has no active proposal in the workspace
When he runs "/proposal rigor show"
Then the comparison table is displayed with all four profiles
And no "Active:" indicator appears in the header
And Marcus can browse profile details without a proposal context

### Acceptance Criteria

- [ ] Summary table shows all four profiles with quality, cost range, review passes, and critique iterations
- [ ] Detail view shows model tier per agent role for the requested profile
- [ ] Active profile indicated in header when a proposal is active
- [ ] Cost displayed as ranges, not exact prices
- [ ] Agent roles displayed, not internal agent names

### Technical Notes

- Profile definitions stored in plugin-level `config/rigor-profiles.json` (read-only)
- Summary and detail views are two display modes of the same command
- No write operations -- purely informational
- Depends on: rigor-profiles.json schema definition

---

## RP-002: Select Rigor Profile for a Proposal

### Problem

Dr. Elena Vasquez is a principal investigator who lost her last Phase II proposal because the debrief cited "insufficient detail in TRL advancement methodology." She suspects a more capable model would have produced deeper technical content, but the plugin gave her no way to tell it "this one matters more." She finds it frustrating that a $1.7M must-win gets the same treatment as a $250K exploratory screening.

### Who

- Principal investigator | Working on a high-stakes proposal after a previous loss | Wants to dial up quality for a must-win opportunity

### Solution

A rigor set command that assigns a named profile to the active proposal. The command displays a diff showing exactly what changed, confirms existing artifacts are preserved, and records the change in history.

### Domain Examples

#### 1: Happy Path -- Elena upgrades to thorough for must-win

Dr. Elena Vasquez has proposal AF243-001 at default "standard" rigor. She runs `/proposal rigor set thorough`. The output shows: writer model standard->strongest, reviewer model standard->strongest, strategist model standard->strongest, compliance model standard->strongest, critique loops 2 iter->3 iter. It confirms "Existing artifacts are preserved -- no re-run required."

#### 2: Edge Case -- Marcus downgrades to lean for screening

Marcus Chen at NovaTech Solutions has just created proposal N244-015 (Undersea Acoustic Sensing, Phase I, $250K, fit score 64). He runs `/proposal rigor set lean`. The output shows: all agents basic model tier, review passes 1 (structural only), critique loops skipped, estimated cost $2-5 per wave. He proceeds to screen the topic cheaply.

#### 3: Error Path -- Elena tries to set an invalid profile name

Dr. Elena Vasquez runs `/proposal rigor set ultra`. The output shows: "Error: Unknown rigor profile 'ultra'. Available profiles: lean, standard, thorough, exhaustive. Run /proposal rigor show to compare profiles."

#### 4: Boundary -- Setting the same profile is a no-op

Dr. Elena Vasquez already has AF243-001 at "thorough." She runs `/proposal rigor set thorough`. The output confirms "Rigor is already set to 'thorough' for AF243-001. No changes made." No history entry is recorded.

### UAT Scenarios (BDD)

#### Scenario: Set rigor profile and view diff

Given Dr. Elena Vasquez has an active proposal "AF243-001" at "standard" rigor
When she runs "/proposal rigor set thorough"
Then the rigor is updated to "thorough"
And a diff displays changes from "standard" to "thorough" per agent role
And the output confirms existing artifacts are preserved

#### Scenario: Set lean rigor for cost-conscious screening

Given Marcus Chen has an active proposal "N244-015" at "standard" rigor
When he runs "/proposal rigor set lean"
Then the rigor is updated to "lean"
And the output shows all agents at basic model tier
And review passes are shown as 1 (structural only)
And critique loops are shown as skipped

#### Scenario: Invalid profile name returns helpful error

Given Dr. Elena Vasquez has an active proposal "AF243-001"
When she runs "/proposal rigor set ultra"
Then an error states "ultra" is not a recognized profile
And the error lists available profiles: lean, standard, thorough, exhaustive
And the error suggests "/proposal rigor show" to compare

#### Scenario: No active proposal returns guidance

Given no proposal is currently active in the workspace
When the user runs "/proposal rigor set thorough"
Then an error states no active proposal exists
And the error suggests "/proposal new" or "/proposal switch"

#### Scenario: Setting same profile is a no-op

Given Dr. Elena Vasquez has proposal "AF243-001" at "thorough" rigor
When she runs "/proposal rigor set thorough"
Then the output confirms rigor is already "thorough"
And no changes are made to rigor-profile.json
And no history entry is recorded

### Acceptance Criteria

- [ ] Profile updated in rigor-profile.json on valid selection
- [ ] Diff displayed showing per-agent-role changes from old to new profile
- [ ] Existing artifacts explicitly confirmed as preserved
- [ ] History entry appended with from/to/timestamp/wave on change
- [ ] Invalid profile name returns error with available profiles listed
- [ ] No-active-proposal returns error with guidance
- [ ] Same-profile set is a no-op with confirmation

### Technical Notes

- Writes to `.sbir/proposals/{topic-id}/rigor-profile.json`
- Atomic write protocol: .tmp -> .bak -> rename
- History array is append-only
- Depends on: RP-001 (profile definitions), active-proposal resolution (multi-proposal workspace)

---

## RP-003: Contextual Rigor Suggestion at Proposal Creation

### Problem

Marcus Chen is a proposal manager at NovaTech Solutions who screens 5-6 SBIR topics per solicitation. He spent $4,200 in API costs last quarter across 8 proposals because the plugin ran every topic at the same quality level. His CEO asked "is this sustainable?" Marcus did not know the rigor feature existed until someone mentioned it -- there was no prompt, no hint, nothing during his normal workflow to make him aware of the option.

### Who

- Proposal manager | Creating new proposals frequently | Needs to discover rigor options naturally within existing workflow

### Solution

During proposal creation, the output includes the default rigor level and a contextual suggestion based on fit score, contract value, and phase. The suggestion is non-blocking -- one informational line, not a decision gate.

### Domain Examples

#### 1: Happy Path -- High-value proposal gets thorough suggestion

Dr. Elena Vasquez creates proposal AF243-001 with fit score 85 and $1.7M Phase II. The creation output includes "Rigor Profile: standard (default)" followed by "Tip: This proposal has a high fit score and Phase II value. Consider /proposal rigor set thorough for maximum quality."

#### 2: Cost-saving suggestion -- Moderate fit gets lean suggestion

Marcus Chen creates proposal N244-015 with fit score 64 and $250K Phase I. The creation output includes "Rigor Profile: standard (default)" followed by "Tip: For exploratory screening, /proposal rigor set lean reduces cost to $2-5/wave while maintaining go/no-go accuracy."

#### 3: No suggestion -- Mid-range proposal gets no nudge

Phil Santos creates proposal DA244-007 with fit score 75 and $250K Phase I. The creation output includes "Rigor Profile: standard (default)" with no additional suggestion because the proposal falls in the standard-appropriate range.

### UAT Scenarios (BDD)

#### Scenario: High-value proposal receives thorough suggestion

Given Dr. Elena Vasquez creates a new proposal from solicitation "AF243-001"
When the proposal is created with fit score 85 and contract value $1.7M Phase II
Then the output shows "Rigor Profile: standard (default)"
And a tip suggests considering "thorough" rigor
And the tip references high fit score and Phase II value
And the tip includes "/proposal rigor show" for comparison

#### Scenario: Moderate-value proposal receives lean suggestion

Given Marcus Chen creates a new proposal from solicitation "N244-015"
When the proposal is created with fit score 64 and contract value $250K Phase I
Then the output shows "Rigor Profile: standard (default)"
And a tip suggests "lean" for exploratory screening
And the tip includes cost range for lean profile

#### Scenario: Mid-range proposal receives no suggestion

Given Phil Santos creates a new proposal from solicitation "DA244-007"
When the proposal is created with fit score 75 and contract value $250K Phase I
Then the output shows "Rigor Profile: standard (default)"
And no rigor upgrade or downgrade suggestion is shown

### Acceptance Criteria

- [ ] All new proposals default to "standard" rigor regardless of metadata
- [ ] rigor-profile.json created in proposal namespace with profile "standard" and empty history
- [ ] Suggestion shown for fit >= 80 + Phase II (suggest thorough)
- [ ] Suggestion shown for fit < 70 + Phase I (suggest lean)
- [ ] No suggestion for proposals in standard-appropriate range
- [ ] Suggestion is non-blocking -- user can proceed without interaction

### Technical Notes

- Suggestion logic reads fit_score, contract_value, phase from proposal-state.json
- Suggestion thresholds should be configurable (future extensibility) but hardcoded is acceptable for MVP
- Depends on: `/proposal new` command (pre-existing), proposal-state.json schema

---

## RP-004: Agent Model Resolution from Rigor Profile

### Problem

Dr. Elena Vasquez is a principal investigator who set her proposal to "thorough" rigor and expects the writer, reviewer, and strategist to use the strongest available model. If agents silently ignore the rigor setting and use their hardcoded defaults, the entire feature is a placebo dial -- Elena is paying more and getting nothing. This is the highest-scoring opportunity outcome (16.5) in the JTBD analysis, meaning it is the single most important requirement for the feature to deliver value.

### Who

- Principal investigator | Expecting rigor to control agent quality | Would lose trust in the entire feature if agents ignore the setting

### Solution

All 18 agents resolve their model tier from the active proposal's rigor profile through a defined resolution chain: active proposal -> rigor-profile.json -> rigor-profiles.json -> model tier per agent role. No agent uses a hardcoded model from its own frontmatter.

### Domain Examples

#### 1: Happy Path -- Writer uses strongest model at thorough rigor

Dr. Elena Vasquez has proposal AF243-001 at "thorough" rigor. During Wave 4 drafting, the writer agent is invoked for Section 3 (Technical Approach). The writer resolves its model tier from rigor-profiles.json: thorough -> writer -> strongest. The wave output shows "Model: strongest" for the writer step.

#### 2: Lean rigor reduces all agents to basic tier

Marcus Chen has proposal N244-015 at "lean" rigor. During Wave 0 topic analysis, the topic-scout agent resolves: lean -> topic-scout -> basic. The reviewer runs 1 structural pass (not 2). Critique loops are skipped entirely. The total Wave 0 cost is $3.20 instead of $14.80.

#### 3: Fallback -- Missing rigor-profile.json defaults to standard

Phil Santos opens a proposal created before the rigor feature was installed. There is no rigor-profile.json in the proposal namespace. The agent resolution chain detects the missing file and falls back to "standard" profile behavior. No error is shown to the user.

### UAT Scenarios (BDD)

#### Scenario: Writer agent uses model tier from thorough profile

Given Dr. Elena Vasquez has proposal "AF243-001" at "thorough" rigor
When the writer agent is invoked during Wave 4 drafting
Then the writer uses the model tier specified by "thorough" for the writer role
And the wave step output shows "Model: strongest"

#### Scenario: Reviewer uses configured review pass count

Given Dr. Elena Vasquez has proposal "AF243-001" at "thorough" rigor
When the reviewer agent is invoked during Wave 4
Then the reviewer executes 2 review passes as configured by "thorough"
And both structural and evaluator scoring passes are performed

#### Scenario: Lean rigor reduces agent capabilities

Given Marcus Chen has proposal "N244-015" at "lean" rigor
When any agent is invoked during Wave 0
Then the agent uses "basic" model tier
And review passes are limited to 1
And critique loops are skipped

#### Scenario: Missing rigor-profile.json falls back to standard

Given Phil Santos opens a proposal created before the rigor feature existed
And no rigor-profile.json exists in the proposal namespace
When any agent is invoked
Then the agent behaves as if "standard" profile is active
And no error is displayed to the user

### Acceptance Criteria

- [ ] All 18 agents resolve model tier from the active rigor profile, not hardcoded frontmatter
- [ ] Resolution chain: active proposal -> rigor-profile.json -> rigor-profiles.json -> model tier
- [ ] Reviewer respects configured review pass count per profile
- [ ] Visual assets agent respects configured critique loop iteration cap
- [ ] Missing rigor-profile.json falls back to "standard" without error
- [ ] Wave output shows model tier per step as evidence of rigor application

### Technical Notes

- This is the foundational technical requirement -- without it, all other stories are cosmetic
- All 18 agent markdown files need frontmatter updated to resolve model from rigor chain
- Agent roles must be mapped to agent names (e.g., sbir-writer -> writer role)
- rigor-profiles.json must define model tier for every agent role
- Depends on: RP-001 (profile definitions), rigor-profile.json schema

---

## RP-005: Rigor Display in Wave Execution

### Problem

Dr. Elena Vasquez set her proposal to "thorough" but has no way to tell if the setting is actually doing anything during wave execution. Without visible evidence, rigor feels like a placebo dial. The Four Forces analysis identified this as the primary anxiety: "Will changing the model actually produce better proposals, or am I just spending more for the same output?"

### Who

- Principal investigator | Running waves after setting rigor | Needs visible evidence that rigor is controlling agent behavior

### Solution

Wave execution output includes the active rigor level in the wave header and model tier plus depth setting per step. The user can see, at every step, that rigor is active.

### Domain Examples

#### 1: Happy Path -- Elena sees thorough rigor in Wave 1 strategy

Dr. Elena Vasquez runs Wave 1 strategy for AF243-001 at "thorough" rigor. The wave header shows "Wave 1: Requirements & Strategy | Rigor: thorough." Each step shows its model tier: "[1/3] Topic analysis... Model: strongest | Depth: comprehensive." She can see that "thorough" is not just a label.

#### 2: Lean rigor visibly different during screening

Marcus Chen runs Wave 0 for N244-015 at "lean" rigor. The wave header shows "Rigor: lean." Steps show "Model: basic | Depth: structural." Marcus sees that lean execution is visibly lighter.

#### 3: Standard rigor as baseline reference

Phil Santos runs Wave 4 for DA244-007 at "standard" rigor. The header shows "Rigor: standard." Steps show "Model: standard | Reviewing: 2 passes." This is the baseline -- not the cheapest, not the most thorough.

### UAT Scenarios (BDD)

#### Scenario: Wave header displays active rigor level

Given Dr. Elena Vasquez has proposal "AF243-001" at "thorough" rigor
When she runs Wave 1 strategy
Then the wave header displays "Rigor: thorough"

#### Scenario: Per-step output shows model tier

Given Dr. Elena Vasquez has proposal "AF243-001" at "thorough" rigor
When she runs Wave 1 strategy
Then each step in the wave output shows the model tier being used
And model tier is displayed as "basic," "standard," or "strongest" -- not specific model names

#### Scenario: Lean rigor visibly reduces execution depth

Given Marcus Chen has proposal "N244-015" at "lean" rigor
When he runs Wave 0 topic analysis
Then the wave header displays "Rigor: lean"
And steps show "Model: basic"
And review depth is shown as 1 structural pass

### Acceptance Criteria

- [ ] Wave header includes "Rigor: {profile_name}" for every wave execution
- [ ] Each step in wave output shows model tier (basic/standard/strongest)
- [ ] Model tier names used, not specific model names (Opus/Sonnet/Haiku)
- [ ] Review pass count shown when reviewer is involved

### Technical Notes

- Display-only requirement -- no new state written
- Wave execution code must read rigor profile to populate header and step displays
- Depends on: RP-004 (agent model resolution)

---

## Phase 2 Stories (Job 4)

---

## RP-006: Rigor in Proposal Status and Portfolio View

### Problem

Dr. Elena Vasquez manages three simultaneous proposals at different priority levels: a $1.7M must-win at "thorough," a $250K moderate at "standard," and a $250K exploratory at "lean." When she runs `/proposal status`, she cannot see the rigor allocation across her portfolio. She has to remember which proposal is set to which level. When her VP asks "how are we allocating effort across the three open proposals?", she cannot show a single view that tells the story.

### Who

- Principal investigator | Managing 2-3 simultaneous proposals | Wants portfolio-level visibility of resource allocation

### Solution

The status command includes rigor level for the active proposal and all other proposals in the workspace. Rigor is displayed alongside fit score and contract value so the resource allocation story is visible at a glance.

### Domain Examples

#### 1: Happy Path -- Elena sees rigor across her portfolio

Dr. Elena Vasquez runs `/proposal status` with three active proposals. The active proposal (AF243-001) shows "Phase II | $1.7M | Fit: 85 | Rigor: thorough." The other proposals show: "N244-012 AUV Navigation Phase I $250K Fit: 72 standard" and "DA244-003 Sensor Fusion Phase I $250K Fit: 58 lean." She can see that her resource allocation matches her strategic priorities.

#### 2: After switch -- rigor follows the proposal

Elena runs `/proposal switch n244-012`. The status now shows N244-012 as active at "standard" rigor. AF243-001 moves to the "Other proposals" list showing "thorough." Rigor is per-proposal, not per-session.

#### 3: Single proposal -- no portfolio view needed

Phil Santos has only one active proposal. Status shows his proposal with "Rigor: standard" in the header. No "Other proposals" section appears.

### UAT Scenarios (BDD)

#### Scenario: Status shows rigor for all proposals in workspace

Given the workspace contains:
  | topic_id  | name                    | rigor    | fit_score |
  | AF243-001 | Compact Directed Energy | thorough | 85        |
  | N244-012  | AUV Navigation          | standard | 72        |
  | DA244-003 | Sensor Fusion           | lean     | 58        |
When Dr. Elena Vasquez runs "/proposal status"
Then the active proposal line includes its rigor level
And each proposal in the "Other proposals" listing shows its rigor level
And rigor is displayed alongside fit score and contract value

#### Scenario: Switching proposals loads target rigor

Given Dr. Elena Vasquez has "AF243-001" active at "thorough" rigor
And proposal "N244-012" exists at "standard" rigor
When she runs "/proposal switch n244-012"
Then the active proposal becomes "N244-012"
And the displayed rigor is "standard"
And subsequent commands use "standard" rigor settings

#### Scenario: Single-proposal workspace shows rigor in header

Given Phil Santos has only one active proposal "DA244-007" at "standard" rigor
When he runs "/proposal status"
Then the status shows "Rigor: standard" for the active proposal
And no "Other proposals" section is displayed

### Acceptance Criteria

- [ ] Active proposal line in status includes "Rigor: {profile_name}"
- [ ] Each proposal in "Other proposals" shows its rigor level
- [ ] Rigor displayed alongside fit score and contract value
- [ ] Switching proposals loads target proposal's rigor level
- [ ] No rigor "bleed" between proposals after switch

### Technical Notes

- Status reads rigor-profile.json from each proposal namespace in `.sbir/proposals/*/`
- Switch already loads per-proposal state -- rigor follows the same pattern
- Depends on: RP-002 (profile stored per-proposal), multi-proposal workspace (pre-existing)

---

## RP-007: Adjust Rigor Mid-Proposal

### Problem

Dr. Elena Vasquez started her exploratory proposal DA244-003 at "lean" rigor. After Wave 2 research, the topic turns out to be a stronger fit than expected -- the fit score improved from 58 to 78. She wants to upgrade to "standard" for the remaining waves without re-running Waves 0-2 (which would cost $20+ and take 45 minutes for work that is already adequate). She needs to change rigor mid-stream with confidence that nothing is lost or broken.

### Who

- Principal investigator | Re-prioritizing a proposal based on new information | Wants to change rigor without disrupting completed work

### Solution

The rigor set command works at any point in the proposal lifecycle. When changing mid-proposal, the output clarifies what was produced at the old level, what will use the new level, and offers guidance for selective re-processing if desired.

### Domain Examples

#### 1: Happy Path -- Elena upgrades DA244-003 from lean to standard at Wave 3

Dr. Elena Vasquez runs `/proposal rigor set standard` for DA244-003, currently at Wave 3. The output shows: "Rigor updated: lean -> standard" with per-agent-role diff. "Waves 0-2 retain their existing artifacts (produced at lean). Wave 3+ will use standard settings." A note suggests `/proposal iterate <section>` for selective re-processing of earlier sections.

#### 2: History recorded for debrief

After the change, rigor-profile.json history array contains: `{from: "lean", to: "standard", at: "2026-04-15T10:30:00Z", wave: 3}`. When Elena later runs debrief, this change is shown in the rigor summary with the wave number where it occurred.

#### 3: Multiple changes tracked

Phil Santos changes N244-012 from standard to thorough at Wave 4, then back to standard at Wave 6 (after the critical section passes). Both changes are in the history array and both appear in the debrief rigor summary.

### UAT Scenarios (BDD)

#### Scenario: Change rigor mid-proposal preserves existing artifacts

Given Dr. Elena Vasquez has proposal "DA244-003" at "lean" rigor
And Waves 0-2 have been completed at "lean" rigor
When she runs "/proposal rigor set standard"
Then the rigor is updated to "standard"
And the output states Waves 0-2 artifacts are preserved
And the output states Wave 3 onward will use "standard" settings
And no automatic re-run of completed waves occurs

#### Scenario: Rigor change records history for debrief

Given Dr. Elena Vasquez has proposal "DA244-003" at "lean" rigor
And the proposal is currently on Wave 3
When she runs "/proposal rigor set standard"
Then the rigor history records the change with timestamp
And the history entry includes previous profile "lean," new profile "standard," and wave 3

#### Scenario: Re-processing guidance offered after upgrade

Given Dr. Elena Vasquez has proposal "DA244-003" at "lean" rigor
And Waves 0-2 have been completed
When she runs "/proposal rigor set standard"
Then the output includes a note about earlier waves produced at "lean"
And the output suggests "/proposal iterate <section>" for selective re-processing

### Acceptance Criteria

- [ ] Rigor can be changed at any wave in the proposal lifecycle
- [ ] Existing artifacts preserved -- no automatic re-run
- [ ] Output shows which waves were produced at the old level
- [ ] Output shows which waves will use the new level
- [ ] History entry appended with from/to/timestamp/wave
- [ ] Re-processing guidance offered when prior waves exist at a different rigor

### Technical Notes

- Forward-application boundary uses current_wave from proposal-state.json
- Re-processing via `/proposal iterate` is existing functionality -- rigor change just suggests it
- Depends on: RP-002 (profile set), proposal-state.json current_wave field

---

## RP-008: Rigor Summary in Proposal Debrief

### Problem

Dr. Elena Vasquez submitted proposal AF243-001 at "thorough" rigor and wants to know if the investment paid off. When evaluation results come back, she needs to correlate rigor settings with reviewer scores. Without a rigor summary in the debrief, she has no record of what quality level was applied, how many review cycles ran, or whether the rigor was consistent throughout.

### Who

- Principal investigator | Post-submission, awaiting evaluation results | Wants to correlate rigor investment with proposal outcome

### Solution

The debrief command includes a rigor summary section showing profile used, total review cycles, critique loop statistics, profile change history (if any), and guidance to correlate with evaluation feedback.

### Domain Examples

#### 1: Happy Path -- Consistent thorough rigor throughout

Dr. Elena Vasquez runs `/proposal debrief` for AF243-001. The rigor summary shows: "Profile: thorough (used throughout). Waves completed: 10/10. Review cycles: 24 total (avg 2.4/section). Critique loops: 8 figures, 3 iterations avg. Profile changes: None."

#### 2: Rigor changed mid-proposal

Dr. Elena Vasquez runs debrief for DA244-003. The rigor summary shows: "Profile: standard (changed from lean at Wave 3). Profile changes: lean -> standard at Wave 3 (2026-04-15)."

#### 3: Lean screening proposal

Marcus Chen runs debrief for N244-015 (screened at lean, never upgraded). The summary shows: "Profile: lean (used throughout). Review cycles: 6 total (avg 1.0/section). Critique loops: 0 (skipped at lean)."

### UAT Scenarios (BDD)

#### Scenario: Debrief shows rigor summary for consistent profile

Given Dr. Elena Vasquez has completed all 10 waves for "AF243-001" at "thorough" rigor
When she runs "/proposal debrief"
Then the debrief includes a rigor summary section
And the summary shows profile "thorough" used throughout
And the summary shows total review cycles and average per section
And the summary shows critique loop count and average iterations

#### Scenario: Debrief shows rigor change history

Given Dr. Elena Vasquez has completed proposal "DA244-003"
And the rigor was changed from "lean" to "standard" at Wave 3
When she runs "/proposal debrief"
Then the debrief rigor summary shows the profile change
And the change is annotated with wave number 3 and timestamp

#### Scenario: Debrief for lean-only proposal

Given Marcus Chen has completed proposal "N244-015" at "lean" rigor throughout
When he runs "/proposal debrief"
Then the rigor summary shows "lean" used throughout
And critique loops are shown as "0 (skipped at lean)"

### Acceptance Criteria

- [ ] Debrief includes rigor summary section with profile name
- [ ] Summary shows total review cycles and per-section average
- [ ] Summary shows critique loop count and average iterations
- [ ] Profile changes shown with wave number and timestamp
- [ ] "Used throughout" indicated when no changes occurred

### Technical Notes

- Reads rigor-profile.json (profile + history) and proposal-state.json (review/critique counts)
- Review cycle and critique loop counts must be accumulated during wave execution (prerequisite data)
- Depends on: RP-004 (agent resolution tracking), `/proposal debrief` command (pre-existing)
