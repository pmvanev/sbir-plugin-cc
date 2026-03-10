<!-- markdownlint-disable MD024 -->

# Phase C3 User Stories -- SBIR Proposal Writing Plugin

Scope: Waves 5-9 (Visual Assets, Formatting & Assembly, Final Review, Submission, Post-Submission Learning).
All stories trace to C3 JTBD analysis jobs (J6, J7, J9, J10, J11) and journey steps.
C1 stories (US-001 through US-009) are in `user-stories.md` -- not modified here.

---

## US-010: Visual Asset Generation from Outline Placeholders

### Problem

Phil Santos is an engineer who has spent 8-12 hours drafting and reviewing a proposal. Now he needs 3-5 figures (system diagrams, timelines, data charts) to strengthen the narrative. He finds it tedious to create each figure manually in draw.io or PowerPoint, spending 30-60 minutes per figure. Cross-references between text and figures break when sections are reordered. Today, figures are afterthoughts added at the last minute.

### Who

- Engineer | All sections approved, entering Wave 5 | Wants professional figures that strengthen the technical argument without hours of manual drawing

### Solution

A visual asset generation workflow that inventories all figure placeholders from the approved outline, classifies each by type and generation method, generates drafts (Mermaid, SVG, Graphviz, or image API), presents each for human review and iteration, validates cross-references, and produces a clean cross-reference log.

### Domain Examples

#### 1: Happy Path -- Phil generates system architecture diagram

Phil runs `/proposal wave visuals` for AF243-001. The tool identifies 5 figure placeholders from the outline. Figure 1 (Section 3.1) is a system architecture diagram. The tool generates a Mermaid block diagram showing the solid-state laser subsystem, beam director, power supply, and cooling. Phil reviews, asks for the power supply to be more prominent, and the tool regenerates. Phil approves.

#### 2: Edge Case -- Figure requires manual creation

Figure 5 (Section 3.4) is a test setup photograph. The tool cannot generate this. It creates an external brief: "Needed: photograph of laboratory bench-top laser test setup, showing beam path alignment. Minimum resolution: 300 DPI. Dimensions: 6" x 4". Content: laser source, beam expander, target surface, measurement equipment." Phil provides his own JPEG file via `/proposal wave visuals --replace 5 ./photos/bench-test.jpg`.

#### 3: Error Path -- Cross-reference mismatch detected

After generating all figures, the cross-reference validation finds that Section 3.3 references "Figure 6" but only 5 figures exist. The tool flags: "Section 3.3 references Figure 6 which does not exist. Either add a figure or update the text reference." Phil updates the text.

### UAT Scenarios (BDD)

#### Scenario: Generate figure inventory from outline

Given all sections are approved for AF243-001
And the outline contains 5 figure placeholders across 4 sections
When Phil runs "/proposal wave visuals"
Then the tool generates a figure inventory with 5 entries
And each entry has a type, recommended generation method, and target section
And the inventory is written to "./artifacts/wave-5-visuals/figure-inventory.md"

#### Scenario: Generate Mermaid diagram and present for review

Given Figure 1 is classified as a block diagram with method "Mermaid"
When the tool generates Figure 1 from Section 3.1 content
Then an SVG file is produced in "./artifacts/wave-5-visuals/figures/"
And the figure is presented to Phil for review
And Phil can approve, request revision, or replace with a manual file

#### Scenario: Create external brief for non-generatable figure

Given Figure 5 requires a photograph that cannot be generated
When the tool classifies Figure 5
Then it generates an external brief with content description, dimensions, and resolution
And Phil can provide a manual file with "--replace 5 ./my-file.jpg"

#### Scenario: Cross-reference validation catches orphaned reference

Given 5 figures are generated and Section 3.3 references "Figure 6"
When the tool runs cross-reference validation
Then it flags "Figure 6 referenced in Section 3.3 does not exist"
And the cross-reference log records the mismatch

#### Scenario: PES blocks Wave 5 when sections have RED PDCs

Given section 3.2 still has a RED Tier 2 PDC item
When Phil runs "/proposal wave visuals"
Then PES blocks the command
And displays "Wave 5 requires all sections to have Tier 1+2 PDCs GREEN"

### Acceptance Criteria

- [ ] Tool inventories all figure placeholders from the approved outline
- [ ] Each figure is classified by type and generation method
- [ ] Figures are generated via Mermaid, SVG, Graphviz, or image API as appropriate
- [ ] External brief is created for figures that cannot be generated
- [ ] Each figure is presented for human review with approve/revise/replace options
- [ ] Cross-reference validation catches orphaned references and missing figures
- [ ] PES enforces PDC gate: all sections must have Tier 1+2 GREEN before Wave 5

### Technical Notes

- Figure generation methods: Mermaid (diagrams), Graphviz (network/flow), SVG (data charts), Gemini API (concept illustrations, requires GEMINI_API_KEY)
- External brief fallback when no generation method is viable
- Cross-reference log tracks figure-to-text consistency across assembly
- Depends on: approved outline (from Wave 3), approved sections (from Wave 4), PES PDC gate

---

## US-011: Document Formatting and Volume Assembly

### Problem

Phil Santos is an engineer who dreads the formatting phase of proposal writing. After spending 8-12 hours on content, he still faces 2-3 hours of mechanical work: applying fonts, margins, headers, inserting figures at correct positions, formatting references, counting pages, and assembling separate volumes into the file structure the solicitation requires. A last-minute section edit once shifted all his pages and cost him 3 hours of reformatting. One proposal was returned for wrong font size in headers. Today, formatting is entirely manual in Word or Google Docs.

### Who

- Engineer | All figures approved, entering Wave 6 | Wants formatting handled by template, not by hand

### Solution

A formatting and assembly workflow that applies solicitation-specific format rules (font, margins, headers, section numbering) via templates, inserts approved figures, formats references, runs a jargon audit and page count verification, performs a final compliance matrix check, and assembles all volumes into the required file structure. Human checkpoint at the end for assembled package review.

### Domain Examples

#### 1: Happy Path -- Phil formats AF243-001 for DSIP submission

Phil runs `/proposal format` for AF243-001. The solicitation requires Times New Roman 12pt, 1-inch margins, 20-page limit for the technical volume. Phil selects Word (.docx) as the output medium. The tool applies formatting, inserts 5 figures, formats 23 citations, runs jargon audit (finds 2 undefined acronyms: SWaP-C and COTS), reports page count 19/20, verifies compliance matrix (45/47 covered, 2 waived with reasons), and assembles 3 volumes. Phil reviews the assembled package, fixes the 2 undefined acronyms, and approves.

#### 2: Edge Case -- Page count exceeds limit

After formatting, the technical volume is 22 pages against a 20-page limit. The tool reports: "Page count: 22/20 -- OVER LIMIT by 2 pages. Largest sections: Section 3 (8 pages), Section 4 (5 pages). Consider trimming Section 3 or compressing figure sizes." Phil edits Section 3 to trim 2 pages and re-runs formatting.

#### 3: Error Path -- Compliance matrix has missing items

During the final compliance check, the tool finds 1 compliance item with status "missing" (not covered and not waived). It reports: "1 compliance item MISSING: Item #34 'Proposal shall include a facilities description.' Provide content or waive with reason before proceeding to final review."

### UAT Scenarios (BDD)

#### Scenario: Apply solicitation formatting rules

Given all figures are approved for AF243-001
And the solicitation requires Times New Roman 12pt and 1-inch margins
When Phil runs "/proposal format" and selects "Microsoft Word (.docx)"
Then the tool applies font, margins, headers, footers, and section numbering
And reports formatting progress for each step

#### Scenario: Insert figures and format references

Given 5 approved figures exist and the document has 23 citations
When the tool inserts figures and formats references
Then each figure appears at its correct position with its approved caption
And citations are formatted in a consistent style

#### Scenario: Jargon audit flags undefined acronyms

Given the document uses 15 unique acronyms
And 2 are not defined on first use
When the tool runs the jargon audit
Then it flags the 2 undefined acronyms with their locations
And writes the audit to "./artifacts/wave-6-format/jargon-audit.md"

#### Scenario: Page count within limits

Given the formatted technical volume is 19 pages
And the solicitation limit is 20 pages
When the tool reports the page count
Then it displays "19/20 -- within limit (1 page margin)"

#### Scenario: Page count over limit with guidance

Given the formatted technical volume is 22 pages against a 20-page limit
When the tool reports the page count
Then it displays "22/20 -- OVER LIMIT by 2 pages"
And identifies the 3 largest sections with page counts
And suggests trimming options

#### Scenario: Compliance matrix final check during formatting

Given the compliance matrix has 47 items
And 45 are covered and 2 are waived with reasons
When the tool runs the final compliance check
Then it reports "45/47 covered | 2 waived (with reasons) | 0 missing"

#### Scenario: Assemble volumes and present for review

Given formatting and compliance checks are complete
When the tool assembles volumes
Then it creates Volume 1 (Technical), Volume 2 (Cost), Volume 3 (Company Info)
And writes them to "./artifacts/wave-6-format/assembled/"
And presents a human checkpoint for assembled package review

### Acceptance Criteria

- [ ] Solicitation format rules (font, margins, headers, page limits) are applied via templates
- [ ] Output medium is selectable (Word, LaTeX, Google Docs, PDF)
- [ ] Figures are inserted at correct positions with captions
- [ ] References are formatted consistently
- [ ] Jargon audit flags undefined acronyms with locations
- [ ] Page count is verified against solicitation limits with guidance when exceeded
- [ ] Compliance matrix final check runs and reports coverage
- [ ] Volumes are assembled into required file structure
- [ ] Human checkpoint at assembled package review

### Technical Notes

- Template-based formatting (not LLM layout control) -- templates for common agencies (DoD, NASA, NSF, DOE)
- Orphan/widow control is a template property, not tool logic
- Compliance matrix is the same living document from Wave 1
- Output medium selection recorded in proposal-state.json for Wave 8 packaging
- Depends on: approved figures (US-010), compliance matrix (US-004), outline (from Wave 3)

---

## US-012: Final Review with Simulated Government Evaluator

### Problem

Phil Santos is the sole writer on his SBIR proposals. He has no one to do a proper red team review before submission. His AF241-087 debrief critique said "transition pathway lacked specificity" -- something a thorough review could have caught. He finds it risky to submit a proposal that has only been reviewed by the person who wrote it, especially when his past debriefs contain patterns of weakness that he might repeat. Today, his "final review" is reading the proposal once or twice himself.

### Who

- Engineer | Assembled proposal ready, entering Wave 7 | Wants a simulated adversarial review to catch fatal flaws while there is still time

### Solution

A final review workflow that simulates a government technical evaluator scoring against stated evaluation criteria, runs a red team review to identify the strongest objections, cross-checks against known weaknesses from past debriefs in the corpus, verifies compliance and attachments, iterates on findings (max 2 cycles), and records a human sign-off that gates submission.

### Domain Examples

#### 1: Happy Path -- Phil reviews AF243-001 with simulated evaluator

Phil runs `/proposal wave final-review`. The reviewer simulation scores AF243-001: Technical Merit 8.2/10, Innovation 7.5/10, Phase II Potential 6.8/10, Commercial Potential 7.0/10, Company Capability 8.5/10. Red team identifies 3 objections: (1) HIGH -- SWaP-C claim in Section 3.2 is unsupported by test data, (2) MED -- timeline aggressive for TRL 3 to 5, (3) LOW -- TAM estimate cites 2023 data. Debrief cross-check flags that AF241-087 had a critique about "transition pathway specificity" and notes that the current Section 5 specifically names PMS 501 -- addressed. Phil fixes the HIGH item, acknowledges the MED and LOW items, and signs off.

#### 2: Edge Case -- No past debriefs in corpus

Phil is running his first proposal through the tool. No debrief feedback exists in the corpus. The debrief cross-check reports: "No past debrief data available. As debriefs are ingested in future cycles, this check will become more valuable." The rest of the review proceeds normally.

#### 3: Edge Case -- Two iteration cycles needed

The first review finds 2 HIGH issues. Phil fixes both and re-runs. The second review finds 1 new MED issue introduced by the fix. Phil addresses it and signs off on the third pass (2 iteration cycles, within the max 2 limit).

### UAT Scenarios (BDD)

#### Scenario: Reviewer persona simulation scores proposal

Given the assembled proposal for AF243-001 is ready for final review
When Phil runs "/proposal wave final-review"
Then the tool simulates a government evaluator scoring against 5 criteria
And each score includes a brief rationale
And the scorecard is written to "./artifacts/wave-7-review/reviewer-scorecard.md"

#### Scenario: Red team review identifies strongest objections

Given the reviewer simulation has completed
When the tool runs a red team review
Then it identifies 3 objections tagged by severity (HIGH, MEDIUM, LOW)
And each references a specific section and page
And findings are written to "./artifacts/wave-7-review/red-team-findings.md"

#### Scenario: Debrief-informed review flags known weaknesses

Given past debrief feedback for AF241-087 exists in the corpus
And that debrief said "transition pathway lacked specificity"
When the tool checks against known weaknesses
Then it flags "transition pathway specificity" as a known weakness
And reports whether the current proposal addresses it

#### Scenario: No past debriefs available

Given no debrief feedback exists in the corpus
When the tool runs the debrief cross-check
Then it reports "No past debrief data available"
And notes this check improves as debriefs are ingested

#### Scenario: Issue resolution and re-review

Given the red team found 1 HIGH issue in Section 3.2
When Phil fixes the issue and selects "(i) iterate review"
Then the tool re-reviews and confirms the HIGH issue is resolved
And logs the iteration (max 2 iterations)

#### Scenario: Human sign-off unlocks Wave 8

Given all HIGH issues are addressed
When Phil selects "(s) sign-off"
Then the sign-off is recorded in "./artifacts/wave-7-review/sign-off-record.md"
And proposal-state.json records the sign-off
And Wave 8 is unlocked

### Acceptance Criteria

- [ ] Reviewer persona simulation scores against solicitation evaluation criteria
- [ ] Red team identifies 3-5 strongest objections tagged by severity
- [ ] Debrief-informed review checks against known weaknesses from corpus
- [ ] Handles gracefully when no past debriefs exist
- [ ] Issue resolution loop supports max 2 iteration cycles
- [ ] Final attachment and certification verification runs
- [ ] Human sign-off is required and gates Wave 8 (PES-enforced)
- [ ] After 2 review iterations, sign-off is required even with unresolved issues; unresolved items documented in sign-off record
- [ ] All review artifacts written to ./artifacts/wave-7-review/

### Technical Notes

- Reviewer personas should approximate DoD Phase I evaluation criteria (or agency-specific if different)
- Red team findings tagged with severity guide Phil's attention to highest-impact fixes
- Debrief cross-check queries corpus annotations from Wave 9 of past proposals
- Sign-off gates Wave 8 via PES; no submission without sign-off
- Depends on: assembled volumes (US-011), compliance matrix (US-004), corpus debriefs (US-016)

---

## US-013: Submission Preparation and Portal-Specific Packaging

### Problem

Phil Santos is an engineer who once discovered 2 hours before a deadline that DSIP required a specific file naming convention he had not followed. Repackaging under time pressure was stressful. Another time, he forgot to attach the required Firm Certification form to a Grants.gov submission. He finds it anxiety-inducing that each submission portal (DSIP, Grants.gov, NSPIRES) has different file naming rules, size limits, and required attachments, and that getting any of them wrong after weeks of work could result in a rejected submission. Today, he relies on a personal checklist and triple-checks before clicking submit.

### Who

- Engineer | Reviewed and signed-off proposal, entering Wave 8 | Wants confidence that the submission package is complete and correctly formatted for the specific portal

### Solution

A submission preparation workflow that identifies the correct portal from agency/solicitation, applies portal-specific packaging rules (file naming, size limits, format requirements), verifies all required files are present and correctly named, presents the complete package for human confirmation, and after explicit confirmation creates an immutable archive.

### Domain Examples

#### 1: Happy Path -- Phil submits AF243-001 to DSIP

Phil runs `/proposal submit prep` for AF243-001 (Air Force topic). The tool identifies DSIP as the portal, applies the naming convention (AF243-001_IntaptAI_Vol1_Technical.pdf), verifies 4 files are present (3 volumes + Firm Certification), checks sizes are under 10 MB each, and reports all checks passing. Phil reviews the package, confirms submission with `/proposal submit`, receives confirmation DSIP-2026-AF243-001-7842 at 2026-04-07T14:23:17Z, and an immutable archive is created.

#### 2: Edge Case -- Missing required attachment

The pre-submission check finds that the Firm Certification form is missing. The tool reports: "Missing required file: Firm Certification (SF-XX). Submission blocked. Obtain the form from [URL] and add to the package." Phil adds the form and re-runs prep.

#### 3: Error Path -- Portal naming convention changed

Between solicitation cycles, DSIP changed its naming convention. The tool expected "TopicNumber_CompanyName_Vol1.pdf" but the portal now requires "TopicNumber-CompanyName-TechnicalVolume.pdf". The tool flags the mismatch: "Portal naming convention may have changed. Expected: [old]. Found requirement: [new]. Verify and rename manually or update portal config."

### UAT Scenarios (BDD)

#### Scenario: Identify submission portal and apply packaging rules

Given AF243-001 is an Air Force topic
When Phil runs "/proposal submit prep"
Then the tool identifies DSIP as the submission portal
And applies DSIP file naming conventions to all package files
And verifies file sizes against portal limits

#### Scenario: Pre-submission verification passes

Given all required files are present and correctly named
When the tool runs pre-submission verification
Then it reports all checks passing
And writes the checklist to "./artifacts/wave-8-submission/pre-submission-checklist.md"

#### Scenario: Missing attachment blocks submission

Given the Firm Certification file is missing
When the tool runs pre-submission verification
Then it reports the missing file and blocks submission
And suggests where to obtain the required form

#### Scenario: Human confirms submission at point of no return

Given all checks pass
When the tool presents the submission confirmation
Then Phil must explicitly confirm with "(y) yes"
And "(n) no" returns to preparation

#### Scenario: Manual submission with confirmation entry

Given all checks pass and Phil has confirmed readiness
When Phil submits the proposal through the DSIP portal manually
Then Phil enters the confirmation number "DSIP-2026-AF243-001-7842" into the tool
And the tool records the confirmation number and the current timestamp
And creates an immutable archive in "./artifacts/wave-8-submission/archive/"
And PES marks all proposal artifacts as read-only

#### Scenario: PES blocks modification after submission

Given AF243-001 has been submitted
When Phil attempts to edit any submitted artifact
Then PES blocks the modification
And displays "Proposal AF243-001 is submitted. Artifacts are read-only."

### Acceptance Criteria

- [ ] Portal is identified from agency (DSIP for DoD, Grants.gov for multi-agency, NSPIRES for NASA)
- [ ] Portal-specific file naming, size limits, and format requirements are applied
- [ ] All required files verified present before submission is allowed
- [ ] Missing files block submission with actionable guidance
- [ ] Submission requires explicit human confirmation (point of no return)
- [ ] Confirmation number is manually entered by Phil after portal submission
- [ ] Timestamp captured at confirmation entry
- [ ] Immutable archive is created after confirmation entry
- [ ] PES enforces read-only on all submitted artifacts
- [ ] PES blocks Wave 8 without Wave 7 sign-off

### Technical Notes

- Portal packaging rules stored in `templates/portal-rules/` directory, user-editable to handle rule changes between solicitation cycles
- File naming conventions may change between solicitation cycles; tool flags mismatches
- Submission itself is a manual step -- tool prepares and verifies, Phil clicks submit on the portal
- Confirmation number is manually entered by Phil after portal submission -- tool does not auto-submit
- Immutable archive is a directory copy with PES write-protection
- Depends on: assembled volumes (US-011), sign-off record (US-012), PES immutability invariant

---

## US-014: PES Enforcement for C3 Invariants

### Problem

Phil Santos is an engineer who worries about process mistakes in the production and submission phases -- starting to format before sections are truly approved, submitting without a proper review, or accidentally modifying a submitted proposal. These mistakes are especially costly in the later waves because they affect the final deliverable. The C1 PES foundation (US-006) established the enforcement pattern; C3 needs four additional invariant classes to protect the production and submission lifecycle.

### Who

- Engineer | Working through Waves 5-9 | Needs structural guarantees that production and submission integrity is maintained

### Solution

Four new PES invariant classes extending the C1 foundation: (1) PDC gate blocking Wave 5 without approved sections, (2) deadline blocking that prevents non-essential work when time is critical, (3) submission immutability enforcement, and (4) corpus integrity checks ensuring append-only operations for win/loss data.

### Domain Examples

#### 1: Happy Path -- PES blocks Wave 5 with unapproved section

Phil tries to run `/proposal wave visuals` but Section 3.2 still has a RED Tier 2 PDC item. PES blocks: "Wave 5 requires all sections to have Tier 1+2 PDCs GREEN. Section 3.2 has 1 RED item. Run /proposal:check section-3.2 for details."

#### 2: Happy Path -- PES enforces deadline blocking

With 3 days until deadline and Wave 5 (visual assets) incomplete, Phil runs `/proposal status`. PES surfaces: "3 days remaining -- critical threshold. Non-essential work blocked. Consider: submit with available figures or request deadline extension." Phil can override with a documented waiver.

#### 3: Edge Case -- PES blocks edit of submitted proposal

After submitting AF243-001, Phil accidentally tries to edit Section 3 to fix a typo he noticed. PES blocks: "Proposal AF243-001 is submitted and archived. All artifacts are read-only. Start a new proposal if revisions are needed."

### UAT Scenarios (BDD)

#### Scenario: PDC gate blocks Wave 5 with RED items

Given section 3.2 has 1 RED Tier 2 PDC item
When Phil runs "/proposal wave visuals"
Then PES blocks the command
And displays the specific section and PDC items that remain red

#### Scenario: Deadline blocking surfaces warning

Given 3 days remain until the deadline
And Wave 5 is not complete
When Phil runs "/proposal status"
Then PES displays a critical deadline warning
And suggests submitting with available work or skipping non-essential waves

#### Scenario: Submission immutability prevents edits

Given AF243-001 has been submitted with confirmation recorded
When Phil attempts to write to any file under the proposal artifact directories
Then PES blocks the write operation
And logs the blocked attempt in the audit log

#### Scenario: Corpus integrity enforces append-only tags

Given AF243-001 has a win/loss tag of "not_selected"
When any process attempts to change the tag to "awarded"
Then PES blocks the modification
And displays "Win/loss tags are append-only and cannot be modified"

#### Scenario: PES audit log records all C3 enforcement actions

Given PES has blocked 3 actions during Waves 5-8
When Phil reviews the audit log
Then all 3 blocked actions are recorded with timestamps, rule names, and details

### Acceptance Criteria

- [ ] PDC gate blocks Wave 5 entry when any section has RED Tier 1 or Tier 2 PDC items
- [ ] Deadline blocking surfaces warnings at critical threshold and blocks non-essential waves
- [ ] Submission immutability blocks all writes to submitted proposal artifacts
- [ ] Corpus integrity enforces append-only on win/loss tags and prevents source document modification
- [ ] All enforcement actions are recorded in the PES audit log
- [ ] All four invariant classes are configurable in pes-config.json
- [ ] Existing C1 invariants (session startup, wave ordering, compliance gate) continue to function

### Technical Notes

- Extends PES foundation from US-006; same engine, new rules in pes-config.json
- PDC gate reads PDC evaluation results from ./pdcs/; Wave 5 entry requires all GREEN
- Deadline blocking threshold configurable (warning_days, critical_days in pes-config.json)
- Submission immutability enforced at file-system level (directory permissions or hook-based)
- Corpus integrity enforced via PES write hooks on proposal-state.json outcome fields
- Depends on: US-006 (PES Foundation), proposal-state.json schema (US-007)

---

## US-015: Debrief Ingestion and Critique-to-Section Mapping

### Problem

Phil Santos is an engineer who receives debrief feedback on roughly 60% of his submissions. When he gets a debrief for AF241-087 that says "transition pathway lacked specificity," it takes him 20 minutes to figure out which section that maps to. The critique is useful, but the mapping is manual, the insight lives in his head, and by the next proposal cycle months later he has forgotten the specific lesson. For the 40% of submissions that get no feedback at all, he has no mechanism to learn. Today, debriefs are skimmed once and filed away.

### Who

- Engineer | Received proposal outcome (win or loss) | Wants debrief feedback structured and mapped to sections for lasting institutional learning

### Solution

A debrief ingestion workflow that parses reviewer scores and comments, maps each critique to a specific proposal section, flags critiques that match known weaknesses from previous debriefs, updates win/loss patterns across the corpus, and produces a lessons learned summary. Handles "no debrief received" as a valid state.

### Domain Examples

#### 1: Happy Path -- Phil ingests debrief for AF243-001 (loss)

Phil runs `/proposal debrief ingest ./debriefs/AF243-001-debrief.pdf`. The tool parses 4 reviewer scores (Technical Merit 7.8/10, Innovation 7.2/10, Phase II Plan 5.5/10, Cost Realism 8.0/10) and 3 critique comments. It maps: (1) "transition pathway lacked specificity" to Section 5 page 17, flagged as known weakness (also in AF241-087), (2) "cost estimate for key personnel appears high" to Cost Volume page 3, new finding, (3) "strong prior relevant work evidence" to Section 4 page 15, strength consistent with N222-038 win. Pattern analysis updates: "transition pathway specificity" recurs in 2/4 losses.

#### 2: Edge Case -- No debrief received

Phil records AF243-001 as "not selected" but the agency provides no debrief. He runs the outcome recording only. The tool tags the proposal and notes "debrief can be ingested later if received." No debrief-specific artifacts are created but the outcome feeds pattern analysis.

#### 3: Happy Path -- Phil ingests outcome for a win

AF243-001 was awarded. Phil records the outcome as "awarded." The winning proposal is archived with outcome tag. The tool extracts winning discriminators (strong prior work, specific PMS 501 transition pathway) and notes: "prior relevant work evidence" present in 3/3 wins. Suggests beginning Phase II pre-planning.

### UAT Scenarios (BDD)

#### Scenario: Ingest debrief and map critiques to sections

Given AF243-001 was not selected and Phil has a debrief letter
When Phil runs "/proposal debrief ingest ./debriefs/AF243-001-debrief.pdf"
Then the tool parses reviewer scores and critique comments
And maps each critique to a specific proposal section and page
And flags critiques matching known weaknesses from past debriefs
And writes structured debrief and critique map to ./artifacts/wave-9-learning/

#### Scenario: Win/loss pattern analysis updates

Given the corpus contains 7 proposals (3 awarded, 4 not selected)
When the tool updates pattern analysis
Then it identifies recurring weaknesses across losses
And identifies recurring strengths across wins
And writes pattern analysis to "./artifacts/wave-9-learning/pattern-analysis.md"

#### Scenario: Record outcome without debrief

Given AF243-001 was not selected
And no debrief letter is available
When Phil records the outcome
Then the outcome tag is appended to proposal-state.json
And no debrief artifacts are created
And the tool notes "debrief can be ingested later"

#### Scenario: Record awarded outcome and archive winner

Given AF243-001 was awarded
When Phil records the outcome as "awarded"
Then the winning proposal is archived with outcome tag
And winning discriminators are extracted for pattern analysis
And the tool suggests Phase II pre-planning

#### Scenario: Ingest unstructured debrief with minimal content

Given a debrief letter is a single paragraph with no scores or structured comments
When Phil runs "/proposal debrief ingest ./debriefs/AF243-001-debrief.pdf"
Then the tool preserves the full text as freeform feedback
And notes "Structured scores could not be extracted from this debrief"
And the freeform text is still available for keyword-based pattern matching

#### Scenario: Lessons learned human checkpoint

Given debrief ingestion and pattern analysis are complete
When the tool presents lessons learned
Then Phil can review, edit, and acknowledge before corpus update completes

### Acceptance Criteria

- [ ] Debrief feedback parsed from PDF or text file
- [ ] Each critique mapped to a specific proposal section and page
- [ ] Known weaknesses from past debriefs are flagged when matching critiques found
- [ ] Unstructured debriefs are preserved as freeform text when structured parsing fails
- [ ] Win/loss pattern analysis updates cumulatively across corpus
- [ ] "No debrief received" is a valid terminal state
- [ ] Awarded proposals are archived with outcome tags and winning discriminators extracted
- [ ] Win/loss tags are append-only (PES-enforced)
- [ ] Lessons learned reviewed by human before corpus update
- [ ] Near-zero Phil effort: ingestion of a debrief takes under 5 minutes of Phil's time

### Technical Notes

- Debrief parsing is best-effort; unstructured debriefs are preserved as freeform text
- Critique-to-section mapping uses section numbering from the submitted proposal outline
- Pattern analysis becomes more reliable as corpus grows; tool should note confidence level
- Win/loss tags append-only; PES corpus integrity invariant (US-014) enforces
- Debrief annotations layer on corpus -- source documents never modified
- Depends on: submitted proposal archive (US-013), corpus (US-003), PES (US-014)

---

## US-016: Debrief Request Letter Draft

### Problem

Phil Santos is an engineer who knows he should request a debrief after every loss but finds the administrative friction of drafting a formal debrief request letter annoying. The letter is formulaic -- it references the topic number, submission confirmation, and requests a debrief per FAR 15.505 or agency-specific procedures. Today, Phil sometimes skips the request because writing it feels like one more chore after a disappointing result.

### Who

- Engineer | Proposal not selected | Wants a ready-to-send debrief request letter with minimal effort

### Solution

An automated debrief request letter draft that references the specific topic, confirmation number, and applicable regulations, ready for Phil to review and send.

### Domain Examples

#### 1: Happy Path -- Phil gets a draft debrief request

Phil records AF243-001 as "not selected." The tool generates a debrief request letter addressed to the contracting officer, referencing topic AF243-001, confirmation DSIP-2026-AF243-001-7842, and citing FAR 15.505(a)(1). Phil reviews, adds a personal note, and sends it.

#### 2: Edge Case -- NASA submission with different procedure

For a NASA NSPIRES submission, the debrief request follows a different process. The tool generates a letter referencing the NASA-specific debrief procedure instead of FAR 15.505.

#### 3: Edge Case -- Phil skips the debrief request

Phil decides not to request a debrief (e.g., the loss was expected and he does not want to invest time). The tool records "debrief not requested" and proceeds to outcome recording only.

### UAT Scenarios (BDD)

#### Scenario: Generate debrief request letter for DoD submission

Given AF243-001 was not selected
And the submission confirmation is DSIP-2026-AF243-001-7842
When Phil requests a debrief letter draft
Then the tool generates a letter referencing AF243-001 and the confirmation number
And the letter cites FAR 15.505(a)(1)
And the draft is written to "./artifacts/wave-9-learning/debrief-request-draft.md"

#### Scenario: Generate debrief request for NASA submission

Given N244-012 was submitted to NSPIRES and not selected
When Phil requests a debrief letter draft
Then the tool generates a letter using NASA-specific debrief procedures

#### Scenario: Skip debrief request

Given AF243-001 was not selected
When Phil decides not to request a debrief
Then the tool records "debrief not requested"
And proceeds to outcome recording without creating a request letter

### Acceptance Criteria

- [ ] Debrief request letter draft references topic number, confirmation, and applicable regulations
- [ ] Letter adapts to agency-specific debrief procedures (DoD FAR vs. NASA vs. other)
- [ ] Phil can review and edit before sending
- [ ] Skipping the debrief request is a valid option
- [ ] Letter is written to artifacts directory for record keeping

### Technical Notes

- Letter templates per agency stored in templates/ directory
- FAR 15.505 for DoD; NASA has separate procedures; other agencies vary
- Low-effort feature -- small story, high friction reduction
- Depends on: confirmation record (US-013), proposal-state.json outcome

---

## Story Dependency Map

```
C1 Foundation (existing):
  US-006 (PES Foundation) ──── extends to ──── US-014 (PES C3 Invariants)
  US-004 (Compliance Matrix) ─────────────── consumed by US-011 (Formatting)
  US-007 (State Schema) ─────────────────── consumed by all C3 stories

C3 Dependencies:
  US-010 (Visual Assets)
    |
    +-- US-011 (Formatting & Assembly) -- needs approved figures
    |     |
    |     +-- US-012 (Final Review) -- needs assembled document
    |           |
    |           +-- US-013 (Submission) -- needs sign-off
    |                 |
    |                 +-- US-015 (Debrief Ingestion) -- needs submitted archive
    |                 |
    |                 +-- US-016 (Debrief Request) -- needs confirmation record
    |
    +-- US-014 (PES C3) -- enforces gates across all C3 stories
```

Build order recommendation:
1. US-014 (PES C3 Invariants) -- enforcement layer for all C3 waves
2. US-010 (Visual Assets) -- Wave 5
3. US-011 (Formatting & Assembly) -- Wave 6
4. US-012 (Final Review) -- Wave 7
5. US-013 (Submission) -- Wave 8
6. US-016 (Debrief Request Letter) -- small, low-dependency
7. US-015 (Debrief Ingestion) -- Wave 9

---

## Story Sizing Summary

| Story | Scenarios | Est. Days | Right-Sized? |
|-------|-----------|-----------|-------------|
| US-010 | 5 | 2-3 | Yes |
| US-011 | 7 | 2-3 | Yes |
| US-012 | 6 | 2-3 | Yes |
| US-013 | 6 | 2-3 | Yes |
| US-014 | 5 | 2-3 | Yes |
| US-015 | 6 | 2-3 | Yes |
| US-016 | 3 | 1 | Yes |

Total: 38 scenarios, 13-21 days estimated effort.

---

## Non-Functional Requirements (C3)

### NFR-004: Formatting Fidelity

Template-based formatting produces documents that match solicitation requirements (font, margins, page limits) without manual correction in 90% of cases. The remaining 10% (orphan/widow edge cases, complex table layouts) are clearly flagged for manual adjustment.

### NFR-005: Submission Safety

No irreversible submission action occurs without explicit human confirmation. Pre-submission verification catches 100% of missing required files and file naming violations. Immutable archive is created within 30 seconds of submission confirmation.

### NFR-006: Corpus Integrity

Win/loss tags are append-only. Source documents in the corpus are never modified by debrief annotations. Pattern analysis degrades gracefully with small corpus sizes (< 5 proposals) by noting confidence levels.

### NFR-007: Debrief Ingestion Effort

Debrief ingestion requires under 5 minutes of Phil's time for a typical debrief letter (2-3 pages). Parsing is best-effort; unstructured portions are preserved as freeform text rather than discarded.
