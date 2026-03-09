---
name: tpoc-domain
description: TPOC question generation taxonomy, conversational sequencing strategy, and delta analysis methodology for SBIR proposals
---

# TPOC Domain Knowledge

## Question Categories

Eight categories ordered by strategic value. Each question gets exactly one tag.

| Tag | Purpose | Example |
|-----|---------|---------|
| `scope-clarification` | Resolve what is / is not in scope | "Does Phase I include prototype hardware or simulation only?" |
| `approach-validation` | Test if your technical direction is welcome | "Would an ML-based approach be considered, or is the program looking for physics-based models?" |
| `competitive-intelligence` | Understand landscape without tipping your hand | "How many teams have expressed interest in this topic?" |
| `transition-pathway` | Clarify Phase III realism -- program of record, budget line | "Is there an existing program of record for Phase III transition?" |
| `budget-signal` | Probe flexibility and agency cost expectations | "Is there flexibility on the Phase I ceiling, or is $250K firm?" |
| `deliverable-clarification` | Confirm what completion looks like | "Does the final deliverable include a working demo or a feasibility report?" |
| `team-validation` | Confirm team structure and partners resonate | "Is the agency looking for academic partnerships on this topic?" |
| `incumbent-landscape` | Understand prior attempts and why they fell short | "Have previous Phase I efforts on this topic transitioned to Phase II?" |

## Question Input Sources

Questions draw from multiple inputs when available:

- Compliance matrix (required) -- ambiguities and gaps drive priority 1 and 2 questions
- Raw solicitation text (required) -- the baseline for all questions
- Company capability profile (`~/.sbir/company-profile.json`) -- tailor questions to company strengths
- Past proposals from corpus -- avoid asking questions already answered in prior cycles
- Research summaries -- inform strategic probes with technical context
- Prior debrief feedback -- surface recurring evaluator concerns as questions

## Question Sources

Questions derive from three sources, mapped to domain model categories:

| Source | Domain Category | Priority |
|--------|----------------|----------|
| Ambiguities flagged in compliance matrix | `QuestionCategory.AMBIGUITY` | 1 (highest) |
| Gaps between requirements and available info | `QuestionCategory.COMPLIANCE_GAP` | 2 |
| Strategic probes for competitive positioning | `QuestionCategory.STRATEGIC_PROBE` | 3 |

## Conversational Sequencing Strategy

TPOC calls are conversations, not interrogations. Order questions for natural flow:

1. **Opener** (1-2 questions): Relationship-building, broad scope questions. Show you read the solicitation. Categories: `scope-clarification`, `deliverable-clarification`.
2. **Core** (3-5 questions): Technical depth and approach validation. Categories: `approach-validation`, `scope-clarification`, `team-validation`.
3. **Strategic** (2-3 questions): Competitive landscape and transition. Categories: `competitive-intelligence`, `incumbent-landscape`, `transition-pathway`.
4. **Closer** (1-2 questions): Budget signals and follow-up opening. Categories: `budget-signal`, `deliverable-clarification`.

Within each block, order by priority (ambiguities first, then gaps, then probes).

## Editable Question Format

Output questions to markdown file the user edits before the call:

```markdown
# TPOC Questions -- {topic-number}

Generated: {date}
Status: DRAFT -- edit before your call

## Opener
1. [scope-clarification] {question text}
   _Rationale: {why this matters}_

## Core
3. [approach-validation] {question text}
   _Rationale: {why this matters}_

## Strategic
6. [competitive-intelligence] {question text}
   _Rationale: {why this matters}_

## Closer
8. [budget-signal] {question text}
   _Rationale: {why this matters}_

---
## Answer Capture Template
After your call, fill in answers below each question using:
Q1 Answer: {your notes}
Q2 Answer: {your notes}
```

## Delta Analysis Methodology

After ingesting call notes, compare TPOC answers against solicitation text:

1. **Match** answers to original questions using `Q{N} Answer:` pattern
2. **Mark unanswered** questions -- these remain open items
3. **Compare** each answer against the source solicitation requirement
4. **Flag deltas** where TPOC clarified, contradicted, or expanded on solicitation text
5. **Generate compliance updates** for items where TPOC provided new information

Delta types:
- **Clarification**: TPOC narrowed ambiguous requirement -- update compliance matrix
- **Expansion**: TPOC revealed unstated expectation -- add to compliance matrix
- **Contradiction**: TPOC guidance differs from solicitation text -- flag for strategy review
- **Confirmation**: TPOC confirmed existing interpretation -- mark as validated

## "Call Never Happened" Handling

TPOC calls are async events. The call may never happen. Handle gracefully:

- `questions_generated` is a valid terminal state -- do not block proposal progress
- If user advances to strategy without TPOC data, mark TPOC insights as "[pending]"
- If call happens later, re-run ingestion and propagate updates to downstream artifacts
- Never prompt repeatedly about an unscheduled call

## Propagation After Ingestion

Post-ingestion, TPOC insights propagate to downstream artifacts:

- **Compliance matrix**: Updated with clarifications, expansions, and contradiction flags
- **Discrimination table**: TPOC insights on competitive landscape and approach validation feed discriminator refinement
- **Strategy brief**: Transition pathway and budget signal answers update Phase III and cost sections
- **Q&A log**: Write-once artifact after ingestion (PES immutability) -- indexed for corpus retrieval in future proposals

Propagation is the responsibility of the tpoc-analyst (compliance matrix updates) and downstream agents (discrimination table, strategy brief) that read the delta analysis output.
