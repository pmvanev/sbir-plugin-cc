Feature: SBIR Continue -- Detect lifecycle position and resume

  As Phil Santos, a small business engineer returning to a proposal effort,
  I want /sbir:continue to detect where I left off and guide me to the next action,
  so I can resume productive work within seconds instead of re-orienting manually.

  Background:
    Given the SBIR proposal plugin is installed

  # --- Step 1: No Setup ---

  Scenario: First-time user with no configuration
    Given Phil Santos has just installed the SBIR plugin
    And no company profile exists at ~/.sbir/company-profile.json
    And no proposal state exists at .sbir/proposal-state.json
    When Phil runs /sbir:continue
    Then the system displays a welcome message explaining the setup wizard
    And suggests running /sbir:setup
    And the output includes estimated setup time of 10-15 minutes
    And no error messages are displayed

  # --- Step 2: Partial Setup ---

  Scenario: User with profile but no corpus or API key
    Given Phil Santos has a company profile for "Pacific Systems Engineering"
    And no corpus documents have been ingested
    And no GEMINI_API_KEY is configured
    When Phil runs /sbir:continue
    Then the system displays setup status with profile marked as ok
    And prerequisites are marked as ok
    And corpus is marked as incomplete
    And GEMINI_API_KEY is marked as not configured
    And the system offers three options: continue setup, skip to proposal, or quit

  Scenario: User with profile and corpus but no API key
    Given Phil Santos has a company profile for "Pacific Systems Engineering"
    And 12 corpus documents have been ingested
    And no GEMINI_API_KEY is configured
    When Phil runs /sbir:continue
    Then the system treats setup as functionally complete
    And displays no active proposal found
    And suggests starting a proposal

  # --- Step 3: No Active Proposal ---

  Scenario: Setup complete with no active proposal
    Given Phil Santos has a complete setup with 12 corpus documents
    And no proposal state file exists in the current directory
    When Phil runs /sbir:continue
    Then the system displays the company name "Pacific Systems Engineering"
    And displays "12 documents indexed"
    And displays "No active proposal found"
    And suggests /sbir:solicitation find and /sbir:proposal new

  # --- Step 4: Mid-Wave Resume ---

  Scenario: Wave 1 with compliance done and TPOC pending
    Given Phil Santos has proposal "AF243-001" active in Wave 1
    And the compliance matrix has 24 items extracted
    And TPOC status is "questions_generated"
    And strategy brief status is "not_started"
    And the deadline is 28 days away
    When Phil runs /sbir:continue
    Then the system displays "Wave 1: Requirements & Strategy"
    And shows compliance matrix as complete with 24 items
    And shows TPOC as pending call
    And shows strategy brief as not started
    And notes that TPOC call is optional
    And suggests running /sbir:proposal wave strategy

  Scenario: Wave 4 with mixed volume progress
    Given Phil Santos has proposal "AF243-001" active in Wave 4
    And the technical volume status is "approved"
    And the management volume status is "in_review" with 2 open items
    And the cost volume status is "not_started"
    And the deadline is 18 days away
    When Phil runs /sbir:continue
    Then the system displays "Wave 4: Drafting"
    And shows technical volume as approved
    And shows management volume as in review with 2 open items
    And shows cost volume as not started
    And suggests running /sbir:proposal iterate management
    And indicates cost volume drafting as the next step after review

  Scenario: Wave 0 with Go decision pending
    Given Phil Santos has proposal "AF243-001" active in Wave 0
    And go_no_go is "pending"
    And fit scoring has been computed
    When Phil runs /sbir:continue
    Then the system displays "Wave 0: Intelligence & Fit"
    And indicates that Go/No-Go decision is pending
    And suggests reviewing fit scoring results

  Scenario: Wave 0 with Go approved and approach selection pending
    Given Phil Santos has proposal "AF243-001" active in Wave 0
    And go_no_go is "go"
    And approach_selection status is "pending"
    When Phil runs /sbir:continue
    Then the system displays "Wave 0: Intelligence & Fit"
    And indicates that approach selection is pending
    And suggests running /sbir:proposal shape

  # --- Step 5: Between Waves ---

  Scenario: Wave 1 completed, Wave 2 not started
    Given Phil Santos has proposal "AF243-001"
    And Wave 1 status is "completed" with strategy brief approved
    And Wave 2 status is "not_started"
    And current_wave is 2
    And the deadline is 25 days away
    When Phil runs /sbir:continue
    Then the system displays wave progress showing Wave 1 as complete
    And marks Wave 2 as the current position
    And describes Wave 2 as "Research"
    And suggests running /sbir:proposal wave research

  Scenario: Wave 3 completed, Wave 4 not started
    Given Phil Santos has proposal "AF243-001"
    And Waves 0 through 3 are completed
    And Wave 4 status is "not_started"
    And current_wave is 4
    When Phil runs /sbir:continue
    Then the system displays wave progress showing Waves 0-3 as complete
    And describes Wave 4 as "Drafting"
    And suggests running /sbir:proposal draft technical

  # --- Step 6: Post-Submission ---

  Scenario: Proposal submitted, debrief pending
    Given Phil Santos has proposal "AF243-001"
    And Waves 0 through 8 are completed
    And Wave 9 status is "not_started"
    When Phil runs /sbir:continue
    Then the system confirms the proposal has been submitted
    And suggests debrief ingestion with /sbir:proposal debrief ingest
    And offers starting a new proposal as an alternative

  # --- Step 7: Lifecycle Complete ---

  Scenario: All waves completed including debrief
    Given Phil Santos has proposal "AF243-001"
    And all waves 0 through 9 are completed
    When Phil runs /sbir:continue
    Then the system confirms the lifecycle is complete
    And displays "All 10 waves finished"
    And suggests starting a new proposal with /sbir:solicitation find or /sbir:proposal new

  # --- Error and Edge Cases ---

  Scenario: Corrupted proposal state file
    Given Phil Santos has a company profile
    And .sbir/proposal-state.json exists but contains invalid JSON
    When Phil runs /sbir:continue
    Then the system displays an error using the what/why/do pattern
    And suggests running /sbir:proposal status for diagnostics
    And mentions that PES session checker may recover from backup

  Scenario: Deadline warning at critical threshold
    Given Phil Santos has proposal "AF243-001" active in Wave 4
    And the deadline is 3 days away
    When Phil runs /sbir:continue
    Then the system displays normal wave progress
    And includes a deadline warning indicating 3 days remaining
    And the warning is visually distinct from other output

  Scenario: Archived proposal (No-Go decision)
    Given Phil Santos has proposal "AF243-001"
    And go_no_go is "no-go"
    And archived is true
    When Phil runs /sbir:continue
    Then the system indicates the proposal was declined
    And suggests starting a new proposal
    And does not suggest continuing the archived proposal
