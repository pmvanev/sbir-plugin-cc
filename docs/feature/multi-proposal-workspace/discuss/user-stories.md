<!-- markdownlint-disable MD024 -->

# User Stories: Multi-Proposal Workspace

All stories trace to JTBD analysis in `jtbd-analysis.md`. Job story references use JS-MPW-{nn} format.

---

## US-MPW-001: Start Additional Proposal in Existing Workspace

### Problem

Phil Santos is an engineer who writes 2-3 SBIR proposals per year for Santos Engineering LLC. He finds it risky to start a second proposal because running `/proposal new` would clobber his existing `.sbir/proposal-state.json` and `artifacts/` directory. Today he works around this by creating a separate project directory for each proposal, which forces him to re-ingest his corpus and manage partner profiles in multiple places.

### Who

- Solo SBIR proposal writer | Has one active proposal in progress | Wants to evaluate a new solicitation without disrupting existing work

### Solution

When Phil runs `/proposal new` in a workspace that already contains proposals, the command creates a per-proposal namespace under `.sbir/proposals/{topic-id}/` and `artifacts/{topic-id}/`. The existing proposal is untouched. Shared resources (corpus, company profile, partners) remain at their current locations and are accessible to all proposals.

### Domain Examples

#### 1: Happy Path -- Phil starts N244-012 while AF263-042 is in Wave 3

Phil Santos has proposal AF263-042 ("Compact Directed Energy for Maritime UAS Defense") in Wave 3 with 27 days to deadline. He downloads solicitation N244-012.pdf ("Autonomous Underwater Vehicle Navigation") and runs `/sbir:proposal new ./solicitations/N244-012.pdf`. The plugin creates `.sbir/proposals/n244-012/proposal-state.json`, sets the active proposal to `n244-012`, and proceeds with fit scoring. Phil's AF263-042 state at `.sbir/proposals/af263-042/proposal-state.json` is byte-identical before and after. The shared corpus of 47 documents is listed as available for the new proposal.

#### 2: Edge Case -- First proposal in fresh workspace creates multi-proposal layout

Phil Santos has his company profile configured but no proposals yet. He runs `/sbir:proposal new ./solicitations/AF263-042.pdf`. The plugin creates `.sbir/proposals/af263-042/` (not the legacy `.sbir/proposal-state.json` at root). The `.sbir/active-proposal` file is created containing `af263-042`. This ensures all new workspaces are multi-proposal-ready from the start.

#### 3: Error/Boundary -- Namespace collision with existing proposal

Phil Santos has an active proposal AF263-042. He receives a resubmission solicitation for the same topic. When he runs `/sbir:proposal new ./solicitations/AF263-042-resubmit.pdf`, the extracted topic ID `af263-042` collides with the existing namespace. The command fails with a clear error: "A proposal with topic ID 'af263-042' already exists. Use `--name af263-042-v2` to create a differently-named proposal."

### UAT Scenarios (BDD)

#### Scenario: Create second proposal preserving existing proposal state

Given Phil Santos has an active proposal AF263-042 "Compact Directed Energy" in Wave 3
And the workspace has multi-proposal layout at ".sbir/proposals/"
And the shared corpus contains 47 documents
When Phil runs "/sbir:proposal new ./solicitations/N244-012.pdf"
Then a new namespace "n244-012" is created at ".sbir/proposals/n244-012/"
And ".sbir/proposals/n244-012/proposal-state.json" exists with topic ID "N244-012"
And ".sbir/proposals/af263-042/proposal-state.json" is unchanged
And the active proposal is set to "n244-012"
And the output lists shared resources: corpus (47 documents), company profile, partners

#### Scenario: First proposal in workspace creates multi-proposal layout

Given Phil Santos has a company profile at "~/.sbir/company-profile.json"
And no ".sbir/" directory exists in the workspace
When Phil runs "/sbir:proposal new ./solicitations/AF263-042.pdf"
Then ".sbir/proposals/af263-042/" is created
And ".sbir/active-proposal" contains "af263-042"
And no ".sbir/proposal-state.json" is created at root

#### Scenario: Namespace collision produces helpful error

Given Phil Santos has an active proposal AF263-042
When Phil runs "/sbir:proposal new" with a solicitation whose topic ID is "af263-042"
Then the command fails with error "A proposal with topic ID 'af263-042' already exists"
And the error suggests "--name af263-042-v2"
And no files are created or modified

#### Scenario: Custom namespace via --name flag

Given Phil Santos has an active proposal AF263-042
When Phil runs "/sbir:proposal new ./solicitations/AF263-042-resubmit.pdf --name af263-042-resub"
Then a new namespace "af263-042-resub" is created
And the proposal state records the original topic ID "AF263-042" and namespace "af263-042-resub"

### Acceptance Criteria

- [ ] Creating a new proposal in a workspace with existing proposals does not modify existing proposal state files
- [ ] New proposals are namespaced under `.sbir/proposals/{topic-id}/` and `artifacts/{topic-id}/`
- [ ] Fresh workspaces use multi-proposal layout from the first proposal
- [ ] Namespace collisions produce a clear error with `--name` guidance
- [ ] Shared resources (corpus, company profile, partners) are listed as available during new proposal creation
- [ ] Active proposal is automatically set to the newly created proposal

### Technical Notes

- The topic ID is extracted from the solicitation during parsing (existing behavior). It becomes the default namespace.
- The `--name` flag overrides the namespace but preserves the original topic ID in state.
- `JsonStateAdapter` already accepts `state_dir` as a constructor parameter -- the change is in how the hook adapter and orchestrator resolve `state_dir`.
- Dependency: US-MPW-004 (path resolution layer) should be implemented first or concurrently.

---

## US-MPW-002: Multi-Proposal Dashboard

### Problem

Phil Santos is an engineer who returns to his workspace after days away and has 2 proposals at different lifecycle stages with different deadlines. He finds it impossible to see both proposals at once -- he would have to mentally track which directories contain which proposals. Today he relies on memory and directory names, which breaks down when deadlines overlap.

### Who

- Solo SBIR proposal writer | Has 2-3 active proposals | Returns after days away needing quick orientation

### Solution

The `/sbir:continue` command detects multi-proposal layout and displays a table of all proposals with topic ID, title, current wave, deadline, and status. Active and completed proposals are separated. The closest deadline drives the suggested action. The currently active proposal is indicated.

### Domain Examples

#### 1: Happy Path -- Phil has two active proposals at different stages

Phil Santos returns after a long weekend. He has AF263-042 in Wave 3 (deadline April 15, 27 days) and N244-012 in Wave 0 (deadline May 30, 72 days). He runs `/sbir:continue`. The dashboard shows both proposals in a table, with AF263-042's closer deadline highlighted in the suggestion: "AF263-042 has a closer deadline (27 days). Consider: `/sbir:proposal switch af263-042`."

#### 2: Edge Case -- One active, one completed proposal

Phil has submitted AF263-042 and is working on N244-012. The dashboard shows N244-012 under "Active Proposals" and AF263-042 under "Completed Proposals" with its submission date. No switch suggestion since only one is active.

#### 3: Error/Boundary -- One proposal has corrupted state

Phil has two proposals. AF263-042's state file is corrupted (invalid JSON). The dashboard shows N244-012 normally and shows AF263-042 with an error indicator: "[!!] AF263-042 -- state file corrupted. Run `/sbir:proposal status` for recovery." The dashboard does not crash.

### UAT Scenarios (BDD)

#### Scenario: Dashboard shows multiple proposals with deadline-based suggestion

Given Phil Santos has proposal AF263-042 in Wave 3 with deadline "2026-04-15" (27 days)
And Phil has proposal N244-012 in Wave 0 with deadline "2026-05-30" (72 days)
And the active proposal is "n244-012"
When Phil runs "/sbir:continue"
Then the dashboard shows a table with both proposals
And the suggested action mentions AF263-042 has the closer deadline
And "Currently active: n244-012" is displayed

#### Scenario: Dashboard separates active and completed proposals

Given Phil Santos has submitted proposal AF263-042 (Wave 8 complete, submitted 2026-04-14)
And Phil has active proposal N244-012 in Wave 1
When Phil runs "/sbir:continue"
Then AF263-042 appears under "Completed Proposals" with "Submitted 2026-04-14"
And N244-012 appears under "Active Proposals"

#### Scenario: Dashboard handles corrupted proposal gracefully

Given Phil Santos has proposal N244-012 with valid state
And proposal AF263-042 has corrupted state (invalid JSON)
When Phil runs "/sbir:continue"
Then N244-012 is displayed normally
And AF263-042 shows "[!!] State corrupted" with recovery guidance
And the dashboard completes without crashing

#### Scenario: Single proposal shows familiar display

Given Phil Santos has only one proposal AF263-042 in Wave 2
When Phil runs "/sbir:continue"
Then the output resembles the current single-proposal display
And no "switch" suggestion is shown

### Acceptance Criteria

- [ ] Dashboard displays a table of all proposals with topic ID, title, wave, deadline, and status
- [ ] Active and completed proposals are visually separated
- [ ] Suggested action references the proposal with the closest deadline
- [ ] Currently active proposal is indicated
- [ ] Corrupted state for one proposal does not crash the dashboard
- [ ] Single-proposal workspaces show a familiar (non-table) display

### Technical Notes

- The continue agent enumerates `.sbir/proposals/*/proposal-state.json` to discover all proposals.
- Deadline sorting is computed at display time.
- The `continue-detection` skill needs a new detection priority for multi-proposal workspaces (insert between "no proposal" and "archived" checks).
- Read-only operation -- no state modifications.
- Dependency: US-MPW-001 (multi-proposal layout must exist)

---

## US-MPW-003: Switch Active Proposal Context

### Problem

Phil Santos is an engineer working on one proposal when he needs to switch to another -- perhaps a TPOC call just happened for a different topic, or the closer deadline demands attention. He finds it error-prone to issue commands without knowing which proposal they affect. Today, with separate directories, he `cd`s to the right one -- but in a shared workspace, he needs an explicit mechanism.

### Who

- Solo SBIR proposal writer | Has multiple proposals in one workspace | Needs to redirect all commands to a specific proposal

### Solution

A `/sbir:proposal switch <topic-id>` command that updates the active proposal pointer, immediately shows the target proposal's status summary, and suggests the next action. The switch confirmation makes it unambiguous which proposal is now active.

### Domain Examples

#### 1: Happy Path -- Phil switches from N244-012 to AF263-042

Phil Santos is working on N244-012 but realizes AF263-042's deadline is closer. He runs `/sbir:proposal switch af263-042`. The output confirms: "Switched from: N244-012 (AUV Navigation). Switched to: AF263-042 (Compact Directed Energy)." It shows AF263-042's current wave (3), deadline (27 days), task checklist, and suggests `/sbir:proposal wave outline`.

#### 2: Edge Case -- Phil switches to an already-active proposal

Phil runs `/sbir:proposal switch af263-042` when AF263-042 is already active. The command responds: "AF263-042 is already the active proposal." and shows the current status summary. No state changes occur.

#### 3: Error/Boundary -- Phil types a nonexistent topic ID

Phil runs `/sbir:proposal switch xyz-999`. The command fails: "No proposal found with topic ID 'xyz-999'. Available proposals: af263-042, n244-012." Phil sees the correct IDs and retries.

### UAT Scenarios (BDD)

#### Scenario: Switch active proposal and see status summary

Given Phil Santos has active proposal N244-012
And proposal AF263-042 exists in Wave 3 with deadline "2026-04-15" (27 days)
When Phil runs "/sbir:proposal switch af263-042"
Then ".sbir/active-proposal" contains "af263-042"
And the output shows "Switched from: N244-012" and "Switched to: AF263-042"
And the AF263-042 status summary is displayed (wave, deadline, task checklist)
And the next suggested command is shown

#### Scenario: Switch to nonexistent proposal shows available options

Given Phil Santos has proposals AF263-042 and N244-012
When Phil runs "/sbir:proposal switch xyz-999"
Then the command fails with "No proposal found with topic ID 'xyz-999'"
And the error lists "Available proposals: af263-042, n244-012"

#### Scenario: Switch to already-active proposal is idempotent

Given Phil Santos has active proposal AF263-042
When Phil runs "/sbir:proposal switch af263-042"
Then the output confirms "AF263-042 is already the active proposal"
And the current status summary is displayed
And no files are modified

#### Scenario: Switch to completed proposal for debrief access

Given Phil Santos has completed proposal AF263-042 (submitted 2026-04-14)
And Phil has active proposal N244-012
When Phil runs "/sbir:proposal switch af263-042"
Then the active proposal changes to AF263-042
And the status shows "Submitted (awaiting debrief)"
And Wave 9 commands are indicated as available

### Acceptance Criteria

- [ ] Switch command updates `.sbir/active-proposal` to the target proposal
- [ ] Switch confirmation shows the from/to proposals and target status summary
- [ ] Nonexistent topic ID produces error listing available proposals
- [ ] Switching to already-active proposal is idempotent with status display
- [ ] Completed proposals are switchable for Wave 9 (debrief) access

### Technical Notes

- The switch command reads `.sbir/active-proposal`, validates target exists in `.sbir/proposals/`, writes new value.
- Status summary after switch reuses the continue-detection skill's mid-wave display logic.
- Dependency: US-MPW-001 (multi-proposal layout), US-MPW-004 (path resolution)

---

## US-MPW-004: Proposal-Scoped Path Resolution

### Problem

Phil Santos is an engineer whose plugin currently reads state from a hardcoded `.sbir/proposal-state.json` path and writes artifacts to `artifacts/wave-N-name/`. In a multi-proposal workspace, every component that reads or writes state and artifacts must resolve paths relative to the active proposal namespace. If path resolution is inconsistent, commands could read one proposal's state and write to another proposal's artifacts.

### Who

- Solo SBIR proposal writer | Uses multi-proposal workspace | Expects all commands to operate on the correct proposal without manual path management

### Solution

A path resolution layer that reads `.sbir/active-proposal` and derives the correct state directory (`.sbir/proposals/{active}/`) and artifact directory (`artifacts/{active}/`) for all downstream consumers. The hook adapter, state adapter, and agent dispatch all use this resolution. Legacy workspaces (no `.sbir/proposals/`) fall back to the root paths.

### Domain Examples

#### 1: Happy Path -- All paths resolve to active proposal

Phil Santos has active proposal AF263-042. The hook adapter reads `.sbir/active-proposal` -> `af263-042`, resolves state_dir to `.sbir/proposals/af263-042/`, and passes it to the enforcement engine. The orchestrator dispatches the writer agent with artifact base `artifacts/af263-042/`. State reads and artifact writes are consistent.

#### 2: Edge Case -- Legacy workspace with no .sbir/proposals/

Phil Santos has an older workspace with `.sbir/proposal-state.json` at root and no `.sbir/proposals/` directory. The path resolver detects legacy layout and returns `.sbir/` as state_dir and `artifacts/` as artifact base. All commands work identically to the current behavior.

#### 3: Error/Boundary -- Active proposal file missing in multi-proposal workspace

Phil Santos has `.sbir/proposals/` with two proposals but `.sbir/active-proposal` is missing (perhaps deleted accidentally). The path resolver detects this state and returns a clear error: "No active proposal selected. Available: af263-042, n244-012. Run `/sbir:proposal switch <topic-id>`."

### UAT Scenarios (BDD)

#### Scenario: Path resolution uses active proposal namespace

Given Phil Santos has active proposal "af263-042" in a multi-proposal workspace
When any component requests the state directory
Then the resolved path is ".sbir/proposals/af263-042/"
And when any component requests the artifact base directory
Then the resolved path is "artifacts/af263-042/"

#### Scenario: Legacy workspace falls back to root paths

Given Phil Santos has a workspace with ".sbir/proposal-state.json" at root
And no ".sbir/proposals/" directory exists
When any component requests the state directory
Then the resolved path is ".sbir/"
And when any component requests the artifact base directory
Then the resolved path is "artifacts/"

#### Scenario: Missing active-proposal file produces clear error

Given Phil Santos has ".sbir/proposals/" with proposals "af263-042" and "n244-012"
And ".sbir/active-proposal" does not exist
When any component requests the state directory
Then a clear error is returned listing available proposals
And suggesting "/sbir:proposal switch <topic-id>"

#### Scenario: PES hook adapter resolves active proposal for enforcement

Given Phil Santos has active proposal "n244-012"
And N244-012 is in Wave 0 with go_no_go "pending"
When a PES PreToolUse hook fires
Then the hook adapter reads ".sbir/active-proposal" to get "n244-012"
And loads state from ".sbir/proposals/n244-012/proposal-state.json"
And enforcement is scoped to N244-012 wave state

#### Scenario: Audit log entries tagged with proposal ID

Given Phil Santos has active proposal "af263-042"
When PES records an enforcement decision
Then the audit entry includes "proposal_id: af263-042"
And the audit log is written to ".sbir/proposals/af263-042/audit/"

### Acceptance Criteria

- [ ] Path resolution reads `.sbir/active-proposal` and derives state_dir and artifact base
- [ ] Legacy workspaces (no `.sbir/proposals/`) fall back to root paths transparently
- [ ] Missing `.sbir/active-proposal` in multi-proposal workspace produces clear error with available proposals
- [ ] PES hook adapter uses resolved paths for enforcement scoping
- [ ] Audit log entries include the active proposal ID

### Technical Notes

- The hook adapter's `main()` function currently hardcodes `state_dir = os.path.join(os.getcwd(), ".sbir")`. This must change to a resolution function.
- `JsonStateAdapter` already accepts `state_dir` as a constructor parameter -- no change needed there.
- Resolution function: check for `.sbir/proposals/` -> read `.sbir/active-proposal` -> derive paths. Else -> return `.sbir/` (legacy).
- Every agent markdown file that references `.sbir/` or `artifacts/` paths will need updates to use the orchestrator-provided resolved path.
- This is the foundational story -- US-MPW-001, US-MPW-002, US-MPW-003 all depend on this.

---

## US-MPW-005: Backward-Compatible Legacy Support

### Problem

Phil Santos is an engineer who has existing single-proposal workspaces from before multi-proposal support was added. He finds it unacceptable if updating the plugin breaks his in-progress proposals. Today his workspace has `.sbir/proposal-state.json` at root and `artifacts/wave-N-name/` at root. These must continue working without forced migration.

### Who

- Existing plugin user | Has in-progress proposals in legacy layout | Expects plugin update to be non-breaking

### Solution

The plugin detects the workspace layout (multi-proposal vs legacy) and routes accordingly. Legacy workspaces work exactly as before -- no multi-proposal UI, no `.sbir/proposals/` directory created, no migration required. An optional `/proposal migrate` command is available for users who want to opt-in to multi-proposal layout.

### Domain Examples

#### 1: Happy Path -- Legacy workspace continues working unchanged

Phil Santos has an in-progress proposal in a legacy workspace (`.sbir/proposal-state.json` at root, `artifacts/wave-3-outline/` at root). He updates the plugin. He runs `/sbir:continue`. The output is identical to the current behavior -- single-proposal status display, no table, no "switch" suggestion. All wave commands read and write at root paths.

#### 2: Edge Case -- Opt-in migration from legacy to multi-proposal

Phil Santos decides to start a second proposal in his legacy workspace. He runs `/sbir:proposal new ./solicitations/new-topic.pdf`. The plugin detects the legacy layout and asks: "Single-proposal layout detected. Enable multi-proposal support? (m)igrate existing proposal into namespace / (s)tart a new workspace instead." Phil chooses migrate. The existing proposal is moved to `.sbir/proposals/{topic-id}/` and `artifacts/{topic-id}/`. The new proposal is created alongside it.

#### 3: Error/Boundary -- Migration preserves .bak safety net

During migration, Phil's existing `proposal-state.json` is copied to `.sbir/proposals/af263-042/proposal-state.json`. The original `.sbir/proposal-state.json` is renamed to `.sbir/proposal-state.json.migrated` (not deleted). If anything goes wrong, Phil can restore the original by renaming it back.

### UAT Scenarios (BDD)

#### Scenario: Legacy workspace works unchanged after plugin update

Given Phil Santos has a legacy workspace with ".sbir/proposal-state.json" at root
And "artifacts/wave-3-outline/" exists at root
When Phil runs "/sbir:continue"
Then the output matches current single-proposal behavior
And no ".sbir/proposals/" directory is created
And no multi-proposal UI elements appear

#### Scenario: Opt-in migration when starting second proposal in legacy workspace

Given Phil Santos has a legacy workspace with proposal AF263-042
When Phil runs "/sbir:proposal new ./solicitations/N244-012.pdf"
Then the plugin detects legacy layout
And prompts: migrate or separate workspace
And if Phil chooses migrate, AF263-042 is moved to ".sbir/proposals/af263-042/"
And "artifacts/" contents are moved to "artifacts/af263-042/"
And the original ".sbir/proposal-state.json" is preserved as ".sbir/proposal-state.json.migrated"
And the new proposal N244-012 is created in the multi-proposal layout

#### Scenario: Migration preserves original files as safety net

Given Phil Santos chooses to migrate a legacy workspace
When the migration moves proposal-state.json to ".sbir/proposals/af263-042/"
Then ".sbir/proposal-state.json.migrated" exists as a backup
And Phil can restore legacy layout by renaming ".migrated" back

### Acceptance Criteria

- [ ] Legacy workspaces (`.sbir/proposal-state.json` at root) continue working identically after plugin update
- [ ] No `.sbir/proposals/` directory created in legacy workspaces during normal operations
- [ ] `/proposal new` in a legacy workspace prompts for migration before creating a second proposal
- [ ] Migration preserves the original state file as `.migrated` safety net
- [ ] All wave commands, status, and PES enforcement work in legacy mode

### Technical Notes

- Layout detection is the first check in path resolution (US-MPW-004).
- Migration is a separate code path from normal `proposal new` -- only triggered when legacy layout + new proposal requested.
- Migration moves: `.sbir/proposal-state.json` -> `.sbir/proposals/{topic-id}/proposal-state.json`, `.sbir/compliance-matrix.json` -> `.sbir/proposals/{topic-id}/compliance-matrix.json`, `artifacts/wave-*` -> `artifacts/{topic-id}/wave-*`.
- Dependency: US-MPW-004 (path resolution must support both layouts)

---

## US-MPW-006: Completed Proposal Lifecycle Management

### Problem

Phil Santos is an engineer who writes 2-3 proposals per year. Over time, his workspace would accumulate completed proposals. He finds it cluttering when old proposals take up as much visual space as active ones. But he also needs to access completed proposals for debrief (Wave 9) when evaluator feedback arrives months later. Today, with separate directories, completed proposals just sit in their directories.

### Who

- Solo SBIR proposal writer | Has a mix of active and completed proposals | Needs decluttered view without losing access

### Solution

The dashboard separates active and completed proposals. Completed proposals (Wave 8 done or `archived: true`) appear in a "Completed Proposals" section. When the last active proposal in a multi-proposal set completes, the active pointer auto-switches to the remaining active one (if exactly one) or prompts for selection (if multiple). Completed proposals remain fully accessible via `/proposal switch` for Wave 9 debrief.

### Domain Examples

#### 1: Happy Path -- Auto-switch after submission with one remaining active proposal

Phil Santos submits AF263-042 (Wave 8 complete). He has one remaining active proposal, N244-012. The active proposal auto-switches to N244-012. The dashboard shows AF263-042 under "Completed" and N244-012 under "Active" with the note "Active proposal auto-switched after AF263-042 submission."

#### 2: Edge Case -- Multiple active proposals remain after one completes

Phil Santos has three proposals: AF263-042, N244-012, and DA-26-003. He submits AF263-042. Two active proposals remain. The plugin does not auto-switch -- instead it prompts: "AF263-042 submitted. Choose active proposal: (1) N244-012 (2) DA-26-003." Phil selects N244-012.

#### 3: Error/Boundary -- All proposals completed

Phil Santos has submitted all his proposals for this cycle. The dashboard shows only completed proposals. The suggested action is: "No active proposals. Start a new one with `/sbir:proposal new` or wait for debrief feedback."

### UAT Scenarios (BDD)

#### Scenario: Auto-switch to sole remaining active proposal

Given Phil Santos has active proposals AF263-042 and N244-012
And Phil completes Wave 8 submission for AF263-042
When the submission is confirmed
Then the active proposal auto-switches to "n244-012"
And the output confirms "Active proposal switched to N244-012"

#### Scenario: Prompt for selection when multiple active proposals remain

Given Phil Santos has active proposals AF263-042, N244-012, and DA-26-003
And Phil completes Wave 8 submission for AF263-042
When the submission is confirmed
Then the output prompts Phil to choose between N244-012 and DA-26-003
And the active-proposal file is not updated until Phil selects

#### Scenario: All proposals completed shows guidance

Given Phil Santos has submitted all proposals in the workspace
When Phil runs "/sbir:continue"
Then only the "Completed Proposals" section is shown
And the suggested action is to start a new proposal or wait for debrief

#### Scenario: Completed proposal accessible for debrief months later

Given Phil Santos submitted AF263-042 six months ago
And evaluator feedback has arrived
When Phil runs "/sbir:proposal switch af263-042"
Then the context switches to AF263-042
And the status shows "Submitted (awaiting debrief)"
And "/sbir:proposal debrief ingest" is available

### Acceptance Criteria

- [ ] Completed proposals (Wave 8 done or archived) appear in "Completed" section of dashboard
- [ ] Auto-switch occurs when exactly one active proposal remains after submission
- [ ] Selection prompt appears when multiple active proposals remain after submission
- [ ] Completed proposals are switchable for Wave 9 debrief access
- [ ] All-completed workspace shows guidance to start new proposal or await debrief

### Technical Notes

- "Completed" is determined by: `waves.8.status == "completed"` or `archived == true` or `go_no_go == "no-go"`.
- Auto-switch logic belongs in the orchestrator's submission confirmation flow.
- Debrief (Wave 9) operates on completed proposals identically to active ones -- the only difference is dashboard placement.
- Dependency: US-MPW-001 (multi-proposal layout), US-MPW-003 (switch command)

---

## Story Dependency Map

```
US-MPW-004 (Path Resolution)    <-- foundational, implement first
     |
     +-- US-MPW-001 (Create Additional Proposal)
     |        |
     |        +-- US-MPW-002 (Multi-Proposal Dashboard)
     |        |
     |        +-- US-MPW-003 (Switch Context)
     |        |        |
     |        |        +-- US-MPW-006 (Completed Proposal Lifecycle)
     |        |
     +-- US-MPW-005 (Backward Compatibility)
```

## MoSCoW Prioritization

| Story | Priority | Rationale |
|-------|----------|-----------|
| US-MPW-004 | Must Have | Foundational -- all other stories depend on path resolution |
| US-MPW-001 | Must Have | Core value -- ability to create multiple proposals |
| US-MPW-005 | Must Have | Non-negotiable -- existing workspaces must not break |
| US-MPW-003 | Must Have | Without switch, multi-proposal is unusable |
| US-MPW-002 | Should Have | Orientation is critical for usability but single-proposal status works as fallback |
| US-MPW-006 | Should Have | Improves long-term experience but not blocking for first 2-proposal use case |
