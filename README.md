# SBIR Proposal Plugin for Claude Code

A multi-agent Claude Code plugin that guides you through the full SBIR/STTR proposal lifecycle — from topic discovery through submission and post-award learning.

All interaction happens in the Claude Code CLI. State persists as local JSON files. No web UI, no server, no database.

## Prerequisites

- [Claude Code](https://claude.ai/claude-code) installed and authenticated
- Python 3.12+
- Git

## Install

```bash
claude plugin install github:pmvanev/sbir-plugin-cc
```

## Getting Started

After installing, run the setup wizard:

```bash
cd my-proposal-project
/sbir:setup
```

The wizard guides you through everything interactively:

1. **Prerequisites check** — verifies Python 3.12+, Git, and Claude Code with pass/fail indicators
2. **Company profile** — builds your profile via document extraction, guided interview, or both (delegates to the profile builder agent)
3. **Corpus ingestion** — helps you locate past proposals, debriefs, and capability documents, then ingests them
4. **API key setup** (optional) — walks you through configuring Gemini for concept figure generation in Wave 5
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

### Find Solicitations

```bash
/sbir:solicitation find                              # All open topics, ranked by fit
/sbir:solicitation find --agency "Air Force" --phase I  # Filter by agency/phase
```

The topic-scout scores every open topic against your company profile and returns a ranked shortlist with go/evaluate/no-go recommendations.

### Start a Proposal

```bash
/sbir:proposal new AF263-042                  # From ranked results
/sbir:proposal new ./solicitations/topic.pdf  # From a PDF you already have
```

## Returning Users (Second+ Proposal)

Your company profile at `~/.sbir/company-profile.json` carries over automatically. Run `/sbir:setup` in your new project directory — it detects your existing profile and offers to keep, update, or start fresh. Corpus from previous projects can be re-ingested or pointed at the same directory.

```bash
cd my-new-proposal-project
/sbir:setup                                    # Detects existing profile, sets up corpus
/sbir:solicitation find --agency "Navy"         # Search with enriched corpus
/sbir:proposal new N261-095                     # Start the new proposal
```

Each completed proposal enriches the corpus. Fit scoring improves with more past performance data, the writer pulls better exemplars, and the reviewer cross-references debrief patterns.

## The 10-Wave Lifecycle

Each wave produces specific artifacts and ends with a human checkpoint (approve / revise / skip). PES enforces wave ordering — you cannot skip ahead without completing prerequisites.

### Wave 0: Intelligence & Fit

Score topics against your company profile. Optionally generate candidate technical approaches.

```bash
/sbir:solicitation find                    # Search and rank open topics
/sbir:proposal new <topic-or-file>         # Start proposal, Go/No-Go checkpoint
/sbir:proposal shape                       # Generate 3-5 candidate approaches (optional)
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
```

## Command Reference

| Command | Wave | Purpose |
|---------|------|---------|
| `/sbir:setup` | Pre | Guided first-time setup (profile, corpus, API key, validation) |
| `/sbir:proposal profile setup` | Pre | Create company profile (standalone) |
| `/sbir:proposal profile update` | Pre | Update company profile |
| `/sbir:proposal corpus add <dir>` | Pre | Ingest past proposals and documents (standalone) |
| `/sbir:solicitation find` | 0 | Search and rank open topics by fit |
| `/sbir:proposal new <topic-or-file>` | 0 | Start proposal with Go/No-Go checkpoint |
| `/sbir:proposal shape` | 0 | Generate candidate technical approaches |
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
