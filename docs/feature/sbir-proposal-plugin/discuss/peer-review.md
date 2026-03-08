# Peer Review -- Phase C1 Requirements Package

## Review Metadata

- Reviewer: product-owner (review mode)
- Artifact: docs/feature/sbir-proposal-plugin/discuss/user-stories.md
- Iteration: 1

---

## Strengths

1. **Strong problem-first framing**: Every story starts from user pain in domain language ("disorienting to return after days away", "penalty is disqualification"). No "Implement X" anti-patterns detected.

2. **Real data throughout**: AF243-001, N244-012, "Compact Directed Energy for Maritime UAS Defense", PMS 501, 47 compliance items. No generic user123 or test@test.com.

3. **Async event handling explicit**: TPOC call as an external async event with "pending" as a valid terminal state is a design insight that many requirements would miss.

4. **Dependency map clear**: Build order and dependency graph make the sequence unambiguous for the solution architect.

5. **10-15 hour constraint threaded throughout**: The time-value constraint from discovery is reflected in design implications (near-zero ingestion overhead, immediately useful on first command).

6. **PES extensibility as an explicit requirement**: Phase C1 scopes three invariants but requires the architecture to support adding more without engine changes. This prevents C2/C3 from hitting a wall.

---

## Issues Identified

### Confirmation Bias

**Issue 1: Single-persona coverage**
Severity: MEDIUM
Location: All stories
Finding: All 8 stories are from Phil Santos's perspective only. The discovery identified 8 other writers as future users, but no story addresses the "second user onboarding" experience. This is acceptable for Phase C1 (single-user, opinionated) but should be noted as a gap for Phase C2 planning.
Recommendation: No change needed for C1 handoff. Add a note to the handoff package that Phase C2 should include a "second user onboarding" story.

**Issue 2: Happy path bias in corpus ingestion**
Severity: MEDIUM
Location: US-003
Finding: No scenario covers what happens when a document is too large to ingest, when the corpus directory is on a network drive with latency, or when a PDF is password-protected. These are realistic failure modes.
Recommendation: Add one more error scenario to US-003: "Password-protected or corrupted document is skipped with a warning."

### Completeness Gaps

**Issue 3: No NFR for response time**
Severity: HIGH
Location: All stories
Finding: No story specifies how fast commands should respond. The TUI patterns skill says "print something in <100ms." For a tool where re-entry after days away is critical (US-001), the status command should have a response time expectation.
Recommendation: Add a property-shaped NFR: "Status command responds within 1 second. Commands that trigger parsing or search display a progress indicator within 100ms."

**Issue 4: Missing strategy brief checkpoint scenario**
Severity: MEDIUM
Location: US-005
Finding: The journey shows a strategy alignment checkpoint (Step 2d) but no user story explicitly covers the strategy brief generation and approval. US-005 covers TPOC questions and ingestion, but the strategy brief -- which is the Wave 1 exit gate -- is not a story.
Recommendation: Either expand US-004 or US-005 to cover strategy brief approval, or add a US-009 for the Wave 1 checkpoint. This is a gap.

### Clarity Issues

**Issue 5: "Supported document types" not defined**
Severity: MEDIUM
Location: US-003 Technical Notes
Finding: "Supported formats: PDF, .docx, .doc, .txt, .md" is in technical notes but not in AC. The user expects to know which formats are supported via the tool itself.
Recommendation: Add AC: "Tool displays supported formats when asked or when unsupported files are skipped."

### Testability Concerns

No critical testability issues found. All AC are observable and measurable.

### Priority Validation

- Q1 (Largest bottleneck): YES -- Phase C1 addresses the two highest-scored jobs (J1, J2) that all 9 sources confirmed.
- Q2 (Simpler alternatives): ADEQUATE -- Discovery considered existing tools (Procura, ChatGPT, manual checklists) and found them insufficient.
- Q3 (Constraint prioritization): CORRECT -- 10-15 hour budget is the dominant constraint and is threaded through stories.
- Q4 (Data justified): JUSTIFIED -- 9 sources, 100% confirmation, $5-10K current spend.
- Verdict: PASS

---

## Remediation Required

| # | Issue | Severity | Action |
|---|-------|----------|--------|
| 2 | Corpus ingestion missing error scenario | MEDIUM | Add scenario for corrupted/protected documents |
| 3 | No NFR for response time | HIGH | Add response time property to handoff package |
| 4 | Strategy brief checkpoint not covered | MEDIUM | Add US-009 or expand existing story |
| 5 | Supported formats not in AC | MEDIUM | Add AC to US-003 |

---

## Remediation Applied (Iteration 2)

| # | Issue | Remediation |
|---|-------|-------------|
| 2 | Corpus ingestion missing error scenario | Added scenario for corrupted/protected documents to US-003; added AC for format display |
| 3 | No NFR for response time | Added NFR-001 (response time), NFR-002 (data safety), NFR-003 (CLI accessibility) to user-stories.md |
| 4 | Strategy brief checkpoint not covered | Added US-009: Strategy Brief and Wave 1 Checkpoint |
| 5 | Supported formats not in AC | Added AC to US-003: "Tool displays supported file formats when unsupported files are skipped" |

---

## Approval Status

**APPROVED** -- all issues remediated. 9 stories, 39 scenarios, all DoR items passed.

No critical or high issues remaining.
