# Solution Testing -- SBIR Proposal Writing Plugin

## Solution Architecture: Option C (Phased Delivery)

### Phase C1 -- MVP: Corpus Search + Compliance Tracking

**Agents:** orchestrator, corpus-librarian, compliance-sheriff, topic-scout, fit-scorer
**Waves:** 0 (Intelligence & Fit), 1 (Requirements & Strategy)
**Enforcement:** PES ships from day one

### Phase C2 -- Guardrailed Drafting

**Agents:** + writer, reviewer, strategist, tpoc-analyst, researcher
**Waves:** + 2 (Research), 3 (Discrimination & Outline), 4 (Drafting)
**Key feature:** Confidence flagging, claim verification, human checkpoints per section

### Phase C3 -- Full Lifecycle

**Agents:** + formatter, submission-agent, debrief-analyst
**Waves:** + 5-9 (Visual Assets through Post-Submission)

## Hypotheses

### H1 -- Corpus Search Value (Phase C1)

**We believe** building a semantic search corpus from past proposals, debriefs, and TPOC logs **for** SBIR proposal writers **will achieve** measurable reduction in document search time.

**TRUE when:** 4+ of 5 test users complete a "find relevant past performance for this topic" task in under 2 minutes vs. current method.

**FALSE when:** Search results are not relevant enough to use, or ingestion time exceeds time saved.

**Test method:** Build prototype corpus from 3-5 past proposals; run retrieval tasks with 5 internal writers.
**Effort:** 1-2 weeks
**Priority:** Immediate

### H2 -- Compliance Matrix Value (Phase C1)

**We believe** automated compliance matrix generation from solicitation parsing **for** SBIR proposal writers **will achieve** fewer missed requirements and reduced manual tracking.

**TRUE when:** Tool extracts 90%+ of "shall" statements that human review finds, and users say it catches items they would have missed.

**FALSE when:** Extraction accuracy below 80%, or users spend more time correcting the matrix than building it manually.

**Test method:** Parse 3 real solicitations; compare extraction to manual review.
**Effort:** 1 week
**Priority:** Immediate

### H3 -- Standalone Adoption (Phase C1)

**We believe** corpus search + compliance tracking alone (without AI drafting) **for** SBIR proposal writers **will achieve** sufficient value to justify tool adoption.

**TRUE when:** 3+ of 5 test users say they would use the tool on their next proposal based on these features alone.

**FALSE when:** Users say "nice but I need it to write sections" before they would adopt.

**Test method:** After H1+H2 testing, ask commitment question.
**Effort:** 0 (part of H1/H2 testing)
**Priority:** Immediate -- this determines whether Option C phasing works

### H4 -- Guardrailed Drafting (Phase C2)

**We believe** AI drafting with PES enforcement (confidence flagging, claim verification, human checkpoint per section) **for** SBIR proposal writers **will achieve** trusted first drafts that reduce revision cycles.

**TRUE when:** 4+ of 5 test users say draft quality is "good enough to edit" rather than "easier to rewrite."

**FALSE when:** Users still describe output as "hallucinatory" or "garbage" despite guardrails.

**Test method:** Prototype one section draft with confidence flags; test with 5 writers.
**Effort:** 2-3 weeks
**Priority:** After H1-H3 validated

### H5 -- Wave-Based Autonomous Iteration (Phase C2)

**We believe** structured multi-agent iteration (writer + reviewer + compliance check) with PES guardrails and human checkpoints between waves **for** SBIR proposal writers **will achieve** quality improvement without mid-wave micromanagement.

**TRUE when:** Users approve wave outputs without intervening mid-wave more than once per section.

**FALSE when:** Users intervene at every agent step, defeating multi-agent architecture.

**Test method:** End-to-end prototype of Wave 3 (discrimination + outline) with PES checks.
**Effort:** 3-4 weeks
**Priority:** After H4 validated

## Competitive Landscape

### Positioning Map

```
                    SBIR-Specific
                         |
    Procura              |         THIS PLUGIN
    (analyze +           |         (full lifecycle +
     formulate)          |          corpus + CLI)
                         |
  General ---------------+--------------- Deep
  Purpose                |               Workflow
                         |
    ChatGPT/Claude       |         Proposal Firms
    (raw AI)             |         ($5-10K human)
                         |
                    Broad Federal
```

### Competitor Analysis

| Competitor | What They Solve | What They Miss |
|---|---|---|
| **Procura Federal** | AI contract analysis, opportunity evaluation, requirement extraction | SaaS (not tailor-made); broadly federal (not SBIR-specific); no institutional memory; no enforcement layer |
| **Proposal writing firms** ($5-10K) | Full proposal production | No institutional learning; same win rate as internal; expensive per proposal |
| **ChatGPT/Claude (raw)** | Boilerplate, first drafts | "Hallucinatory promises"; no compliance tracking; no corpus; no structure |
| **GovCon platforms** (GovWin, BGOV) | Market intelligence, pipeline | Not proposal writing; enterprise pricing |
| **Shipley/Lohfeld** (methodology) | Process discipline | Methodology not tooling; no AI; no automation |
| **Internal AI scrubbing tool** (user-built) | Topic scanning and ranking | Topic discovery only; does not address proposal writing |

### Defensible Differentiation

1. **Compounding corpus** -- institutional memory that improves with every proposal cycle
2. **PES enforcement** -- structural guarantees, not just instructions to agents
3. **CLI-native for engineers** -- lives in the engineering environment, tailor-made by design
4. **SBIR-specific depth** -- not a general federal contracting tool
5. **Open architecture** -- users see prompts, can modify agents, control their data locally

## Assumption Tracker (Final State)

| # | Assumption | Final Score | Status |
|---|---|---|---|
| A1 | Users would adopt CLI AI tool | 8 | Partially validated -- engineers who code |
| A2 | Target user comfortable with CLI | 10 | Needs direct testing |
| A3 | LLM draft quality reduces effort | 14 | High risk -- deferred to Phase C2 with guardrails |
| A4 | Corpus/compounding knowledge differentiates | 11 | Promising but unvalidated at scale |
| A5 | 10 waves / structured workflow fits | 9 | Validated -- users want structure with checkpoints |
| A6 | TPOC question generation is valuable | 11 | Logically sound; test in Phase C2 |
| A7 | Users invest in corpus ingestion | 8 | Partially validated -- built internal tool |
| A8 | Compliance automation beats existing tools | 10 | Test in H2 |
| A9 | PES enforcement adds value not friction | 7 | Test later |
| A10 | Visual asset generation via CLI viable | 7 | Phase C3 |
| A11 | Submission packaging automatable | 6 | Phase C3 |
| A12 | Win/loss analysis actionable with small corpus | 5 | Phase C3 |
| A13 | Autonomous agent iteration viable | 11 | Reframed: viable WITH guardrails. Test in H5 |
| A14 | Formatting solvable in LLM tool | 12 | Feasibility spike needed; may require template approach |
| A15 | O1 + O2 deliver standalone value | 12 | Critical -- test in H3 |
| A16 | PES feasible in Claude Code plugin | 10 | DES precedent; needs feasibility spike |

## Gate G3 Evaluation

| Criterion | Target | Result |
|---|---|---|
| Hypotheses defined | Yes | PASS (5 hypotheses with clear TRUE/FALSE criteria) |
| Test plan actionable | Yes | PASS (methods, effort, priority defined) |
| Value perception | >70% | PARTIAL (strong signals but no prototype test yet) |
| Users tested with prototype | 5+ | PENDING (builder is user; can self-test H1-H3) |

**Gate G3: CONDITIONAL PASS**

Conditions: H1-H3 must be tested during early Phase C1 development. Builder is the target user, enabling dogfooding as validation.
