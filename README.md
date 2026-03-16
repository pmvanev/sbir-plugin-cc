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

## Getting Started (First Time)

Before writing any proposals, you need to set up two things: your **company profile** and your **corpus** of past work.

### Step 1: Gather Your Documents

Collect these before running the plugin:

| Document | Purpose | Required? |
|----------|---------|-----------|
| SAM.gov registration (CAGE code, UEI) | Federal contract eligibility | Yes |
| Capability statement or corporate brochure | Extract technical keywords, personnel, capabilities | Recommended |
| Past proposals (PDF/Word) | Corpus — informs fit scoring, strategy, and drafting | Recommended |
| Past debriefs (PDF/Word) | Corpus — win/loss patterns, reviewer feedback | If available |
| TPOC call notes from prior proposals | Corpus — agency interaction patterns | If available |

Organize them in a directory you can point the plugin at:

```
~/sbir-corpus/
  proposals/
    AF241-087-phase-i.pdf        # Past proposal (winning)
    N243-051-phase-i.pdf         # Past proposal (losing)
  debriefs/
    AF241-087-debrief.pdf        # Agency feedback
    N243-051-debrief.pdf
  company/
    capability-statement.pdf     # Marketing/capability docs
    sam-gov-registration.pdf     # SAM.gov entity page
```

The exact directory structure doesn't matter — the plugin indexes by content hash, not file path. But organizing by type helps you keep track of what you've ingested.

### Step 2: Build Your Company Profile

```bash
cd my-proposal-project
/sbir:proposal profile setup
```

The profile builder agent will walk you through one of three modes:

- **Documents** — paste or point to your capability statement and SAM.gov data; the agent extracts structured fields
- **Interview** — guided Q&A covering each profile section
- **Both** — extract from documents first, then fill gaps via interview

What gets captured:

| Field | Example | Impact on Fit Scoring |
|-------|---------|----------------------|
| Technical capabilities | "directed energy", "RF engineering", "ML" | Subject matter expertise (35% weight) |
| Key personnel | "Dr. Chen \| PI \| fiber laser technology" | Team alignment with topic requirements |
| SAM.gov (CAGE, UEI) | CAGE: 1AB2C | Required — missing CAGE = auto NO-GO |
| Socioeconomic certs | 8(a), HUBZone, WOSB, SDVOSB | Enables set-aside topics |
| Security clearance | Secret, Top Secret, None | Gates classified topics |
| ITAR status | Yes/No | Gates export-controlled topics |
| Past performance | "Air Force \| Fiber Lasers \| WIN" | Past performance relevance (25% weight) |
| Research partners | "MIT Lincoln Lab" | STTR eligibility (10% weight) |

The profile saves to `~/.sbir/company-profile.json` — a **global** file shared across all proposals. You create it once and update it as your company evolves.

```bash
# Later, when you hire someone or win an award:
/sbir:proposal profile update
```

### Step 3: Ingest Your Corpus

```bash
/sbir:proposal corpus add ~/sbir-corpus/
```

The corpus librarian indexes your documents by content hash (SHA-256) for deduplication. Supported formats: `.pdf`, `.docx`, `.doc`, `.txt`, `.md`.

The corpus is stored in `.sbir/corpus/` and persists across proposals in the same project directory. Every proposal you complete feeds back into the corpus — debriefs, strategies, and lessons learned accumulate over time.

### Step 4: Find Solicitations

```bash
# Search all open topics, ranked by company fit
/sbir:solicitation find

# Filter by agency or phase
/sbir:solicitation find --agency "Air Force" --phase I

# Search a specific solicitation cycle
/sbir:solicitation find --solicitation "DOD_SBIR_2026_P1_C3"
```

The topic-scout agent queries public SBIR portals (DSIP, Grants.gov, NSPIRES), scores every open topic against your company profile across five dimensions, and returns a ranked shortlist:

```
Rank | Topic ID    | Agency    | Title                             | Score | Rec      | Deadline
   1 | AF263-042   | Air Force | Compact Directed Energy for C-UAS | 0.84  | GO       | 2026-05-15
   2 | N241-095    | Navy      | Underwater Navigation Systems     | 0.67  | EVALUATE | 2026-06-02
   3 | AF263-099   | Air Force | Classified Sensor Fusion          | 0.00  | NO-GO    | 2026-05-15

Disqualified: AF263-099 — requires TS clearance (profile: Secret)
```

### Step 5: Start a Proposal

Select a topic from the ranked list, or provide a solicitation file directly:

```bash
# From the ranked results
/sbir:proposal new AF263-042

# Or from a PDF you already have
/sbir:proposal new ./solicitations/AF263-042.pdf
```

The orchestrator parses the solicitation, searches your corpus for related past work, scores company fit, and presents a **Go/No-Go checkpoint**. If you confirm Go, the plugin creates `.sbir/proposal-state.json` and unlocks Wave 1.

## Returning Users (Second+ Proposal)

If you already have a company profile and corpus from a previous proposal:

```bash
cd my-new-proposal-project

# Your profile at ~/.sbir/company-profile.json carries over automatically.
# Your corpus carries over if you're in the same project directory,
# or you can re-ingest:
/sbir:proposal corpus add ~/sbir-corpus/

# Search for new topics — your corpus now includes past proposal outcomes
/sbir:solicitation find --agency "Navy" --phase I

# Start the new proposal
/sbir:proposal new N261-095

# Check where you are at any time
/sbir:proposal status
```

Each completed proposal enriches the corpus. Fit scoring improves with more past performance data, the writer pulls better exemplars from winning sections, and the reviewer cross-references debrief patterns.

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
| `/sbir:proposal profile setup` | Pre | Create company profile |
| `/sbir:proposal profile update` | Pre | Update company profile |
| `/sbir:proposal corpus add <dir>` | Pre | Ingest past proposals and documents |
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
