# Problem Validation: Solution Shaper

## Discovery Context

| Field | Value |
|-------|-------|
| Feature | solution-shaper |
| Date | 2026-03-13 |
| Phase | 1 -- Problem Validation |
| User | Phil (solo SBIR proposal writer, small defense tech company) |
| Method | Codebase analysis + user-described workflow gap |

---

## The Problem Statement

**In the user's words**: "ok, now we have the company profile and a good overview of all available solicitations and we have picked a single solicitation we want to write a proposal on. Now help me figure out what I should actually propose"

**The gap**: After the user picks a solicitation to pursue (Wave 0 Go decision) but before proposal writing begins (Wave 1+), there is no structured process for figuring out WHAT to propose. The user jumps from "this topic fits our company" directly to "write a strategy brief" without first exploring and evaluating what technical approach to take.

---

## Evidence: Past Behavior Analysis

### Evidence 1: Current Workflow Has a Missing Step

The existing wave structure shows a clear gap:

- **Wave 0 (topic-scout)**: Scores company FIT against solicitation -- "should we pursue this?" Answer: GO.
- **Wave 1 (strategist)**: Generates strategy brief with six sections including technical_approach, TRL, budget, risks. But the strategy brief ASSUMES a technical approach already exists -- it reads from compliance matrix and generates strategy around it.
- **Wave 2 (researcher)**: Conducts technical landscape, patent scanning, market research. But this happens AFTER strategy, and the researcher's Phase 1 requires reading the strategy brief first.

The question "what should we actually propose?" is never explicitly answered. The strategist frames whatever approach the user brings. The researcher validates after the fact. Nobody generates and evaluates candidate approaches.

**Signal strength**: STRONG -- structural gap visible in agent dependencies and workflow sequencing.

### Evidence 2: Existing Agents Assume the Answer

Three agents touch the technical approach but none own the question of WHICH approach:

1. **sbir-strategist**: "Summarize innovation, map to solicitation needs" -- synthesizes an approach the user already has, does not generate candidates.
2. **sbir-researcher**: "Survey current technical approaches in the domain" -- catalogs what exists but does not score approaches against company fit.
3. **discrimination-table skill**: Compares "Our Approach" vs. "Prior Art" -- assumes "Our Approach" is already decided.

The approach decision is currently implicit: the user arrives at Wave 1 already knowing what they want to propose (or guessing). For an experienced proposer this works. For the workflow to be systematically useful, the approach selection needs to be explicit and evidence-backed.

**Signal strength**: STRONG -- three agents reference "the approach" without any agent owning its generation.

### Evidence 3: Fit Scoring Stops at Company-Level

The topic-scout scores five dimensions of company fit against a solicitation. But "our company fits this topic" is different from "this specific technical approach fits this topic given our capabilities." The scoring gap:

- **What exists**: Company SME overlap (keyword matching), past performance relevance, certifications, eligibility
- **What is missing**: Approach-level scoring -- which of 3-5 candidate approaches best leverages OUR specific capabilities, personnel, IP, and past performance?

A company may have 70% keyword overlap with a directed energy topic but radically different fit depending on whether they propose a fiber laser, solid-state laser, or RF approach.

**Signal strength**: STRONG -- the fit-scoring-methodology skill explicitly stops at company-level scoring.

### Evidence 4: Discrimination Table Needs Upstream Input

The discrimination-table skill (Wave 3) is designed to compare "Our Approach" against competitors and prior art. Its construction process starts with "Read strategy brief (competitive positioning section)." But the discrimination table's value depends entirely on the approach selection being correct.

Currently the table answers "why our approach is better than alternatives" -- but nobody systematically asked "which of OUR possible approaches is strongest against this solicitation?"

**Signal strength**: MODERATE -- the discrimination table would be sharper with deliberate approach selection feeding it.

### Evidence 5: Commercialization Assessment Is Deferred to Wave 2

The researcher builds TAM/SAM/SOM and commercialization pathway in Wave 2. But commercialization potential should INFORM approach selection, not just validate it after the fact. Two approaches to the same problem may have wildly different Phase III pathways -- one might be dual-use with a $2B commercial market, the other purely military with a $50M niche.

**Signal strength**: MODERATE -- commercialization is currently a research output, not an approach selection input.

---

## Problem Confirmation Assessment

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Problem confirmed by past behavior | PASS | User explicitly described the gap; codebase confirms no agent owns approach selection |
| Problem articulated in user's words | PASS | "help me figure out what I should actually propose" |
| Frequency | PASS | Occurs every proposal -- every time a GO decision is made on a topic |
| Current workaround | PASS | User arrives at Wave 1 with an assumed approach; no structured evaluation |
| Emotional intensity | PASS | The user built an entire plugin to structure this workflow; the gap represents the highest-uncertainty decision point |

### Workaround Cost

The current workaround is that Phil mentally evaluates approaches based on experience and arrives at Wave 1 with a decision already made. This works when:
- The company has deep domain expertise in the topic area
- There is an obvious technical approach
- The user has written proposals on similar topics before

It fails when:
- The topic is adjacent to core expertise (the most common case for growth)
- Multiple viable approaches exist with different tradeoffs
- The user needs to assess whether commercialization potential differs by approach
- The user wants a systematic record of WHY this approach was chosen (useful for debrief)

---

## Assumption Tracker

| # | Assumption | Category | Risk Score | Priority |
|---|-----------|----------|------------|----------|
| A1 | The approach selection decision is currently implicit and would benefit from being explicit and structured | Value | 11 (I:3 U:2 E:1) | Test soon |
| A2 | Multiple candidate approaches typically exist for a given solicitation topic | Value | 10 (I:2 U:2 E:2) | Test soon |
| A3 | Company fit varies meaningfully across candidate approaches (not just at company level) | Value | 12 (I:3 U:2 E:1) | Test first |
| A4 | Commercialization potential should inform approach selection, not just validate it afterward | Value | 9 (I:2 U:2 E:1) | Test soon |
| A5 | The solution-shaper fits as a pre-Wave-1 step rather than being folded into existing waves | Feasibility | 10 (I:3 U:1 E:2) | Test soon |
| A6 | This can be implemented as markdown agents/skills/commands without new Python services | Feasibility | 7 (I:2 U:1 E:1) | Test later |
| A7 | The user will actually use structured approach evaluation vs. just jumping to Wave 1 | Value | 11 (I:3 U:2 E:1) | Test soon |

---

## Gate G1 Evaluation

| Criterion | Target | Actual | Status |
|-----------|--------|--------|--------|
| Interviews / evidence sources | 5+ | 5 (user statement + 4 codebase evidence points) | PASS |
| Problem confirmation rate | >60% | 100% (5/5 evidence points confirm the gap) | PASS |
| Problem in customer words | Yes | "help me figure out what I should actually propose" | PASS |
| Concrete examples | 3+ | 5 (strategy assumes approach, researcher validates after, fit scoring stops at company, discrimination table needs input, commercialization deferred) | PASS |

**G1 Decision: PROCEED to Phase 2 -- Opportunity Mapping**

The problem is real: there is a structural gap between "this topic fits our company" (Wave 0) and "here is our strategy for this approach" (Wave 1). No agent currently owns approach generation, evaluation, and selection. The user described this gap explicitly, and the codebase confirms it through agent dependency analysis.
