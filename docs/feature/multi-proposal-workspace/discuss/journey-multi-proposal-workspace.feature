Feature: Multi-Proposal Workspace
  As Phil Santos, an engineer writing 2-3 SBIR proposals per year,
  I want to manage multiple proposals from a single workspace
  so I can share resources, track all deadlines, and switch between proposals easily.

  Background:
    Given Phil Santos has a company profile at "~/.sbir/company-profile.json" for "Santos Engineering LLC"
    And Phil has partner profiles for CU Boulder, NDSU, and SWRI
    And the workspace corpus contains 47 documents from past proposals

  # ---- Step 1: Start Second Proposal ----

  Scenario: Create second proposal in existing workspace
    Given Phil has an active proposal AF263-042 "Compact Directed Energy" in Wave 3
    And the workspace uses multi-proposal layout with ".sbir/proposals/"
    When Phil runs "/sbir:proposal new ./solicitations/N244-012.pdf"
    Then a new proposal namespace "n244-012" is created at ".sbir/proposals/n244-012/"
    And the proposal state file exists at ".sbir/proposals/n244-012/proposal-state.json"
    And the AF263-042 state file at ".sbir/proposals/af263-042/proposal-state.json" is unchanged
    And the active proposal is set to "n244-012"
    And the output shows existing proposals with AF263-042 listed
    And shared resources are listed: corpus (47 documents), company profile, partners

  Scenario: First proposal in workspace creates multi-proposal layout
    Given Phil has a company profile but no existing proposals
    When Phil runs "/sbir:proposal new ./solicitations/AF263-042.pdf"
    Then the multi-proposal layout is created at ".sbir/proposals/"
    And the proposal namespace "af263-042" is created
    And the active proposal is set to "af263-042"
    And the ".sbir/active-proposal" file contains "af263-042"

  Scenario: Proposal namespace collision rejected with guidance
    Given Phil has an active proposal AF263-042
    When Phil runs "/sbir:proposal new ./solicitations/AF263-042-resubmit.pdf"
    And the topic ID extracted is "af263-042"
    Then the command fails with a namespace collision error
    And the error suggests "--name af263-042-v2" to use a custom namespace

  # ---- Step 2: Orient Across All Proposals ----

  Scenario: Dashboard shows multiple proposals sorted by deadline proximity
    Given Phil has proposal AF263-042 in Wave 3 with deadline "2026-04-15"
    And Phil has proposal N244-012 in Wave 0 with deadline "2026-05-30"
    And the active proposal is "n244-012"
    When Phil runs "/sbir:continue"
    Then the dashboard shows a table with both proposals
    And the suggested action references AF263-042 because its deadline is closer
    And the "Currently active" indicator shows "n244-012"

  Scenario: Dashboard separates active and completed proposals
    Given Phil has submitted proposal AF263-042 (Wave 8 complete)
    And Phil has active proposal N244-012 in Wave 1
    When Phil runs "/sbir:continue"
    Then AF263-042 appears under "Completed Proposals" with submission date
    And N244-012 appears under "Active Proposals"
    And the suggested action references N244-012

  Scenario: Dashboard handles single proposal gracefully
    Given Phil has only one proposal AF263-042 in Wave 2
    When Phil runs "/sbir:continue"
    Then the dashboard shows AF263-042 as the only active proposal
    And no "switch" suggestion is shown
    And the output resembles the current single-proposal status display

  # ---- Step 3: Switch Active Proposal Context ----

  Scenario: Switch active proposal context
    Given Phil has active proposal N244-012
    And proposal AF263-042 exists in Wave 3 with deadline in 27 days
    When Phil runs "/sbir:proposal switch af263-042"
    Then the active proposal changes to "af263-042"
    And the ".sbir/active-proposal" file contains "af263-042"
    And the switch confirmation shows AF263-042 status summary
    And the suggested next command is shown

  Scenario: Switch to nonexistent proposal shows helpful error
    Given Phil has proposals AF263-042 and N244-012
    When Phil runs "/sbir:proposal switch xyz-999"
    Then the command fails with a clear error message
    And the error lists available proposals: "af263-042, n244-012"

  Scenario: Switch to already-active proposal is a no-op with confirmation
    Given Phil has active proposal AF263-042
    When Phil runs "/sbir:proposal switch af263-042"
    Then the output confirms AF263-042 is already active
    And the current status summary is displayed

  # ---- Step 4: Work in Active Context ----

  Scenario: Wave command operates on active proposal
    Given Phil has switched to proposal AF263-042
    And AF263-042 is in Wave 3
    When Phil runs "/sbir:proposal wave outline"
    Then the wave command reads state from ".sbir/proposals/af263-042/proposal-state.json"
    And artifacts are written to "artifacts/af263-042/wave-3-outline/"
    And the output header shows "AF263-042" as the active proposal

  Scenario: PES enforcement scoped to active proposal
    Given Phil has switched to proposal N244-012
    And N244-012 is in Wave 0 with go_no_go "pending"
    When Phil attempts a Wave 1 command
    Then PES blocks the command based on N244-012 state
    And the block message references N244-012 specifically

  Scenario: Status command shows active proposal context
    Given Phil has switched to proposal AF263-042
    When Phil runs "/sbir:proposal status"
    Then the status shows AF263-042 wave progress, deadline, and tasks
    And the output includes "Active proposal: AF263-042"

  # ---- Step 5: Complete and Archive ----

  Scenario: Completed proposal moves to archive section in dashboard
    Given Phil has submitted proposal AF263-042 (Wave 8 complete)
    And Phil has one remaining active proposal N244-012
    When Phil views the workspace dashboard
    Then AF263-042 appears under "Completed Proposals" with "Submitted" status
    And N244-012 appears under "Active Proposals"
    And the active proposal is automatically set to "n244-012"

  Scenario: Auto-switch when only one active proposal remains
    Given Phil has active proposals AF263-042 and N244-012
    And Phil completes Wave 8 for AF263-042
    When the submission is confirmed
    Then the active proposal auto-switches to "n244-012"
    And the switch is confirmed in the output

  Scenario: No auto-switch when multiple active proposals remain
    Given Phil has active proposals AF263-042, N244-012, and DA-26-003
    And Phil completes Wave 8 for AF263-042
    When the submission is confirmed
    Then the output prompts Phil to select the next active proposal
    And the active-proposal file is not changed until Phil selects

  # ---- Step 6: Return for Debrief ----

  Scenario: Switch to completed proposal for debrief
    Given Phil has completed proposal AF263-042 (submitted 6 months ago)
    And evaluator feedback file exists at "./feedback/af263-042-eval.pdf"
    When Phil runs "/sbir:proposal switch af263-042"
    Then the context switches to AF263-042
    And the status shows "Submitted (awaiting debrief)"
    And Wave 9 commands are available

  Scenario: Debrief artifacts written to correct namespace
    Given Phil has switched to completed proposal AF263-042
    When Phil runs "/sbir:proposal debrief ingest ./feedback/af263-042-eval.pdf"
    Then debrief artifacts are written to "artifacts/af263-042/wave-9-debrief/"
    And lessons learned are accessible from the shared corpus

  # ---- Backward Compatibility ----

  Scenario: Legacy single-proposal directory continues working
    Given Phil has a workspace with legacy layout (".sbir/proposal-state.json" at root)
    And no ".sbir/proposals/" directory exists
    When Phil runs "/sbir:continue"
    Then the output shows the single proposal status (current behavior)
    And no multi-proposal UI elements are displayed
    And no migration is forced

  Scenario: Legacy layout detected during proposal new
    Given Phil has a workspace with legacy layout
    When Phil runs "/sbir:proposal new ./solicitations/new-topic.pdf"
    Then the output offers migration: "Enable multi-proposal support? (m)igrate / (s)eparate directory"
    And if Phil chooses migrate, the existing proposal is moved to ".sbir/proposals/{topic-id}/"
    And if Phil chooses separate directory, the command suggests creating a new workspace

  Scenario: Fresh workspace gets multi-proposal layout from first proposal
    Given Phil has a company profile but no ".sbir/" directory
    When Phil runs "/sbir:proposal new ./solicitations/AF263-042.pdf"
    Then the multi-proposal layout is created automatically
    And the proposal is namespaced at ".sbir/proposals/af263-042/"

  # ---- Error Paths ----

  Scenario: No active proposal set in multi-proposal workspace
    Given Phil has proposals AF263-042 and N244-012
    And the ".sbir/active-proposal" file is missing or empty
    When Phil runs any proposal command
    Then the error shows "No active proposal selected"
    And lists available proposals
    And suggests "/sbir:proposal switch <topic-id>"

  Scenario: Active proposal points to deleted namespace
    Given the ".sbir/active-proposal" file contains "deleted-topic"
    And no ".sbir/proposals/deleted-topic/" directory exists
    When Phil runs "/sbir:continue"
    Then the error shows "Active proposal 'deleted-topic' not found"
    And lists available proposals
    And suggests switching to an existing proposal
