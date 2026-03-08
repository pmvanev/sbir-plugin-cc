Feature: SBIR Proposal Lifecycle
  As an engineer writing SBIR proposals at a small business
  I want a structured, AI-assisted proposal workflow with enforcement guardrails
  So I can write winning proposals faster with less effort and trust the output

  Background:
    Given Phil Santos is an engineer at IntaptAI (small business, 15 employees)
    And Phil writes 2-3 SBIR proposals per year at 10-15 hours each
    And Phil is comfortable with CLI tools and Claude Code

  # ==========================================================================
  # PHASE C1 (MVP) -- Walking Skeleton
  # ==========================================================================

  # --- Step 0: Entry & Reorientation ---

  Scenario: Start a new proposal project from a solicitation URL
    Given Phil has found solicitation AF243-001 on SBIR.gov
    When Phil runs "/proposal new" and provides the URL "https://www.sbir.gov/node/12345"
    Then the tool parses the solicitation and displays topic ID "AF243-001"
    And the tool displays agency "Air Force", phase "I", and deadline "2026-04-15"
    And the tool creates proposal-state.json with the parsed topic metadata

  Scenario: Start a new proposal project from a local PDF
    Given Phil has downloaded solicitation AF243-001 as a PDF
    When Phil runs "/proposal new --file ./solicitations/AF243-001.pdf"
    Then the tool parses the PDF and displays the same topic metadata
    And the tool creates proposal-state.json

  Scenario: Reorient after days away from a proposal
    Given Phil has an active proposal for topic AF243-001 in Wave 1
    And the TPOC call status is "pending"
    And 18 days remain until the deadline
    When Phil runs "/proposal status"
    Then the tool displays the current wave as "Wave 1: Requirements & Strategy"
    And the tool shows "TPOC questions generated (23 questions) -- PENDING CALL"
    And the tool suggests the next action: "Have TPOC call, then /proposal tpoc ingest"
    And the tool displays "18 days to deadline"

  Scenario: PES session startup detects and recovers from state issue
    Given Phil's last session ended unexpectedly
    And an orphaned draft file exists without a compliance matrix entry
    When Phil starts a new Claude Code session with the proposal plugin active
    Then PES runs an integrity check on proposal-state.json
    And PES surfaces a warning: "Section 3.2 draft exists but has no compliance matrix entry"
    And PES suggests: "Run /proposal compliance check for details"

  # --- Step 1: Intelligence & Fit (Wave 0) ---

  Scenario: Corpus search finds relevant past work
    Given Phil has ingested 5 past proposals into the corpus
    And two proposals are related to directed energy topics
    When the tool scores company fit for topic AF243-001
    Then the tool displays 2 related proposals with relevance scores
    And the tool displays "AF241-087 (2024) -- Relevance: 0.87 | Outcome: Not selected"
    And the tool displays "N222-038 (2023) -- Relevance: 0.62 | Outcome: Awarded"

  Scenario: Corpus is empty on first use
    Given Phil has never ingested any documents into the corpus
    When the tool scores company fit for topic AF243-001
    Then the tool displays "No corpus documents found"
    And the tool suggests "Add past proposals with: /proposal corpus add <directory>"
    And the tool continues with fit scoring based on solicitation parsing alone

  Scenario: Directory-based corpus ingestion
    Given Phil has a directory "./past-proposals/" containing 5 proposal PDFs and 2 debrief letters
    When Phil runs "/proposal corpus add ./past-proposals/"
    Then the tool ingests all 7 documents from the directory
    And the tool displays the count and type of each ingested document
    And the corpus index is updated for semantic search

  Scenario: Go/No-Go decision recorded
    Given the tool has displayed a fit score and recommendation for AF243-001
    When Phil selects "(g) go" at the Go/No-Go checkpoint
    Then proposal-state.json records go_no_go as "go"
    And the tool proceeds to Wave 1

  Scenario: No-Go decision archives the proposal
    Given the tool has displayed a fit score for AF243-001
    When Phil selects "(n) no-go" at the Go/No-Go checkpoint
    Then proposal-state.json records go_no_go as "no-go"
    And the tool archives the proposal state
    And the tool confirms: "AF243-001 archived as no-go."

  # --- Step 2: Requirements & Strategy (Wave 1) ---

  Scenario: Compliance matrix generated from solicitation
    Given Phil has an active proposal for AF243-001 with go_no_go "go"
    When Phil runs "/proposal wave strategy"
    Then the tool parses the solicitation for all "shall" statements
    And the tool generates a compliance matrix with 47 items
    And each item is mapped to a proposal section
    And 3 ambiguities are flagged for clarification
    And the matrix is written to "./artifacts/wave-1-strategy/compliance-matrix.md"

  Scenario: Manually add a missed compliance item
    Given a compliance matrix exists with 47 items for AF243-001
    And Phil discovers a requirement the parser missed
    When Phil runs "/proposal compliance add 'Section 3 shall include risk mitigation table'"
    Then the compliance matrix is updated to 48 items
    And the new item is marked as manually added

  Scenario: TPOC questions generated from gaps and ambiguities
    Given a compliance matrix exists with 3 flagged ambiguities
    When Phil runs "/proposal tpoc questions"
    Then the tool generates 23 prioritized questions
    And questions are tagged by category (scope-clarification, approach-validation, etc.)
    And questions are ordered by strategic priority
    And the questions are written to "./artifacts/wave-1-strategy/tpoc-questions.md"

  Scenario: TPOC call happens days later and answers are ingested
    Given TPOC questions were generated 5 days ago
    And Phil had the TPOC call and took notes in "./notes/tpoc-call-2026-03-15.txt"
    When Phil runs "/proposal tpoc ingest" and provides the file path
    Then the tool matches 18 of 23 questions to answers
    And 5 unanswered questions are marked as such
    And a solicitation delta analysis is generated
    And the compliance matrix is updated with TPOC clarifications
    And tpoc_status changes from "pending" to "completed"

  Scenario: TPOC call never happens -- tool handles gracefully
    Given TPOC questions were generated 14 days ago
    And Phil never had the TPOC call
    When Phil runs "/proposal status"
    Then the status shows "TPOC questions pending -- no call recorded"
    And the tool does not block progress on any wave
    And Phil can proceed to strategy alignment without TPOC answers

  Scenario: Strategy alignment checkpoint
    Given compliance matrix and TPOC answers (or pending status) exist
    And the tool has drafted a strategy brief
    When the strategy alignment checkpoint is presented
    Then Phil reviews the strategy brief summary
    And Phil can approve, revise with feedback, or skip
    And approval is recorded and unlocks Wave 2

  # ==========================================================================
  # PHASE C2 -- Guardrailed Drafting (deferred implementation)
  # ==========================================================================

  Scenario: Research wave produces evidence base
    Given the strategy brief is approved for AF243-001
    When Phil runs "/proposal wave research"
    Then the tool produces technical landscape, market research, and TRL assessment
    And a research review checkpoint is presented for approval

  Scenario: Discrimination table built from evidence
    Given research is approved for AF243-001
    When Phil runs "/proposal wave outline"
    Then the tool drafts a discrimination table with company vs. competitor vs. prior art
    And the tool drafts a proposal outline with page budgets and thesis statements
    And both artifacts are presented for iterative review

  Scenario: PDCs generated before drafting begins
    Given the outline is approved for AF243-001
    When Phil runs "/proposal:distill --all"
    Then PDC files are generated for each proposal section
    And each PDC contains Tier 1 (mechanical), Tier 2 (rubric), Tier 3 (persona) checks
    And a master proposal.pdc cross-section file is created

  Scenario: Drafting with confidence flagging
    Given PDCs exist for section 3 of AF243-001
    When Phil runs "/proposal draft section-3"
    Then the writer agent produces a draft against the approved outline and PDCs
    And claims not supported by corpus documents are flagged with "[CONFIDENCE: LOW]"
    And Phil can review each flagged claim and provide evidence or remove it

  Scenario: PDC check identifies red items
    Given a draft exists for section 3
    When Phil runs "/proposal:check section-3"
    Then Tier 1 mechanical checks run (page count, TRL stated, acronyms, figures)
    And Tier 2 rubric checks run (topic response, novelty, Phase II pathway)
    And results show 10/12 GREEN and 2 RED with specific failure reasons
    And Phil can run "/proposal iterate section-3" to target red items

  Scenario: Iterate until all PDCs green then human review
    Given section 3 has 2 RED PDC items
    When Phil runs "/proposal iterate section-3"
    Then the writer agent revises targeting only the red items
    And "/proposal:check section-3" shows 12/12 GREEN
    And Phil runs "/proposal review section-3" for human review with Tier 3 persona output
    And Phil approves the section with "/proposal:approve section-3"

  # ==========================================================================
  # PHASE C3 -- Full Lifecycle (deferred implementation)
  # ==========================================================================

  Scenario: Visual assets generated for figure placeholders
    Given all sections are drafted and approved for AF243-001
    When Phil runs "/proposal wave visuals"
    Then the tool generates figures for each placeholder in the outline
    And each figure is presented for iterative review
    And approved figures are cross-referenced in the text

  Scenario: Document formatted and assembled per solicitation requirements
    Given all sections and figures are approved
    When Phil runs "/proposal format"
    Then the tool applies formatting per solicitation (font, margins, headers)
    And the tool assembles all volumes into the required file structure
    And a final compliance matrix check runs
    And the assembled package is presented for review

  Scenario: Final review with simulated government evaluator
    Given the formatted proposal is assembled
    When Phil runs "/proposal wave final-review"
    Then a reviewer persona simulation scores the proposal against evaluation criteria
    And a red team review identifies the strongest objections
    And Phil reviews and addresses any issues
    And Phil provides final sign-off

  Scenario: Submission packaging and archiving
    Given final review sign-off is recorded
    When Phil runs "/proposal submit prep" then "/proposal submit"
    Then the tool packages the proposal per portal requirements
    And the tool captures a submission confirmation with timestamp
    And an immutable archive snapshot is created
    And the submitted package is marked read-only by PES

  Scenario: Debrief ingestion after award decision
    Given AF243-001 was not selected and Phil received a debrief letter
    When Phil runs "/proposal debrief ingest ./debriefs/AF243-001-debrief.pdf"
    Then the tool parses reviewer scores and comments
    And maps each critique to a specific proposal section
    And updates the win/loss pattern analysis in the corpus
    And writes a lessons-learned summary

  # ==========================================================================
  # Error Paths
  # ==========================================================================

  Scenario: Solicitation URL cannot be parsed
    Given Phil provides a URL that returns a login page
    When the tool attempts to parse the solicitation
    Then the tool displays "Could not parse solicitation at this URL"
    And the tool suggests "Try downloading the PDF and providing a local file path"

  Scenario: PES blocks drafting without compliance matrix entry
    Given Phil tries to draft section 3.2 which has no compliance matrix entry
    When Phil runs "/proposal draft section-3.2"
    Then PES blocks the action
    And displays "No compliance matrix entry covers section 3.2"
    And suggests "/proposal compliance add" or "/proposal compliance check"

  Scenario: PES deadline warning at critical threshold
    Given 3 days remain until the AF243-001 deadline
    And Wave 4 drafting is not complete
    When Phil runs "/proposal status"
    Then PES displays a critical deadline warning
    And suggests skipping non-essential waves with documented waivers
