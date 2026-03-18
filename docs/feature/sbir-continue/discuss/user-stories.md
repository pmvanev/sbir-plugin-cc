<!-- markdownlint-disable MD024 -->

# User Stories: sbir-continue

## US-CONT-01: Continue From No Setup

### Problem
Phil Santos is a small business engineer who just installed the SBIR plugin and types `/sbir:continue` expecting it to work. He finds it frustrating to get a bare error like "No active proposal found" because he does not yet know the command vocabulary. He needs a welcoming entry point that meets him where he is.

### Who
- First-time SBIR plugin user | Has just installed the plugin | Wants to start using the tool without reading documentation first

### Solution
When `/sbir:continue` detects no company profile and no proposal state, it displays a welcoming message explaining the setup wizard, what it does, estimated time, and the exact command to run.

### Domain Examples
#### 1: First Install -- Phil Santos installs the SBIR plugin on a fresh project directory. No `~/.sbir/company-profile.json` exists. No `.sbir/` directory exists. He types `/sbir:continue`. The system displays "No configuration detected. Let's get you set up." with setup wizard description and "Run: /sbir:setup".

#### 2: Plugin Reinstall -- Dr. Elena Vasquez reinstalled the plugin after a system migration. Her profile was lost. She types `/sbir:continue`. The system detects no profile and routes her to setup, not to an error about missing proposals.

#### 3: Wrong Directory -- Marcus Chen types `/sbir:continue` in a directory that is not an SBIR project (no `.sbir/`). But `~/.sbir/company-profile.json` exists from a previous project. The system detects no proposal state but recognizes the profile, so routes to the "no active proposal" flow (US-CONT-03), not the "no setup" flow.

### UAT Scenarios (BDD)
#### Scenario: First-time user with no configuration
Given Phil Santos has installed the SBIR plugin
And no company profile exists at ~/.sbir/company-profile.json
And no proposal state exists at .sbir/proposal-state.json
When Phil runs /sbir:continue
Then the system displays a welcome message with setup wizard description
And suggests running /sbir:setup
And includes estimated setup time of 10-15 minutes
And no error messages are displayed

#### Scenario: No profile but corpus directory exists
Given Dr. Elena Vasquez has no company profile
And a .sbir/corpus/ directory exists with stale files from a previous installation
When Elena runs /sbir:continue
Then the system routes to setup (profile is the primary gate)
And does not mention the stale corpus files

#### Scenario: Plugin installed on non-project directory
Given Marcus Chen has a company profile for "Pacific Systems Engineering"
And no .sbir/ directory exists in the current directory
When Marcus runs /sbir:continue
Then the system detects the profile but no proposal
And routes to the no-active-proposal flow
And does not show a "no setup" message

### Acceptance Criteria
- [ ] Displays welcome message when no profile and no proposal state exist
- [ ] Suggests /sbir:setup as the next action
- [ ] Includes estimated time (10-15 minutes) in the output
- [ ] No error messages, warnings, or stack traces in the output
- [ ] Differentiates "no profile at all" from "profile exists but no proposal"

### Technical Notes
- Read-only command: does not create files, does not modify state
- Must check `~/.sbir/company-profile.json` (global) and `.sbir/proposal-state.json` (project-local) independently
- Depends on: sbir-setup-wizard agent existing and being invocable via /sbir:setup

### Dependencies
- /sbir:setup command must exist (already delivered)
- No new Python/PES code required

### Job Story Traceability
- JS-02: First-Time User Without Setup

---

## US-CONT-02: Continue From Partial Setup

### Problem
Phil Santos is a small business engineer who started the setup wizard last week but quit after creating his company profile. He returns and types `/sbir:continue`, hoping the system remembers his progress. He finds it tedious to re-run the full setup wizard and press "keep" for steps already completed.

### Who
- Returning user with partial setup | Has company profile but missing corpus or API key | Wants to resume setup without repeating completed steps

### Solution
When `/sbir:continue` detects a company profile but missing corpus or API key, it displays a setup status checklist showing what is done and what remains, with options to continue setup, skip to proposal, or quit.

### Domain Examples
#### 1: Profile Only -- Phil Santos has `~/.sbir/company-profile.json` for "Pacific Systems Engineering" but no corpus documents and no GEMINI_API_KEY. `/sbir:continue` shows profile as [ok], corpus as [--], API key as [--], and offers (c) continue setup, (s) skip to proposal, (q) quit.

#### 2: Profile and Corpus -- Dr. Elena Vasquez has a profile and 8 corpus documents but no GEMINI_API_KEY. `/sbir:continue` treats setup as functionally complete (API key is optional) and routes to the "no active proposal" flow, not partial setup.

#### 3: Profile with Inactive SAM.gov -- Marcus Chen has a profile with SAM.gov marked inactive and no corpus. `/sbir:continue` shows profile as [ok] (profile exists), corpus as [--], and includes a note that SAM.gov inactive status will affect fit scoring.

### UAT Scenarios (BDD)
#### Scenario: Profile exists but no corpus
Given Phil Santos has a company profile for "Pacific Systems Engineering"
And no corpus documents have been ingested
And no GEMINI_API_KEY is configured
When Phil runs /sbir:continue
Then the system displays setup status with profile as ok
And corpus marked as incomplete
And API key marked as not configured
And offers continue setup, skip to proposal, and quit options

#### Scenario: Profile and corpus exist but no API key
Given Dr. Elena Vasquez has a company profile for "Vasquez Photonics"
And 8 corpus documents have been ingested
And no GEMINI_API_KEY is configured
When Elena runs /sbir:continue
Then the system treats setup as functionally complete
And displays the no-active-proposal flow with profile name and corpus count
And does not show partial setup options

#### Scenario: User selects skip to proposal
Given Phil Santos has a company profile but no corpus
When Phil runs /sbir:continue
And selects (s) skip to proposal
Then the system displays the no-active-proposal flow
And suggests /sbir:solicitation find and /sbir:proposal new

#### Scenario: User selects continue setup
Given Phil Santos has a company profile but no corpus
When Phil runs /sbir:continue
And selects (c) continue setup
Then the system suggests running /sbir:setup
And notes that setup will detect existing profile and skip to corpus step

### Acceptance Criteria
- [ ] Displays checklist with [ok]/[--] indicators for profile, corpus, and API key
- [ ] Considers setup functionally complete if profile and corpus exist (API key is optional)
- [ ] Offers three options: continue setup, skip to proposal, quit
- [ ] "Continue setup" routes to /sbir:setup which handles idempotent re-entry
- [ ] "Skip to proposal" routes to the no-active-proposal display
- [ ] Displays company name from profile in the status output

### Technical Notes
- Must read `~/.sbir/company-profile.json` for company_name
- Must check `.sbir/corpus/` directory for document count
- Must check GEMINI_API_KEY environment variable
- API key absence is informational, not a blocker -- it is used only in Wave 5
- Setup completeness threshold: profile exists AND corpus has >= 1 document

### Dependencies
- US-CONT-01 (detection logic is prerequisite)
- /sbir:setup command handles idempotent re-entry (already delivered)

### Job Story Traceability
- JS-03: Resume Incomplete Setup

---

## US-CONT-03: Continue With No Active Proposal

### Problem
Phil Santos is a small business engineer with a fully configured plugin (profile, corpus, API key) but no active proposal in the current directory. He types `/sbir:continue` expecting guidance on what to do next. He finds it unhelpful to just see "No active proposal found" without concrete next steps.

### Who
- Configured user without active proposal | Setup is complete | Wants to know how to start a proposal or find solicitations

### Solution
When `/sbir:continue` detects a complete setup but no proposal state, it displays the company name, corpus count, and concrete commands to find solicitations or start a new proposal.

### Domain Examples
#### 1: Ready to Start -- Phil Santos has profile "Pacific Systems Engineering", 12 corpus documents, and GEMINI_API_KEY configured. No `.sbir/proposal-state.json` exists. `/sbir:continue` shows profile name, "12 documents indexed", and suggests `/sbir:solicitation find` and `/sbir:proposal new <solicitation>`.

#### 2: Different Project Directory -- Dr. Elena Vasquez has a profile but is in a new project directory with no `.sbir/`. `/sbir:continue` shows profile name, "0 documents indexed", and suggests the same commands.

#### 3: Previous Proposal in Different Directory -- Marcus Chen completed a proposal in another directory. He is now in a clean directory. `/sbir:continue` shows his profile and suggests starting fresh.

### UAT Scenarios (BDD)
#### Scenario: Setup complete with no active proposal
Given Phil Santos has a company profile for "Pacific Systems Engineering"
And 12 corpus documents are indexed
And no proposal state file exists
When Phil runs /sbir:continue
Then the system displays "Pacific Systems Engineering"
And displays "12 documents indexed"
And displays "No active proposal found"
And suggests /sbir:solicitation find and /sbir:proposal new

#### Scenario: Setup complete with zero corpus documents
Given Dr. Elena Vasquez has a company profile for "Vasquez Photonics"
And 0 corpus documents are indexed
When Elena runs /sbir:continue
Then the system displays "Vasquez Photonics"
And displays "0 documents indexed"
And still suggests starting a proposal

#### Scenario: Profile exists but corpus directory missing entirely
Given Marcus Chen has a company profile for "Chen Defense Solutions"
And no .sbir/ directory exists in the current directory
When Marcus runs /sbir:continue
Then the system displays the profile name
And treats corpus count as 0
And suggests starting a proposal

### Acceptance Criteria
- [ ] Displays company name from profile
- [ ] Displays corpus document count (0 if no corpus)
- [ ] Displays "No active proposal found" text
- [ ] Suggests both /sbir:solicitation find and /sbir:proposal new
- [ ] Does not display error messages for zero-corpus state

### Technical Notes
- Read company_name from `~/.sbir/company-profile.json`
- Count files in `.sbir/corpus/` if directory exists; 0 otherwise
- Read-only: does not create .sbir/ directory or any files

### Dependencies
- US-CONT-01, US-CONT-02 (detection priority: no setup > partial setup > no proposal)
- /sbir:solicitation find and /sbir:proposal new commands must exist (already delivered)

### Job Story Traceability
- JS-02: First-Time User Without Setup (partial -- the "setup complete" branch)

---

## US-CONT-04: Continue Mid-Wave

### Problem
Phil Santos is a small business engineer partway through Wave 1 (compliance matrix done, TPOC pending, strategy brief not started). After a multi-day break, he types `/sbir:continue` and cannot remember which tasks within the wave are complete. He finds it frustrating to have to manually check each artifact and remember the wave task sequence.

### Who
- Active proposal user mid-wave | Has completed some within-wave tasks | Wants a clear picture of remaining work and the next command to run

### Solution
When `/sbir:continue` detects an active wave with incomplete tasks, it displays the proposal header (topic, wave, deadline), a within-wave task checklist showing complete/pending/not-started tasks, and suggests the specific command for the next incomplete task.

### Domain Examples
#### 1: Wave 1 Partial -- Phil Santos has proposal AF243-001 in Wave 1. Compliance matrix has 24 items. TPOC questions generated but call pending. Strategy brief not started. Deadline is April 15, 2026 (28 days away). `/sbir:continue` shows compliance as [ok], TPOC as [..] pending call, strategy as [  ] not started, and suggests `/sbir:proposal wave strategy`.

#### 2: Wave 4 Multi-Volume -- Dr. Elena Vasquez has proposal N00014-26-001 in Wave 4. Technical volume approved. Management volume in review with 2 open items. Cost volume not started. Deadline is March 30, 2026 (12 days). `/sbir:continue` shows volumes with status, suggests `/sbir:proposal iterate management` first, then notes `/sbir:proposal draft cost` as the subsequent step.

#### 3: Wave 0 Go Decision Pending -- Marcus Chen has proposal DA-26-003 in Wave 0. Fit scoring completed but Go/No-Go not yet decided. `/sbir:continue` shows Wave 0 status and indicates Go/No-Go checkpoint is pending, suggesting he review fit scoring results.

#### 4: Wave 0 Post-Go Approach Pending -- Phil Santos has proposal AF243-001 in Wave 0. Go decision is "go" but approach_selection is "pending". `/sbir:continue` suggests `/sbir:proposal shape` to select an approach.

### UAT Scenarios (BDD)
#### Scenario: Wave 1 with compliance done and TPOC pending
Given Phil Santos has proposal "AF243-001" active in Wave 1
And the compliance matrix has 24 items extracted
And TPOC status is "questions_generated"
And strategy brief status is "not_started"
And the deadline is 28 days away
When Phil runs /sbir:continue
Then the system displays "Wave 1: Requirements & Strategy"
And displays the deadline with 28 days remaining
And shows compliance matrix as complete with 24 items
And shows TPOC as pending call
And shows strategy brief as not started
And notes that TPOC call is optional
And suggests /sbir:proposal wave strategy

#### Scenario: Wave 4 with mixed volume progress
Given Dr. Elena Vasquez has proposal "N00014-26-001" active in Wave 4
And the technical volume status is "approved"
And the management volume status is "in_review" with 2 open items
And the cost volume status is "not_started"
And the deadline is 12 days away
When Elena runs /sbir:continue
Then the system displays "Wave 4: Drafting"
And shows technical volume as approved
And shows management volume as in review with open item count
And shows cost volume as not started
And suggests /sbir:proposal iterate management

#### Scenario: Wave 0 with Go decision pending
Given Marcus Chen has proposal "DA-26-003" active in Wave 0
And go_no_go is "pending"
When Marcus runs /sbir:continue
Then the system displays "Wave 0: Intelligence & Fit"
And indicates Go/No-Go decision is pending
And suggests reviewing fit scoring results

#### Scenario: Wave 0 with Go approved and approach pending
Given Phil Santos has proposal "AF243-001" active in Wave 0
And go_no_go is "go"
And approach_selection status is "pending"
When Phil runs /sbir:continue
Then the system displays "Wave 0: Intelligence & Fit"
And indicates approach selection is pending
And suggests running /sbir:proposal shape

#### Scenario: Async TPOC does not block suggestion
Given Phil Santos has proposal "AF243-001" in Wave 1
And TPOC status is "questions_generated"
And strategy brief status is "not_started"
When Phil runs /sbir:continue
Then the system does not suggest waiting for TPOC call
And suggests proceeding with strategy brief generation
And notes TPOC data will be marked as pending in the brief

### Acceptance Criteria
- [ ] Displays proposal header with topic ID, title, wave name, and deadline countdown
- [ ] Shows within-wave task checklist using [ok]/[..]/[  ] indicators
- [ ] Identifies the first incomplete task and suggests its command
- [ ] Handles Wave 0 specially: Go/No-Go and approach selection states
- [ ] Handles Wave 4 specially: per-volume status with open review item counts
- [ ] Treats async events (TPOC) as optional -- never blocks progress suggestions
- [ ] Displays output format (latex/docx) at Wave 3+

### Technical Notes
- Must read and interpret wave-specific state fields:
  - Wave 0: go_no_go, approach_selection, fit_scoring
  - Wave 1: compliance_matrix, tpoc, strategy_brief
  - Wave 4: volumes.technical, volumes.management, volumes.cost, open_review_items
  - Other waves: wave status and checkpoint state
- Command suggestion logic must use the command-to-agent routing table from wave-agent-mapping skill
- Deadline warning thresholds: 7 days (warning), 3 days (critical)

### Dependencies
- US-CONT-01, US-CONT-02, US-CONT-03 (detection priority)
- wave-agent-mapping skill (command routing table)
- proposal-state-schema.json (state field definitions)

### Job Story Traceability
- JS-01: Resume After Session Break
- JS-04: Resume Mid-Wave Work

---

## US-CONT-05: Continue Between Waves

### Problem
Phil Santos is a small business engineer who approved the Wave 1 strategy alignment checkpoint yesterday. He returns today and does not remember what Wave 2 involves or which command starts it. He finds it disorienting to transition between waves without context about what the next wave entails.

### Who
- Active proposal user between waves | Has completed current wave's exit gate | Wants guidance on next wave's purpose and entry command

### Solution
When `/sbir:continue` detects that the current wave is completed and the next wave has not started, it displays wave progress, celebrates the completed wave, describes the next wave's purpose, and suggests the command to begin it.

### Domain Examples
#### 1: Wave 1 to Wave 2 -- Phil Santos approved the strategy brief for proposal AF243-001. Wave 1 is "completed", Wave 2 is "not_started", current_wave is 2. Deadline is 25 days away. `/sbir:continue` shows wave progress with Waves 0-1 checked, marks Wave 2 as current position, describes it as "Research -- deep dive into technical landscape, prior art, and competitive analysis", and suggests `/sbir:proposal wave research`.

#### 2: Wave 3 to Wave 4 -- Dr. Elena Vasquez approved the outline for proposal N00014-26-001. Waves 0-3 completed. Wave 4 not started. `/sbir:continue` describes Wave 4 as "Drafting" and suggests `/sbir:proposal draft technical` as the first drafting step.

#### 3: Wave 7 to Wave 8 -- Marcus Chen approved the final review. Waves 0-7 completed. Wave 8 not started. `/sbir:continue` describes Wave 8 as "Submission -- package assembly and portal preparation" and suggests `/sbir:proposal submit prep`.

### UAT Scenarios (BDD)
#### Scenario: Wave 1 completed, Wave 2 not started
Given Phil Santos has proposal "AF243-001"
And Wave 1 status is "completed" with strategy brief approved
And Wave 2 status is "not_started"
And current_wave is 2
And the deadline is 25 days away
When Phil runs /sbir:continue
Then the system shows wave progress with Wave 1 as complete
And marks Wave 2 as current position
And describes Wave 2 as "Research"
And suggests /sbir:proposal wave research

#### Scenario: Wave 7 completed, Wave 8 not started
Given Marcus Chen has proposal "DA-26-003"
And Waves 0 through 7 are completed
And Wave 8 status is "not_started"
And current_wave is 8
When Marcus runs /sbir:continue
Then the system shows wave progress with Waves 0-7 complete
And describes Wave 8 as "Submission"
And suggests /sbir:proposal submit prep

#### Scenario: Deadline warning during wave transition
Given Phil Santos has proposal "AF243-001"
And Wave 3 is completed, Wave 4 is not_started
And the deadline is 5 days away
When Phil runs /sbir:continue
Then the system shows the wave transition guidance
And includes a deadline warning at the 5-day threshold

### Acceptance Criteria
- [ ] Displays wave progress list with completed/active/pending indicators
- [ ] Marks the next wave as the current position
- [ ] Describes the next wave's purpose (name and brief description)
- [ ] Suggests the specific command to begin the next wave
- [ ] Includes deadline countdown in the display
- [ ] Surfaces deadline warnings at 7-day and 3-day thresholds

### Technical Notes
- Wave descriptions from wave-agent-mapping skill
- Must verify exit gate was approved (waves.{N}.status = "completed" implies gate passed)
- Wave transition detected when: current_wave = N, waves.{N}.status = "not_started", waves.{N-1}.status = "completed"

### Dependencies
- US-CONT-04 (mid-wave detection must run before between-waves detection)
- wave-agent-mapping skill (wave names, descriptions, commands)

### Job Story Traceability
- JS-05: Transition Between Waves

---

## US-CONT-06: Continue Post-Submission and Completion

### Problem
Phil Santos is a small business engineer who submitted his proposal last week. He returns to the project directory and types `/sbir:continue`, wondering if there is anything left to do. He finds it easy to forget about the debrief step and wants the tool to proactively guide him through the complete lifecycle including post-submission.

### Who
- User with submitted or completed proposal | Has finished Wave 8 or all waves | Wants closure and forward guidance

### Solution
When `/sbir:continue` detects a submitted proposal (Wave 8 complete, Wave 9 pending), it confirms submission and guides to debrief ingestion. When all waves are complete, it confirms lifecycle completion and suggests starting a new proposal.

### Domain Examples
#### 1: Post-Submission Debrief Pending -- Phil Santos submitted proposal AF243-001. Wave 8 is "completed", Wave 9 is "not_started". `/sbir:continue` says "Proposal submitted" and suggests `/sbir:proposal debrief ingest <feedback-file>` when evaluator feedback arrives, plus offers starting a new proposal.

#### 2: Lifecycle Complete -- Dr. Elena Vasquez completed all waves including debrief for proposal N00014-26-001. All waves 0-9 are "completed". `/sbir:continue` says "Proposal lifecycle complete. All 10 waves finished." and suggests `/sbir:solicitation find` or `/sbir:proposal new`.

#### 3: Archived No-Go -- Marcus Chen's proposal DA-26-003 received a "no-go" decision in Wave 0 and was archived. `/sbir:continue` says "This proposal was declined" and suggests starting a new proposal. It does not offer to resume the archived proposal.

### UAT Scenarios (BDD)
#### Scenario: Proposal submitted with debrief pending
Given Phil Santos has proposal "AF243-001"
And Waves 0 through 8 are completed
And Wave 9 status is "not_started"
When Phil runs /sbir:continue
Then the system confirms the proposal has been submitted
And suggests /sbir:proposal debrief ingest for when feedback arrives
And offers starting a new proposal as an alternative

#### Scenario: All waves completed including debrief
Given Dr. Elena Vasquez has proposal "N00014-26-001"
And all waves 0 through 9 are completed
When Elena runs /sbir:continue
Then the system confirms lifecycle is complete
And displays "All 10 waves finished"
And suggests /sbir:solicitation find and /sbir:proposal new

#### Scenario: Archived proposal with No-Go decision
Given Marcus Chen has proposal "DA-26-003"
And go_no_go is "no-go"
And archived is true
When Marcus runs /sbir:continue
Then the system indicates the proposal was declined
And suggests starting a new proposal
And does not offer to resume the archived proposal

#### Scenario: Deferred proposal
Given Phil Santos has proposal "AF243-001"
And go_no_go is "deferred"
When Phil runs /sbir:continue
Then the system indicates the proposal is deferred
And offers to resume the Go/No-Go evaluation or start a new proposal

### Acceptance Criteria
- [ ] Distinguishes between submitted (Wave 8 done), complete (Wave 9 done), archived, and deferred states
- [ ] Confirms submission explicitly for post-submission state
- [ ] Suggests debrief ingestion with command syntax including path placeholder
- [ ] Confirms lifecycle completion for all-waves-done state
- [ ] Handles archived/no-go proposals without offering resume
- [ ] Handles deferred proposals with option to resume evaluation
- [ ] Suggests starting new proposal in all terminal states

### Technical Notes
- Check `archived` boolean field in state
- Check `go_no_go` for "no-go" and "deferred" values
- Wave 9 completed = lifecycle complete
- Wave 8 completed + Wave 9 not_started = post-submission

### Dependencies
- US-CONT-04, US-CONT-05 (detection priority: mid-wave and between-waves checked before terminal states)
- /sbir:proposal debrief ingest command must exist (already delivered)

### Job Story Traceability
- JS-06: Post-Submission and Completion

---

## US-CONT-07: Continue With Error Handling

### Problem
Phil Santos is a small business engineer who encounters a corrupted proposal state file or a deadline that has already passed. He types `/sbir:continue` and needs clear, actionable error messages instead of cryptic failures. He finds it anxiety-inducing when tools fail silently or display raw error output.

### Who
- Any user encountering error conditions | State file may be corrupted, deadline passed, or schema incompatible | Wants clear error messages with recovery steps

### Solution
When `/sbir:continue` encounters error conditions (corrupt state, invalid JSON, schema mismatch, past deadline), it displays error messages following the what/why/do pattern and suggests recovery actions.

### Domain Examples
#### 1: Corrupted State -- Phil Santos's `.sbir/proposal-state.json` contains invalid JSON (perhaps from a crash mid-write). `/sbir:continue` displays: WHAT: "Could not read proposal state." WHY: "The state file contains invalid JSON, possibly from an interrupted write." DO: "Run /sbir:proposal status for diagnostics. PES session checker may recover from the .bak backup."

#### 2: Past Deadline -- Dr. Elena Vasquez returns to a proposal whose deadline was March 10, 2026. Today is March 18. `/sbir:continue` displays the normal wave status but includes a prominent "Deadline passed 8 days ago" warning. It still shows the next action -- the tool does not block based on deadline.

#### 3: Schema Version Mismatch -- Marcus Chen's state file has schema_version "1.0.0" but the plugin expects "2.0.0". `/sbir:continue` displays: WHAT: "State file uses an older schema version." WHY: "The plugin was updated but the state file was not migrated." DO: "Run /sbir:proposal status to check compatibility."

### UAT Scenarios (BDD)
#### Scenario: Corrupted proposal state file
Given Phil Santos has a company profile
And .sbir/proposal-state.json exists but contains invalid JSON
When Phil runs /sbir:continue
Then the system displays an error following the what/why/do pattern
And the WHAT explains the state file cannot be read
And the WHY explains possible corruption from interrupted write
And the DO suggests /sbir:proposal status and mentions PES backup recovery

#### Scenario: Deadline has passed
Given Dr. Elena Vasquez has proposal "N00014-26-001" active in Wave 4
And the deadline was 8 days ago
When Elena runs /sbir:continue
Then the system displays normal wave progress information
And includes a prominent warning that the deadline has passed
And still suggests the next action (does not block)

#### Scenario: Deadline at critical threshold
Given Phil Santos has proposal "AF243-001" active in Wave 4
And the deadline is 3 days away
When Phil runs /sbir:continue
Then the system displays normal wave progress
And includes a critical deadline warning with 3 days remaining
And the warning is visually distinct from standard output

### Acceptance Criteria
- [ ] Corrupted state file produces what/why/do error message (no stack traces)
- [ ] Past-deadline state produces a warning but does not block progress suggestions
- [ ] 3-day deadline threshold produces critical warning
- [ ] 7-day deadline threshold produces standard warning
- [ ] Schema version mismatch produces informative message with migration guidance
- [ ] All error messages follow the what/why/do pattern established in the architecture

### Technical Notes
- Error handling is the responsibility of the continue command/agent, not PES
- PES session checker runs at SessionStart and may recover corrupt state before continue runs
- Deadline computation: parse topic.deadline as ISO 8601, subtract from current date
- Past deadline = negative days_remaining; display as "Deadline passed N days ago"

### Dependencies
- All previous US-CONT stories (error handling applies across all detection paths)
- PES session checker (may recover corrupt state before continue is invoked)

### Job Story Traceability
- JS-01: Resume After Session Break (error conditions during resume)
- JS-04: Resume Mid-Wave Work (deadline awareness during mid-wave resume)

---

# Definition of Ready Validation

## US-CONT-01: Continue From No Setup

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | Phil Santos, first-time user, bare error unhelpful, needs welcoming entry point |
| User/persona identified | PASS | First-time SBIR plugin user, just installed, no documentation read |
| 3+ domain examples | PASS | First install, plugin reinstall, wrong directory (3 examples) |
| UAT scenarios (3-7) | PASS | 3 scenarios covering no config, stale corpus, and non-project directory |
| AC derived from UAT | PASS | 5 criteria derived from scenarios |
| Right-sized | PASS | 1 day effort, 3 scenarios, single detection path |
| Technical notes | PASS | Read-only, profile and state paths documented, no new Python code |
| Dependencies tracked | PASS | /sbir:setup exists (delivered) |

### DoR Status: PASSED

## US-CONT-02: Continue From Partial Setup

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | Phil Santos, quit setup early, tedious to re-walk all steps |
| User/persona identified | PASS | Returning user with partial setup, profile exists, corpus missing |
| 3+ domain examples | PASS | Profile only, profile+corpus, profile with inactive SAM.gov (3 examples) |
| UAT scenarios (3-7) | PASS | 4 scenarios: no corpus, corpus+no API, skip selection, continue selection |
| AC derived from UAT | PASS | 6 criteria derived from scenarios |
| Right-sized | PASS | 1 day effort, 4 scenarios |
| Technical notes | PASS | Profile path, corpus check, API key check, completeness threshold documented |
| Dependencies tracked | PASS | US-CONT-01 (detection order), /sbir:setup (delivered) |

### DoR Status: PASSED

## US-CONT-03: Continue With No Active Proposal

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | Phil Santos, configured but no proposal, unhelpful bare "no proposal" message |
| User/persona identified | PASS | Configured user without active proposal, setup complete |
| 3+ domain examples | PASS | Ready to start, different directory, previous proposal elsewhere (3 examples) |
| UAT scenarios (3-7) | PASS | 3 scenarios: complete setup, zero corpus, missing corpus directory |
| AC derived from UAT | PASS | 5 criteria derived from scenarios |
| Right-sized | PASS | 1 day effort, 3 scenarios |
| Technical notes | PASS | Profile read, corpus count, read-only behavior documented |
| Dependencies tracked | PASS | US-CONT-01, US-CONT-02 (detection priority), existing commands (delivered) |

### DoR Status: PASSED

## US-CONT-04: Continue Mid-Wave

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | Phil Santos, partway through Wave 1, cannot remember within-wave progress |
| User/persona identified | PASS | Active proposal user mid-wave, completed some tasks, needs clarity |
| 3+ domain examples | PASS | Wave 1 partial, Wave 4 multi-volume, Wave 0 go pending, Wave 0 approach pending (4 examples) |
| UAT scenarios (3-7) | PASS | 5 scenarios covering Wave 1, Wave 4 volumes, Wave 0 states, async TPOC |
| AC derived from UAT | PASS | 7 criteria derived from scenarios |
| Right-sized | PASS | 2-3 days effort (most complex story), 5 scenarios |
| Technical notes | PASS | Wave-specific state fields, routing table, deadline thresholds documented |
| Dependencies tracked | PASS | US-CONT-01/02/03, wave-agent-mapping skill, proposal-state-schema |

### DoR Status: PASSED

## US-CONT-05: Continue Between Waves

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | Phil Santos, approved gate, does not remember next wave's purpose or command |
| User/persona identified | PASS | Active proposal user between waves, exit gate approved |
| 3+ domain examples | PASS | Wave 1->2, Wave 3->4, Wave 7->8 (3 examples) |
| UAT scenarios (3-7) | PASS | 3 scenarios: Wave 1->2, Wave 7->8, deadline warning during transition |
| AC derived from UAT | PASS | 6 criteria derived from scenarios |
| Right-sized | PASS | 1 day effort, 3 scenarios |
| Technical notes | PASS | Wave descriptions source, gate verification, transition detection documented |
| Dependencies tracked | PASS | US-CONT-04, wave-agent-mapping skill |

### DoR Status: PASSED

## US-CONT-06: Continue Post-Submission and Completion

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | Phil Santos, submitted proposal, forgets debrief step, needs lifecycle closure |
| User/persona identified | PASS | User with submitted or completed proposal |
| 3+ domain examples | PASS | Post-submission debrief pending, lifecycle complete, archived no-go (3 examples) |
| UAT scenarios (3-7) | PASS | 4 scenarios: submitted, complete, archived, deferred |
| AC derived from UAT | PASS | 7 criteria derived from scenarios |
| Right-sized | PASS | 1 day effort, 4 scenarios |
| Technical notes | PASS | Archived field, go_no_go values, wave completion detection documented |
| Dependencies tracked | PASS | US-CONT-04/05, /sbir:proposal debrief ingest (delivered) |

### DoR Status: PASSED

## US-CONT-07: Continue With Error Handling

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | Phil Santos, corrupted state or past deadline, needs clear actionable errors |
| User/persona identified | PASS | Any user encountering error conditions |
| 3+ domain examples | PASS | Corrupted state, past deadline, schema mismatch (3 examples) |
| UAT scenarios (3-7) | PASS | 3 scenarios: corrupt state, past deadline, critical deadline threshold |
| AC derived from UAT | PASS | 6 criteria derived from scenarios |
| Right-sized | PASS | 1 day effort, 3 scenarios |
| Technical notes | PASS | Error responsibility, PES interaction, deadline computation documented |
| Dependencies tracked | PASS | All US-CONT stories, PES session checker |

### DoR Status: PASSED

---

# Story-to-Job Traceability Matrix

| Story | Job Stories | Opportunity Score |
|-------|-----------|------------------|
| US-CONT-01 | JS-02 | 12.0 |
| US-CONT-02 | JS-03 | 10.5 |
| US-CONT-03 | JS-02 | 12.0 |
| US-CONT-04 | JS-01, JS-04 | 16.0, 13.5 |
| US-CONT-05 | JS-05 | 12.0 |
| US-CONT-06 | JS-06 | 11.5 |
| US-CONT-07 | JS-01, JS-04 | 16.0, 13.5 |

# MoSCoW Prioritization

| Priority | Stories | Rationale |
|----------|---------|-----------|
| Must Have | US-CONT-01, US-CONT-03, US-CONT-04 | Core value: detect no-setup, no-proposal, and mid-wave states. Without these, the command has no purpose. |
| Must Have | US-CONT-07 | Error handling is non-negotiable for any user-facing command. |
| Should Have | US-CONT-05, US-CONT-06 | Between-waves and post-submission are important lifecycle states but less frequent than mid-wave. |
| Should Have | US-CONT-02 | Partial setup detection improves UX but users can fall through to setup or no-proposal paths. |
