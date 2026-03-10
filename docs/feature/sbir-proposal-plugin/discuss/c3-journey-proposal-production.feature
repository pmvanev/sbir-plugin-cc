Feature: SBIR Proposal Production & Learning (Phase C3)
  As an engineer who has completed drafting and review of an SBIR proposal
  I want to produce visual assets, format the document, pass final review, submit correctly, and learn from results
  So I can submit a polished, compliant proposal on time and improve with every cycle

  Background:
    Given Phil Santos is an engineer at IntaptAI (small business, 15 employees)
    And Phil has completed Waves 0-4 for proposal AF243-001
    And all sections are drafted, reviewed, and approved with Tier 1+2 PDCs GREEN
    And the compliance matrix has 47 items tracked
    And 14 days remain until the deadline

  # ==========================================================================
  # WAVE 5 -- Visual Assets
  # ==========================================================================

  Scenario: Generate figure inventory from proposal outline
    Given the approved outline for AF243-001 contains 5 figure placeholders
    When Phil runs "/proposal wave visuals"
    Then the tool generates a figure inventory listing all 5 placeholders
    And each figure has a type classification (block diagram, chart, illustration, photo)
    And each figure has a recommended generation method (Mermaid, SVG, Gemini API, external)
    And the inventory is written to "./artifacts/wave-5-visuals/figure-inventory.md"

  Scenario: Generate system architecture diagram via Mermaid
    Given Figure 1 is classified as "block diagram" with method "Mermaid"
    When the tool generates Figure 1 from the Section 3.1 draft content
    Then an SVG diagram is produced in "./artifacts/wave-5-visuals/figures/"
    And the figure is presented for Phil's review
    And Phil can approve, request revision, or provide a manual replacement

  Scenario: Fall back to external brief when generation fails
    Given Figure 5 requires a test setup photograph that cannot be generated
    When the tool attempts to generate Figure 5
    Then the tool creates an external brief describing the needed figure
    And the brief includes dimensions, resolution requirements, and content description
    And Phil can provide a manual file: "/proposal wave visuals --replace 5 ./my-photo.jpg"

  Scenario: Cross-reference validation for all figures
    Given all 5 figures have been generated or provided
    When the tool runs cross-reference validation
    Then every figure has a caption
    And every figure reference in the text resolves to an existing figure file
    And any orphaned figures (not referenced in text) are flagged
    And the cross-reference log is written to "./artifacts/wave-5-visuals/cross-reference-log.md"

  Scenario: PES blocks Wave 5 if Wave 4 is incomplete
    Given section 3.2 has a RED Tier 2 PDC item ("Phase II pathway uses generic language")
    When Phil runs "/proposal wave visuals"
    Then PES blocks the command
    And displays "Wave 5 requires all sections to have Tier 1+2 PDCs GREEN"
    And suggests "/proposal:check section-3.2" to see the remaining red items

  Scenario: Deadline pressure during visual asset generation
    Given 3 days remain until the deadline
    And 2 of 5 figures are still pending generation
    When Phil runs "/proposal status"
    Then PES displays a critical deadline warning
    And suggests "Skip remaining figures and proceed to formatting with 3 available figures"
    And Phil can choose to skip or continue

  # ==========================================================================
  # WAVE 6 -- Formatting & Assembly
  # ==========================================================================

  Scenario: Format document per solicitation requirements
    Given all figures are approved for AF243-001
    And the solicitation requires Times New Roman 12pt, 1-inch margins, and 20-page limit
    When Phil runs "/proposal format"
    Then the tool applies font, margins, headers, footers, and section numbering
    And the tool reports formatting progress for each step
    And the formatted document is presented for review

  Scenario: Select output medium for document generation
    Given Phil runs "/proposal format"
    When the tool asks for output medium preference
    And Phil selects "Microsoft Word (.docx)"
    Then the tool generates formatted output in .docx format
    And the output medium is recorded for submission packaging

  Scenario: Insert figures at correct positions
    Given 5 approved figures exist in the figures directory
    When the tool inserts figures into the formatted document
    Then each figure appears at its designated position in the text
    And each figure has its approved caption
    And figure numbering is sequential (Figure 1, Figure 2, etc.)

  Scenario: Compliance matrix final check during formatting
    Given the compliance matrix has 47 items
    And 45 items are covered and 2 are waived with reasons
    When the tool runs the final compliance matrix check
    Then the tool reports "45/47 covered | 2 waived (with reasons) | 0 missing"
    And the final check is written to "./artifacts/wave-6-format/compliance-final-check.md"

  Scenario: Page count exceeds solicitation limit
    Given the technical volume is formatted
    And the page count is 22 pages against a 20-page limit
    When the tool reports the page count
    Then the tool displays "Page count: 22/20 -- OVER LIMIT by 2 pages"
    And identifies the 3 largest sections by page consumption
    And suggests specific trimming options

  Scenario: Jargon audit verifies all acronyms defined on first use
    Given the formatted document uses 15 unique acronyms
    When the tool runs a jargon audit
    Then 13 acronyms are found defined on first use
    And 2 acronyms are flagged as undefined: "SWaP-C" (Section 3.2), "COTS" (Section 3.4)
    And the jargon audit is written to "./artifacts/wave-6-format/jargon-audit.md"

  Scenario: Assemble volumes into required file structure
    Given all formatting is complete
    And all figures are inserted
    And the compliance check shows no missing items
    When the tool assembles volumes
    Then Volume 1 (Technical), Volume 2 (Cost), and Volume 3 (Company Info) are created
    And volumes are written to "./artifacts/wave-6-format/assembled/"
    And a human checkpoint is presented for assembled package review

  # ==========================================================================
  # WAVE 7 -- Final Review
  # ==========================================================================

  Scenario: Reviewer persona simulation scores proposal
    Given the assembled proposal for AF243-001 is ready for final review
    When Phil runs "/proposal wave final-review"
    Then the tool simulates a government technical evaluator
    And scores the proposal against evaluation criteria (Technical Merit, Innovation, Phase II Potential, Commercial Potential, Company Capability)
    And each score includes a brief rationale
    And the scorecard is written to "./artifacts/wave-7-review/reviewer-scorecard.md"

  Scenario: Red team review identifies strongest objections
    Given the reviewer simulation has completed
    When the tool runs a red team review
    Then it identifies 3-5 strongest objections a skeptical reviewer would raise
    And each objection is tagged by severity (HIGH, MEDIUM, LOW)
    And each objection references a specific section and page
    And findings are written to "./artifacts/wave-7-review/red-team-findings.md"

  Scenario: Debrief-informed review checks against known weaknesses
    Given Phil has past debrief feedback for AF241-087 in the corpus
    And AF241-087's debrief said "transition pathway lacked specificity"
    When the tool checks the current proposal against known weaknesses
    Then the tool flags that "transition pathway specificity" is a known weakness
    And reports whether Section 5 in the current proposal addresses this critique
    And writes the cross-check to "./artifacts/wave-7-review/debrief-cross-check.md"

  Scenario: Final attachment and certification verification
    Given the assembled package requires 4 files (3 volumes + Firm Certification)
    When the tool verifies attachments
    Then all 4 required files are confirmed present
    And each file is verified as readable and non-empty
    And any missing files would be flagged before sign-off is allowed

  Scenario: Issue resolution and re-review iteration
    Given the red team found 1 HIGH-severity issue in Section 3.2
    When Phil selects "(f) fix issues" and revises Section 3.2
    Then the tool re-runs the final review on the updated section
    And the issue is verified as resolved
    And the iteration count is logged (max 2 iterations before sign-off is required)

  Scenario: Human sign-off before submission
    Given all HIGH-severity issues are addressed
    And the compliance check is clean
    And all attachments are present
    When Phil selects "(s) sign-off"
    Then the sign-off is recorded in "./artifacts/wave-7-review/sign-off-record.md"
    And proposal-state.json records the sign-off timestamp
    And Wave 8 is unlocked

  # ==========================================================================
  # WAVE 8 -- Submission
  # ==========================================================================

  Scenario: Identify submission portal from agency
    Given AF243-001 is an Air Force topic
    When Phil runs "/proposal submit prep"
    Then the tool identifies DSIP as the submission portal
    And displays the portal URL and any special requirements
    And applies DSIP-specific file naming conventions

  Scenario: Pre-submission verification catches all file issues
    Given the submission package contains 4 files
    When the tool runs pre-submission verification
    Then file naming is checked against DSIP convention (TopicNumber_CompanyName_Volume.pdf)
    And file sizes are checked against portal limits
    And file formats are verified (PDF, readable, non-corrupted)
    And the checklist is written to "./artifacts/wave-8-submission/pre-submission-checklist.md"

  Scenario: Missing required attachment blocks submission
    Given the Firm Certification file is missing from the package
    When the tool runs pre-submission verification
    Then the tool reports "Missing required file: Firm Certification"
    And submission is blocked until the file is provided
    And the tool suggests where to obtain the form

  Scenario: Human confirmation before submission
    Given all pre-submission checks pass
    When the tool presents the submission confirmation
    Then it displays "POINT OF NO RETURN" with the package contents summary
    And Phil must explicitly confirm with "(y) yes" before any submission occurs
    And "(n) no" returns to preparation without any irreversible action

  Scenario: Manual submission with confirmation entry
    Given Phil has confirmed readiness and submitted through the DSIP portal manually
    When Phil enters the confirmation number "DSIP-2026-AF243-001-7842" into the tool
    Then the tool records the confirmation number and the current timestamp
    And writes the record to "./artifacts/wave-8-submission/confirmation-record.md"
    And creates an immutable archive snapshot in "./artifacts/wave-8-submission/archive/"
    And PES marks all proposal artifacts as read-only
    And proposal-state.json records the submission

  Scenario: PES blocks modification after submission
    Given AF243-001 has been submitted and archived
    When Phil attempts to modify any submitted artifact (e.g., edit Section 3)
    Then PES blocks the modification
    And displays "Proposal AF243-001 is submitted and archived. Artifacts are read-only."
    And suggests starting a new proposal if revisions are needed

  Scenario: PES blocks Wave 8 without Wave 7 sign-off
    Given Phil has not completed the final review sign-off
    When Phil runs "/proposal submit prep"
    Then PES blocks the command
    And displays "Wave 8 requires final review sign-off from Wave 7"
    And suggests "/proposal wave final-review"

  # ==========================================================================
  # WAVE 9 -- Post-Submission & Learning
  # ==========================================================================

  Scenario: Record proposal outcome as not selected
    Given AF243-001 was submitted 90 days ago
    And Phil received notification that the proposal was not selected
    When Phil records the outcome as "not selected"
    Then proposal-state.json records the outcome
    And the corpus tags AF243-001 as "not_selected"
    And the tool suggests drafting a debrief request letter

  Scenario: Draft debrief request letter
    Given AF243-001 is recorded as "not selected"
    When Phil requests a debrief letter draft
    Then the tool generates a debrief request letter addressed to the contracting officer
    And the letter references topic AF243-001 and the submission confirmation number
    And the draft is written to "./artifacts/wave-9-learning/debrief-request-draft.md"

  Scenario: Ingest debrief feedback and map critiques to sections
    Given Phil received a debrief letter for AF243-001
    When Phil runs "/proposal debrief ingest ./debriefs/AF243-001-debrief.pdf"
    Then the tool parses reviewer scores and comments
    And maps each critique to a specific proposal section
    And flags critiques that match known weaknesses from previous debriefs
    And writes structured debrief to "./artifacts/wave-9-learning/debrief-structured.md"
    And writes critique mapping to "./artifacts/wave-9-learning/critique-section-map.md"

  Scenario: Win/loss pattern analysis updates across corpus
    Given the corpus contains 7 proposals with outcomes (3 awarded, 4 not selected)
    And 4 proposals have debrief feedback
    When the tool updates win/loss pattern analysis
    Then it identifies recurring weaknesses across losses (e.g., "transition pathway specificity" in 2/4 losses)
    And identifies recurring strengths across wins (e.g., "prior relevant work evidence" in 3/3 wins)
    And writes pattern analysis to "./artifacts/wave-9-learning/pattern-analysis.md"

  Scenario: Corpus and capability profile update
    Given the debrief has been ingested for AF243-001
    When the tool updates the corpus
    Then win/loss tags are appended (not overwritten) to proposal-state.json
    And debrief annotations are added to the corpus as a layer (source document not modified)
    And the company capability profile is updated with any new past performance data
    And lessons learned summary is written to "./artifacts/wave-9-learning/lessons-learned.md"

  Scenario: Ingest unstructured debrief with minimal content
    Given AF243-001 was not selected
    And the debrief letter is a single paragraph with no scores or structured comments
    When Phil runs "/proposal debrief ingest ./debriefs/AF243-001-debrief.pdf"
    Then the tool preserves the full text as freeform feedback
    And notes "Structured scores could not be extracted from this debrief"
    And the freeform text is available for keyword-based pattern matching

  Scenario: Debrief not received -- record outcome only
    Given AF243-001 was not selected
    And no debrief letter was provided by the agency
    When Phil records the outcome without a debrief
    Then proposal-state.json records outcome as "not_selected"
    And the corpus tags AF243-001 with outcome only
    And the tool notes "Debrief can be ingested later if received"

  Scenario: Record awarded proposal and archive as win
    Given AF243-001 was awarded
    When Phil records the outcome as "awarded"
    Then proposal-state.json records the outcome
    And the winning proposal is archived in the corpus with outcome tag "awarded"
    And the tool extracts winning discriminators and strategies for pattern analysis
    And the tool suggests beginning Phase II pre-planning if this was a Phase I award

  Scenario: Lessons learned human checkpoint
    Given debrief has been ingested and patterns updated
    When the tool presents the lessons learned summary
    Then Phil reviews the summary
    And can edit or annotate before acknowledging
    And the final lessons learned are written to the corpus

  # ==========================================================================
  # PES Enforcement Additions (C3)
  # ==========================================================================

  @property
  Scenario: PES PDC gate blocks Wave 5 without approved sections
    Given any section has a RED Tier 1 or Tier 2 PDC item
    Then PES blocks entry to Wave 5 (visual assets)
    And displays the specific sections and PDC items that remain red

  @property
  Scenario: PES deadline blocking prevents non-essential work
    Given days_to_deadline is below the critical threshold
    Then PES warns on every command execution
    And blocks non-essential waves (visual refinement, pattern analysis)
    And suggests submitting with available work

  @property
  Scenario: PES submission immutability enforcement
    Given a proposal has been submitted and a confirmation exists
    Then all artifacts under the proposal directory are marked read-only
    And any write attempt to submitted artifacts is blocked by PES
    And the audit log records the blocked attempt

  @property
  Scenario: PES corpus integrity for win/loss data
    Given win/loss tags exist in proposal-state.json
    Then tags are append-only and cannot be modified or deleted
    And debrief annotations are added as a layer on top of source documents
    And source documents in the corpus are never modified
