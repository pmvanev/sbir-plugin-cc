# Journey: Proposal Production & Learning (C3) -- Visual Map

## Persona

Phil Santos -- small business engineer, 2-3 proposals/year, sole writer, CLI-native. By Wave 5, he has invested 8-12 hours in Waves 0-4.

## Emotional Arc

```
Confidence
    ^
    |                                                    *** Relieved & Hopeful
    |                                          *** Confident (submitted + archive)
    |                                *** Relieved (formatted, assembled)
    |                      *** Cautious (final review -- last chance)
    |            *** Satisfied (figures done)
    |   *** Fatigued but engaged (writing done, production begins)
    +------------------------------------------------------------> Time
   Wave 5     Wave 6       Wave 7       Wave 8       Wave 9
   Visuals   Format      Review      Submit      Learning
```

Start: Engaged but fatigued ("The hard intellectual work is done; now the mechanical work")
Middle: Cautious and methodical ("Last chance to catch problems before the point of no return")
End: Relieved and hopeful ("It is submitted, archived, and every proposal makes the next one better")

Peak tension: Wave 8 (Submission) -- point of no return after weeks of investment.

---

## Full C3 Lifecycle Flow

```
 ============================================================================
  PHASE C3 -- Proposal Production & Learning (Waves 5-9)
  Precondition: Wave 4 complete (all sections approved, PDCs GREEN)
 ============================================================================


 WAVE 5: Visual Assets
 ─────────────────────
 Jobs: J9 (Produce visual assets that strengthen narrative)
 Commands: /proposal wave visuals
 Agent: formatter, writer

 Flow:
   Review outline    For each figure:    Cross-reference
   for figure    --> generate draft  --> validation
   placeholders      + human review      (all figures have
                     + iterate/replace   captions, all refs
                                         resolve)

 +-- /proposal wave visuals ------------------------------------------+
 |                                                                    |
 |  WAVE 5: VISUAL ASSETS                                             |
 |  Topic: AF243-001 | 14 days to deadline                            |
 |                                                                    |
 |  Figure inventory from outline:                                    |
 |    5 figures identified across 4 sections                          |
 |                                                                    |
 |  Figure 1: System Architecture Diagram (Section 3.1)               |
 |    Type: Block diagram | Method: Mermaid                           |
 |    Status: [generated -- review needed]                            |
 |                                                                    |
 |  Figure 2: Phase I Timeline (Section 4)                            |
 |    Type: Gantt chart | Method: Mermaid                             |
 |    Status: [generated -- review needed]                            |
 |                                                                    |
 |  Figure 3: SWaP-C Comparison (Section 3.2)                         |
 |    Type: Data chart | Method: SVG                                  |
 |    Status: [pending generation]                                    |
 |                                                                    |
 |  Figure 4: Concept Illustration (Section 3.3)                      |
 |    Type: Technical illustration | Method: Gemini API               |
 |    Status: [pending generation]                                    |
 |                                                                    |
 |  Figure 5: Test Setup Photo (Section 3.4)                          |
 |    Type: Photo | Method: External (manual)                         |
 |    Status: [external brief generated]                              |
 |                                                                    |
 |  Actions:                                                          |
 |    (r) review figure  (g) generate next  (s) skip to formatting    |
 +--------------------------------------------------------------------+

 Emotion: Fatigued -> Satisfied
 "Figures strengthen the narrative. The proposal is starting to look real."

 Shared Artifacts Created:
   figure_inventory         <- ./artifacts/wave-5-visuals/figure-inventory.md
   cross_reference_log      <- ./artifacts/wave-5-visuals/cross-reference-log.md
   generated_figures        <- ./artifacts/wave-5-visuals/figures/

 Error Path E7: Figure generation failure
   -> External brief generated. Phil provides manual figure file.
 Error Path E12: Deadline critical during Wave 5
   -> PES warns. Skip remaining figures, format with what you have.

 ──────────────────────────────────────────────────────────────────────


 WAVE 6: Formatting & Assembly
 ─────────────────────────────
 Jobs: J6 (Format and assemble without manual labor)
 Commands: /proposal format
 Agent: formatter, compliance-sheriff

 Flow:
   Select output   Apply          Insert     Compliance    Assemble
   medium       -> formatting  -> figures -> + jargon   -> volumes
   (Word/LaTeX/    (font,         at correct  audit +      into file
    Google Docs)    margins,       positions   page count   structure
                    headers)                   verification

 +-- /proposal format ------------------------------------------------+
 |                                                                    |
 |  WAVE 6: FORMATTING & ASSEMBLY                                      |
 |  Topic: AF243-001 | 12 days to deadline                            |
 |                                                                    |
 |  Solicitation format requirements:                                 |
 |    Font: Times New Roman 12pt | Margins: 1" all sides              |
 |    Page limit: 20 pages (technical volume)                         |
 |    Header: Topic number, company name, page number                 |
 |                                                                    |
 |  Output medium: Microsoft Word (.docx)                             |
 |                                                                    |
 |  Formatting progress:                                              |
 |    [done] Section numbering and heading styles applied             |
 |    [done] Headers and footers applied                              |
 |    [done] Figures inserted (5 figures)                             |
 |    [done] References formatted (23 citations)                      |
 |    [done] Jargon audit (all acronyms defined on first use)         |
 |                                                                    |
 |  Page count: 19/20                                                  |
 |    Within limit. 1 page of margin.                                  |
 |                                                                    |
 |  Compliance matrix final check:                                    |
 |    45/47 covered | 2 waived (with reasons) | 0 MISSING             |
 |                                                                    |
 |  Volumes assembled:                                                |
 |    Volume 1: Technical (19 pages)                                   |
 |    Volume 2: Cost (8 pages)                                         |
 |    Volume 3: Company Information (3 pages)                          |
 |                                                                    |
 |  CHECKPOINT: Review assembled package                              |
 |    (a) approve -- proceed to final review                          |
 |    (r) revise  -- provide feedback on formatting                   |
 +--------------------------------------------------------------------+

 Emotion: Dreading mechanical work -> Relieved
 "Formatting is handled. The document looks professional."

 Shared Artifacts:
   compliance_final         <- ./artifacts/wave-6-format/compliance-final-check.md
   jargon_audit             <- ./artifacts/wave-6-format/jargon-audit.md
   assembled_volumes        <- ./artifacts/wave-6-format/assembled/

 Error Path E8: Page count exceeded
   -> Tool identifies largest sections, suggests cuts.
 Error Path E12: Deadline critical during Wave 6
   -> PES warns. Submit with available formatting.

 Integration Checkpoint:
   All figures from Wave 5 inserted.
   All compliance items covered or waived.
   Page count within limits.
   Cross-references resolve. Compliance matrix is THE matrix from Wave 1.

 ──────────────────────────────────────────────────────────────────────


 WAVE 7: Final Review
 ────────────────────
 Jobs: J11 (Catch fatal flaws before submission)
 Commands: /proposal wave final-review
 Agent: reviewer, compliance-sheriff

 Flow:
   Reviewer persona   Red team     Debrief      Final         Issue
   simulation      -> review    -> cross-    -> compliance -> resolution
   (score against     (strongest   check        + attachment  loop
    eval criteria)     objections)  (corpus)     verification  (max 2 iter)
                                                              |
                                                              v
                                                          Human sign-off

 +-- /proposal wave final-review -------------------------------------+
 |                                                                    |
 |  WAVE 7: FINAL REVIEW                                               |
 |  Topic: AF243-001 | 10 days to deadline                            |
 |                                                                    |
 |  REVIEWER PERSONA SIMULATION                                        |
 |  Evaluating against 5 criteria (DoD Phase I standard)...            |
 |                                                                    |
 |  Simulated Scores:                                                 |
 |    Technical Merit:       8.2/10                                    |
 |    Innovation/Novelty:    7.5/10                                    |
 |    Phase II Potential:    6.8/10                                    |
 |    Commercial Potential:  7.0/10                                    |
 |    Company Capability:    8.5/10                                    |
 |                                                                    |
 |  Overall: 7.6/10                                                    |
 |                                                                    |
 |  RED TEAM FINDINGS (3 objections):                                  |
 |    1. [HIGH] Section 3.2: SWaP-C claim unsupported by test data    |
 |    2. [MED]  Section 4: Timeline aggressive for TRL 3->5           |
 |    3. [LOW]  Section 6: TAM estimate cites 2023 data               |
 |                                                                    |
 |  DEBRIEF CROSS-CHECK:                                               |
 |    ! AF241-087 debrief: "transition pathway lacked specificity"    |
 |      Current Section 5: Specific PMS 501 transition named -- OK    |
 |                                                                    |
 |  COMPLIANCE: All 47 items covered or waived.                        |
 |  ATTACHMENTS: 4/4 required forms present.                           |
 |                                                                    |
 |  Actions:                                                          |
 |    (f) fix issues  (i) iterate review  (s) sign-off                |
 +--------------------------------------------------------------------+

 Emotion: Cautious -> Confident
 "A simulated reviewer found issues and I addressed them. No fatal flaws."

 Shared Artifacts:
   reviewer_scorecard       <- ./artifacts/wave-7-review/reviewer-scorecard.md
   red_team_findings        <- ./artifacts/wave-7-review/red-team-findings.md
   debrief_cross_check      <- ./artifacts/wave-7-review/debrief-cross-check.md
   sign_off_record          <- ./artifacts/wave-7-review/sign-off-record.md

 Integration Checkpoint:
   Assembled document from Wave 6 exists.
   All HIGH-severity findings addressed.
   Sign-off recorded. PES gate: Wave 8 requires sign-off.

 ──────────────────────────────────────────────────────────────────────


 WAVE 8: Submission
 ──────────────────
 Jobs: J10 (Survive submission without errors)
 Commands: /proposal submit prep | /proposal submit
 Agent: submission-agent

 Flow:
   Identify     Portal-specific    Pre-submission    Human         Submit +
   portal    -> packaging       -> verification   -> confirmation -> archive
   (DSIP,       (file naming,      (all files       (point of
    Grants.gov,  size limits,       present, named   no return)
    NSPIRES)     format rules)      correctly)

 +-- /proposal submit prep -------------------------------------------+
 |                                                                    |
 |  WAVE 8: SUBMISSION PREPARATION                                     |
 |  Topic: AF243-001 | 8 days to deadline                             |
 |                                                                    |
 |  Submission portal: DSIP (Defense SBIR/STTR Innovation Portal)     |
 |  Portal URL: https://www.dodsbirsttr.mil/submissions               |
 |                                                                    |
 |  Package contents:                                                 |
 |    [ok] AF243-001_IntaptAI_Vol1_Technical.pdf (2.3 MB)             |
 |    [ok] AF243-001_IntaptAI_Vol2_Cost.pdf (0.8 MB)                  |
 |    [ok] AF243-001_IntaptAI_Vol3_CompanyInfo.pdf (0.4 MB)           |
 |    [ok] AF243-001_IntaptAI_FirmCert.pdf (0.1 MB)                   |
 |                                                                    |
 |  File naming check: PASS (DSIP convention)                          |
 |  Size limits: PASS (all under 10 MB limit)                          |
 |  Format check: PASS (all PDF, all readable)                         |
 |                                                                    |
 |  Pre-submission checklist: 4/4 items verified                       |
 |                                                                    |
 +--------------------------------------------------------------------+

 +-- /proposal submit ------------------------------------------------+
 |                                                                    |
 |  POINT OF NO RETURN                                                  |
 |  Once submitted, PES marks all artifacts as read-only.              |
 |                                                                    |
 |  Confirm submission? (y/n)                                          |
 |  > y                                                                |
 |                                                                    |
 |  SUBMITTED at 2026-04-07T14:23:17Z                                   |
 |  Confirmation: DSIP-2026-AF243-001-7842                              |
 |                                                                    |
 |  Archive created: ./artifacts/wave-8-submission/archive/            |
 |  PES: All proposal artifacts marked READ-ONLY.                      |
 |                                                                    |
 |  Next: Await award notification (~90-120 days).                     |
 |  When result arrives: /proposal debrief ingest <path>              |
 |                                                                    |
 +--------------------------------------------------------------------+

 Emotion: Anxious -> Relieved
 "It is submitted. I have a confirmation and an archive. Nothing is lost."

 Shared Artifacts:
   submission_package       <- ./artifacts/wave-8-submission/package/
   confirmation_record      <- ./artifacts/wave-8-submission/confirmation-record.md
   immutable_archive        <- ./artifacts/wave-8-submission/archive/

 Error Path E9: Missing attachment
   -> Submission blocked until attachment provided.
 Error Path E10: Portal requirements changed
   -> Display expected vs. actual. Manual adjustment needed.

 Integration Checkpoint:
   Wave 7 sign-off recorded.
   All files present, named correctly, within limits.
   Human confirmed submission.
   PES immutability enforced on all artifacts.

 ──────────────────────────────────────────────────────────────────────


 WAVE 9: Post-Submission & Learning
 ───────────────────────────────────
 Jobs: J7 (Learn from win/loss patterns)
 Commands: /proposal debrief ingest <path>
 Agent: debrief-analyst, corpus-librarian

 Note: Wave 9 occurs weeks/months after Wave 8.
 Two paths: award or not selected.

 Flow (not selected path):
   Record      Draft debrief    Ingest      Map critiques   Update
   outcome  -> request       -> debrief  -> to sections  -> patterns
   (awarded/   letter           feedback    and known       + corpus
    not                                     weaknesses      + lessons
    selected)

 +-- /proposal debrief ingest ----------------------------------------+
 |                                                                    |
 |  WAVE 9: POST-SUBMISSION LEARNING                                   |
 |  Topic: AF243-001 -- "Compact Directed Energy for Maritime UAS"    |
 |                                                                    |
 |  Outcome: Not Selected                                              |
 |                                                                    |
 |  Parsing debrief: ./debriefs/AF243-001-debrief.pdf                  |
 |                                                                    |
 |  DEBRIEF SUMMARY                                                    |
 |  ┌──────────────────────────────────────────────────────────────┐  |
 |  │ Reviewer Scores:                                             │  |
 |  │   Technical Merit: 7.8/10                                    │  |
 |  │   Innovation:      7.2/10                                    │  |
 |  │   Phase II Plan:   5.5/10                                    │  |
 |  │   Cost Realism:    8.0/10                                    │  |
 |  └──────────────────────────────────────────────────────────────┘  |
 |                                                                    |
 |  CRITIQUE-TO-SECTION MAPPING                                        |
 |  ┌──────────────────────────────────────────────────────────────┐  |
 |  │ 1. "Transition pathway lacked specificity"                   │  |
 |  │    -> Section 5: Phase II/III Plan (page 17)                 │  |
 |  │    -> Known weakness: YES (also flagged in AF241-087)        │  |
 |  │                                                              │  |
 |  │ 2. "Cost estimate for key personnel appears high"            │  |
 |  │    -> Cost Volume: Labor Rates (page 3)                      │  |
 |  │    -> Known weakness: NO (new finding)                       │  |
 |  │                                                              │  |
 |  │ 3. "Strong prior relevant work evidence"                     │  |
 |  │    -> Section 4: Company Qualifications (page 15)            │  |
 |  │    -> Strength: consistent with N222-038 win pattern         │  |
 |  └──────────────────────────────────────────────────────────────┘  |
 |                                                                    |
 |  WIN/LOSS PATTERN UPDATE                                            |
 |    Proposals in corpus: 7                                           |
 |    Win rate: 3/7 (43%)                                              |
 |    Recurring weakness: "transition pathway specificity" (2/4 losses)|
 |    Recurring strength: "prior relevant work" (3/3 wins)             |
 |                                                                    |
 |  Lessons learned: ./artifacts/wave-9-learning/lessons-learned.md   |
 |                                                                    |
 |  CHECKPOINT: Lessons Learned Review                                |
 |    (a) acknowledge  (e) edit lessons  (d) done                     |
 +--------------------------------------------------------------------+

 Emotion: Reflective -> Hopeful
 "Every proposal makes the next one better. I can see the patterns now."

 Shared Artifacts:
   proposal_outcome         <- proposal-state.json#volumes.*.outcome
   debrief_structured       <- ./artifacts/wave-9-learning/debrief-structured.md
   critique_section_map     <- ./artifacts/wave-9-learning/critique-section-map.md
   pattern_analysis         <- ./artifacts/wave-9-learning/pattern-analysis.md
   lessons_learned          <- ./artifacts/wave-9-learning/lessons-learned.md
   win_loss_tags            <- proposal-state.json (append-only, PES enforced)

 Error Path E11: Debrief not received
   -> Record outcome without debrief. Can ingest later.

 Integration Checkpoint:
   Submission confirmation exists (Wave 8 complete).
   Outcome recorded before debrief ingestion.
   Win/loss tags are append-only. PES corpus integrity enforced.
   Debrief annotations layer -- source documents never modified.
```

---

## Error Paths Summary (C3)

| ID | Error | Trigger | Recovery |
|----|-------|---------|----------|
| E7 | Figure generation failure | Malformed output, API unavailable | External brief for manual creation |
| E8 | Page count exceeded | Assembled doc over limit | Identify largest sections, suggest cuts |
| E9 | Missing attachment | Required form not in package | Block submission until provided |
| E10 | Portal requirements changed | Naming/size convention differs | Display expected vs. actual |
| E11 | Debrief not received | Agency provides no feedback | Record outcome only, ingest later |
| E12 | Deadline critical during formatting | Critical threshold hit in Wave 5/6 | PES warning, skip non-essential work |

---

## PES Gate Summary (C3)

```
Wave 4 ──[PDC Gate]──> Wave 5
  All sections Tier 1+2 GREEN; human review recorded per section.

Wave 5 ──[Figure Gate]──> Wave 6
  All figure placeholders either generated or marked external/skipped.

Wave 6 ──[Compliance Gate]──> Wave 7
  All compliance items covered or waived. All figures inserted.
  Page count within limits.

Wave 7 ──[Sign-Off Gate]──> Wave 8
  Final review sign-off recorded.

Wave 8 ──[Immutability]──> Wave 9
  Submission confirmed. All artifacts marked read-only.
  PES blocks any modification to submitted files.

Any Wave ──[Deadline Block]──> Non-essential work
  When days_to_deadline < critical threshold, PES blocks optional
  waves and surfaces "submit what you have" guidance.
```
