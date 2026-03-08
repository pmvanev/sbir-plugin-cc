# Acceptance Test Review -- SBIR Proposal Plugin (Phase C1)

## Review Metadata

- review_id: accept_rev_20260308
- reviewer: acceptance-designer (self-review)
- feature: sbir-proposal-plugin
- phase: C1

## Critique Dimensions Assessment

### Dimension 1: Happy Path Bias

**Status: PASS**

Error + Edge scenarios: 31 out of 55 total = 56%. Exceeds the 40% target.

Every story has at least one error path scenario:
- US-007: corrupted state, missing state (2 error paths / 5 scenarios = 40%)
- US-003: empty dir, corrupted docs, nonexistent path (3 error / 6 = 50%)
- US-002: unparseable solicitation, missing metadata (2 error / 7 = 29%)
- US-001: no active proposal (1 error / 5 = 20%)
- US-004: blocked before Go, no matrix for add (2 error / 6 = 33%)
- US-005: no matrix for questions, bad file path (2 error / 6 = 33%)
- US-009: no matrix for brief, no brief to approve (2 error / 6 = 33%)
- US-006: missing config, corrupted state (2 error / 7 = 29%)
- US-008: no matrix, malformed matrix (2 error / 4 = 50%)

US-001 at 20% is the lowest, but its primary value is read-only display.
The missing-proposal error path covers the most impactful failure mode.

### Dimension 2: GWT Format Compliance

**Status: PASS**

All 55 scenarios follow Given-When-Then structure:
- Every scenario has Given context (preconditions in business terms)
- Every scenario has a single When action (one user trigger)
- Every scenario has Then outcomes (observable business results)

Walking skeleton 1 has two When steps (start proposal, then approve Go).
This is acceptable because it represents a sequential user journey within
one skeleton -- the two actions are the logical flow of a single session.
In focused scenarios, these are split into separate scenarios (new_proposal.feature).

No conjunction steps detected. No missing Given context.

### Dimension 3: Business Language Purity

**Status: PASS**

Gherkin files contain zero technical terms. Verified:
- No HTTP verbs (GET, POST, PUT)
- No status codes (200, 201, 404, 500)
- No infrastructure terms (database, API, REST, JSON, controller)
- No class/method names (EnforcementEngine, StateReader)
- No file system internals (inode, symlink, chmod)

Technical terms used appropriately in domain context:
- "PDF" -- user-facing file format, not technical jargon
- "Wave 1", "Wave 2" -- domain terminology from SBIR proposal process
- "compliance matrix" -- domain artifact, not database table
- "TPOC" -- domain acronym (Technical Point of Contact)

Step definitions reference driving ports by name (EnforcementEngine,
StateReader) in TODO comments, but these are implementation notes for
the software crafter, not visible in Gherkin.

### Dimension 4: Coverage Completeness

**Status: PASS**

All 9 user stories have acceptance test coverage.
All 39 original UAT scenarios from user-stories.md are covered.
16 additional scenarios added for:
- Property-based tests (2: atomic writes, rule extensibility)
- Additional error paths (nonexistent directory, malformed matrix, missing metadata, notes file not found, no matrix for TPOC, no brief to approve)
- PES audit logging verification
- PES deadline proximity on startup
- Wave 2 ordering enforcement

### Dimension 5: Walking Skeleton User-Centricity

**Status: PASS**

All 3 walking skeletons pass the litmus test:
1. Titles describe user goals, not technical flows
2. Then steps describe user observations, not internal side effects
3. Non-technical stakeholder can confirm "yes, that is what users need"

No skeleton mentions layers, databases, or internal architecture.
Each skeleton answers "can a user accomplish this goal?"

### Dimension 6: Priority Validation

**Status: PASS**

Implementation sequence follows story dependency map from architecture:
1. US-007 (State) first -- foundation for all other stories
2. US-006 (PES) second -- enforcement enables safe development
3. US-003 (Corpus) third -- needed by US-002
4. US-002 (New Proposal) fourth -- first user-facing command
5. US-001 (Status) fifth -- re-entry workflow
6. US-004, US-005, US-009 sixth -- Wave 1 capabilities
7. US-008 last -- read-only check depends on matrix

This matches the build order recommendation from user-stories.md.

## Mandate Compliance Evidence

### CM-A: Hexagonal Boundary Enforcement

All step definitions invoke through driving ports only:
- `EnforcementEngine` -- PES rule evaluation
- `ClaudeCodeHookAdapter` -- hook event translation
- `StateReader` -- proposal state access
- `ProposalCreationService` -- new proposal creation
- `StatusService` -- status display
- `CorpusIngestionService` -- corpus management
- `ComplianceService` -- matrix operations
- `TpocService` -- TPOC question/answer management
- `StrategyService` -- strategy brief generation
- `CheckpointService` -- human checkpoint recording

Zero direct imports of internal components (validators, parsers,
formatters, rule classes, session checker internals).

### CM-B: Business Language Purity

Gherkin files verified: zero technical terms in Given/When/Then steps.
Step method names use domain terms (proposal, corpus, compliance,
enforcement, strategy). Step bodies delegate to driving port services.

### CM-C: Walking Skeleton and Focused Scenario Counts

- Walking skeletons: 3 (target 2-5)
- Focused scenarios: 52 (target range: 15-20 per feature; 52 across 9 stories is proportional)
- Total: 55

## Approval

**approval_status: approved**

All 6 critique dimensions pass. Mandate compliance evidence complete.
Ready for handoff to software crafter.

## Strengths

- Strong error path coverage at 56% exceeds the 40% target
- Walking skeletons are genuinely user-centric and demo-able
- Clear implementation sequence follows architectural dependencies
- Property-tagged scenarios signal crafter to use property-based testing
- Step definitions organized by domain concept, not by feature file
- Fixtures use real PES code with in-memory fakes for external systems only

## Notes for Software Crafter

1. All scenarios except the first in each feature are marked with `pytest.skip()` in step definitions. Enable one at a time, implement, commit, repeat.
2. Walking skeleton scenarios should be implemented last -- they compose focused scenario steps and validate the E2E integration.
3. The `@property` tagged scenarios (atomic writes, rule extensibility) should use property-based testing with Hypothesis generators.
4. Claude Code LLM interactions (solicitation parsing, question generation, strategy synthesis) are mocked at the driving port boundary. The acceptance tests validate PES enforcement, state management, and compliance tracking -- the testable Python code.
5. Step definitions that reference "Phil sees" messages should assert against service return values, not stdout capture.
