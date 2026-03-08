# Opportunity Solution Tree -- SBIR Proposal Writing Plugin

## Desired Outcome

Write winning SBIR/STTR proposals faster with less effort, using AI that engineers can trust.

## Opportunity Scoring

Formula: Score = Importance + Max(0, Importance - Satisfaction)
Importance: 1-10 | Satisfaction: 1-10 | Max score: 20

| # | Opportunity | Imp | Sat | Score | Rationale |
|---|---|---|---|---|---|
| O8 | Generate trustworthy technical narrative (not hallucinatory) | 9 | 2 | 16 | Highest importance AND lowest satisfaction; hardest to solve |
| O1 | Reduce time searching/gathering past documents and evidence | 9 | 3 | 15 | Named by multiple writers; built tool to partially solve |
| O2 | Ensure compliance without manual tracking | 9 | 4 | 14 | Top pain; manual checklists inadequate; disqualification risk |
| O4 | Understand real technical need behind vague solicitation language | 8 | 3 | 13 | TPOC calls help but limited; no tool solves this |
| O5 | Build "why us" and "why better" competitive positioning | 8 | 3 | 13 | Requires deep company knowledge; firms do not solve better |
| O6 | Reduce formatting and assembly time | 7 | 2 | 12 | Real pain, very low satisfaction, feasibility uncertain |
| O7 | Learn from win/loss patterns across cycles | 7 | 2 | 12 | Vague/no feedback; high value if solvable |
| O9 | Reduce total person-hours per proposal | 8 | 4 | 12 | Meta-outcome depending on other opportunities |
| O3 | Generate credible boilerplate from company corpus | 8 | 5 | 11 | AI boilerplate "works well"; partially satisfied |
| O10 | Scan and rank solicitations for fit | 7 | 6 | 8 | Already partially solved; Procura exists |

## Opportunity Solution Tree

```
Desired Outcome: Write winning SBIR proposals faster with less effort
|
+-- O8: Trustworthy technical narrative (16) *** [Phase C2]
|     +-- Human-in-loop drafting (AI proposes, human approves each claim)
|     +-- Claim verification against cited sources
|     +-- Confidence flagging -- AI marks uncertain statements
|     +-- PES enforcement on technical accuracy claims
|
+-- O1: Reduce document search time (15) *** [Phase C1 -- MVP]
|     +-- Corpus librarian with semantic search
|     +-- Auto-link past performance to solicitation requirements
|     +-- Boilerplate library with smart retrieval
|
+-- O2: Compliance without manual tracking (14) *** [Phase C1 -- MVP]
|     +-- Automated compliance matrix from solicitation parsing
|     +-- Live compliance tracking as sections are drafted
|     +-- Pre-submission compliance gate (PES-enforced)
|
+-- O4: Understand real technical need (13)
|     +-- TPOC question generation from gap analysis
|     +-- Solicitation ambiguity detection
|     +-- Prior award analysis on same topic
|
+-- O5: Competitive positioning arguments (13)
|     +-- Discrimination table builder from company profile
|     +-- Past performance matching engine
|     +-- Competitor landscape analysis
|
+-- O6: Formatting and assembly (12)
|     +-- Template-based document generation (Word/LaTeX)
|     +-- Pre-formatted section scaffolds
|     +-- Automated cross-reference management
|
+-- O7: Win/loss pattern learning (12)
|     +-- Debrief feedback parser and pattern tracker
|     +-- Proposal section scoring against historical outcomes
|
+-- O10: Solicitation scanning and ranking (8)
|     +-- Existing internal tool covers this partially
|     +-- Procura covers this commercially
```

## Top 3 Opportunities Selected

1. **O1 (Score 15)** -- Corpus search and document retrieval
2. **O2 (Score 14)** -- Automated compliance tracking
3. **O8 (Score 16)** -- Trustworthy technical narrative (deferred to Phase C2)

## Strategic Decision: Option C (Phased Delivery)

**Phase C1 (MVP):** Ship O1 + O2 -- corpus search and compliance tracking. These use AI capabilities that are proven reliable. Earn trust.

**Phase C2:** Layer in O8 -- guardrailed AI drafting with PES enforcement, confidence flagging, and human checkpoints. Address the trust problem after the tool has proven value.

**Phase C3 (Full Lifecycle):** Waves 5-9 -- formatting, final review, submission, post-submission learning.

## Job Map

| Step | Job Activity | Primary Opportunity | Phase |
|---|---|---|---|
| Define | Identify which solicitation to pursue | O10 | C1 (partial -- existing tool) |
| Locate | Gather past performance, research, solicitation details | O1 | C1 |
| Prepare | Understand real technical need; validate fit | O4 | C1 |
| Confirm | Validate company fit and competitive positioning | O5 | C2 |
| Execute | Draft all sections to spec | O8 | C2 |
| Monitor | Track compliance, page limits, cross-references | O2 | C1 |
| Modify | Iterate based on review feedback | O8 | C2 |
| Conclude | Format, assemble, submit | O6 | C3 |
| Learn | Understand win/loss patterns | O7 | C3 |

## Gate G2 Evaluation

| Criterion | Target | Result |
|---|---|---|
| Opportunities identified | 5+ distinct | PASS (10) |
| Top scores | >8 / max 20 | PASS (16, 15, 14) |
| Job step coverage | 80%+ | PASS (8/9 steps covered) |
| Team alignment | Stakeholder confirmed | PASS (Option C selected) |

**Gate G2: PASS -- Proceed to Solution Testing**
