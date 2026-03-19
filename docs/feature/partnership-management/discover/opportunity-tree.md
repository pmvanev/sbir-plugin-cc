# Opportunity Solution Tree: Partnership Management

## Discovery State

- **Phase**: 2 -- Opportunity Mapping
- **Feature ID**: partnership-management
- **Gate G2 status**: IN PROGRESS

## Desired Outcome

**Minimize the time and risk of incorporating a partner into an SBIR/STTR proposal.**

(Customer words: "make suggestions based on the two entities in isolation and as a partnered pair")

## Job Map

| Step | Current State | Pain Level | Evidence |
|------|--------------|------------|----------|
| **Define** -- Determine that a partner is needed | Low friction -- user knows from topic requirements | Low | Q1: clear when STTR requires partner |
| **Locate** -- Find a suitable partner | Ad hoc: contacts, conferences, Google, cold calls | Medium | Q1: limited search methods |
| **Prepare** -- Gather partner information | 2-3 exchanges, 14 calendar days for new partners. No re-gathering for repeats | High (new) / Low (repeat) | Q6, Q9 |
| **Confirm** -- Verify partner commitment/fit | No structured process; discovered too late when partner backed out | High | Q8: failure case |
| **Execute** -- Write partnered proposal sections | Unknown -- not yet probed | Unknown | -- |
| **Monitor** -- Track partner deliverables (SOW, budget) | Waiting is the hardest part; 14 days elapsed | High | Q4, Q6 |
| **Modify** -- Adjust if partner issues arise | Partner backed out after extensive investment | Critical (rare) | Q8 |
| **Conclude** -- Submit proposal with partner | Unknown -- not yet probed | Unknown | -- |

## Opportunities

### O1: AI-Assisted Partner-Proposal Suggestions
**Score: 15** (Importance: 9, Satisfaction: 3) -- Score = 9 + max(0, 9-3) = 15

Generate AI suggestions for how company + partner capabilities combine to address a topic. Use rich profiles of both entities.

- Evidence: Q10 commitment signal -- "make suggestions based on the two entities in isolation and as a partnered pair"
- Job steps served: Execute, Conclude
- Assumptions tested: A5, A6, A8

### O2: Partner Coordination Acceleration
**Score: 14** (Importance: 9, Satisfaction: 4) -- Score = 9 + max(0, 9-4) = 14

Reduce the 14-day information exchange cycle through structured templates (SOW, budget, technical profile) that partners can fill asynchronously.

- Evidence: Q4 (hardest part is waiting), Q6 (14 calendar days, 2-3 exchanges)
- Job steps served: Prepare, Monitor
- Assumptions tested: A4, A7

### O3: New Partner Commitment/Fit Screening
**Score: 13** (Importance: 8, Satisfaction: 2) -- Score = 8 + max(0, 8-2) = 13

Detect partner bandwidth/commitment risks early before investing weeks in meetings and facility tours.

- Evidence: Q8 failure case -- research institution backed out after extensive engagement
- Job steps served: Confirm, Modify
- Assumptions tested: A9

### O4: Partner Profile Repository
**Score: 9** (Importance: 7, Satisfaction: 5) -- Score = 7 + max(0, 7-5) = 9

Store structured partner data (personnel, facilities, capabilities, past proposals) for reuse.

- Evidence: Q2 (info types), Q3 (3 reused partners). WEAKENED by Q9 (no re-gathering needed for repeats)
- Job steps served: Locate, Prepare
- Assumptions tested: A2, A3, A8
- Note: Value is primarily as a prerequisite for O1 (AI suggestions need structured data), not standalone

### O5: Partner Discovery/Matching
**Score: 8** (Importance: 6, Satisfaction: 3) -- Score = 6 + max(0, 6-3) = 8

Help find new partners matched to specific topic requirements.

- Evidence: Q1 (ad hoc search), Q7 (2/year, usually prior partners)
- Job steps served: Define, Locate
- Assumptions tested: A1, A6
- Note: Low frequency (2/year, usually repeats) limits value. May be more valuable for teams with less established networks.

## Opportunity Ranking

| Rank | ID | Opportunity | Score | Action |
|------|-----|------------|-------|--------|
| 1 | O1 | AI-assisted partner-proposal suggestions | 15 | **Pursue** |
| 2 | O2 | Partner coordination acceleration | 14 | **Pursue** |
| 3 | O3 | New partner commitment screening | 13 | **Pursue** |
| 4 | O4 | Partner profile repository | 9 | Evaluate (enabler for O1) |
| 5 | O5 | Partner discovery/matching | 8 | Evaluate (low frequency) |

**Top 3 selected**: O1, O2, O3 (all score >8)

## Solution Ideas (Initial -- Phase 3 will test)

### For O1: AI-Assisted Partner-Proposal Suggestions

- **S1a**: Rich partner profile schema (mirroring company profile) that the plugin's AI agents can reference when generating proposal content
- **S1b**: "Partnership brief" generator that analyzes both profiles against a topic and produces a capabilities-complementarity summary
- **S1c**: Automated work-split suggestions (which entity covers which topic requirement) based on profile matching

### For O2: Partner Coordination Acceleration

- **S2a**: Pre-structured SOW/budget template that the plugin generates from the partner profile + topic requirements
- **S2b**: Partner onboarding checklist with status tracking (what info is still needed)
- **S2c**: Async information request -- generate a structured questionnaire the partner can complete independently

### For O3: New Partner Commitment/Fit Screening

- **S3a**: Partner readiness checklist (bandwidth, timeline alignment, STTR eligibility, complementary capabilities)
- **S3b**: Lightweight "letter of intent" template that surfaces commitment early before heavy investment
- **S3c**: Fit scoring based on topic requirements vs partner capabilities

## G2 Gate Evaluation

| Criterion | Target | Actual | Status |
|-----------|--------|--------|--------|
| Opportunities identified | 5+ distinct | 5 | PASS |
| Top scores | >8 (max 20) | 15, 14, 13 | PASS |
| Job step coverage | 80%+ | 6/8 steps covered (75%) | MARGINAL |
| Team alignment | Confirmed | Single user -- inherent | PASS (adapted) |

### Coverage Gap

Job steps **Execute** and **Conclude** are only partially addressed by O1. We did not probe the actual proposal-writing experience with a partner. This is acceptable for now since O1 targets exactly this gap, and Phase 3 testing will validate.

**G2 Decision**: PROCEED to Phase 3 for top 3 opportunities.
