# SBIR Proposal Plugin for Claude Code

A multi-agent Claude Code plugin that guides you through the full SBIR/STTR proposal lifecycle — from topic discovery through submission and post-award learning.

All interaction happens in the Claude Code CLI. State persists as local JSON files. No web UI, no server, no database.

Built with [nWave](https://github.com/nwave-ai/nwave) — agents and skills created via `nw:forge`, development driven by nWave's wave-based methodology (`nw:discuss` → `nw:design` → `nw:distill` → `nw:deliver`). The Proposal Enforcement System (PES) is inspired by nWave's Design Enforcement System (DES).

## Prerequisites

**Required:**
- [Claude Code](https://claude.ai/claude-code) installed and authenticated
- Python 3.12+
- Git

**Optional:**
- LaTeX distribution (e.g., TeX Live, MiKTeX) — only if you choose LaTeX output format instead of DOCX
- Gemini API key — only for AI-generated concept figures in Wave 5 (see [Image Generation Setup](#image-generation-setup-optional))

## Install

```bash
/plugin install sbir@pmvanev-plugins
```

## Quick Start

Never used the plugin before? Here's the complete path from install to your first proposal:

```bash
# 1. Create a project directory and open Claude Code in it
mkdir my-first-proposal && cd my-first-proposal
claude

# 2. Run setup — the wizard walks you through everything
/sbir:setup

# 3. Find solicitations that match your company
/sbir:solicitation find

# 4. Start a proposal from a topic you like
/sbir:proposal new AF263-042

# 5. Coming back later? Pick up where you left off
/sbir:continue
```

That's it. The plugin guides you through each step interactively. You don't need to memorize commands — `/sbir:continue` always tells you what to do next.

### Sending feedback

At any point — before, during, or after a proposal — you can submit feedback directly to the plugin developer:

```bash
/sbir:developer-feedback
```

The agent walks you through three steps: pick a type (bug report, feature suggestion, or quality rating), optionally rate specific proposal sections, and optionally add free text. It automatically attaches a context snapshot (wave, state, rigor profile, corpus size) so bug reports include enough information to reproduce the issue without exposing any proposal content.

### What setup covers

The setup wizard detects your environment and adapts. First-time users build everything from scratch; returning users can keep their existing profile and corpus or update them.

1. **Prerequisites check** — verifies Python 3.12+, Git, and Claude Code
2. **Company profile** — searches the web for your company (SAM.gov, SBIR award history, capabilities), then lets you verify and fill gaps via document extraction, guided interview, or both
3. **Corpus ingestion** — locates past proposals, debriefs, and capability documents
4. **API key setup** (optional) — configures Gemini for concept figure generation in Wave 5
5. **Validation** — re-checks everything and displays a unified status summary
6. **Next steps** — tells you exactly what command to run next

Have your SAM.gov registration data (CAGE code, UEI) and any past proposals or capability statements handy. The wizard will tell you what it needs at each step.

When setup completes, you'll see:

```
  Prerequisites
    [ok]  Python 3.12.4
    [ok]  Git 2.44.0
    [ok]  Claude Code authenticated

  Company Profile
    [ok]  ~/.sbir/company-profile.json
    [ok]  SAM.gov active (CAGE: 7XY3Z)

  Corpus
    [ok]  14 documents indexed

  Optional
    [--]  GEMINI_API_KEY not configured (Wave 5 only)

  STATUS: READY

  Next: /sbir:solicitation find
```

Your company profile at `~/.sbir/company-profile.json` carries over across projects. Each completed proposal enriches the corpus — fit scoring improves with more past performance data, the writer pulls better exemplars, and the reviewer cross-references debrief patterns.

## Decision Tree

```
                        /sbir:setup
                            |
                    Prerequisites pass?
                   /                  \
                 NO                   YES
            Fix & rerun          Build profile
                                      |
                              /sbir:solicitation find
                             (shows partnership scoring
                              when partner profiles exist)
                                      |
                              Pick a topic
                                      |
                            STTR topic? ──YES──> /sbir:proposal partner-setup
                              |                  /sbir:proposal partner-screen (optional)
                              NO                        |
                              |   <─────────────────────+
                         /sbir:proposal new <topic>
                                      |
                               Go / No-Go?
                              /       |       \
                           NO-GO   DEFER     GO
                          archive   pause      |
                                     |    /sbir:proposal shape (optional)
                                     |         |
                                     |    /sbir:proposal check
                                     |    /sbir:proposal tpoc questions
                                     |         |
                                     |    [TPOC call happens]
                                     |         |
                                     |    /sbir:proposal tpoc ingest
                                     |         |
                                     |    /sbir:proposal wave strategy
                                     |         |
                                     |    Approve strategy? -----> Revise
                                     |         |
                                     |    [Wave 2: Research runs]
                                     |         |
                                     |    [Wave 3: Outline + discrimination table]
                                     |         |
                                     |    Approve outline? ------> Revise
                                     |         |
                                     |    /sbir:proposal draft <section>
                                     |    /sbir:proposal iterate <section>
                                     |         |  (max 2 revision cycles)
                                     |         |
                                     |    /sbir:proposal wave visuals
                                     |         |
                                     |    /sbir:proposal format
                                     |         |
                                     |    /sbir:proposal wave final-review
                                     |         |
                                     |    Sign off? ----------------> Revise
                                     |         |
                                     |    /sbir:proposal submit prep
                                     |         |
                                     |    [You upload to portal]
                                     |         |
                                     |    /sbir:proposal submit confirm
                                     |         |
                                     |    [Archive locked — read-only]
                                     |         |
                                     |    /sbir:proposal debrief outcome
                                     |    /sbir:proposal debrief lessons
                                     |         |
                                     |    [Lessons feed back into corpus]
                                     |         |
          /sbir:continue  <-----------+---------+
          (resume from any point)
```

At every gate (strategy approval, outline approval, final sign-off), you choose: **approve** to proceed, **revise** to iterate, **skip** to defer, or **quit** to save state and exit. `/sbir:continue` picks up from wherever you stopped.

## The 10-Wave Lifecycle

Each wave produces specific artifacts and ends with a human checkpoint. PES enforces wave ordering — you cannot skip ahead without completing prerequisites.

### Wave 0: Setup, Intelligence & Fit

Set up your environment (profile, corpus, partner profiles), then score topics against your company profile. Optionally generate candidate technical approaches.

```bash
/sbir:setup                                # First-time setup or re-run to update config
/sbir:proposal partner-setup               # Create a research institution partner profile
/sbir:proposal partner-screen "MIT"        # Screen a new potential partner for readiness
/sbir:solicitation find                    # Search and rank open topics (partnership-aware)
/sbir:proposal new <topic-or-file>         # Start proposal, Go/No-Go checkpoint
/sbir:proposal partner-set cu-boulder      # Designate partner for active proposal
/sbir:proposal shape                       # Generate 3-5 candidate approaches (optional)
/sbir:continue                             # Pick up where you left off (works in any wave)
```

**Artifacts:** `artifacts/wave-0-intelligence/` — topic digest, go-no-go brief, approach brief

### Wave 1: Requirements & Strategy

Extract compliance requirements, prepare for TPOC call, build strategy brief.

```bash
/sbir:proposal check                       # View compliance matrix status
/sbir:proposal compliance add "<text>"     # Add a missed compliance item
/sbir:proposal tpoc questions              # Generate prioritized TPOC questions
/sbir:proposal tpoc ingest ./notes.txt     # Parse TPOC call notes (after the call)
/sbir:proposal wave strategy               # Generate strategy brief → approve/revise/skip
```

**Artifacts:** `artifacts/wave-1-strategy/` — compliance matrix, TPOC questions, TPOC Q&A log, solicitation delta, strategy brief

**Gate:** Strategy brief approved before Wave 2 begins.

### Wave 2: Research

Technical landscape, prior awards, market analysis, TRL assessment.

**Artifacts:** `artifacts/wave-2-research/` — technical landscape, prior awards, market research, TRL assessment

### Wave 3: Discrimination & Outline

Competitive positioning, section-by-section outline with page budgets, figure plan.

**Artifacts:** `artifacts/wave-3-outline/` — discrimination table, proposal outline, figure plan, PDC files

**Gate:** Discrimination table and outline approved before drafting begins.

### Wave 4: Drafting

Draft each proposal section with iterative human review (max 2 revision cycles per section).

```bash
/sbir:proposal draft technical-approach    # Draft a section
/sbir:proposal draft sow
/sbir:proposal draft key-personnel
/sbir:proposal iterate technical-approach  # Submit for reviewer iteration
```

**Artifacts:** `artifacts/wave-4-drafts/sections/` — all proposal sections; `artifacts/wave-4-drafts/review-records/` — reviewer feedback per iteration

### Wave 5: Visual Assets

Generate figures, diagrams, and concept illustrations.

```bash
/sbir:proposal wave visuals                # Initialize figure specs + tool detection
/sbir:proposal draft figure "system-arch"  # Generate a specific figure
```

**Artifacts:** `artifacts/wave-5-visuals/` — figure inventory, cross-reference log, generated figures (SVG/PNG/Mermaid)

### Wave 6: Format & Assembly

Apply agency-specific formatting rules, assemble submission volumes.

```bash
/sbir:proposal format                      # Format and assemble → approve/revise
```

**Artifacts:** `artifacts/wave-6-format/` — compliance final check, jargon audit, assembled volumes

### Wave 7: Final Review

Simulated government evaluator scoring and red team analysis.

```bash
/sbir:proposal wave final-review           # Run review → iterate/sign-off
```

**Artifacts:** `artifacts/wave-7-review/` — reviewer scorecard, red team findings, debrief cross-check, sign-off record

**Gate:** Sign-off required before submission.

### Wave 8: Submission

Package files for the submission portal. You perform the actual upload manually.

```bash
/sbir:proposal submit prep                 # Prepare package → approve/revise
/sbir:proposal submit confirm              # Confirm submission, create immutable archive
```

**Artifacts:** `artifacts/wave-8-submission/` — pre-submission checklist, portal-ready package, immutable archive

After confirmation, the proposal archive becomes **read-only** (PES-enforced).

### Wave 9: Post-Submission

Record outcomes, request debriefs, extract lessons learned.

```bash
/sbir:proposal debrief outcome WIN         # Record result
/sbir:proposal debrief request-letter      # Draft debrief request (if LOSS)
/sbir:proposal debrief ingest ./debrief.pdf  # Parse agency feedback
/sbir:proposal debrief lessons             # Generate lessons learned
```

**Artifacts:** `artifacts/wave-9-learning/` — debrief request draft, structured debrief, critique section map, pattern analysis, lessons learned

Lessons and debrief data feed back into the corpus for future proposals.

## Proposal Enforcement System (PES)

The PES is a Python-based guardrail system that validates every action against proposal lifecycle rules. It runs automatically via Claude Code hooks — you never invoke it directly, but it prevents mistakes like skipping waves, drafting before strategy approval, or modifying a submitted proposal.

Inspired by nWave's [Design Enforcement System (DES)](https://github.com/nwave-ai/nwave), which enforces wave ordering in software development workflows. PES adapts the same concept for the SBIR proposal domain.

### How it works

PES hooks into two Claude Code events:

- **SessionStart** — validates state file integrity when you open a project. If `.sbir/proposal-state.json` is corrupted, PES attempts recovery from the `.bak` backup.
- **PreToolUse** — evaluates every tool call against active enforcement rules before it executes. If a rule is violated, PES blocks the action with an explanation of what's wrong and what to do instead.

### What PES enforces

| Rule | Example |
|------|---------|
| **Wave ordering** | Can't start Wave 4 drafting until Wave 3 outline is approved |
| **Gate compliance** | Can't proceed past strategy brief until it's explicitly approved |
| **Deadline awareness** | Warnings at 7 days, blocks at critical thresholds |
| **Submission immutability** | Can't modify proposal content after submission is confirmed |
| **Quality gates** | Validates quality profile consistency when quality discovery is active |

### Architecture

PES uses ports-and-adapters architecture to keep domain rules pure and testable:

- **Domain** (`scripts/pes/domain/`) — pure Python business rules with no infrastructure imports
- **Ports** (`scripts/pes/ports/`) — abstract interfaces (StateReader, StateWriter, RulePort)
- **Adapters** (`scripts/pes/adapters/`) — JSON file persistence, Claude Code hook protocol translation

Hook protocol: JSON on stdin/stdout, exit codes 0 (allow), 1 (block with explanation).

## Agents

18 specialized agents collaborate across the lifecycle. Each agent owns a specific domain and is dispatched by the orchestrator based on proposal state.

| Agent | Waves | What it does |
|-------|-------|-------------|
| **setup-wizard** | Pre | Orchestrates first-time setup: prerequisites, profile, corpus, API key, validation. Detects existing config and adapts for returning users. |
| **profile-builder** | Pre | Builds company profile via web research (SAM.gov, sbir.gov, company site), document extraction, and guided interview. Explains how each field affects fit scoring. |
| **partner-builder** | Pre,0 | Creates and manages research institution partner profiles. Conversational interview with web research, schema validation, combined capability analysis. Also supports readiness screening mode for evaluating new potential partners. |
| **quality-discoverer** | Pre | Extracts writing quality intelligence from past proposals and evaluator feedback. Builds preferences, winning patterns, and quality profile artifacts that downstream agents consume. |
| **corpus-librarian** | 0,1,3,4,9 | Indexes past proposals, debriefs, and capability documents. Provides wave-aware retrieval: fit exemplars in Wave 0, section structures in Wave 3, tone references in Wave 4. Manages corpus image reuse with adapted captions. |
| **topic-scout** | 0 | Scores open solicitations against company profile using five-dimension fit scoring (subject matter 0.35, past performance 0.25, certifications 0.15, phase eligibility 0.15, STTR 0.10). Partnership-aware: when partner profiles exist, shows dual-column scoring (solo vs. partnership) with delta and recommendation elevation. Detects disqualifiers: clearance gaps, missing STTR partner, expired deadlines. |
| **solution-shaper** | 0 | Generates 3-5 candidate technical approaches post-Go decision. Scores each against personnel alignment, past performance, technical readiness, solicitation fit, and commercialization potential with traceability to specific people and contracts. |
| **compliance-sheriff** | 1,6,7 | Extracts every SHALL, FORMAT, and implicit requirement from the solicitation into a living compliance matrix. Preserves original contractual wording. Flags ambiguities as TPOC question opportunities. Runs final compliance audit in Wave 7. |
| **tpoc-analyst** | 1 | Generates 7-15 strategically sequenced TPOC questions (opener → core → strategic → closer) with rationale. After the call, ingests notes and produces delta analysis: clarifications, expansions, contradictions, and confirmations against the solicitation. |
| **strategist** | 1 | Generates strategy brief covering six required dimensions: technical approach, TRL assessment, teaming, Phase III commercialization, budget scaffold, and risk analysis. Every claim cites its source (solicitation, compliance item, TPOC answer, corpus data). |
| **researcher** | 2 | Produces six research artifacts: technical landscape, patent landscape, prior award analysis (SBIR.gov, USASpending.gov), market research with bottom-up sizing, commercialization pathway, and TRL refinement. Every claim sourced. |
| **writer** | 3,4 | Builds discrimination table (Wave 3), creates section-by-section outline with page budgets (Wave 3), then drafts each section (Wave 4). Compliance-matrix-driven: every paragraph traces to a requirement. Supports configurable writing style skills — Strunk & White (active voice, no needless words, positive form, parallel construction) ships built-in; additional style guides can be added as skill files. Style selection is stored in proposal state. Pulls corpus exemplars for calibration without copying verbatim. |
| **reviewer** | 4,7 | Simulates government evaluator scoring using the agency's actual rubric (adjectival for DoD, binary for NSF, numeric for NIH). Produces actionable findings with location, severity, and specific fix suggestions. Red team analysis identifies 3-5 strongest reasons not to fund. Checks drafts against debrief history and quality profile. Max 2 revision cycles per section. |
| **formatter** | 5,6 | Generates figures from the Wave 3 plan using available tools (Mermaid, Graphviz, SVG, Gemini). Checks tool availability before selecting method. Applies agency-specific formatting rules (fonts, margins, headers, page limits) and assembles submission volumes. Solicitation FORMAT requirements override all defaults. |
| **submission-agent** | 8 | Packages proposal for the target portal with correct naming conventions and size limits. Runs pre-submission verification (PDF validity, budget consistency, company identifiers). Generates step-by-step upload instructions. After user confirms with portal confirmation number, creates immutable SHA-256 checksummed archive. |
| **debrief-analyst** | 9 | Records outcomes, drafts debrief request letters (for losses), ingests evaluator feedback, and maps every comment to a specific proposal section. Categorizes loss root causes (technical, cost, strategic, past performance, compliance). Extracts winning practices from wins. Updates institutional weakness profile. |
| **orchestrator** | All | Dispatches specialist agents based on proposal state and user commands. Enforces human checkpoints at every wave exit. Surfaces deadline warnings. Never writes proposal content — coordinates only. |
| **continue** | All | Read-only state detector. Checks setup status, proposal state, and corpus to determine where you left off. Suggests the exact command to run next. |
| **feedback-collector** | Any | Guides a 3-step interactive feedback flow (type → optional quality ratings → optional free text), calls the feedback CLI, and confirms the saved feedback ID and file path. |

## Project Structure

```
my-proposal-project/
  .sbir/
    proposal-state.json          # Lifecycle state (wave, status, decisions)
    corpus/                      # Indexed past proposals, debriefs, boilerplate
  artifacts/
    wave-0-intelligence/         # Topic digest, go-no-go, approach brief
    wave-1-strategy/             # Compliance matrix, TPOC Q&A, strategy brief
    wave-2-research/             # Technical landscape, market research, TRL
    wave-3-outline/              # Discrimination table, outline, figure plan
    wave-4-drafts/               # Drafted sections + review records
    wave-5-visuals/              # Figure specs + generated figures
    wave-6-format/               # Formatted volumes + compliance check
    wave-7-review/               # Scorecard, red team, sign-off
    wave-8-submission/           # Portal package + immutable archive
    wave-9-learning/             # Debrief analysis + lessons learned
  pdcs/                          # Proposal Design Criteria per section

~/.sbir/
  company-profile.json           # Global company profile (shared across all proposals)
  partners/                      # Research institution partner profiles (one JSON per partner)
    cu-boulder.json              # Partner profile: capabilities, personnel, facilities, STTR eligibility
    swri.json
  quality-preferences.json       # Writing style preferences (tone, detail, evidence style)
  winning-patterns.json          # Proposal ratings and winning practices by agency
  writing-quality-profile.json   # Evaluator feedback patterns by agency and section
```

## Command Reference

| Command | Wave | Purpose |
|---------|------|---------|
| `/sbir:setup` | Pre | Guided first-time setup (profile, corpus, API key, validation) |
| `/sbir:proposal profile setup` | Pre | Create company profile (standalone) |
| `/sbir:proposal profile update` | Pre | Update company profile |
| `/sbir:proposal partner-setup` | Pre | Create or update a research institution partner profile |
| `/sbir:proposal partner-set <slug>` | 0+ | Designate a partner for the active proposal |
| `/sbir:proposal partner-screen <name>` | Pre | Screen a potential partner for readiness (5 signals) |
| `/sbir:proposal corpus add <dir>` | Pre | Ingest past proposals and documents (standalone) |
| `/sbir:proposal quality discover` | Pre | Build writing quality intelligence from past proposals |
| `/sbir:proposal quality update` | Pre | Update quality artifacts from new debrief data |
| `/sbir:proposal quality status` | Pre | Show quality intelligence status |
| `/sbir:solicitation find` | 0 | Search and rank open topics by fit |
| `/sbir:proposal new <topic-or-file>` | 0 | Start proposal with Go/No-Go checkpoint |
| `/sbir:proposal shape` | 0 | Generate candidate technical approaches |
| `/sbir:continue` | Any | Detect where you left off and suggest next action |
| `/sbir:proposal status` | Any | Show current wave, progress, next actions |
| `/sbir:proposal check` | 1+ | View compliance matrix coverage |
| `/sbir:proposal compliance add` | 1+ | Add missed compliance item |
| `/sbir:proposal tpoc questions` | 1 | Generate TPOC call questions |
| `/sbir:proposal tpoc ingest <file>` | 1 | Parse TPOC call notes |
| `/sbir:proposal wave strategy` | 1 | Generate and approve strategy brief |
| `/sbir:proposal draft <section>` | 4 | Draft a proposal section |
| `/sbir:proposal iterate <section>` | 4 | Submit section for reviewer iteration |
| `/sbir:proposal wave visuals` | 5 | Initialize figure generation |
| `/sbir:proposal draft figure <name>` | 5 | Generate a specific figure |
| `/sbir:proposal format` | 6 | Format and assemble volumes |
| `/sbir:proposal wave final-review` | 7 | Red team review and evaluator simulation |
| `/sbir:proposal submit prep` | 8 | Prepare submission package |
| `/sbir:proposal submit confirm` | 8 | Confirm submission, lock archive |
| `/sbir:proposal debrief <action>` | 9 | Outcome, debrief request, ingest, lessons |
| `/sbir:proposal config format <fmt>` | Any | Switch output format between `latex` and `docx` (warns about rework at Wave 3+) |
| `/sbir:proposal rigor [show\|set] <profile>` | Any | View or change the rigor profile (lean / standard / thorough / exhaustive) |
| `/sbir:proposal switch <topic-id>` | Any | Switch active proposal context in a multi-proposal workspace |
| `/sbir:developer-feedback` | Any | Submit bug reports, feature suggestions, or quality ratings with automatic context snapshot |

## Skills Reference

Skills are domain-knowledge files loaded on demand by agents. They are not invoked directly — agents pull them in when needed. The table below shows each skill, which agent owns it, and what it provides.

| Skill | Agent | What it provides |
|-------|-------|-----------------|
| `proposal-state-schema` | common | Schema reference for `proposal-state.json` — shared by all agents that read or write proposal state |
| `compliance-domain` | compliance-sheriff | Requirement types, extraction patterns, section mappings, compliance matrix format, and wave-specific behavior |
| `continue-detection` | continue | State detection priority, wave-to-command mapping, display patterns, and error handling |
| `multi-proposal-dashboard` | continue | Enumeration patterns, display templates, corruption handling, and deadline sorting for the multi-proposal dashboard |
| `corpus-domain-knowledge` | corpus-librarian | Document types, metadata schema, ingestion workflow, and search strategies for corpus management |
| `corpus-image-reuse` | corpus-librarian | Image search strategies, fitness assessment, caption adaptation heuristics, and compliance flagging |
| `proposal-archive-reader` | corpus-librarian | Archive directory layout, immutability constraints, portal-specific packaging, and corpus ingestion strategies |
| `win-loss-analyzer` | corpus-librarian | Pattern extraction from outcome-tagged proposals, weakness profiling, and agency-specific debrief handling |
| `debrief-domain-knowledge` | debrief-analyst | Loss categorization, debrief request letter format, lessons-learned generation, and feedback distribution |
| `visual-asset-generator` | formatter | Generation lifecycle, review checkpoint, cross-reference validation, method selection, and agency format requirements |
| `visual-style-intelligence` | formatter | Agency style database, style profile schema, and recommendation workflow for visual assets |
| `proposal-state-patterns` | orchestrator | State persistence patterns, atomic writes, status rendering, and session continuity |
| `rigor-resolution` | orchestrator | Rigor profile resolution chain, agent-role mapping, and rendering logic |
| `wave-agent-mapping` | orchestrator | Wave definitions, agent routing table, and checkpoint gates |
| `partner-domain` | partner-builder | Partner profile interview guidance, schema reference, STTR eligibility rules, and combined capability analysis |
| `profile-domain` | profile-builder | Company profile field-by-field fit scoring explanations, schema reference, validation rules, and interview guidance |
| `quality-discovery-domain` | quality-discoverer | Feedback taxonomy, auto-categorization keywords, confidence thresholds, and artifact schemas |
| `market-researcher` | researcher | TAM/SAM/SOM sizing methodology, competitor landscape analysis, and commercialization pathway mapping |
| `reviewer-persona-simulator` | reviewer | Government evaluator scoring rubrics, persona construction, red team review, and iteration loop with sign-off gate |
| `setup-domain` | setup-wizard | Prerequisites check commands, validation rules, TUI display patterns, and next-steps guidance |
| `approach-evaluation` | solution-shaper | Approach scoring rubrics, generation patterns (forward/reverse/prior-art), and commercialization quick-assessment |
| `budget-scaffolder` | strategist | Cost modeling by labor category, indirect rates, materials, and phase — scaffolds realistic SBIR budgets |
| `sbir-strategy-knowledge` | strategist | Teaming patterns, Phase III pathways, risk frameworks, competitive positioning, and required brief sections |
| `trl-assessor` | strategist | TRL evidence mapping, gap feasibility analysis, and red flag detection |
| `portal-packaging-rules` | submission-agent | Portal-specific packaging requirements for DSIP, Grants.gov, NSPIRES — file naming, size limits, upload procedures |
| `dsip-cli-usage` | topic-scout | How to call the DSIP topic CLI for fetching, enriching, scoring, and inspecting topics |
| `dsip-enrichment` | topic-scout | DSIP topic detail structure, Q&A format interpretation, and enrichment data for semantic scoring |
| `finder-batch-scoring` | topic-scout | Batch scoring workflow — five-dimension scoring of candidate topics with ranked results and disqualifiers |
| `fit-scoring-methodology` | topic-scout | Five-dimension fit scoring rubrics, composite scoring algorithm, and recommendation thresholds |
| `solicitation-intelligence` | topic-scout | Solicitation sources, document format parsing, and metadata extraction into TopicInfo schema |
| `tpoc-domain` | tpoc-analyst | TPOC question generation taxonomy, conversational sequencing strategy, and delta analysis methodology |
| `discrimination-table` | writer | Three-dimension competitive positioning framework that forms the narrative spine of the proposal |
| `elements-of-style` | writer | Strunk & White writing style adapted for SBIR prose — active voice, brevity, positive form, parallel construction |

## Image Generation Setup (Optional)

The plugin can generate concept figures using Google's Gemini API during Wave 5. Without it, the formatter produces structural diagrams (SVG, Mermaid, Graphviz) and writes specification briefs for figures you create manually.

1. Get an API key at [Google AI Studio](https://ai.google.dev/) (free tier: 500 images/day)
2. Add to your shell profile:
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```
3. Restart your terminal. The formatter agent detects the key automatically during Wave 5.

## License

MIT
