<!-- markdownlint-disable MD024 -->

# Phase C1 User Stories -- SBIR Proposal Writing Plugin

Scope: Walking skeleton (Waves 0-1) plus PES foundation and status/reorientation.
All stories trace to JTBD analysis jobs and journey steps.
Phase C2/C3 stories are covered by journey artifacts, not written here.

---

## US-001: Proposal Status and Reorientation

### Problem

Phil Santos is an engineer who writes 2-3 SBIR proposals per year, working on each across multiple sessions over several weeks. He finds it disorienting to return to a proposal after days away because he has to remember where he left off, what the pending actions are, and how much time remains before the deadline. Today he relies on memory and scattered notes.

### Who

- Engineer | Returning to proposal after days away | Needs to regain context in seconds, not minutes

### Solution

A status command that displays the complete state of the active proposal -- current wave, progress per wave, pending actions (including async events like TPOC calls), deadline countdown, and a suggested next action.

### Domain Examples

#### 1: Happy Path -- Phil returns mid-Wave 1

Phil Santos has an active proposal for topic AF243-001 ("Compact Directed Energy for Maritime UAS Defense"). He generated TPOC questions 5 days ago but has not had the call yet. 18 days remain until deadline. He runs `/proposal status` and immediately sees: Wave 1 active, TPOC questions pending call, compliance matrix generated with 47 items, next action is "Have TPOC call then /proposal tpoc ingest."

#### 2: Edge Case -- Phil returns with deadline pressure

Phil returns to proposal N244-012 ("Autonomous Underwater Vehicle Navigation") with only 4 days remaining. Wave 4 drafting is incomplete. Status shows a PES deadline warning in amber: "4 days remaining -- critical threshold. Consider skipping non-essential waves." The next action suggestion prioritizes the highest-impact incomplete work.

#### 3: Error Path -- No active proposal exists

Phil runs `/proposal status` but has no active proposal. The tool displays: "No active proposal found. Start one with /proposal new or resume from a saved state." No crash, no cryptic error.

### UAT Scenarios (BDD)

#### Scenario: Reorient after days away from active proposal

Given Phil Santos has an active proposal for topic AF243-001 in Wave 1
And the compliance matrix has 47 items
And TPOC questions were generated 5 days ago with status "pending"
And 18 days remain until the deadline
When Phil runs "/proposal status"
Then the tool displays "Wave 1: Requirements & Strategy" as the current wave
And the tool displays "Compliance matrix generated (47 items)"
And the tool displays "TPOC questions generated -- PENDING CALL"
And the tool displays "18 days to deadline"
And the tool suggests "Have TPOC call, then /proposal tpoc ingest"

#### Scenario: Status shows deadline warning at critical threshold

Given Phil Santos has an active proposal for topic N244-012 in Wave 4
And 4 days remain until the deadline
When Phil runs "/proposal status"
Then the tool displays a deadline warning: "4 days remaining -- critical threshold"
And the tool suggests prioritizing the highest-impact incomplete work

#### Scenario: Status with no active proposal

Given no active proposal exists in the current directory
When Phil runs "/proposal status"
Then the tool displays "No active proposal found"
And the tool suggests "/proposal new" to start one

#### Scenario: Status shows completed waves and pending async events

Given Phil Santos has an active proposal with Wave 0 completed (Go approved)
And Wave 1 is active with strategy brief not yet started
And TPOC status is "pending"
When Phil runs "/proposal status"
Then Wave 0 shows "[completed] Go: approved"
And Wave 1 shows "[active]" with detail lines for each sub-task
And subsequent waves show "[not started]"

### Acceptance Criteria

- [ ] Status displays current wave, per-wave progress, and deadline countdown
- [ ] Status shows pending async events (TPOC call) with their state
- [ ] Status suggests a concrete next action based on current state
- [ ] Status shows PES deadline warning when within critical threshold
- [ ] Status handles gracefully when no proposal exists

### Technical Notes

- Reads from proposal-state.json; does not modify state
- Days-to-deadline computed at display time from stored deadline date
- PES deadline thresholds configurable in pes-config.json (warning_days, critical_days)
- Depends on: proposal-state.json schema (US-007)

---

## US-002: Start New Proposal from Solicitation

### Problem

Phil Santos is an engineer who finds a promising SBIR solicitation and wants to evaluate whether it is worth pursuing. He finds it time-consuming to manually parse the solicitation for topic metadata (agency, phase, deadline, title) and assess company fit without structured data. Today he reads the solicitation, eyeballs the fit, and decides in his head.

### Who

- Engineer | Found new solicitation | Wants data-driven Go/No-Go, not gut feel

### Solution

A new-proposal command that accepts a solicitation URL or local file path, parses it for metadata, searches the corpus for relevant past work, scores company fit, and presents a structured Go/No-Go recommendation at a human checkpoint.

### Domain Examples

#### 1: Happy Path -- Phil starts proposal from SBIR.gov URL

Phil provides URL "https://www.sbir.gov/node/12345" for topic AF243-001. The tool parses it: Air Force, Phase I, deadline 2026-04-15, title "Compact Directed Energy for Maritime UAS Defense." Corpus search finds 2 related proposals. Fit scoring shows HIGH subject matter match, MEDIUM past performance. Recommendation: GO. Phil approves.

#### 2: Edge Case -- Empty corpus on first use

Phil has never ingested any documents. He starts a new proposal for topic N244-012. The tool parses the solicitation normally but displays "No corpus documents found. Add past proposals with: /proposal corpus add <directory>." Fit scoring proceeds with solicitation data alone (no past work matches). Phil still gets a recommendation but with lower confidence.

#### 3: Error Path -- Solicitation URL cannot be parsed

Phil provides a URL that redirects to a login page. The tool displays: "Could not parse solicitation at this URL. The page may require authentication. Try downloading the PDF and providing a local file path: /proposal new --file ./solicitation.pdf"

### UAT Scenarios (BDD)

#### Scenario: Start new proposal from SBIR.gov URL

Given Phil Santos has a corpus with 5 ingested past proposals
When Phil runs "/proposal new" and provides URL "https://www.sbir.gov/node/12345"
Then the tool parses the solicitation and displays topic ID "AF243-001"
And displays agency "Air Force", phase "I", deadline "2026-04-15"
And displays title "Compact Directed Energy for Maritime UAS Defense"
And searches the corpus and displays 2 related proposals with relevance scores
And scores company fit across subject matter, past performance, and certifications
And presents a Go/No-Go recommendation

#### Scenario: Start new proposal from local PDF file

Given Phil has downloaded a solicitation PDF to "./solicitations/AF243-001.pdf"
When Phil runs "/proposal new --file ./solicitations/AF243-001.pdf"
Then the tool parses the PDF and displays the same topic metadata
And creates proposal-state.json

#### Scenario: Empty corpus does not block new proposal

Given Phil has never ingested any documents into the corpus
When the tool attempts corpus search for a new proposal
Then the tool displays "No corpus documents found"
And suggests "Add past proposals with: /proposal corpus add <directory>"
And proceeds with fit scoring based on solicitation data alone

#### Scenario: Solicitation URL cannot be parsed

Given Phil provides a URL that returns a login page
When the tool attempts to parse the solicitation
Then the tool displays "Could not parse solicitation at this URL"
And suggests downloading the PDF and using --file flag

#### Scenario: Go decision recorded and unlocks Wave 1

Given the tool has presented a Go/No-Go recommendation for AF243-001
When Phil selects "(g) go"
Then proposal-state.json records go_no_go as "go"
And the tool displays "Proceeding to Wave 1: Requirements & Strategy"

#### Scenario: No-Go decision archives the proposal

Given the tool has presented a Go/No-Go recommendation for AF243-001
When Phil selects "(n) no-go"
Then proposal-state.json records go_no_go as "no-go"
And the tool archives the proposal state
And displays "AF243-001 archived as no-go"

### Acceptance Criteria

- [ ] Tool parses solicitation from URL or local file and extracts topic ID, agency, phase, deadline, title
- [ ] Tool searches corpus for related past work and displays matches with relevance scores
- [ ] Tool scores company fit and presents a structured recommendation
- [ ] Go/No-Go is a human checkpoint with go, no-go, and defer options
- [ ] Go decision records in proposal-state.json and unlocks Wave 1
- [ ] No-Go decision archives the proposal
- [ ] Empty corpus is handled gracefully without blocking the workflow
- [ ] Unparseable solicitation produces actionable error message

### Technical Notes

- Solicitation parsing may require different strategies per source (SBIR.gov HTML, PDF, agency portals)
- Corpus search uses semantic similarity; relevance threshold is configurable
- Company profile (capabilities, certifications) stored in company-profile.json
- Depends on: corpus manager (US-003), proposal-state.json schema (US-007)

---

## US-003: Directory-Based Corpus Ingestion

### Problem

Phil Santos is an engineer who needs past proposals, debriefs, and TPOC logs available for semantic search, but finds it unacceptable to spend hours organizing and ingesting documents one at a time. At 2-3 proposals per year, any ingestion overhead that exceeds a few minutes per batch is a net time loss. Today his past work is scattered across directories with no search capability.

### Who

- Engineer | Has directories of past proposals and debriefs | Wants batch ingestion with near-zero effort

### Solution

A corpus add command that accepts a directory path, ingests all supported documents from it, reports what was found, and makes them available for semantic search. Incremental -- running it again on the same directory adds only new files.

### Domain Examples

#### 1: Happy Path -- Phil ingests a directory of past proposals

Phil has a directory "./past-proposals/" containing 5 proposal PDFs and 2 debrief letters (Word docs). He runs `/proposal corpus add ./past-proposals/`. The tool ingests all 7 documents, displays a summary (5 proposals, 2 debriefs detected), and confirms the corpus is ready for search.

#### 2: Edge Case -- Directory contains non-document files

Phil points the tool at "./projects/af243/" which contains 3 PDFs, 2 Word docs, 1 Excel spreadsheet, and 15 source code files. The tool ingests the 5 supported documents, skips the rest, and reports: "Ingested 5 documents. Skipped 16 unsupported files."

#### 3: Edge Case -- Re-ingesting a directory adds only new files

Phil runs `/proposal corpus add ./past-proposals/` again after adding 1 new PDF to the directory. The tool detects 7 already-ingested files and 1 new file. It ingests only the new file and reports: "1 new document ingested. 7 already in corpus."

### UAT Scenarios (BDD)

#### Scenario: Ingest a directory of past proposals and debriefs

Given Phil Santos has a directory "./past-proposals/" with 5 PDF proposals and 2 Word debrief letters
When Phil runs "/proposal corpus add ./past-proposals/"
Then the tool ingests all 7 documents
And displays "Ingested 7 documents (5 proposals, 2 debriefs)"
And the corpus index is updated for semantic search

#### Scenario: Skip unsupported file types in directory

Given a directory contains 3 PDFs, 2 Word docs, and 15 Python source files
When Phil runs "/proposal corpus add ./projects/af243/"
Then the tool ingests 5 supported documents
And skips 15 unsupported files
And reports "Ingested 5 documents. Skipped 15 unsupported files."

#### Scenario: Re-ingestion adds only new files

Given Phil previously ingested "./past-proposals/" with 7 documents
And Phil has added 1 new PDF to the directory
When Phil runs "/proposal corpus add ./past-proposals/"
Then the tool detects 7 already-ingested documents
And ingests only the 1 new document
And reports "1 new document ingested. 7 already in corpus."

#### Scenario: Empty directory handled gracefully

Given Phil provides a path to an empty directory
When Phil runs "/proposal corpus add ./empty-dir/"
Then the tool reports "No supported documents found in ./empty-dir/"
And suggests supported file types

#### Scenario: Corrupted or protected document skipped with warning

Given a directory contains 4 PDFs, one of which is password-protected
When Phil runs "/proposal corpus add ./mixed-docs/"
Then the tool ingests the 3 readable PDFs
And skips the password-protected PDF with warning: "Skipped 1 unreadable document (password-protected or corrupted)"
And lists the skipped file by name

### Acceptance Criteria

- [ ] Accepts a directory path and ingests all supported document types (PDF, Word, plain text)
- [ ] Reports count and type of ingested documents
- [ ] Skips unsupported file types with a count of skipped files
- [ ] Skips unreadable documents (corrupted, password-protected) with individual warnings
- [ ] Incremental -- re-ingesting a directory adds only new files
- [ ] Empty directory produces helpful message, not error
- [ ] Ingested documents are available for semantic search immediately
- [ ] Tool displays supported file formats when unsupported files are skipped

### Technical Notes

- Supported formats: PDF, .docx, .doc, .txt, .md (extensible list)
- Deduplication by file content hash, not filename
- Corpus stored in ./state/corpus/ with index for semantic retrieval
- No file-by-file confirmation; batch operation by default
- Depends on: corpus storage architecture (ADR-005)

---

## US-004: Automated Compliance Matrix from Solicitation

### Problem

Phil Santos is an engineer who must track dozens of "shall" statements across a solicitation to avoid disqualification. He finds it inadequate to use manual checklists because requirements get missed, especially implicit ones and those buried in appendices. The penalty for missing a compliance item is disqualification -- a complete waste of the 10-15 hours invested. Today he reads the solicitation multiple times and maintains a spreadsheet.

### Who

- Engineer | Parsing a new solicitation | Needs every requirement surfaced and mapped, not hidden in dense text

### Solution

Automated extraction of all "shall" statements and implicit requirements from the solicitation, mapped to proposal sections, with ambiguities flagged. The matrix is a living document -- human-editable, updated across waves.

### Domain Examples

#### 1: Happy Path -- Phil generates compliance matrix for AF243-001

Phil runs `/proposal wave strategy` for AF243-001. The tool parses the solicitation and extracts 47 compliance items: 38 explicit "shall" statements, 6 format requirements (font, margins, page limits), and 3 implicit requirements from evaluation criteria language. Each item is mapped to a proposal section. 3 ambiguities are flagged: "relevant environment" (define what qualifies), "appropriate integration" (scope unclear), "sufficient detail" (subjective threshold).

#### 2: Edge Case -- Phil finds a missed requirement

After generating the matrix, Phil reads the solicitation appendix and finds a requirement the parser missed: "Section 3 shall include a risk mitigation table." He runs `/proposal compliance add 'Section 3 shall include risk mitigation table'` and the matrix updates to 48 items with the new item marked as manually added.

#### 3: Error Path -- Solicitation has few extractable requirements

Phil runs compliance extraction on a short, informal solicitation (e.g., DOE with minimal structure). The tool extracts only 8 items and warns: "Low extraction count (8 items). This solicitation may use informal language. Review manually for implicit requirements."

### UAT Scenarios (BDD)

#### Scenario: Generate compliance matrix from solicitation

Given Phil Santos has an active proposal for AF243-001 with go_no_go "go"
When Phil runs "/proposal wave strategy"
Then the tool extracts compliance items from the solicitation
And generates a compliance matrix with items mapped to proposal sections
And flags ambiguous requirements with explanations
And writes the matrix to "./artifacts/wave-1-strategy/compliance-matrix.md"

#### Scenario: Manually add a missed compliance item

Given a compliance matrix exists with 47 items for AF243-001
When Phil runs "/proposal compliance add 'Section 3 shall include risk mitigation table'"
Then the matrix updates to 48 items
And the new item is marked as "manually added"
And the item is mapped to Section 3

#### Scenario: Low extraction count triggers warning

Given a solicitation with minimal structured requirements
When the tool extracts compliance items
Then the tool warns "Low extraction count. Review manually for implicit requirements."

#### Scenario: Compliance check shows matrix status

Given a compliance matrix exists with 47 items
And 12 items have status "covered" and 35 have status "--"
When Phil runs "/proposal compliance check"
Then the tool displays "12/47 covered | 0 partial | 35 not started"

### Acceptance Criteria

- [ ] Extracts explicit "shall" statements from solicitation text
- [ ] Extracts format requirements (font, margins, page limits)
- [ ] Extracts implicit requirements from evaluation criteria language
- [ ] Maps each item to a proposal section
- [ ] Flags ambiguous requirements with explanation
- [ ] Matrix is human-editable (add, remove, annotate items)
- [ ] `/proposal compliance check` displays current matrix status
- [ ] Low extraction count produces a warning, not silent acceptance

### Technical Notes

- Matrix is a Markdown file, not a database; editable in any text editor
- Item status values: -- (not started), covered, partial, missing, waived
- Waived items require reason (PES enforcement when waiver_requires_reason is true)
- Matrix is a living document updated through Wave 7
- Depends on: solicitation parsing from US-002, proposal-state.json schema (US-007)

---

## US-005: TPOC Question Generation and Answer Ingestion

### Problem

Phil Santos is an engineer who gets one chance to talk to the TPOC (Technical Point of Contact) before submitting. He finds it difficult to generate sharp, strategically sequenced questions from a dense solicitation because he must identify gaps, avoid revealing competitive intent, and sequence for conversational flow -- all under time pressure. Today he reads the solicitation repeatedly and writes questions from intuition. After the call, insights live in handwritten notes and are not systematically propagated to downstream artifacts.

### Who

- Engineer | Preparing for TPOC call | Needs strategically prioritized questions that surface the real requirements

### Solution

Generate a prioritized TPOC question list from solicitation gaps, ambiguities, and strategic probes. After the call (an async event days later), ingest answers and run delta analysis against the solicitation. Propagate insights to compliance matrix and strategy brief. Handle "call never happened" as a valid state.

### Domain Examples

#### 1: Happy Path -- Phil generates questions and ingests answers days later

Phil runs `/proposal tpoc questions` for AF243-001. The tool generates 23 questions categorized by type (scope-clarification, approach-validation, incumbent-landscape, etc.) and ordered by strategic priority. Phil edits the list before his call. Five days later, he runs `/proposal tpoc ingest` and provides his call notes file. The tool matches 18 answers to questions, marks 5 unanswered, and generates a delta analysis showing that "compact" means < 50 lbs and the Phase III transition target is PMS 501.

#### 2: Edge Case -- TPOC call never happens

Phil generates questions for topic N244-012 but the TPOC is unavailable before the deadline. `/proposal status` shows "TPOC questions pending -- no call recorded." Phil proceeds to strategy alignment using solicitation text alone. The pending state does not block any wave.

#### 3: Edge Case -- Phil ingests partial notes

Phil had a 10-minute call instead of the planned 30 minutes and only covered 8 of 23 questions. He ingests his notes. The tool matches 8 answers, marks 15 as unanswered, and generates delta analysis from the 8 answered questions.

### UAT Scenarios (BDD)

#### Scenario: Generate TPOC questions from solicitation gaps

Given a compliance matrix exists for AF243-001 with 3 flagged ambiguities
When Phil runs "/proposal tpoc questions"
Then the tool generates prioritized questions tagged by category
And questions are sequenced for conversational flow (relationship-building first, strategic probes later)
And questions are written to "./artifacts/wave-1-strategy/tpoc-questions.md"

#### Scenario: Ingest TPOC answers from a notes file

Given TPOC questions were generated for AF243-001
And Phil has a notes file "./notes/tpoc-call-2026-03-15.txt"
When Phil runs "/proposal tpoc ingest" and provides the file path
Then the tool matches answers to questions
And marks unanswered questions
And generates a solicitation delta analysis
And updates the compliance matrix with TPOC clarifications
And writes the Q&A log to "./artifacts/wave-1-strategy/tpoc-qa-log.md"

#### Scenario: TPOC call never happens -- status shows pending

Given TPOC questions were generated 14 days ago
And no answers have been ingested
When Phil runs "/proposal status"
Then status shows "TPOC questions generated -- PENDING CALL"
And no wave is blocked by the pending TPOC state

#### Scenario: Partial answer ingestion

Given 23 TPOC questions were generated
And Phil's notes only cover 8 questions
When Phil ingests the partial notes
Then the tool matches 8 answers
And marks 15 questions as unanswered
And generates delta analysis from the 8 answered questions

### Acceptance Criteria

- [ ] Questions are generated from solicitation ambiguities, gaps, and strategic probes
- [ ] Questions are categorized by type and ordered by strategic priority
- [ ] Questions are written to an editable file the user modifies before the call
- [ ] Answer ingestion accepts a file path (text, Markdown, or Word)
- [ ] Ingestion matches answers to original questions and marks unanswered ones
- [ ] Delta analysis identifies differences between TPOC answers and solicitation text
- [ ] Compliance matrix is updated with TPOC clarifications
- [ ] "Call never happened" is a valid terminal state that does not block progress

### Technical Notes

- TPOC call is an async external event; days may pass between question generation and ingestion
- Answer matching is best-effort (semantic, not exact); unmatched answers are preserved as freeform notes
- Delta analysis propagates to compliance matrix and strategy brief
- TPOC Q&A log is write-once after ingestion (PES immutability)
- Depends on: compliance matrix (US-004), proposal-state.json schema (US-007)

---

## US-006: PES Foundation -- Session Startup, Wave Ordering, and Compliance Gate

### Problem

Phil Santos is an engineer who worries about missing compliance requirements and losing work when sessions end unexpectedly. He finds it risky to rely solely on discipline and memory to enforce proposal process integrity. Current AI tools lack structural guardrails -- they rely on agent instructions rather than enforcement hooks. Today, process discipline is entirely manual.

### Who

- Engineer | Working across multiple sessions over weeks | Needs structural guarantees that process integrity is maintained

### Solution

A Proposal Enforcement System (PES) foundation with three invariant classes for Phase C1: (1) session startup integrity checks, (2) wave ordering enforcement, (3) compliance matrix existence gate. Designed to be extensible -- additional invariants added in Phase C2/C3 without architectural changes.

### Domain Examples

#### 1: Happy Path -- PES session startup catches orphaned draft

Phil's last session crashed mid-draft. When he starts a new session, PES runs a silent integrity check on proposal-state.json, detects that section-3.2 has a draft file but no compliance matrix entry, and surfaces: "1 warning: Section 3.2 draft exists but has no compliance matrix entry. Run /proposal compliance check for details."

#### 2: Happy Path -- PES enforces wave ordering

Phil tries to run `/proposal wave strategy` before completing the Go/No-Go decision in Wave 0. PES blocks the command: "Wave 1 cannot start before Go/No-Go decision in Wave 0. Run /proposal status to see current state."

#### 3: Edge Case -- PES extensibility for future invariants

In Phase C2, the team adds a new invariant: "No section draft without a PDC file." The PES configuration accepts the new rule without changing the enforcement engine architecture. The rule is added to pes-config.json and the engine evaluates it alongside existing rules.

### UAT Scenarios (BDD)

#### Scenario: Session startup integrity check detects orphaned draft

Given Phil's last session ended unexpectedly
And a draft file exists for section 3.2 without a compliance matrix entry
When Phil starts a new Claude Code session with the proposal plugin active
Then PES runs an integrity check on proposal-state.json
And PES surfaces: "Section 3.2 draft exists but has no compliance matrix entry"
And PES suggests "/proposal compliance check"

#### Scenario: Session startup with clean state is silent

Given Phil's proposal state is consistent with no orphaned files
When Phil starts a new session
Then PES runs its integrity check silently
And no warnings are displayed

#### Scenario: Wave ordering -- block Wave 1 before Go decision

Given Phil has an active proposal with go_no_go "pending"
When Phil runs "/proposal wave strategy"
Then PES blocks the command
And displays "Wave 1 requires Go decision in Wave 0"

#### Scenario: Wave ordering -- allow Wave 1 after Go decision

Given Phil has an active proposal with go_no_go "go"
When Phil runs "/proposal wave strategy"
Then the command proceeds normally

#### Scenario: PES compliance gate -- block drafting without matrix entry

Given Phil has an active proposal with a compliance matrix
And no matrix entry covers section 3.2
When Phil attempts to draft section 3.2
Then PES blocks the action
And displays "No compliance matrix entry covers section 3.2"
And suggests "/proposal compliance add"

### Acceptance Criteria

- [ ] PES runs silent integrity check on session startup
- [ ] Orphaned files (draft without matrix entry) are detected and warned
- [ ] Clean state produces no output from PES
- [ ] Wave ordering is enforced: Wave 1 requires Go decision
- [ ] Compliance matrix existence is required before drafting a section
- [ ] PES enforcement rules are configurable in pes-config.json
- [ ] PES is extensible: new invariants can be added via configuration without engine changes

### Technical Notes

- PES operates at the command layer, not the agent layer -- enforcement happens before agent execution
- pes-config.json defines enforcement rules, audit log settings, and override policy
- PES escape hatch: `<!-- PES-ENFORCEMENT: exempt -->` with required reason when waiver_requires_reason is true
- Audit log records all enforcement actions and waivers
- Phase C1 invariants: session startup, wave ordering (0 before 1), compliance matrix gate
- Designed for extensibility: Phase C2 adds PDC gates, deadline blocking, corpus integrity
- Depends on: proposal-state.json schema (US-007)

---

## US-007: Proposal State Schema and Persistence

### Problem

Phil Santos is an engineer who works on a proposal across multiple sessions over weeks. He finds it unacceptable to lose work when a session ends or to have inconsistent state between plugin features. Every command reads or writes proposal state, and there is no tolerance for corruption or data loss. Today, proposal state is in his head and in scattered files.

### Who

- Engineer | Working across multiple sessions | Needs reliable state that survives restarts without corruption

### Solution

A structured proposal-state.json schema that serves as the single source of truth for all proposal metadata, wave progress, and artifact statuses. All plugin commands read and write through this schema. State is saved after every meaningful action.

### Domain Examples

#### 1: Happy Path -- State persists across sessions

Phil runs `/proposal new` and completes Go/No-Go. He closes Claude Code. The next day, he runs `/proposal status` and sees the exact state he left: Wave 0 completed, Wave 1 active, Go approved, 17 days to deadline.

#### 2: Edge Case -- State file does not exist

Phil runs `/proposal status` in a directory with no proposal-state.json. The tool reports "No active proposal found. Start one with /proposal new." No crash, no stack trace.

#### 3: Error Path -- State file is corrupted

Phil's proposal-state.json was partially written due to a crash. On next session startup, PES detects the corruption: "proposal-state.json appears corrupted. Attempting recovery from last good backup." If backup exists, state is restored. If not, the tool reports what was lost and guides recovery.

### UAT Scenarios (BDD)

#### Scenario: State persists across sessions

Given Phil completed Go/No-Go for AF243-001 and closed Claude Code
When Phil opens a new session and runs "/proposal status"
Then the tool reads proposal-state.json
And displays the exact state from the previous session

#### Scenario: State file does not exist

Given no proposal-state.json exists in the current directory
When Phil runs "/proposal status"
Then the tool displays "No active proposal found"
And suggests "/proposal new"

#### Scenario: State saved after every meaningful action

Given Phil has an active proposal
When Phil completes a Go/No-Go decision
Then proposal-state.json is updated with go_no_go value
And the updated file is written to disk immediately

#### Scenario: Corrupted state file detected and recovered

Given proposal-state.json was partially written due to a crash
When Phil starts a new session
Then PES detects the corruption
And attempts recovery from backup
And reports what was recovered or lost

### Acceptance Criteria

- [ ] proposal-state.json is created by `/proposal new` with complete schema
- [ ] State is read by all commands; written after every meaningful action
- [ ] State survives Claude Code session restarts
- [ ] Missing state file produces helpful message, not crash
- [ ] Corrupted state file is detected by PES with recovery attempt
- [ ] Schema includes: topic metadata, wave statuses, go_no_go, tpoc status, compliance matrix reference, deadline

### Technical Notes

- JSON schema with versioning (schema_version field for future migrations)
- Atomic writes: write to temp file then rename, to prevent partial writes
- Backup: keep one prior version (proposal-state.json.bak)
- All plugin commands depend on this schema -- it is the first component built
- Depends on: nothing (foundation for all other stories)

---

## US-008: Simplified Compliance Check Command

### Problem

Phil Santos is an engineer who wants to know at any point during the proposal process whether his compliance coverage is on track. He finds it frustrating to open the compliance matrix file, count statuses manually, and figure out what is missing. Today he does this by scanning the spreadsheet and hoping he catches everything.

### Who

- Engineer | Mid-proposal, any wave | Wants a quick compliance health check without opening files

### Solution

A `/proposal:check` command (Phase C1 simplified version) that reads the compliance matrix and reports coverage: how many items are covered, partial, missing, or waived. In Phase C2, this command expands to include PDC evaluation, but in C1 it validates compliance matrix coverage only.

### Domain Examples

#### 1: Happy Path -- Phil checks compliance mid-Wave 1

Phil runs `/proposal:check` after generating the compliance matrix for AF243-001. The tool reports: "47 items | 0 covered | 0 partial | 47 not started | 0 waived." This is expected -- he just generated it and has not started drafting.

#### 2: Happy Path -- Phil checks compliance after some drafting

Phil has been working through Wave 4 (in Phase C2, but the check command works the same). He runs `/proposal:check` and sees: "47 items | 32 covered | 5 partial | 8 missing | 2 waived (with reasons)." He knows exactly what remains.

#### 3: Edge Case -- No compliance matrix exists yet

Phil runs `/proposal:check` before generating the matrix. The tool reports: "No compliance matrix found. Generate one with /proposal wave strategy."

### UAT Scenarios (BDD)

#### Scenario: Compliance check reports matrix coverage

Given a compliance matrix exists with 47 items for AF243-001
And 32 items are covered, 5 partial, 8 missing, 2 waived
When Phil runs "/proposal:check"
Then the tool displays "47 items | 32 covered | 5 partial | 8 missing | 2 waived"

#### Scenario: Compliance check on fresh matrix

Given a compliance matrix was just generated with 47 items all at status "--"
When Phil runs "/proposal:check"
Then the tool displays "47 items | 0 covered | 0 partial | 47 not started | 0 waived"

#### Scenario: Compliance check with no matrix

Given no compliance matrix exists
When Phil runs "/proposal:check"
Then the tool displays "No compliance matrix found"
And suggests "/proposal wave strategy" to generate one

### Acceptance Criteria

- [ ] Reads compliance matrix and reports coverage by status category
- [ ] Shows count of waived items (waived with reason is distinct from missing)
- [ ] Handles missing matrix gracefully with guidance
- [ ] Extensible: Phase C2 adds PDC Tier 1/2 evaluation to this same command

### Technical Notes

- Reads compliance-matrix.md; parses status field per item
- Phase C1: compliance matrix only. Phase C2: adds PDC check (Tier 1 mechanical, Tier 2 rubric)
- Same command (`/proposal:check`), expanded behavior per phase
- Depends on: compliance matrix (US-004)

---

## US-009: Strategy Brief and Wave 1 Checkpoint

### Problem

Phil Santos is an engineer who needs to align his proposal strategy before investing hours in research and drafting. He finds it risky to start writing without a clear, documented strategy because past proposals have suffered from mid-course corrections when the approach, TRL positioning, or teaming plan was not nailed down early. Today, his strategy exists as mental notes and scattered comments in draft files.

### Who

- Engineer | Completing Wave 1 | Needs a documented strategy that all downstream work builds on

### Solution

A strategy brief generated from solicitation parsing, compliance matrix, corpus matches, and TPOC insights (if available). The brief captures key strategic decisions: technical approach direction, TRL entry/target, teaming plan, Phase III pathway, and key risks. Presented at a human checkpoint as the Wave 1 exit gate.

### Domain Examples

#### 1: Happy Path -- Phil reviews and approves strategy brief

Phil has completed compliance matrix generation and TPOC answer ingestion for AF243-001. The tool synthesizes a strategy brief: solid-state laser approach, TRL 3 to 5, solo (no STTR RI), Phase III target PMS 501 (from TPOC), $250K standard budget, key risk is unproven transition pathway. Phil reviews, approves, and Wave 2 unlocks.

#### 2: Edge Case -- Phil approves strategy without TPOC answers

Phil generated TPOC questions for N244-012 but the call never happened. The strategy brief is generated from solicitation and corpus data alone, without TPOC insights. The brief notes "TPOC insights: not available" and Phil approves with that caveat.

#### 3: Edge Case -- Phil revises strategy after review

Phil reviews the strategy brief for AF243-001 and provides feedback: "Change technical approach from solid-state laser to fiber laser based on our AF241-087 experience." The tool regenerates the brief with the revised approach. Phil reviews again and approves.

### UAT Scenarios (BDD)

#### Scenario: Strategy brief generated from full Wave 1 context

Given compliance matrix exists for AF243-001
And TPOC answers have been ingested
And corpus has relevant past proposals
When the strategy brief is generated
Then it includes technical approach, TRL entry/target, teaming plan, Phase III pathway, budget, and key risks
And it references TPOC insights where applicable
And it is written to "./artifacts/wave-1-strategy/strategy-brief.md"

#### Scenario: Strategy brief generated without TPOC answers

Given compliance matrix exists for N244-012
And TPOC questions are in "pending" state
When the strategy brief is generated
Then it is generated from solicitation and corpus data alone
And it notes "TPOC insights: not available"

#### Scenario: Strategy checkpoint -- approve unlocks Wave 2

Given a strategy brief exists for AF243-001
When Phil selects "(a) approve" at the strategy alignment checkpoint
Then the approval is recorded in proposal-state.json
And Wave 2 is unlocked

#### Scenario: Strategy checkpoint -- revise with feedback

Given a strategy brief exists for AF243-001
When Phil selects "(r) revise" and provides feedback
Then the tool regenerates the strategy brief incorporating feedback
And presents the revised brief for another review round

### Acceptance Criteria

- [ ] Strategy brief synthesizes solicitation, compliance matrix, corpus, and TPOC data
- [ ] Brief covers: technical approach, TRL, teaming, Phase III, budget, risks
- [ ] Brief is generated even without TPOC answers (notes their absence)
- [ ] Strategy alignment is a human checkpoint with approve/revise/skip options
- [ ] Approval unlocks Wave 2 (PES-enforced gate)
- [ ] Revision cycles regenerate the brief with user feedback incorporated

### Technical Notes

- Strategy brief is the "proposal ADR" -- documents why strategic decisions were made
- References compliance matrix items and TPOC Q&A log entries
- Written once, referenced by Waves 2-4 but not mutated after approval
- PES gate: Wave 2 requires strategy brief approval
- Depends on: US-004 (compliance matrix), US-005 (TPOC), US-007 (state)

---

## Story Dependency Map

```
US-007 (State Schema)
  |
  +-- US-001 (Status/Reorientation) -- reads state
  |
  +-- US-002 (New Proposal) -- creates state
  |     |
  |     +-- US-003 (Corpus Ingestion) -- feeds search in US-002
  |
  +-- US-004 (Compliance Matrix) -- reads/writes state
  |     |
  |     +-- US-005 (TPOC Questions) -- reads matrix ambiguities
  |     |
  |     +-- US-008 (Compliance Check) -- reads matrix
  |     |
  |     +-- US-009 (Strategy Brief) -- reads matrix, TPOC, corpus
  |
  +-- US-006 (PES Foundation) -- reads/validates state
```

Build order recommendation:
1. US-007 (State Schema) -- everything depends on this
2. US-003 (Corpus Ingestion) -- needed by US-002
3. US-002 (New Proposal) -- first user-facing command
4. US-001 (Status/Reorientation) -- second most important command
5. US-004 (Compliance Matrix) -- core Wave 1 capability
6. US-005 (TPOC Questions) -- depends on matrix
7. US-009 (Strategy Brief) -- Wave 1 exit gate
8. US-006 (PES Foundation) -- enforcement layer
9. US-008 (Compliance Check) -- depends on matrix

---

## Story Sizing Summary

| Story | Scenarios | Est. Days | Right-Sized? |
|-------|-----------|-----------|-------------|
| US-001 | 4 | 1-2 | Yes |
| US-002 | 6 | 2-3 | Yes |
| US-003 | 5 | 1-2 | Yes |
| US-004 | 4 | 2-3 | Yes |
| US-005 | 4 | 2-3 | Yes |
| US-006 | 5 | 2-3 | Yes |
| US-007 | 4 | 1-2 | Yes |
| US-008 | 3 | 1 | Yes |
| US-009 | 4 | 2-3 | Yes |

Total: 39 scenarios, 14-22 days estimated effort.

---

## Non-Functional Requirements

### NFR-001: Command Response Time

All commands that read local state (e.g., `/proposal status`, `/proposal compliance check`) respond within 1 second. Commands that trigger parsing, search, or LLM calls display a progress indicator within 100ms.

### NFR-002: Data Safety

proposal-state.json is written atomically (write to temp then rename). One backup copy retained (proposal-state.json.bak). No user data leaves the local machine.

### NFR-003: CLI Accessibility

All output follows NO_COLOR convention when NO_COLOR env var is set. Color is never the only way to convey information. Error messages follow what/why/what-to-do pattern.

---

## Phase C2 Planning Notes

The following items are explicitly deferred to Phase C2 and are NOT in scope for the DESIGN wave handoff:

- Guardrailed AI drafting with confidence flagging (J3)
- Discrimination table building (J5)
- Market research and commercializability argument (J8)
- PDC generation, Tier 2/3 evaluation, and drafting iteration loop
- PES invariants beyond Phase C1 scope (PDC gates, deadline blocking, corpus integrity)
- Second user onboarding (the 8 other writers)
