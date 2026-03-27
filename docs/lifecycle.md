# Proposal Lifecycle

## Decision Tree

```
                        /sbir:setup
                            |
                    Prerequisites pass?
                   /                  \
                 NO                   YES
            Fix & rerun          Build profile
                                      |
                              /sbir:solicitation-find
                             (shows partnership scoring
                              when partner profiles exist)
                                      |
                              Pick a topic
                                      |
                            STTR topic? ──YES──> /sbir:proposal-partner-setup
                              |                  /sbir:proposal-partner-screen (optional)
                              NO                        |
                              |   <─────────────────────+
                         /sbir:proposal-new <topic>
                                      |
                               Go / No-Go?
                              /       |       \
                           NO-GO   DEFER     GO
                          archive   pause      |
                                     |    /sbir:proposal-shape (optional)
                                     |         |
                                     |    /sbir:proposal-check
                                     |    /sbir:proposal-tpoc-questions
                                     |         |
                                     |    [TPOC call happens]
                                     |         |
                                     |    /sbir:proposal-tpoc-ingest
                                     |         |
                                     |    /sbir:proposal-wave-strategy
                                     |         |
                                     |    Approve strategy? -----> Revise
                                     |         |
                                     |    [Wave 2: Research runs]
                                     |         |
                                     |    [Wave 3: Outline + discrimination table]
                                     |         |
                                     |    Approve outline? ------> Revise
                                     |         |
                                     |    /sbir:proposal-draft <section>
                                     |    /sbir:proposal-iterate <section>
                                     |         |  (max 2 revision cycles)
                                     |         |
                                     |    /sbir:proposal-wave-visuals
                                     |         |
                                     |    /sbir:proposal-format
                                     |         |
                                     |    /sbir:proposal-wave-final-review
                                     |         |
                                     |    Sign off? ----------------> Revise
                                     |         |
                                     |    /sbir:proposal-submit-prep
                                     |         |
                                     |    [You upload to portal]
                                     |         |
                                     |    /sbir:proposal-submit
                                     |         |
                                     |    [Archive locked — read-only]
                                     |         |
                                     |    /sbir:proposal-debrief outcome
                                     |    /sbir:proposal-debrief lessons
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
/sbir:proposal-partner-setup               # Create a research institution partner profile
/sbir:proposal-partner-screen "MIT"        # Screen a new potential partner for readiness
/sbir:solicitation-find                    # Search and rank open topics (partnership-aware)
/sbir:proposal-new <topic-or-file>         # Start proposal, Go/No-Go checkpoint
/sbir:proposal-partner-set cu-boulder      # Designate partner for active proposal
/sbir:proposal-shape                       # Generate 3-5 candidate approaches (optional)
/sbir:continue                             # Pick up where you left off (works in any wave)
```

**Artifacts:** `artifacts/wave-0-intelligence/` — topic digest, go-no-go brief, approach brief

### Wave 1: Requirements & Strategy

Extract compliance requirements, prepare for TPOC call, build strategy brief.

```bash
/sbir:proposal-check                       # View compliance matrix status
/sbir:proposal-compliance-add "<text>"     # Add a missed compliance item
/sbir:proposal-tpoc-questions              # Generate prioritized TPOC questions
/sbir:proposal-tpoc-ingest ./notes.txt     # Parse TPOC call notes (after the call)
/sbir:proposal-wave-strategy               # Generate strategy brief → approve/revise/skip
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
/sbir:proposal-draft technical-approach    # Draft a section
/sbir:proposal-draft sow
/sbir:proposal-draft key-personnel
/sbir:proposal-iterate technical-approach  # Submit for reviewer iteration
```

**Artifacts:** `artifacts/wave-4-drafts/sections/` — all proposal sections; `artifacts/wave-4-drafts/review-records/` — reviewer feedback per iteration

### Wave 5: Visual Assets

Generate figures, diagrams, and concept illustrations.

```bash
/sbir:proposal-wave-visuals                # Initialize figure specs + tool detection
/sbir:proposal-draft-figure "system-arch"  # Generate a specific figure
```

**Artifacts:** `artifacts/wave-5-visuals/` — figure inventory, cross-reference log, generated figures (SVG/PNG/Mermaid)

### Wave 6: Format & Assembly

Apply agency-specific formatting rules, assemble submission volumes.

```bash
/sbir:proposal-format                      # Format and assemble → approve/revise
```

**Artifacts:** `artifacts/wave-6-format/` — compliance final check, jargon audit, assembled volumes

### Wave 7: Final Review

Simulated government evaluator scoring and red team analysis.

```bash
/sbir:proposal-wave-final-review           # Run review → iterate/sign-off
```

**Artifacts:** `artifacts/wave-7-review/` — reviewer scorecard, red team findings, debrief cross-check, sign-off record

**Gate:** Sign-off required before submission.

### Wave 8: Submission

Package files for the submission portal. You perform the actual upload manually.

```bash
/sbir:proposal-submit-prep                 # Prepare package → approve/revise
/sbir:proposal-submit                      # Confirm submission, create immutable archive
```

**Artifacts:** `artifacts/wave-8-submission/` — pre-submission checklist, portal-ready package, immutable archive

After confirmation, the proposal archive becomes **read-only** (PES-enforced).

### Wave 9: Post-Submission

Record outcomes, request debriefs, extract lessons learned.

```bash
/sbir:proposal-debrief outcome WIN         # Record result
/sbir:proposal-debrief request-letter      # Draft debrief request (if LOSS)
/sbir:proposal-debrief ingest ./debrief.pdf  # Parse agency feedback
/sbir:proposal-debrief lessons             # Generate lessons learned
```

**Artifacts:** `artifacts/wave-9-learning/` — debrief request draft, structured debrief, critique section map, pattern analysis, lessons learned

Lessons and debrief data feed back into the corpus for future proposals.
