# SBIR/STTR Proposal Writing Plugin
## Architecture, Agents, Skills & Process Waves

> Inspired by nWave AI's agent orchestration framework for Claude Code.
> A specialized multi-agent system for the full SBIR/STTR proposal lifecycle.

> **Document Status:** This document is the **DISCUSS-phase artifact** for the plugin's own development using nWave. It was produced through an informal DISCOVER/DISCUSS process and serves as the requirements input to `/nw:design`. See *Building This Plugin* at the end of this document for the full nWave build plan.

---

## Overview

This plugin implements a structured, agentic proposal writing workflow as a **pure Claude Code plugin with pure Claude Code CLI interaction**. There is no separate web UI, no external dashboard, and no additional application layer. All interaction — including human review checkpoints, iteration feedback, go/no-go decisions, and configuration — happens through the Claude Code CLI.

Each **Wave** represents a major phase of the proposal lifecycle. Within each wave, one or more **Agents** execute tasks using defined **Skills**. The **Orchestrator** manages state, handoffs, deadlines, and human review checkpoints throughout.

---

## Interaction Model

**Runtime environment:** Claude Code CLI only
**Plugin entry point:** A Claude Code slash command, e.g. `/proposal`
**Human interaction:** All checkpoints, feedback, and decisions are surfaced as Claude Code CLI prompts — the agent pauses, presents output, asks for input or approval, and resumes
**State persistence:** Proposal state is written to and read from local JSON files on disk between sessions, so work survives Claude Code restarts
**No external UI:** All output — drafts, tables, outlines, review scorecards — is rendered in the CLI or written to local files that the user opens in their editor of choice

### Slash Command Interface

```bash
/proposal new                          # Start a new proposal project
/proposal status                       # Show current wave, open items, deadline
/proposal wave [wave-name]             # Jump to or resume a specific wave
/proposal review                       # Trigger human review checkpoint
/proposal corpus add [path]            # Ingest a document into the corpus
/proposal corpus list                  # List corpus contents
/proposal tpoc questions               # Generate TPOC question list
/proposal tpoc ingest                  # Ingest TPOC call Q&A answers
/proposal compliance check             # Run compliance matrix check
/proposal draft [section]             # Draft or re-draft a specific section
/proposal iterate [section]           # Open iteration loop on a section
/proposal format                       # Run formatting and assembly wave
/proposal submit prep                  # Run submission packaging wave
/proposal debrief ingest [path]        # Ingest debrief feedback document
```

### Human Checkpoint Pattern

When the orchestrator reaches a human checkpoint, it follows this pattern in the CLI:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CHECKPOINT: Discrimination Table Review
Wave 3 — Discrimination & Outline
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Discrimination table rendered to CLI or written to ./drafts/discrimination-table.md]

Review complete? Options:
  (a) approve — proceed to outline drafting
  (r) revise  — provide feedback and regenerate
  (s) skip    — mark as deferred and continue
  (q) quit    — save state and exit

> 
```

Feedback for revision is entered as free-form text at the CLI prompt. The agent ingests it, revises, and re-presents for another round.

### Session Continuity

State is persisted to `./proposal-state.json` after every agent action. On restart, `/proposal status` reads state and resumes from the last completed step. No work is lost between sessions.

---

## System Architecture

```
/sbir-proposal-plugin
  /agents
    orchestrator.md
    topic-scout.md
    fit-scorer.md
    compliance-sheriff.md
    tpoc-analyst.md
    researcher.md
    strategist.md
    corpus-librarian.md
    writer.md
    reviewer.md
    formatter.md
    submission-agent.md
    debrief-analyst.md
  /skills
    tpoc-question-generator.md
    compliance-matrix-builder.md
    discrimination-table.md
    win-loss-analyzer.md
    proposal-archive-reader.md
    trl-assessor.md
    market-researcher.md
    visual-asset-generator.md
    budget-scaffolder.md
    reviewer-persona-simulator.md
  /state
    proposal-project.json       # live proposal state object
    company-profile.json        # capabilities, past performance, certs
    corpus/                     # ingested past proposals and debriefs
  /templates
    section-templates/
    sow-template.md
    compliance-matrix-template.md
    discrimination-table-template.md
```

---

## Proposal State Object

The orchestrator maintains a structured project file throughout the lifecycle:

```json
{
  "proposal_id": "string",
  "topic": { "id", "agency", "title", "solicitation_url", "deadline" },
  "phase": "I | II | Direct-to-II",
  "current_wave": "string",
  "go_no_go": "pending | go | no-go",
  "volumes": {
    "technical": { "status", "current_draft", "review_comments", "iterations" },
    "management": { "status", "current_draft", "review_comments", "iterations" },
    "cost": { "status", "current_draft", "review_comments", "iterations" }
  },
  "compliance_matrix": [],
  "discrimination_table": [],
  "tpoc_insights": [],
  "research_summary": {},
  "open_review_items": [],
  "deadline_buffer_alerts": [],
  "submitted_package": {}
}
```

---

## Waves (Process Phases)

### Wave 0 — Intelligence & Fit

**Goal:** Identify relevant open topics and make a data-driven go/no-go decision before investing proposal effort.

**Agents:** `topic-scout`, `fit-scorer`, `corpus-librarian`

**Steps:**
1. Scrape and ingest open solicitations from SBIR.gov, Grants.gov, NSPIRES, agency portals
2. Parse topic descriptions, agency, phase, deadline, and evaluation criteria
3. Score each topic against company capability profile:
   - Subject matter expertise match
   - Past performance relevance
   - SAM.gov registration and socioeconomic certifications
   - Phase I/II eligibility (prior award exclusions)
   - STTR research institution requirements
4. Pull relevant past proposals from corpus for exemplar context
5. Surface top-fit topics with rationale for human review
6. **Human checkpoint:** Select topic(s) to pursue → Go/No-Go decision

**Skills:** `proposal-archive-reader`, `win-loss-analyzer`

**Outputs:**
- Ranked topic shortlist with fit scores and rationale
- Initial exemplar proposals pulled from corpus
- Go/No-Go recommendation per topic

---

### Wave 1 — Requirements & Strategy

**Goal:** Deeply understand what is required and build the strategic foundation before any writing begins.

**Agents:** `compliance-sheriff`, `tpoc-analyst`, `strategist`, `corpus-librarian`

**Steps:**
1. Parse solicitation for all explicit requirements:
   - Page limits, font, margins, file format
   - Required sections and their order
   - Evaluation criteria and weighting language
   - Certifications and attachments required
2. Generate compliance matrix — map every "shall" to a proposal section
3. Flag ambiguities, gaps, and opportunities in the solicitation text
4. Generate prioritized TPOC question list (see Skill below)
5. Conduct TPOC interview with prepared questions
6. Ingest TPOC Q&A — capture structured answers, flag deltas vs. solicitation
7. Augment compliance matrix with informal TPOC requirements
8. Assess teaming needs (subcontractors, research institution for STTR)
9. Audit SAM.gov registration, certifications, and size status
10. Check Phase III transition pathway — program of record or commercial
11. Scaffold rough budget model — labor categories, indirect rates, materials
12. **Human checkpoint:** Strategy alignment review before research begins

**Skills:** `compliance-matrix-builder`, `tpoc-question-generator`, `budget-scaffolder`, `trl-assessor`

**Outputs:**
- Compliance matrix (living document, updated throughout)
- TPOC Q&A structured log
- Solicitation delta analysis (TPOC vs. written)
- Teaming plan
- Budget scaffold
- Strategic brief: TRL positioning, Phase III pathway, key discriminators

---

### Wave 2 — Research

**Goal:** Build the technical and market intelligence foundation that will underpin the proposal narrative.

**Agents:** `researcher`, `strategist`

**Steps:**
1. **Technical research:**
   - Current state of the art and prior art landscape
   - Patent scan — freedom to operate and novelty framing
   - TRL assessment — current vs. target, justification
   - Competing approaches and their limitations
   - Search USASpending.gov and SBIR.gov for prior awards on similar topics
2. **Market research:**
   - TAM / SAM / SOM sizing
   - Commercialization pathway — DoD transition and/or commercial market
   - Competitor landscape
   - Customer discovery beyond the TPOC
   - Regulatory or certification landscape
3. Synthesize findings into research summary document
4. **Human checkpoint:** Research review — validate technical approach direction and market framing

**Skills:** `market-researcher`, `trl-assessor`

**Outputs:**
- Technical landscape summary
- Patent landscape notes
- Prior award analysis
- Market research summary with TAM/SAM/SOM
- Commercialization pathway narrative draft
- Refined TRL positioning

---

### Wave 3 — Discrimination & Outline

**Goal:** Establish the core "why us / why this approach" argument and build the structural skeleton of the proposal before writing begins.

**Agents:** `writer`, `reviewer`, `corpus-librarian`

**Steps:**
1. Draft discrimination table:
   - Company discriminators vs. likely competitors
   - Technical approach discriminators vs. prior art
   - Team discriminators (key personnel, facilities, past performance)
   - Feed in TPOC insights to sharpen framing
2. **Iteration loop:** Human review → revise discrimination table
3. Draft proposal outline:
   - Map sections to compliance matrix requirements
   - Assign page budgets per section
   - Define figure and table placeholders
   - Draft section-level thesis statements
4. **Iteration loop:** Human review → revise outline
5. Pull exemplar section structures from corpus for reference
6. Assign color team roles if applicable (Pink, Red, Gold)

**Skills:** `discrimination-table`, `proposal-archive-reader`, `reviewer-persona-simulator`

**Outputs:**
- Finalized discrimination table
- Approved proposal outline with page budgets
- Section thesis statements
- Figure/table placeholder list

---

### Wave 4 — Drafting

**Goal:** Produce full draft content for all proposal volumes, section by section, with structured review loops.

**Agents:** `writer`, `reviewer`, `corpus-librarian`

**Steps:**
1. Draft each section following approved outline and thesis statements:
   - Technical approach (core narrative)
   - Statement of Work (SOW) — milestone-based, contractual language
   - Key personnel bios and CVs (tailored to topic)
   - Facilities and equipment
   - Past performance write-ups
   - Management plan
   - Commercialization plan
   - Risk identification and mitigation table
   - References
2. For each section:
   - Writer agent produces draft
   - Pull relevant exemplars from corpus for tone/structure reference
   - **Iteration loop:** Human review → revise → re-review
3. Check each section against compliance matrix as drafted
4. Run reviewer persona simulation against stated evaluation criteria
5. Check against known debrief weaknesses from corpus
6. Jargon and acronym audit — all terms defined on first use
7. Reading level and clarity analysis
8. Cross-reference check — figures cited exist, page numbers align
9. **Human checkpoint:** Full draft review before formatting begins

**Skills:** `proposal-archive-reader`, `reviewer-persona-simulator`, `discrimination-table`

**Outputs:**
- Full draft of all required sections
- Updated compliance matrix (all items checked)
- Reviewer persona simulation scorecard
- Open review items list

---

### Wave 5 — Visual Assets

**Goal:** Produce figures, diagrams, and images that strengthen the technical narrative and meet formatting requirements.

**Agents:** `formatter`, `writer`

**Steps:**
1. Review figure placeholder list from outline
2. For each figure:
   - Determine appropriate type (system diagram, block diagram, timeline, chart, concept image)
   - Select generation method:
     - SVG generation (local, precise diagrams and schematics)
     - Mermaid / Graphviz (flow and architecture diagrams)
     - External tool integration (e.g., Napkin.ai, similar) for polished concept figures
     - Chart generation from research data
   - Generate draft
   - **Iteration loop:** Human review → revise
3. Ensure all figures have captions and are cross-referenced in text
4. Verify figures meet agency format requirements (resolution, color vs. grayscale, file size)

**Skills:** `visual-asset-generator`

**Outputs:**
- All figures and diagrams in required format
- Figure captions and cross-reference log

---

### Wave 6 — Formatting & Assembly

**Goal:** Produce a submission-ready, compliant document package.

**Agents:** `formatter`, `compliance-sheriff`

**Steps:**
1. Apply document formatting per solicitation requirements:
   - Font, font size, margins, line spacing
   - Headers and footers (proposal title, topic number, company name, page numbers)
   - Section numbering and heading styles
2. Select and apply output medium:
   - Google Docs / Google Drive
   - Microsoft Word (.docx)
   - LaTeX (for technically dense proposals or agency preference)
   - PDF export
3. Format references — consistent citation style, hyperlinks where appropriate
4. Insert finalized figures at correct positions
5. Run final compliance matrix check — every requirement verified
6. Final jargon audit, cross-reference check, page count verification
7. Assemble all volumes into required file structure
8. **Human checkpoint:** Final assembled document review

**Skills:** `compliance-matrix-builder`, `visual-asset-generator`

**Outputs:**
- Fully formatted proposal document(s)
- Assembled submission package per agency file structure requirements
- Final compliance matrix sign-off

---

### Wave 7 — Final Review

**Goal:** Simulate adversarial review and catch any remaining issues before submission.

**Agents:** `reviewer`, `compliance-sheriff`

**Steps:**
1. Full reviewer persona simulation — score proposal as a government technical evaluator would
2. Red team review — identify the strongest objections a skeptical reviewer could raise
3. Check against all known debrief critiques from corpus
4. Final page count and formatting compliance check
5. Verify all attachments, certifications, and required forms are included
6. **Iteration loop:** Address any issues surfaced → re-review
7. **Human checkpoint:** Final human sign-off before submission

**Skills:** `reviewer-persona-simulator`, `compliance-matrix-builder`, `win-loss-analyzer`

**Outputs:**
- Reviewer simulation scorecard with identified weaknesses
- Final open items resolved log
- Human sign-off record

---

### Wave 8 — Submission

**Goal:** Submit the proposal package without errors, on time, with full version archiving.

**Agents:** `submission-agent`

**Steps:**
1. Identify submission portal (DSIP, Grants.gov, NSPIRES, agency-specific)
2. Apply portal-specific packaging rules and upload requirements
3. Verify file naming conventions, size limits, and format requirements
4. Submit package
5. Capture submission confirmation and timestamp
6. Archive immutable snapshot of exactly what was submitted
7. Set deadline tracking and buffer alerts for any required follow-ups

**Outputs:**
- Submission confirmation record
- Archived submission snapshot
- Any required post-submission notifications sent

---

### Wave 9 — Post-Submission & Learning

**Goal:** Close the loop — win or lose — and feed institutional knowledge back into the corpus.

**Agents:** `debrief-analyst`, `corpus-librarian`

**Steps:**
1. Track award notification timeline
2. If **awarded:**
   - Archive winning proposal in corpus with outcome tag
   - Begin Phase II pre-planning scaffold if Phase I
   - Extract winning discriminators and strategies for pattern analysis
3. If **not selected:**
   - Draft debrief request letter
   - Ingest debrief feedback when received:
     - Parse reviewer scores and comments
     - Map each critique to specific proposal section
     - Add to known weakness profile in corpus
   - Identify whether loss was technical, cost, or strategic
4. Update win/loss pattern analysis
5. Update company capability profile with any new past performance
6. Feed lessons learned into fit-scorer and reviewer agent heuristics
7. **Human checkpoint:** Lessons learned review

**Skills:** `win-loss-analyzer`, `proposal-archive-reader`

**Outputs:**
- Updated corpus with outcome-tagged proposal
- Debrief feedback structured log
- Updated known weakness profile
- Lessons learned summary
- Win/loss pattern analysis update

---

## Agent Definitions

| Agent | Role | Primary Waves |
|---|---|---|
| `orchestrator` | Master PM — owns state, handoffs, deadlines, human checkpoints | All |
| `topic-scout` | Scrapes and ingests open solicitations | 0 |
| `fit-scorer` | Scores topics against company profile and corpus | 0 |
| `compliance-sheriff` | Parses requirements, builds and maintains compliance matrix | 1, 6, 7 |
| `tpoc-analyst` | TPOC question generation, interview ingestion, delta analysis | 1 |
| `researcher` | Technical and market deep research | 2 |
| `strategist` | TRL, teaming, budget, Phase III pathway | 1, 2 |
| `corpus-librarian` | Company proposal archive, retrieval, win/loss analysis | 0, 3, 4, 9 |
| `writer` | Section drafting, SOW, outline, discrimination table | 3, 4 |
| `reviewer` | Persona simulation, red team, clarity and compliance audit | 4, 7 |
| `formatter` | Document formatting, visual assets, assembly | 5, 6 |
| `submission-agent` | Portal-specific packaging, submission, archiving | 8 |
| `debrief-analyst` | Post-award feedback ingestion, lessons learned | 9 |

---

## Skill Definitions

| Skill | Description | Used By |
|---|---|---|
| `tpoc-question-generator` | Generates and iterates a prioritized TPOC interview question list from topic, company history, research, and flagged ambiguities | `tpoc-analyst` |
| `compliance-matrix-builder` | Extracts all "shall" statements and maps them to proposal sections; tracks compliance throughout lifecycle | `compliance-sheriff` |
| `discrimination-table` | Drafts and iterates the company/approach discrimination table | `writer`, `reviewer` |
| `proposal-archive-reader` | Ingests and retrieves past proposals from corpus; extracts reusable content and exemplars | `corpus-librarian` |
| `win-loss-analyzer` | Analyzes outcome-tagged proposals and debrief feedback for patterns | `corpus-librarian`, `debrief-analyst` |
| `trl-assessor` | Assesses current and target TRL with justification narrative | `researcher`, `strategist` |
| `market-researcher` | TAM/SAM/SOM sizing, competitor landscape, commercialization pathway | `researcher` |
| `visual-asset-generator` | Generates diagrams, figures, and concept images via SVG, Mermaid, or external tools | `formatter` |
| `budget-scaffolder` | Rough cost modeling by labor category, indirect rates, materials, and phase | `strategist` |
| `reviewer-persona-simulator` | Simulates government technical evaluator scoring against stated criteria; surfaces weak spots | `reviewer` |

---

## TPOC Question Generator — Skill Detail

Because of its strategic importance, this skill warrants additional definition.

**Inputs:**
- Raw solicitation text
- Company capability profile
- Relevant past proposals from corpus
- Technical research summary
- Market research summary
- Flagged ambiguities from compliance sheriff
- Prior debrief feedback on related topics

**Question Categories & Tags:**

| Tag | Purpose |
|---|---|
| `scope-clarification` | Resolve ambiguities in what is / isn't in scope |
| `approach-validation` | Test whether your intended technical direction is welcome |
| `competitive-intelligence` | Understand the landscape without tipping your hand |
| `transition-pathway` | Clarify Phase III realism — program of record, budget line |
| `budget-signal` | Probe flexibility and agency expectations on cost |
| `deliverable-clarification` | Confirm what Phase I/II completion actually looks like |
| `team-validation` | Confirm whether your team structure and partners resonate |
| `incumbent-landscape` | Understand prior attempts and why they fell short |

**Iteration Rounds:**
1. **Generate** — broad unconstrained list from all input sources, tagged by category
2. **Prioritize & Prune** — score by strategic value, remove redundancies, flag questions that may signal weakness or tip competitive hand
3. **Sequence** — order for natural conversational flow; open with relationship-building, build to strategic probes
4. **Human Review** — present list with rationale per question; proposer edits before call
5. **Answer Capture** — structured ingestion post-call; flag follow-ups; run delta analysis
6. **Propagate** — push insights to compliance matrix, discrimination table, fit assessment

**Output:**
- Prioritized question list with rationale and strategic intent tag
- Recommended conversational sequence
- Answer capture template (ready for post-call ingestion)
- Post-call: structured Q&A log + solicitation delta analysis

---

## Corpus Librarian — Institutional Memory

The corpus librarian is the only agent whose knowledge base **compounds with every proposal cycle.** It is the system's long-term memory and IntaptAI's durable competitive advantage.

**Corpus Contents:**
- Past proposals (all phases, all agencies) — tagged by topic area, agency, phase, outcome
- Debrief letters and score sheets — parsed and mapped to sections
- TPOC Q&A logs — indexed by agency and topic area
- Boilerplate library — facilities, key personnel bios, past performance, capability statements
- Win/loss pattern database

**Capabilities:**
- Semantic retrieval of relevant exemplars by topic similarity
- Reusable content extraction — pulls boilerplate candidates for human review
- Voice and style extraction — characterizes successful proposal writing patterns
- Agency preference modeling — learns what resonates with specific agencies and PMs
- Known weakness profile — active checklist built from debrief feedback, checked by reviewer agent on every proposal

---

## Wave → Agent → Command Cross-Reference

The table below maps each wave to the agents responsible for it, the primary slash commands that invoke it, and the human checkpoint that closes it.

| Wave | Name | Primary Agents | Slash Commands | Checkpoint |
|---|---|---|---|---|
| 0 | Intelligence & Fit | `topic-scout`, `fit-scorer`, `corpus-librarian` | `/proposal new`<br>`/proposal wave fit` | Go/No-Go decision |
| 1 | Requirements & Strategy | `compliance-sheriff`, `tpoc-analyst`, `strategist`, `corpus-librarian` | `/proposal wave strategy`<br>`/proposal tpoc questions`<br>`/proposal tpoc ingest`<br>`/proposal compliance check` | Strategy alignment review |
| 2 | Research | `researcher`, `strategist` | `/proposal wave research` | Research direction review |
| 3 | Discrimination & Outline | `writer`, `reviewer`, `corpus-librarian` | `/proposal wave outline`<br>`/proposal iterate discrimination`<br>`/proposal iterate outline` | Discrimination table + outline approval |
| 4 | Drafting | `writer`, `reviewer`, `corpus-librarian` | `/proposal draft [section]`<br>`/proposal iterate [section]`<br>`/proposal review` | Full draft review |
| 5 | Visual Assets | `formatter`, `writer` | `/proposal wave visuals`<br>`/proposal draft figure [name]` | Figure review |
| 6 | Formatting & Assembly | `formatter`, `compliance-sheriff` | `/proposal format`<br>`/proposal compliance check` | Final assembled document review |
| 7 | Final Review | `reviewer`, `compliance-sheriff` | `/proposal review`<br>`/proposal wave final-review` | Final sign-off |
| 8 | Submission | `submission-agent` | `/proposal submit prep`<br>`/proposal submit` | Submission confirmation |
| 9 | Post-Submission & Learning | `debrief-analyst`, `corpus-librarian` | `/proposal debrief ingest [path]`<br>`/proposal corpus add [path]` | Lessons learned review |

### Command → Wave Quick Reference

For the inverse view — which wave a given command belongs to:

| Command | Wave(s) |
|---|---|
| `/proposal new` | 0 — kick off topic discovery and fit scoring |
| `/proposal status` | All — reads current state, shows active wave and open items |
| `/proposal wave [name]` | All — jump to or resume any named wave |
| `/proposal review` | 3, 4, 7 — trigger a human checkpoint in the current wave |
| `/proposal corpus add [path]` | 0, 9 — ingest document into institutional corpus |
| `/proposal corpus list` | 0, 9 — list corpus contents and metadata |
| `/proposal tpoc questions` | 1 — generate prioritized TPOC interview question list |
| `/proposal tpoc ingest` | 1 — ingest TPOC call Q&A and run delta analysis |
| `/proposal compliance check` | 1, 6, 7 — run compliance matrix against current draft state |
| `/proposal draft [section]` | 4 — draft or re-draft a named proposal section |
| `/proposal draft figure [name]` | 5 — generate a specific figure or diagram |
| `/proposal iterate [section]` | 3, 4 — open an iteration loop on a section or artifact |
| `/proposal format` | 6 — run formatting and document assembly |
| `/proposal submit prep` | 8 — package proposal per portal requirements |
| `/proposal submit` | 8 — execute submission |
| `/proposal debrief ingest [path]` | 9 — parse and ingest debrief feedback document |

---

## Human Checkpoints Summary

| Wave | Checkpoint |
|---|---|
| 0 | Topic selection and Go/No-Go decision |
| 1 | Strategy alignment before research begins |
| 2 | Research review — validate technical direction and market framing |
| 3 | Discrimination table approval; outline approval |
| 4 | Full draft review before formatting |
| 6 | Final assembled document review |
| 7 | Final sign-off before submission |
| 9 | Lessons learned review |

---

## nWave Inspiration & Design Philosophy

### What nWave Is

[nWave](https://github.com/nWave-ai/nWave) is an open-source Claude Code plugin that implements a structured, human-in-the-loop agentic workflow for software feature delivery. It installs via `pipx` and places agents, commands, and configuration into `~/.claude/`, making them available globally inside any Claude Code session.

nWave's core philosophy is captured in this pattern:

```
  machine        human         machine        human         machine
    │              │              │              │              │
    ▼              ▼              ▼              ▼              ▼
  Agent ──→ Documentation ──→ Review ──→ Decision ──→ Agent ──→ ...
 generates    artifacts      validates   approves    continues
```

> "The machine never runs unsupervised end-to-end."

Each wave produces artifacts. A human reviews them. A human approves them. Only then does the next wave begin. This is not just a UX preference — it is a structural guarantee enforced at the execution layer.

### nWave's Full Six-Wave Command Set

nWave's complete workflow spans six waves, each with a dedicated slash command and specialist agent:

| Wave | Command | Agent | Artifact Produced |
|---|---|---|---|
| DISCOVER | `/nw:discover` | product-discoverer | Market validation |
| DISCUSS | `/nw:discuss` | product-owner | Requirements spec |
| DESIGN | `/nw:design` | solution-architect | Architecture + ADRs |
| DEVOPS | `/nw:devops` | platform-architect | Infrastructure readiness |
| DISTILL | `/nw:distill` | acceptance-designer | Given-When-Then acceptance tests |
| DELIVER | `/nw:deliver` | software-crafter | Working implementation + test suite |

22 agents total: 6 wave agents, 5 cross-wave specialists, and 11 peer reviewers that can be invoked at any stage. The elegance of the command naming is that each verb describes what the *human* is doing — discovering, discussing, designing — not what the machine is doing. The human remains the subject of the process throughout.

Notable waves for our analogue thinking:
- **DISCOVER** establishes that market validation is a first-class wave, not a prerequisite — it produces its own artifact and requires human approval before requirements work begins
- **DEVOPS** establishes that infrastructure readiness (CI/CD, environments, platform) is a distinct wave before implementation — the proposal equivalent is submission infrastructure readiness (SAM.gov, portal accounts, output tooling)
- The **11 peer reviewers** are cross-wave specialists, not assigned to any single wave — they can be invoked at any stage for targeted quality review

### Design Independence — Inspiration, Not Constraint

**This plugin does not attempt to map its phases 1:1 to nWave's phases.** The proposal lifecycle is a different problem from software feature delivery, and forcing a strict structural mapping would produce awkward seams that serve the analogy rather than the goal.

What we take from nWave:

- **The machine-human-machine rhythm** — agents produce artifacts, humans review and approve, agents continue. Never unsupervised end-to-end.
- **Named, versioned artifacts as the unit of review** — not raw agent output or CLI conversation, but specific files that can be opened, annotated, and approved
- **An enforcement layer at the execution level** — PES, analogous to DES, enforces invariants through hooks rather than relying on agent instructions alone
- **Rigor as a configurable dial** — `/proposal:rigor` mirrors `/nw:rigor`, letting enforcement depth match the stakes of the work
- **ATDD as a quality driver** — PDCs mirror Given-When-Then acceptance criteria, generating a checkable definition of done before drafting begins
- **The `~/.claude/agents/` and `~/.claude/commands/` conventions** — same file placement, same markdown format, same Claude Code plugin architecture

What we do differently, because our problem demands it:

- **Non-linear iteration** — proposal waves loop and reference each other. TPOC feedback in Wave 1 can reopen Wave 3 discrimination framing. The plugin supports re-entry into any wave without losing state. nWave flows forward; we don't have that luxury.
- **Human intelligence as first-class input** — TPOC interviews, debrief letters, go/no-go judgment calls are not agent outputs. They are external events the system ingests and acts on. This is architecturally different from nWave, where all inputs are either code or human approval decisions.
- **A compounding institutional corpus** — nWave starts fresh on each feature. Our corpus librarian accumulates across every proposal cycle. The system gets materially better the longer it's used. This is a fundamentally different architecture: the corpus is a persistent organizational asset, not a session artifact.
- **Compliance as the quality contract** — in software, tests define done. In SBIR, the compliance matrix defines done. Every "shall" in the solicitation is a contractual obligation with disqualification consequences. PES treats compliance coverage with the same non-negotiable weight that DES gives to test coverage.
- **Our wave count and agent roster are determined by what produces good proposals** — not by how many waves nWave has. If we need 10 waves and 13 agents to do this right, that's what we build. If we later discover two waves can be merged without losing quality, we merge them.

### `/nw:forge` — Building Agents with nWave's Meta-Tool

`/nw:forge` is nWave's cross-wave meta-command for creating new agents and commands. It is not part of the end-user feature delivery workflow — it is a **developer tool for building the plugin itself**, which makes it exactly the right tool for building this plugin's agents.

**Command definition:**
```
/nw:forge [agent-name]
  --type=[specialist|reviewer|orchestrator]
  --pattern=[react|reflection|router|planning|sequential|parallel|hierarchical]

Wave: CROSS_WAVE
Agent: Zeus (nw-agent-builder)
```

**The forge 5-phase workflow: ANALYZE → DESIGN → CREATE → VALIDATE → REFINE**

Zeus, the `nw-agent-builder` specialist, executes a structured 5-phase process for each agent:

1. **ANALYZE** — examines the agent's role, responsibilities, inputs, outputs, and relationships to other agents; identifies what domain knowledge needs to be extracted to Skills
2. **DESIGN** — selects agent type and design pattern; defines the agent's behavioral contract; drafts the YAML frontmatter
3. **CREATE** — writes the agent markdown file following nWave's v2 approach: focused core (200–400 lines) with Skills carrying domain knowledge
4. **VALIDATE** — runs the 11-point validation checklist; checks against the `agent-builder-reviewer` skill's critique dimensions
5. **REFINE** — addresses any validation failures; optimizes for clarity and correctness

**The `agent-builder-reviewer` pairing**

Alongside Zeus, nWave provides a dedicated `agent-builder-reviewer` skill with its own `review-workflow.md` and `critique-dimensions.md`. This is the peer reviewer that validates what Zeus produces — the same machine-human-machine pattern applied recursively to agent creation itself. After forge creates an agent, the reviewer skill validates it before it's considered done.

**Agent output structure:**
```
~/.claude/agents/nw/nw-{agent-name}.md      # The agent definition
~/.claude/skills/nw/{agent-name}/*.md        # Skill files (if domain knowledge > 50 lines)
```

### Forge Success Criteria — Constraints That Govern Our Agent Writing

The forge validation checklist defines the quality bar every agent must meet. These constraints apply directly to all agents we build for this plugin:

| Criterion | Implication for Our Agents |
|---|---|
| Under 400 lines | Agents stay focused; domain knowledge lives in Skills, not agent bodies |
| Official YAML frontmatter (name, description, tools, maxTurns) | Every agent has structured metadata, not just prose |
| 11-point validation checklist passes | We run forge's validator on every agent before considering it done |
| Only divergent behaviors specified | Don't instruct Claude to do what it does by default; only specify what's different |
| 3–5 canonical examples included | Each agent has concrete worked examples, not just abstract instructions |
| Domain knowledge extracted to Skills if >50 lines | Our skill files (TPOC question generator, compliance matrix builder, etc.) are the right place for domain depth |
| No aggressive language (no CRITICAL/MANDATORY/ABSOLUTE) | Agent instructions use clear professional language, not emphatic prose |
| Safety via platform features (frontmatter/hooks), not prose | PES enforcement happens in hooks and frontmatter gating, not by telling agents to be careful |

The "only divergent behaviors" constraint is particularly important — it means our agent files should be lean specifications of what makes each agent *different* from Claude's defaults, not exhaustive instructions for every behavior. The corpus librarian agent doesn't need to be told how to read a file; it needs to be told what the corpus schema looks like and how to retrieve from it.

### Agent Type and Design Pattern Classification

Forge supports three agent types and eight design patterns. Classifying our agents upfront guides Zeus during the CREATE phase:

| Our Agent | Type | Pattern | Rationale |
|---|---|---|---|
| `orchestrator` | orchestrator | hierarchical | Coordinates all other agents; manages state, handoffs, and checkpoints across the full lifecycle |
| `topic-scout` | specialist | sequential | Scrapes sources in order, normalizes output, scores in sequence |
| `fit-scorer` | specialist | react | Needs to reason about company profile vs. topic, may loop to pull corpus exemplars |
| `compliance-sheriff` | specialist | sequential | Parses solicitation linearly, maps items to sections in order |
| `tpoc-analyst` | specialist | reflection | Generates questions, reflects on strategic gaps, revises — then ingests answers and reflects on deltas |
| `researcher` | specialist | react | Web research loop: search, evaluate, decide whether to go deeper, synthesize |
| `strategist` | specialist | planning | Builds a multi-part strategy (TRL + teaming + budget + pathway) that must be internally consistent |
| `corpus-librarian` | specialist | router | Routes retrieval requests to the right corpus partition (proposals, debriefs, TPOC logs, boilerplate) |
| `writer` | specialist | sequential | Drafts section by section following the approved outline |
| `reviewer` | reviewer | reflection | Reviews draft, identifies gaps, reflects on evaluation criteria alignment, produces scorecard |
| `formatter` | specialist | sequential | Applies formatting rules in order; assembles volumes |
| `submission-agent` | specialist | sequential | Portal-specific packaging steps in strict sequence |
| `debrief-analyst` | specialist | reflection | Reads feedback, reflects on which proposal decisions led to each critique, maps to sections |

### The Forge Build Sequence for This Plugin

Using `/nw:forge` to build every agent in our roster, in dependency order:

```bash
# Phase 1 — Kernel agents first (everything depends on these)
/nw:forge proposal-orchestrator --type=orchestrator --pattern=hierarchical
/nw:forge corpus-librarian --type=specialist --pattern=router

# Phase 2 — Wave 0-1 agents
/nw:forge topic-scout --type=specialist --pattern=sequential
/nw:forge fit-scorer --type=specialist --pattern=react
/nw:forge compliance-sheriff --type=specialist --pattern=sequential
/nw:forge tpoc-analyst --type=specialist --pattern=reflection
/nw:forge strategist --type=specialist --pattern=planning

# Phase 3 — Wave 2-4 agents
/nw:forge researcher --type=specialist --pattern=react
/nw:forge writer --type=specialist --pattern=sequential
/nw:forge reviewer --type=reviewer --pattern=reflection

# Phase 4 — Wave 5-9 agents
/nw:forge formatter --type=specialist --pattern=sequential
/nw:forge submission-agent --type=specialist --pattern=sequential
/nw:forge debrief-analyst --type=specialist --pattern=reflection
```

After each agent is created by Zeus, the `agent-builder-reviewer` skill validates it. Only reviewer-approved agents are considered complete and moved to the plugin's `~/.claude/agents/` directory.

The PES Python layer and session hooks are the only parts of the plugin that are **not** built with forge — those are real code with testable behavior, built using nWave's standard `/nw:discuss` → `/nw:design` → `/nw:distill` → `/nw:deliver` workflow with full TDD enforcement.

---

## PES — Proposal Enforcement System

### What DES Is (The Inspiration)

In nWave, the **DES (Delivery Enforcement System)** is a quality enforcement layer that runs alongside agents during the `/nw:deliver` wave. From the nWave documentation:

> *"DES is nWave's quality enforcement layer — it monitors every agent tool invocation during feature delivery to enforce TDD discipline and protect accidental edits."*

DES is not a workflow tracker. It is an **active enforcement hook** that operates at the invocation level — watching what agents actually *do*, not just whether they report completing a step. Its key behaviors:

- Prevents an agent from writing implementation code without a corresponding test artifact existing first
- Blocks file edits outside the scope of an active DES task
- Detects when agent prompts accidentally match step-ID patterns and flags them
- Provides an explicit escape hatch (`<!-- DES-ENFORCEMENT: exempt -->`) for cases where a developer knowingly wants to bypass enforcement, with the bypass logged
- Runs **session housekeeping** at startup: removes stale audit logs, cleans up signal files from crashed sessions, rotates skill-loading logs
- Is configured via `~/.nwave/des-config.json`, including enforcement level, audit log retention, and update check frequency

The DES config structure:
```json
// ~/.nwave/des-config.json
{
  "update_check": {
    "frequency": "daily | weekly | every_session | never"
  }
  // enforcement rules, audit retention, signal file paths
}
```

The core insight DES embodies: **guardrails belong at the execution layer, not just in the instructions given to agents.** An agent told "write tests first" can still write implementation first. An agent operating under DES enforcement physically cannot.

### PES — The Proposal Equivalent

**PES (Proposal Enforcement System)** is our analogue to DES. Where DES enforces TDD discipline, PES enforces **proposal integrity discipline** — the set of structural, content, and process invariants that distinguish a compliant, well-formed proposal from one that will be disqualified or score poorly.

PES is not a checklist the agent consults. It is an enforcement layer that monitors agent actions and blocks or flags violations before they propagate forward in the workflow.

#### PES Configuration

```json
// ~/.proposal/pes-config.json
{
  "enforcement": {
    "wave_ordering": "strict",
    "compliance_gate": true,
    "acronym_audit": true,
    "page_limit_check": true,
    "figure_reference_check": true,
    "submission_immutability": true,
    "corpus_write_protection": true
  },
  "deadlines": {
    "warning_days": 7,
    "critical_days": 3,
    "block_nonessential_at_critical": true
  },
  "audit_log": {
    "retention_days": 365,
    "path": "~/.proposal/audit/",
    "log_human_decisions": true,
    "log_waiver_reasons": true
  },
  "overrides": {
    "allow_wave_skip": false,
    "allow_compliance_waiver": true,
    "waiver_requires_reason": true,
    "waiver_marker": "<!-- PES-ENFORCEMENT: exempt -->"
  },
  "update_check": {
    "frequency": "every_session"
  }
}
```

#### Invariant Classes

PES enforces four classes of invariants:

**1. Structural Invariants** — wave and artifact ordering rules that are always true:

| Rule | Enforcement |
|---|---|
| No section draft may exist without a compliance matrix entry covering it | Block — agent cannot create draft file without entry |
| Outline cannot be approved before discrimination table is approved | Block — approval command rejected |
| Formatting wave cannot begin before all drafts have ≥1 human-approved iteration | Block — `/proposal format` rejected |
| Submission prep cannot begin before final review sign-off | Block — `/proposal submit prep` rejected |
| Submitted package artifact is immutable after submission confirmation | Block — any write to submitted archive triggers error |
| Corpus proposals tagged `submitted` or `awarded` are read-only | Block — corpus write to tagged entries rejected |

**2. Content Invariants** — checks run against draft content at each iteration:

| Rule | Enforcement |
|---|---|
| Every acronym used in a section must have a definition on first use in the document | Warning flagged in iteration review output |
| Every figure referenced in text must have a corresponding file in `/figures/` | Warning — blocks formatting wave if unresolved |
| Page count must be within solicitation limits | Warning at draft; Block at formatting wave |
| Every compliance matrix item must have a status (`covered` / `partial` / `missing` / `waived`) | Block — compliance check command reports open items |
| SOW milestones must be numbered and have explicit deliverables | Warning flagged in SOW section review |

**3. Temporal Invariants** — deadline-aware enforcement:

| Condition | PES Behavior |
|---|---|
| ≤ warning_days remaining, wave incomplete | Warning surfaced at session start and on `/proposal status` |
| ≤ critical_days remaining, non-critical work active | Warning escalated; optional block via config |
| Deadline passed, proposal not submitted | Block all non-archival actions; flag for debrief prep |

**4. Corpus Integrity** — institutional memory protection:

| Rule | Enforcement |
|---|---|
| Debrief feedback may annotate but not modify archived submitted proposals | Block — debrief ingest writes to annotation layer only |
| Win/loss tags are append-only | Block — existing outcome tags cannot be overwritten |
| TPOC Q&A logs are immutable after ingestion | Block — TPOC logs are write-once |

#### Session Startup Housekeeping

Mirroring DES's session-start behavior, PES runs silent housekeeping every time Claude Code opens with the proposal plugin active:

```
PES SESSION START
─────────────────────────────────────────
✓ proposal-state.json integrity check
✓ Orphaned draft files reconciled with state
✓ Figures directory cross-referenced with draft citations
✓ Compliance matrix completeness check
✓ Deadline proximity check — 14 days remaining (NORMAL)
✓ Audit log rotation (logs > 365 days pruned)
✓ Corpus index refresh
✓ Plugin version check
─────────────────────────────────────────
1 warning: Section 3.2 draft exists but has no compliance matrix entry.
Run /proposal compliance check for details.
```

Housekeeping is silent unless it finds something. When it does, it surfaces a single summary warning — never blocks the session, always guides toward resolution.

#### The PES Escape Hatch

Some enforcement violations are intentional. A facilities section may be deliberately omitted for a particular agency. A compliance item may be knowingly waived because the TPOC indicated it was not actually required. PES provides an explicit escape hatch analogous to DES's `<!-- DES-ENFORCEMENT: exempt -->`:

```markdown
<!-- PES-ENFORCEMENT: exempt
     reason: TPOC confirmed facilities section not evaluated for this topic (2026-03-01 call)
     authorized-by: Phil
-->
```

The waiver marker is:
- Required to include a `reason` when `waiver_requires_reason: true` in config
- Logged to the audit trail with timestamp and authorizing user
- Surfaced in the final review wave's compliance report as a named waiver, not a silent omission
- Never silent — every waiver is visible in the compliance matrix with its reason

This means the final proposal package always has a complete audit trail: every requirement either covered, partially covered, or explicitly waived with documented rationale.

#### PES Audit Log

Every agent action and every human decision is logged to `~/.proposal/audit/`:

```
2026-03-07T09:14:22Z  WAVE_START       wave=1 topic=AF243-001
2026-03-07T09:31:05Z  AGENT_ACTION     agent=compliance-sheriff action=matrix_generated items=47
2026-03-07T10:02:18Z  HUMAN_DECISION   checkpoint=strategy_review decision=approve
2026-03-07T10:45:33Z  AGENT_ACTION     agent=tpoc-analyst action=questions_generated count=23
2026-03-07T14:22:11Z  HUMAN_DECISION   checkpoint=tpoc_review decision=revise feedback="add TRL question"
2026-03-07T14:38:44Z  AGENT_ACTION     agent=tpoc-analyst action=questions_revised count=24
2026-03-07T14:41:02Z  HUMAN_DECISION   checkpoint=tpoc_review decision=approve
2026-03-07T15:10:55Z  PES_ENFORCEMENT  rule=compliance_gate section=3.2 action=blocked reason="no matrix entry"
2026-03-07T15:12:30Z  PES_WAIVER       rule=compliance_gate section=3.2 reason="TPOC exempt" authorized-by=Phil
```

Audit logs rotate based on `retention_days` in config. Logs for submitted proposals are retained for the full retention window regardless of rotation.

---

---

## PDC — Proposal Distillation Criteria

### The nWave ATDD Analogy

nWave's `/nw:distill` command is the pivot point of its entire quality model. Before a single line of implementation code is written, the human and agent collaborate to produce **acceptance criteria** — concrete, checkable assertions about what "done" looks like for the feature. These criteria become the test suite that drives the `/nw:deliver` red/green/refactor loop. The human's judgment is front-loaded into the criteria definition phase; it is not re-expended on every draft iteration. The tests say done. Not the human's feeling about the draft.

The nWave ATDD loop:
```
/nw:distill  →  acceptance criteria defined, human approves
/nw:deliver  →  agent implements
               → tests run → RED items listed
               → agent targets red items
               → tests run → fewer RED
               → repeat until all GREEN
               → human reviews GREEN state and approves
```

The critical insight: **the human approves criteria once, then the machine iterates against them autonomously.** Human judgment is not required on every pass — only at criteria definition and final GREEN review.

### The Proposal Equivalent

In proposals, the equivalent of "the tests say done" is the intersection of three things:
- The solicitation's evaluation criteria (the official scoring rubric — what government evaluators are literally instructed to score)
- The compliance matrix (every "shall" — the contractual floor that determines disqualification vs. eligibility)
- The discrimination table (every claimed differentiator — which must be evidenced somewhere in the narrative or it is just marketing)

**PDCs (Proposal Distillation Criteria)** are generated by `/proposal:distill` before drafting begins. They are the checkable assertions that drive the draft/check/iterate loop, exactly as acceptance criteria drive the implement/test/refactor loop.

### `/proposal:distill` Command

```bash
/proposal:distill [section]        # Generate PDCs for a specific section
/proposal:distill --all            # Generate PDCs for all sections from full context
/proposal:distill --update         # Refresh PDCs after TPOC ingestion or strategy change
```

**Inputs consumed:**
- Raw solicitation text (evaluation criteria section especially)
- Compliance matrix (all "shall" statements mapped to sections)
- Discrimination table (all claimed differentiators)
- TPOC Q&A log (informal requirements and insights)
- Corpus patterns for this agency (what has historically passed review)
- Research summary (claims that need to be supportable)

**Output:** A `.pdc` file per section, plus a master `proposal.pdc` cross-section file, written to `/pdcs/`.

### PDC File Structure

Each PDC file contains assertions organized into four evaluability tiers — from fully automatable to requiring adversarial LLM judgment:

```markdown
# PDC: Section 3 — Technical Approach
# Generated: 2026-03-07 | Topic: AF243-001 | Wave: 3

---

## Tier 1: Mechanical (PES auto-checks on every /proposal:check run)
- [ ] Page count ≤ 15 (solicitation limit)
- [ ] Current TRL stated as explicit integer (e.g., "TRL 4")
- [ ] Target TRL at Phase I completion stated as explicit integer
- [ ] No placeholder text remaining ([TBD], [INSERT], [XX])
- [ ] All figures referenced in text exist in /figures/
- [ ] All acronyms defined on first use in this section
- [ ] Word count within section page budget (±10%)
- [ ] At least 1 figure or diagram present

## Tier 2: Rubric (LLM evaluator — scored pass/fail against stated criteria)
- [ ] Technical approach directly responds to topic objective statement
      CHECK: First 2 paragraphs contain explicit reference to topic's stated technical challenge
      SOURCE: Solicitation §2.1 objective language
- [ ] Novelty claim is differentiated from prior art
      CHECK: ≥2 named competing approaches described; explicit limitation of each stated
      SOURCE: Discrimination table row "Technical Novelty"
- [ ] TRL justification is evidence-based
      CHECK: TRL claim supported by named prior work, test results, or publication
      SOURCE: Research summary §TRL
- [ ] Phase II pathway described with specificity
      CHECK: Contains named milestones, not generic "we will continue development" language
      SOURCE: Solicitation evaluation criterion "Phase II Potential"
- [ ] TPOC informal requirement addressed
      CHECK: Integration with [system X] mentioned per TPOC call 2026-03-01
      SOURCE: TPOC Q&A log item #7

## Tier 3: Persona (adversarial LLM reviewer — simulates government technical evaluator)
- [ ] Skeptical DoD technical evaluator finds no unanswered feasibility questions
      CHECK: Reviewer simulation scores Technical Feasibility ≥ 4/5
- [ ] Every discrimination table differentiator is evidenced in narrative
      CHECK: Each row of discrimination table has ≥1 citation in this section
- [ ] No claims made without supporting rationale or citation
      CHECK: Reviewer simulation flags unsupported assertions; count = 0

## Tier 4: Cross-Section (consistency checks against other sections)
- [ ] Every technical task described here has a corresponding SOW milestone (→ SOW.pdc)
- [ ] Key personnel named in tasks appear in management section (→ Section 4.pdc)
- [ ] Phase I cost is consistent with labor hours implied by task descriptions (→ Budget.pdc)
- [ ] Market need stated here is consistent with commercialization section (→ Section 6.pdc)
```

### The PDC-Driven Draft Loop

With PDCs defined, the drafting loop becomes genuinely structured and partially autonomous:

```
/proposal:distill [section]   →  PDCs generated, human approves
/proposal:draft [section]     →  Agent drafts against PDCs
/proposal:check [section]     →  PES runs all Tier 1 + Tier 2 PDCs
                                  → RED items listed with specific failure reasons
/proposal:iterate [section]   →  Agent revises targeting red items specifically
/proposal:check [section]     →  PDCs re-run → fewer RED
... repeat until Tier 1 + Tier 2 all GREEN
/proposal:review [section]    →  Human reviews GREEN state + Tier 3 persona output
                                  → approve / revise with feedback
                                  → if revise: back to iterate loop
/proposal:approve [section]   →  Section locked, cross-section checks queued
```

The `/proposal:check` command is the test runner. The agent does not ask "is this good?" — it asks "which PDCs are red?" and targets those specifically. Tier 3 persona review happens at the human checkpoint, not on every pass, because it requires judgment — but the human is reviewing a document that has already cleared Tiers 1 and 2 automatically. The quality floor is guaranteed before human eyes touch it.

### PDC Coverage as a Progress Metric

The master `proposal.pdc` tracks aggregate GREEN/RED state across all sections, giving a live proposal health dashboard:

```
/proposal:status

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROPOSAL STATUS — AF243-001
Wave 4: Drafting | 11 days to deadline
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PDC Coverage:
  Section 1 (Executive Summary)   ████████░░  80% GREEN  [2 RED]
  Section 2 (Background/Need)     ██████████ 100% GREEN  [approved ✓]
  Section 3 (Technical Approach)  ██████░░░░  60% GREEN  [4 RED]
  Section 4 (Management)          ░░░░░░░░░░   0% GREEN  [not started]
  Section 5 (Cost/Budget)         ░░░░░░░░░░   0% GREEN  [not started]
  Section 6 (Commercialization)   ████░░░░░░  40% GREEN  [6 RED]
  SOW                             ███████░░░  70% GREEN  [3 RED]
  Cross-section                   ██░░░░░░░░  20% GREEN  [8 RED]

Compliance Matrix: 41/47 items COVERED | 3 PARTIAL | 3 MISSING
Deadline: 11 days | Critical path: Section 3, Cross-section checks
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Artifact Catalog

### nWave's Artifact Model (The Inspiration)

nWave's full workflow has six waves. Each wave produces artifacts that the human reviews before the next wave begins. The machine never runs unsupervised end-to-end.

While nWave's internal artifact naming is not fully public, the pattern inferred from the repository and documentation is:

| nWave Wave | Command | Artifact Produced | Purpose |
|---|---|---|---|
| Requirements | `/nw:discuss` | Feature Specification (feature-spec.md) | Human-readable statement of what to build and why |
| Architecture | `/nw:design` | Architecture Decision Record (ADR) | Captures the technical approach chosen and alternatives rejected |
| Acceptance Tests | `/nw:distill` | Acceptance Criteria / Test Spec | The checkable definition of done that drives delivery |
| Implementation | `/nw:deliver` | Working code + test suite + refactor log | The actual deliverable, proven green against the test spec |

The ADR is particularly notable — it is not just documentation, it is a **decision record** that captures *why* an approach was chosen and what alternatives were considered and rejected. This makes the artifact valuable not just for the current feature but as institutional memory for future decisions. It answers the question a new team member or future agent would ask: "why does it work this way?"

The ITD (Implementation Task Decomposition) appears to be the structural breakdown that `/nw:deliver` uses to organize the implementation wave into discrete, DES-trackable steps — the bridge between the acceptance criteria and the actual code changes.

### Our Artifact Model

Every wave in this plugin produces named, versioned, human-reviewable artifacts written to a structured `/artifacts/` directory. Artifacts are the unit of human review at each checkpoint — not the raw agent output or the CLI conversation, but a specific file that can be opened, annotated, and approved.

```
/artifacts
  /wave-0-fit
    topic-digest.md           # Parsed solicitation summaries with fit scores
    go-no-go-brief.md         # Recommendation with rationale, exemplars cited
  /wave-1-strategy
    compliance-matrix.md      # Living document — updated through Wave 7
    tpoc-questions.md         # Prioritized question list with strategic intent tags
    tpoc-qa-log.md            # Structured Q&A from call, with delta annotations
    strategy-brief.md         # TRL, teaming, budget scaffold, Phase III pathway
    solicitation-delta.md     # TPOC vs. written solicitation gap analysis
  /wave-2-research
    technical-landscape.md    # State of art, prior art, patent notes
    prior-awards.md           # USASpending / SBIR.gov prior award analysis
    market-research.md        # TAM/SAM/SOM, competitor landscape
    trl-assessment.md         # Current/target TRL with justification
  /wave-3-outline
    discrimination-table.md   # Company/approach discriminators vs. competitors
    proposal-outline.md       # Section structure, page budgets, thesis statements
    figure-plan.md            # Placeholder list for all planned figures/diagrams
  /wave-4-drafting
    /sections
      section-1-executive-summary.md
      section-2-background.md
      section-3-technical-approach.md
      section-4-management.md
      section-5-cost.md
      section-6-commercialization.md
      sow.md
      references.md
    /review-records
      section-3-v1-review.md  # Human feedback captured per iteration
      section-3-v2-review.md
  /wave-5-visuals
    /figures
      fig-1-system-architecture.svg
      fig-2-trl-roadmap.svg
      fig-3-market-landscape.png
    figure-log.md             # Caption, cross-reference, format compliance per figure
  /pdcs
    section-3.pdc             # PDC file per section
    proposal.pdc              # Master cross-section PDC
    pdc-status.md             # Aggregate GREEN/RED dashboard
  /wave-6-assembly
    assembled-proposal.docx   # (or .pdf / .tex depending on medium)
    formatting-checklist.md   # Final compliance formatting check
  /wave-7-final-review
    persona-scorecard.md      # Reviewer simulation scores per evaluation criterion
    red-team-report.md        # Adversarial review findings
    final-compliance-report.md # All matrix items resolved or waived with reasons
  /wave-8-submission
    submission-manifest.md    # File list, checksums, portal confirmation
    submitted/                # Immutable archive of exactly what was submitted
  /wave-9-postsubmission
    debrief-feedback.md       # Parsed reviewer scores and comments
    debrief-section-map.md    # Feedback mapped to specific proposal sections
    lessons-learned.md        # Strategic retrospective for corpus
```

### Artifact Roles — The Proposal ADR Equivalents

In software, the ADR captures *why* a technical decision was made so future developers (and agents) understand the reasoning, not just the outcome. Proposals have several analogous artifacts where the *reasoning* is as important as the *content*:

**Strategy Brief** (Wave 1) — the proposal ADR
The strategy brief is the closest equivalent to a software ADR. It captures the key strategic decisions made before writing begins and why: why this technical approach over alternatives, why this TRL entry point, why this teaming configuration, what the TPOC said that shaped the approach. Without this document, future iterations — or a Phase II proposal — cannot reconstruct *why* the proposal was shaped the way it was.

```markdown
# Strategy Brief — AF243-001
## Technical Approach Decision
Chosen: Federated edge-compute architecture
Alternatives considered: Centralized cloud processing, Hybrid edge-cloud
Rejected because: TPOC indicated latency requirements rule out cloud round-trip;
                  centralized approach has been tried (see prior award AF241-087, not selected)
Decision date: 2026-03-07 | Authorized: Phil

## TRL Entry Point Decision
Current TRL: 3 (proof of concept demonstrated in lab)
Target TRL at Phase I completion: 5 (prototype validated in relevant environment)
Justification: Solicitation evaluation criterion weights "demonstration feasibility" heavily;
               jumping to TRL 6 is not credible in Phase I timeline/budget
...
```

**Discrimination Table** (Wave 3) — the proposal design document
Like an architecture design document, the discrimination table captures the *structure* of the argument before the narrative is written. It is the skeleton that the technical approach section hangs on. Each row is a claim that must be evidenced somewhere in the proposal body.

**PDC Files** (Wave 3/4) — the acceptance criteria
The PDC files are the direct ATDD analogue — the checkable definition of done per section, generated before drafting, that drives autonomous iteration.

**Persona Scorecard** (Wave 7) — the code review equivalent
Where nWave produces a peer review artifact during delivery, the persona scorecard is the proposal's equivalent — a structured evaluation of the proposal from the perspective of the government reviewer who will actually score it, surfacing gaps before submission rather than in the debrief.

**Lessons Learned** (Wave 9) — the retrospective that feeds the corpus
Where software ADRs feed future architecture decisions, lessons learned feed the corpus librarian's win/loss pattern analysis. Each lessons-learned document is a structured retrospective that captures not just what happened but why, and how it should change approach on the next proposal.

### Artifact Naming and Versioning

Every artifact that goes through human review iterations is versioned:

```
section-3-technical-approach-v1.md   # First draft
section-3-technical-approach-v1-review.md  # Human feedback on v1
section-3-technical-approach-v2.md   # Revised draft
section-3-technical-approach-v2-review.md  # Human feedback on v2
section-3-technical-approach-v3-approved.md  # Final approved version
```

The `-approved` suffix is written by the orchestrator only when the human runs `/proposal:approve [section]`. PES enforces that only approved artifacts can be referenced in downstream waves — a draft cannot be pulled into formatting until it carries the approved marker.

### The `/nw:rigor` Analogue — `/proposal:rigor`

nWave enforces proven engineering practices at every step. Use `/nw:rigor` to adjust the depth of quality practices to match your task's risk level. A config tweak needs less rigor than a security-critical feature.

Our plugin has an equivalent concept. Not all proposals warrant the same depth of process. A quick Phase I response to a familiar topic with a known TPOC is different from a cold Phase II to a new agency with a large budget. `/proposal:rigor` sets the enforcement profile:

```bash
/proposal:rigor lean       # Fast mode: Tier 1 PDC checks only, single review round per section
/proposal:rigor standard   # Default: Tier 1 + Tier 2 PDCs, persona review at final wave
/proposal:rigor full       # Maximum: All PDC tiers, red team wave, mutation-style adversarial review
/proposal:rigor custom     # Interactive: configure each enforcement dimension individually
```

Rigor profiles affect:
- Which PDC tiers are run automatically vs. on-demand
- Number of required iteration rounds before a section can be approved
- Whether a red team wave is mandatory or optional
- Whether cross-section consistency checks block or merely warn
- Whether corpus pattern matching is run on every draft or only at final review

Rigor is set once per proposal project and persists across sessions, stored in `proposal-state.json`.

---

---

## Building This Plugin

### This Document as a nWave DISCUSS Artifact

This architecture document was produced through an informal DISCOVER and DISCUSS process — the equivalent of nWave's `/nw:discover` (market/problem validation) and `/nw:discuss` (requirements elicitation) waves, conducted conversationally rather than through the formal nWave commands.

The document now serves as the **DISCUSS-phase artifact** — the requirements spec that the solution architect reads before producing Architecture Decision Records in `/nw:design`. It captures:

- The problem domain (SBIR/STTR proposal lifecycle)
- The full wave/agent/skill/command architecture
- The enforcement model (PES)
- The quality model (PDCs, `/proposal:distill`, `/proposal:check`)
- The artifact catalog
- The nWave inspiration and design independence rationale
- The forge build plan for agent construction

The next formal step is `/nw:design`, which consumes this document and produces ADRs for each major architectural decision before any code or agent files are written.

---

### Why nWave End-to-End

This plugin is built almost entirely using nWave itself — not just inspired by it. The reasoning:

**The plugin has real Python components.** PES enforcement hooks, session housekeeping, the PDC checker (`/proposal:check`), the state schema and persistence layer, and the pip/pipx installer all require actual code with testable behavior. Any Python presence makes this a legitimate nWave `/nw:deliver` project.

**Agent and command markdown files are built with `/nw:forge`.** Forge's Zeus agent (`nw-agent-builder`) produces well-structured, validated agent files using the 5-phase ANALYZE → DESIGN → CREATE → VALIDATE → REFINE workflow. The paired `agent-builder-reviewer` skill validates each agent before it's considered done. This is strictly better than writing agent files by hand without a validation harness.

**The build process is self-documenting.** Using nWave to build this plugin means every architectural decision is captured in an ADR, every Python component has a test suite, and every agent definition passes the 11-point forge validation checklist. The plugin ships with the same quality guarantees it asks users to apply to their proposals.

---

### Build Phases

#### Pre-Build: Formalize the DISCUSS Artifact

Before invoking any nWave commands, this document should be reviewed and approved as the requirements spec. Any open questions about scope, wave design, or agent responsibilities should be resolved here first.

**Human checkpoint:** Requirements review and sign-off on this document.

---

#### Phase 1: Design (`/nw:design`)

The solution architect produces ADRs for each major decision domain. Inputs: this document.

```bash
/nw:design --architecture=plugin
```

**ADRs to be produced:**

| ADR | Decision |
|---|---|
| ADR-001 | Plugin installation approach — pipx + `~/.claude/` placement |
| ADR-002 | State persistence schema — `proposal-state.json` structure and versioning |
| ADR-003 | PES enforcement architecture — hook mechanism, pre-execution interception vs. command-layer gating |
| ADR-004 | PDC evaluation architecture — Tier 1/2 automation vs. Tier 3 LLM persona invocation |
| ADR-005 | Corpus storage architecture — file layout, indexing, retrieval mechanism |
| ADR-006 | Agent communication pattern — how orchestrator hands off to specialist agents |
| ADR-007 | Wave re-entry model — how state is preserved and restored when a human re-enters an earlier wave |
| ADR-008 | Output medium abstraction — how the formatter agent supports docx/LaTeX/PDF without coupling |

**Human checkpoint:** ADR review and approval before any code or agent files are written.

---

#### Phase 2: DevOps (`/nw:devops`)

The platform architect ensures the development and distribution infrastructure is ready before implementation begins.

```bash
/nw:devops
```

**Deliverables:**
- Repository structure established (`/plugins/proposal/`, `/src/`, `/tests/`, `/docs/`)
- Python project scaffolded (`pyproject.toml`, `uv` toolchain, CI configuration)
- `~/.claude/` target directory structure validated
- Test infrastructure configured (pytest, fixtures for state JSON and corpus)
- Release pipeline design (PyPI packaging, version tagging)

**Human checkpoint:** Infrastructure readiness review.

---

#### Phase 3: Python Components (`/nw:distill` → `/nw:deliver`)

Each Python component is built as a distinct nWave feature with its own acceptance tests and TDD delivery. Components in dependency order:

```bash
# State manager — everything reads/writes proposal-state.json
/nw:distill "proposal-state-manager"
/nw:deliver

# PES enforcement layer — hooks, audit logging, invariant checks
/nw:distill "pes-enforcement"
/nw:deliver

# PDC checker — /proposal:check command runner, Tier 1/2 evaluation
/nw:distill "pdc-checker"
/nw:deliver

# Corpus manager — ingestion, indexing, retrieval
/nw:distill "corpus-manager"
/nw:deliver

# Session housekeeping — startup integrity checks, log rotation
/nw:distill "session-housekeeping"
/nw:deliver

# Installer — pipx entry point, ~/.claude/ placement, config scaffolding
/nw:distill "plugin-installer"
/nw:deliver
```

Each `/nw:distill` produces Given-When-Then acceptance tests. Each `/nw:deliver` implements against those tests under DES enforcement. Human review checkpoint after each deliver.

---

#### Phase 4: Agent and Command Files (`/nw:forge`)

Every agent and command markdown file is built using `/nw:forge`, which invokes Zeus (`nw-agent-builder`) and validates output with the `agent-builder-reviewer` skill.

Built in dependency order — kernel agents first, then wave agents, then cross-wave specialists:

```bash
# Kernel — everything depends on these
/nw:forge proposal-orchestrator --type=orchestrator --pattern=hierarchical
/nw:forge corpus-librarian      --type=specialist   --pattern=router

# Wave 0-1 agents
/nw:forge topic-scout           --type=specialist   --pattern=sequential
/nw:forge fit-scorer            --type=specialist   --pattern=react
/nw:forge compliance-sheriff    --type=specialist   --pattern=sequential
/nw:forge tpoc-analyst          --type=specialist   --pattern=reflection
/nw:forge strategist            --type=specialist   --pattern=planning

# Wave 2-4 agents
/nw:forge researcher            --type=specialist   --pattern=react
/nw:forge writer                --type=specialist   --pattern=sequential
/nw:forge reviewer              --type=reviewer     --pattern=reflection

# Wave 5-9 agents
/nw:forge formatter             --type=specialist   --pattern=sequential
/nw:forge submission-agent      --type=specialist   --pattern=sequential
/nw:forge debrief-analyst       --type=specialist   --pattern=reflection
```

After Zeus creates each agent, the `agent-builder-reviewer` skill validates it against the 11-point checklist. Only reviewer-approved agents are committed to the plugin.

**Skill files** are also built through forge — any agent whose domain knowledge exceeds 50 lines extracts that content into a paired skill directory:

```bash
# Skills generated alongside their parent agents:
~/.claude/skills/proposal/tpoc-analyst/tpoc-question-generator.md
~/.claude/skills/proposal/compliance-sheriff/compliance-matrix-builder.md
~/.claude/skills/proposal/corpus-librarian/win-loss-analyzer.md
~/.claude/skills/proposal/corpus-librarian/proposal-archive-reader.md
~/.claude/skills/proposal/researcher/market-researcher.md
~/.claude/skills/proposal/researcher/trl-assessor.md
~/.claude/skills/proposal/writer/discrimination-table.md
~/.claude/skills/proposal/reviewer/reviewer-persona-simulator.md
~/.claude/skills/proposal/strategist/budget-scaffolder.md
~/.claude/skills/proposal/formatter/visual-asset-generator.md
```

**Human checkpoint:** Each agent reviewed and approved before the next is forged.

---

#### Phase 5: Integration and Dogfooding

With all components built, the plugin is installed and used to manage its own ongoing development — the dogfooding phase.

**Integration testing:**
- Install the plugin via `pipx install` into a test `~/.claude/` environment
- Run `/proposal new` and walk through Waves 0–3 against a real open SBIR solicitation
- Verify PES enforcement fires correctly on wave ordering violations
- Verify `/proposal:check` correctly identifies red PDC items
- Verify corpus ingestion and retrieval with a sample past proposal

**Dogfooding:**
- Use `/proposal:distill` to define PDCs for each remaining agent markdown file
- Use `/proposal:check` to evaluate new agent files as they are written
- The plugin now enforces quality on its own development artifacts

**Human checkpoint:** Integration test review and dogfooding sign-off.

---

### Component Ownership Summary

| Component | Build Method | Tool |
|---|---|---|
| `proposal-state-manager` (Python) | TDD delivery | `/nw:distill` → `/nw:deliver` |
| `pes-enforcement` (Python) | TDD delivery | `/nw:distill` → `/nw:deliver` |
| `pdc-checker` (Python) | TDD delivery | `/nw:distill` → `/nw:deliver` |
| `corpus-manager` (Python) | TDD delivery | `/nw:distill` → `/nw:deliver` |
| `session-housekeeping` (Python) | TDD delivery | `/nw:distill` → `/nw:deliver` |
| `plugin-installer` (Python) | TDD delivery | `/nw:distill` → `/nw:deliver` |
| All agent `.md` files | Forge + review | `/nw:forge` + `agent-builder-reviewer` |
| All skill `.md` files | Forge + review | `/nw:forge` + `agent-builder-reviewer` |
| All command `.md` files | Forge + review | `/nw:forge` + `agent-builder-reviewer` |
| ADRs | Design wave | `/nw:design` |
| This document | DISCUSS artifact | Informal → formalized |

---

*This document is a living DISCUSS-phase artifact. It evolves through /nw:design ADR production and is superseded by ADRs for specific architectural decisions once the design wave is complete.*
