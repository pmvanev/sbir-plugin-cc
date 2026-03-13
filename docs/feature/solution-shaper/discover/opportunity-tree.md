# Opportunity Solution Tree: Solution Shaper

## Discovery Context

| Field | Value |
|-------|-------|
| Feature | solution-shaper |
| Date | 2026-03-13 |
| Phase | 2 -- Opportunity Mapping |
| User | Phil (solo SBIR proposal writer, small defense tech company) |

---

## Desired Outcome

**Minimize the time and uncertainty between "GO on this topic" and "here is what we should propose and why."**

Currently this takes an unstructured amount of time (hours to days of mental noodling) with no audit trail. The desired state is a structured, evidence-backed process that produces a defensible approach selection in under an hour.

---

## Job Map

| Job Step | Goal | Current State | Desired Outcome |
|----------|------|---------------|-----------------|
| **Define** | Understand what the solicitation actually needs | User re-reads topic description from Wave 0 | Minimize time to extract solicitation requirements, objectives, and evaluation criteria into actionable form |
| **Locate** | Identify candidate technical approaches | User relies on personal expertise and memory | Minimize effort to enumerate viable approaches given the problem space |
| **Prepare** | Evaluate approaches against company capabilities | No structured evaluation -- gut feel | Minimize likelihood of selecting an approach that does not leverage company strengths |
| **Confirm** | Score and compare approaches systematically | No comparison framework | Minimize uncertainty about which approach is strongest |
| **Execute** | Converge on a recommended approach with rationale | Implicit decision, no documentation | Minimize time from "approaches identified" to "approach selected with evidence" |
| **Monitor** | Validate approach against commercialization potential | Deferred to Wave 2 (too late to change approach) | Minimize risk of selecting an approach with weak Phase III pathway |
| **Modify** | Adjust if TPOC feedback or research changes the picture | Currently happens ad hoc during Wave 1-2 | Minimize effort to revise approach selection when new information arrives |
| **Conclude** | Hand off selected approach to strategy (Wave 1) | Approach enters Wave 1 implicitly | Minimize information loss between approach selection and strategy brief generation |

---

## Opportunity Scoring

Scoring method: Importance (1-10) + Max(0, Importance - Satisfaction). Max score = 20.
Importance and Satisfaction estimated from user context and codebase analysis.

| # | Opportunity | Imp | Sat | Score | Action |
|---|------------|-----|-----|-------|--------|
| O1 | Deep-read solicitation into structured requirements/objectives/criteria | 9 | 5 | 13 | Pursue |
| O2 | Generate candidate technical approaches from solicitation + company capabilities | 10 | 2 | 18 | Pursue |
| O3 | Score approaches against company-specific fit (personnel, IP, past performance) | 10 | 1 | 19 | Pursue |
| O4 | Evaluate commercialization potential per approach (TAM/SAM/SOM, dual-use, Phase III) | 8 | 2 | 14 | Pursue |
| O5 | Build discrimination view: our approach vs. alternatives vs. incumbents | 8 | 3 | 13 | Pursue |
| O6 | Converge on recommended approach with documented rationale | 9 | 1 | 17 | Pursue |
| O7 | Validate fit: approach addresses solicitation problem AND broader generalized problem | 7 | 2 | 12 | Pursue |
| O8 | Provide structured handoff artifact for Wave 1 strategist | 7 | 3 | 11 | Pursue |

All opportunities score >8. Top 3 by score: O3 (19), O2 (18), O6 (17).

---

## Opportunity Solution Tree

```
Desired Outcome: Minimize time and uncertainty between "GO on topic" and "approach selected with evidence"
  |
  +-- O3: Score approaches against company-specific fit (19)
  |     +-- S3a: Approach-level fit matrix (approach x dimension scoring grid)
  |     +-- S3b: Key personnel alignment check (map personnel expertise to approach needs)
  |     +-- S3c: Past performance relevance scoring per approach
  |
  +-- O2: Generate candidate technical approaches (18)
  |     +-- S2a: LLM-powered approach brainstorm from solicitation + capabilities
  |     +-- S2b: Prior art scan to identify known approaches in the problem space
  |     +-- S2c: Company capability reverse-mapping (what approaches do our strengths enable?)
  |
  +-- O6: Converge on recommended approach with rationale (17)
  |     +-- S6a: Weighted decision matrix with configurable criteria
  |     +-- S6b: Narrative recommendation artifact ("here is what to propose and why")
  |     +-- S6c: Go/Pivot/Kill checkpoint for approach selection
  |
  +-- O4: Evaluate commercialization per approach (14)
  |     +-- S4a: Quick Phase III pathway assessment per approach
  |     +-- S4b: Dual-use screening (does this approach have commercial applications?)
  |     +-- S4c: Market size delta analysis (which approach opens bigger markets?)
  |
  +-- O1: Deep-read solicitation into structured form (13)
  |     +-- S1a: Solicitation deep-read artifact (requirements, objectives, eval criteria, constraints)
  |     +-- S1b: Reuse/extend TopicInfo parsing from topic-scout
  |
  +-- O5: Build discrimination view (13)
  |     +-- S5a: Lightweight pre-Wave-3 discrimination sketch (not full table)
  |     +-- S5b: Competitive positioning per approach candidate
  |
  +-- O7: Validate dual fit (12)
  |     +-- S7a: Solicitation-specific fit check (does approach solve THEIR stated problem?)
  |     +-- S7b: Generalized problem fit check (does approach solve the BROADER problem?)
  |
  +-- O8: Structured handoff to Wave 1 (11)
  |     +-- S8a: Approach brief artifact consumed by strategist agent
  |     +-- S8b: Bridge state between solution-shaper and proposal-state.json
```

---

## Top Opportunities Deep Dive

### O3: Score Approaches Against Company-Specific Fit (Score: 19)

**Why it matters**: The topic-scout scores company-level fit, but two approaches to the same topic can have completely different company fit. A fiber laser approach might leverage 3 key personnel; a solid-state approach might leverage 1. Past performance may be strong for one approach and nonexistent for another.

**Solution direction**: An approach-level fit matrix that scores each candidate approach across:
- Personnel alignment (which key personnel have relevant expertise?)
- Past performance relevance (do we have past work in this approach area?)
- IP/capability match (do we have relevant prototypes, algorithms, facilities?)
- TRL starting point (where are we with this approach vs. that one?)

**Existing assets to leverage**: `fit-scoring-methodology` skill dimensions, `company-profile.json` schema, `topic_scoring.py` scoring logic.

### O2: Generate Candidate Technical Approaches (Score: 18)

**Why it matters**: The hardest part of "what should we propose" is enumerating the option space. An experienced proposer might think of 2-3 approaches; a systematic process should surface 4-6 including non-obvious combinations.

**Solution direction**: Multi-source approach generation:
1. LLM reasoning from solicitation description + company capabilities
2. Prior art awareness (what approaches have others tried?)
3. Company capability reverse-mapping (given our strengths, what approaches are natural?)

**Existing assets to leverage**: `sbir-researcher` already does technical landscape and prior art (but in Wave 2, too late). Bring a lightweight version forward.

### O6: Converge on Recommended Approach (Score: 17)

**Why it matters**: Without explicit convergence, the approach decision remains implicit. The user needs an artifact that says "propose X because of Y" -- both for their own confidence and as input to Wave 1.

**Solution direction**: A structured recommendation artifact that:
- Names the selected approach
- Shows the scoring rationale (why this one, not the others)
- Notes risks and open questions to validate in Wave 1-2
- Provides a checkpoint for the user to approve/revise

**Existing assets to leverage**: Checkpoint pattern from all existing agents. Strategy brief structure as format precedent.

---

## Gate G2 Evaluation

| Criterion | Target | Actual | Status |
|-----------|--------|--------|--------|
| Opportunities identified | 5+ distinct | 8 | PASS |
| Top scores | >8 (max 20) | 19, 18, 17 | PASS |
| Job step coverage | 80%+ | 8/8 job steps mapped to opportunities | PASS |
| Team alignment | Confirmed | Single user + codebase analysis aligned | PASS |

**G2 Decision: PROCEED to Phase 3 -- Solution Testing**

Eight distinct opportunities identified, all scoring above 8. The top three (approach-level scoring, approach generation, convergence with rationale) form the core of the solution. The remaining five (commercialization evaluation, solicitation deep-read, discrimination sketch, dual fit validation, Wave 1 handoff) are supporting capabilities.
