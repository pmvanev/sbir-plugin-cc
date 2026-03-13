# Quickstart: Write Your First SBIR Proposal

This guide walks through the full proposal lifecycle using the SBIR plugin. Each step maps to a wave (0-9) and uses a specific command.

## Before You Start

You need:
- Claude Code with this plugin installed
- A solicitation document (PDF or text) for the topic you want to pursue
- Your company information (personnel, past performance, certifications)

## Step 1: Set Up Your Company Profile (One-Time)

```
/sbir:company-profile setup
```

The profile builder interviews you about your company: capabilities, key personnel and their expertise, past performance (contracts, agencies, outcomes), certifications (SAM.gov, security clearances, socioeconomic status), and research institution partners.

Profile saves to `~/.sbir/company-profile.json` and is reused across proposals.

To update later: `/sbir:company-profile update`

## Step 2: Find Solicitations (Wave 0)

```
/sbir:solicitation find --agency "Air Force" --phase I
```

Searches the DSIP API for open topics, pre-filters by your company capabilities, and scores each topic across 5 dimensions: subject matter expertise, past performance, certifications, eligibility, STTR requirements.

Results display as a ranked table with GO / EVALUATE / NO-GO recommendations.

**Or, if you already have a solicitation document:**

```
/sbir:proposal new --file ./my-solicitation.pdf
```

Parses the solicitation, scores fit, and prompts for a Go/No-Go decision.

## Step 3: Select Your Technical Approach (Wave 0)

```
/sbir:proposal shape
```

After your Go decision, the solution shaper:
1. Deep-reads the full solicitation (not just the summary)
2. Generates 3-5 candidate technical approaches
3. Scores each against your company's personnel, past performance, TRL, solicitation fit, and commercialization potential
4. Recommends the best-fit approach with rationale

You approve, revise, or explore alternatives at the checkpoint.

Output: `./artifacts/wave-0-intelligence/approach-brief.md`

**Optional writing style:** Before drafting (Step 7), you can set a prose style in `.sbir/proposal-state.json`:
```json
"writing_style": "elements"
```
This loads Strunk & White prose guidance for the writer and reviewer. Leave unset for standard prose conventions.

## Step 4: Extract Compliance Requirements (Wave 1)

```
/sbir:proposal compliance check
```

The compliance sheriff extracts every requirement from the solicitation into a structured compliance matrix. This matrix drives everything downstream -- every section you draft traces back to a compliance item.

## Step 5: TPOC Call (Wave 1, Optional)

```
/sbir:proposal tpoc questions
```

Generates prioritized questions for the Technical Point of Contact call based on solicitation ambiguities and strategic probes.

After the call:
```
/sbir:proposal tpoc ingest
```

Feed your call notes back in. The system matches answers to questions and runs delta analysis.

## Step 6: Build Strategy Brief (Wave 1)

```
/sbir:proposal wave strategy
```

The strategist builds a 6-section strategy brief:
1. Technical approach (from your approach brief + compliance matrix)
2. TRL assessment (current level, target, gap analysis)
3. Teaming strategy (capability gaps, partnership needs)
4. Phase III pathway (commercialization, transition programs)
5. Budget strategy (cost allocation, rate structures)
6. Risk assessment (technical, schedule, cost, commercialization, team)

Checkpoint: approve, revise, or skip.

Output: `./artifacts/wave-1-strategy/strategy-brief.md`

## Step 7: Research (Wave 2)

The researcher agent is invoked by the orchestrator to:
- Conduct literature review for the selected approach
- Analyze the competitive landscape
- Validate TRL claims with published evidence
- Deep-dive on commercialization pathway

Output: `./artifacts/wave-2-research/`

## Step 8: Discrimination Table and Outline (Wave 3)

The writer builds a discrimination table -- what makes your proposal different from what competitors will submit -- across three dimensions: company vs. competitors, technical approach vs. prior art, and team discriminators.

Then builds a compliance-traced proposal outline with page budgets per section.

Output: `./artifacts/wave-3-outline/discrimination-table.md`, `./artifacts/wave-3-outline/proposal-outline.md`

## Step 9: Draft Sections (Wave 4)

```
/sbir:proposal draft technical-approach
/sbir:proposal draft sow
/sbir:proposal draft key-personnel
/sbir:proposal draft past-performance
/sbir:proposal draft commercialization
/sbir:proposal draft management
/sbir:proposal draft risks
/sbir:proposal draft facilities
```

Each section is:
- Compliance-traced to the matrix
- Page-budgeted per the outline
- Calibrated against corpus exemplars (if you've added past proposals)
- Checked for acronyms, cross-references, and jargon

After drafting, iterate with the reviewer:
```
/sbir:proposal iterate technical-approach
```

The reviewer simulates a government evaluator, scores against the solicitation criteria, and produces findings. The writer revises. Max 2 review cycles.

Output: `./artifacts/wave-4-drafts/sections/`

## Step 10: Visual Assets (Wave 5)

```
/sbir:proposal wave visuals
```

Generates figure specifications and creates visual assets (system architecture diagrams, project timelines, data flow diagrams) using available tools.

Output: `./artifacts/wave-5-visuals/`

## Step 11: Format and Assemble (Wave 6)

```
/sbir:proposal format
```

Formats the drafted proposal to solicitation specifications (page limits, margins, fonts) and assembles submission-ready volumes.

Output: `./artifacts/wave-6-formatted/`

## Step 12: Final Review (Wave 7)

```
/sbir:proposal wave final-review
```

Full simulated government evaluator review:
- Scores every evaluation criterion across all volumes
- Red team: 3-5 strongest objections a skeptical reviewer would raise
- Debrief cross-check: known weakness patterns from past proposals
- Jargon and cross-reference audit

Max 2 iteration rounds, then forced sign-off.

Output: `./artifacts/wave-7-review/`

## Step 13: Submit (Wave 8)

```
/sbir:proposal submit prep
```

Assembles the final submission package, verifies compliance, and prepares for portal upload.

```
/sbir:proposal submit
```

Human-confirmed submission with immutable archival.

## Step 14: Debrief (Wave 9, Post-Decision)

After you receive the agency decision:

```
/sbir:proposal debrief outcome win
/sbir:proposal debrief outcome loss
```

For losses, request and ingest the debrief:
```
/sbir:proposal debrief request
/sbir:proposal debrief ingest ./debrief-notes.txt
/sbir:proposal debrief lessons
```

Feeds lessons learned back into the system for future proposals.

## Key Files

| File | Purpose |
|------|---------|
| `~/.sbir/company-profile.json` | Your company profile (global, reused across proposals) |
| `.sbir/proposal-state.json` | Current proposal state (per-proposal, tracks progress) |
| `./artifacts/wave-N-name/` | Output artifacts per wave |
| `.sbir/compliance-matrix.json` | Extracted compliance requirements |

## Tips

- **Check status anytime:** `/sbir:proposal status` shows current wave, progress, and suggested next actions
- **Corpus helps quality:** Add past proposals with `/sbir:proposal corpus add ./past-proposals/` before starting. The writer calibrates tone and the reviewer checks debrief patterns.
- **TPOC is optional but valuable:** You can skip the TPOC step, but insights from the call significantly improve strategy and technical approach sections.
- **Writing style is optional:** Set `"writing_style": "elements"` in proposal state for Strunk & White prose guidance. Leave unset for standard conventions.
- **Page budgets matter:** The writer tracks word count against the outline's page allocations. Over-budget sections get flagged, not silently truncated.
