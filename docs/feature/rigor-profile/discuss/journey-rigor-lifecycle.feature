Feature: Rigor Profile Lifecycle
  As an SBIR proposal author managing proposals of varying strategic importance,
  I want to configure quality/cost tradeoffs per proposal through named rigor profiles,
  so I can invest maximum effort on must-win opportunities and conserve resources on exploratory work.

  Background:
    Given the SBIR proposal plugin is installed with 18 agents
    And all agents currently use "model: inherit" for model selection
    And the following rigor profiles are defined:
      | profile    | quality  | cost_per_wave | review_passes | critique_iterations |
      | lean       | Basic    | $2-5          | 1             | 0                   |
      | standard   | Balanced | $8-15         | 2             | 2                   |
      | thorough   | Deep     | $20-35        | 2             | 3                   |
      | exhaustive | Maximum  | $40-60        | 3             | 4                   |

  # ---- Step 1: Discover Rigor Profiles (Job 6) ----

  Scenario: New proposal defaults to standard rigor
    Given Dr. Elena Vasquez creates a new proposal from solicitation "AF243-001"
    When the proposal is created with fit score 85 and contract value $1.7M Phase II
    Then the proposal rigor is set to "standard"
    And the output mentions the default rigor profile
    And the proposal can proceed to Wave 0 without further rigor configuration

  Scenario: High-value proposal receives contextual rigor suggestion
    Given Dr. Elena Vasquez creates a new proposal from solicitation "AF243-001"
    When the proposal is created with fit score 85 and contract value $1.7M Phase II
    Then the output suggests considering "thorough" rigor
    And the suggestion references the high fit score and Phase II value
    And the suggestion includes how to compare profiles

  Scenario: Moderate-value proposal receives no upgrade suggestion
    Given Marcus Chen creates a new proposal from solicitation "N244-012"
    When the proposal is created with fit score 64 and contract value $250K Phase I
    Then the output shows the default rigor profile "standard"
    And the output suggests "lean" for exploratory screening
    And no suggestion to upgrade rigor is shown

  # ---- Step 2: Understand and Select Profile (Job 6, Job 1, Job 2) ----

  Scenario: View rigor profile comparison table
    Given Dr. Elena Vasquez has an active proposal "AF243-001" at "standard" rigor
    When she runs "/proposal rigor show"
    Then a comparison table is displayed with all available profiles
    And each profile row shows quality level, cost range, review passes, and critique iterations
    And the active profile "standard" is indicated
    And the output offers detail view with "/proposal rigor show <profile>"

  Scenario: View detailed profile configuration
    Given Dr. Elena Vasquez has an active proposal "AF243-001" at "standard" rigor
    When she runs "/proposal rigor show thorough"
    Then a detail view shows model tier per agent role
    And agent roles include strategist, writer, reviewer, researcher, compliance, and visual assets
    And review depth, critique loop limits, and iteration caps are shown
    And estimated cost per wave is displayed

  Scenario: Select thorough profile for must-win proposal
    Given Dr. Elena Vasquez has an active proposal "AF243-001" at "standard" rigor
    When she runs "/proposal rigor set thorough"
    Then the rigor is updated to "thorough"
    And a diff is displayed showing what changed from "standard" to "thorough"
    And the diff includes model tier changes per agent role
    And the output confirms existing artifacts are preserved

  # ---- Step 3: Execute Waves with Rigor Applied (Job 1) ----

  Scenario: Wave execution shows active rigor level
    Given Dr. Elena Vasquez has proposal "AF243-001" at "thorough" rigor
    When she runs Wave 1 strategy
    Then the wave header displays "Rigor: thorough"
    And each step shows the model tier being used
    And the reviewer runs the configured number of review passes

  Scenario: Agent resolves model from rigor profile, not hardcoded frontmatter
    Given Dr. Elena Vasquez has proposal "AF243-001" at "thorough" rigor
    When the writer agent is invoked during Wave 4 drafting
    Then the writer uses the model tier specified by the "thorough" profile for the writer role
    And the writer does not use a hardcoded model from its own frontmatter

  Scenario: Lean rigor reduces review depth during screening
    Given Marcus Chen has proposal "N244-015" at "lean" rigor
    When he runs Wave 0 topic analysis
    Then the wave header displays "Rigor: lean"
    And review passes are limited to 1 structural pass
    And critique loops are skipped entirely

  # ---- Step 4: Monitor Portfolio with Rigor Context (Job 4) ----

  Scenario: Status display shows rigor for active proposal
    Given Dr. Elena Vasquez has proposal "AF243-001" at "thorough" rigor
    When she runs "/proposal status"
    Then the active proposal line includes "Rigor: thorough"
    And rigor is displayed alongside fit score and contract value

  Scenario: Status display shows rigor for all proposals in workspace
    Given the workspace contains:
      | topic_id   | name                    | rigor    | fit_score |
      | AF243-001  | Compact Directed Energy | thorough | 85        |
      | N244-012   | AUV Navigation          | standard | 72        |
      | DA244-003  | Sensor Fusion           | lean     | 58        |
    When Dr. Elena Vasquez runs "/proposal status"
    Then each proposal in the listing shows its rigor level
    And rigor levels are visible in the portfolio summary

  Scenario: Switching proposals loads target proposal rigor
    Given Dr. Elena Vasquez has "AF243-001" active at "thorough" rigor
    And proposal "N244-012" exists at "standard" rigor
    When she runs "/proposal switch n244-012"
    Then the active proposal becomes "N244-012"
    And the displayed rigor is "standard"
    And subsequent wave commands use "standard" rigor settings

  # ---- Step 5: Adjust Rigor Mid-Proposal (Job 4, Job 2) ----

  Scenario: Change rigor mid-proposal preserves existing artifacts
    Given Dr. Elena Vasquez has proposal "DA244-003" at "lean" rigor
    And Waves 0-2 have been completed at "lean" rigor
    When she runs "/proposal rigor set standard"
    Then the rigor is updated to "standard"
    And the output states that Waves 0-2 artifacts are preserved
    And the output states that Wave 3 onward will use "standard" settings
    And no automatic re-run of completed waves occurs

  Scenario: Rigor change records history for debrief
    Given Dr. Elena Vasquez has proposal "DA244-003" at "lean" rigor
    And the proposal is currently on Wave 3
    When she runs "/proposal rigor set standard"
    Then the rigor history records the change with timestamp
    And the history entry includes previous profile "lean", new profile "standard", and wave number 3

  Scenario: Rigor change suggests re-processing earlier sections
    Given Dr. Elena Vasquez has proposal "DA244-003" at "lean" rigor
    And Waves 0-2 have been completed at "lean" rigor
    When she runs "/proposal rigor set standard"
    Then the output includes a note about earlier waves produced at "lean"
    And the output suggests "/proposal iterate <section>" for selective re-processing

  # ---- Step 6: Cost-Conscious Exploration (Job 2) ----

  Scenario: Marcus screens six topics at lean rigor
    Given Marcus Chen has created 6 proposals for Navy topics at "lean" rigor
    When he runs Wave 0 on each proposal
    Then each Wave 0 run uses basic model tier for all agents
    And review passes are limited to 1 per proposal
    And the total cost across 6 topics is in the $12-30 range

  Scenario: Marcus upgrades promising topic from lean to standard
    Given Marcus Chen has proposal "N244-015" at "lean" rigor
    And Wave 0 shows a fit score of 78 (higher than initially expected)
    When he runs "/proposal rigor set standard"
    Then the rigor is updated from "lean" to "standard"
    And subsequent waves use balanced model tier and 2 review passes

  # ---- Step 7: Debrief with Rigor Context (Job 1) ----

  Scenario: Debrief includes rigor summary for consistent profile
    Given Dr. Elena Vasquez has completed all 10 waves for "AF243-001" at "thorough" rigor
    When she runs "/proposal debrief"
    Then the debrief includes a rigor summary section
    And the summary shows profile "thorough" used throughout
    And the summary shows total review cycles and average per section
    And the summary shows critique loop count and average iterations
    And the summary states no profile changes occurred

  Scenario: Debrief includes rigor change history
    Given Dr. Elena Vasquez has completed proposal "DA244-003"
    And the rigor was changed from "lean" to "standard" at Wave 3
    When she runs "/proposal debrief"
    Then the debrief rigor summary shows the profile change
    And the change is annotated with the wave number where it occurred

  # ---- Error Paths ----

  Scenario: Unknown profile name returns helpful error
    Given Dr. Elena Vasquez has an active proposal "AF243-001"
    When she runs "/proposal rigor set ultra"
    Then an error message states "ultra" is not a recognized profile
    And the error lists all available profiles: lean, standard, thorough, exhaustive
    And the error suggests "/proposal rigor show" to compare

  Scenario: Setting rigor without active proposal returns guidance
    Given no proposal is currently active in the workspace
    When the user runs "/proposal rigor set thorough"
    Then an error message states no active proposal exists
    And the error suggests "/proposal new" or "/proposal switch"

  Scenario: Setting rigor to current profile is a no-op
    Given Dr. Elena Vasquez has proposal "AF243-001" at "thorough" rigor
    When she runs "/proposal rigor set thorough"
    Then the output confirms rigor is already "thorough"
    And no changes are made to rigor-profile.json
    And no history entry is recorded
