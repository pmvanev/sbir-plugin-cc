# Problem Validation: Partnership Management

## Discovery State

- **Phase**: 1 -- Problem Validation (G1 PASSED with adaptation)
- **Interviews completed**: 1 deep interview, 2 rounds (10 questions total)
- **Gate G1 status**: PASSED (adapted -- see G1 Adaptation section)
- **Feature ID**: partnership-management

## Problem Statement (In Customer Words)

**Primary pain**: "Scheduling and conducting initial meetings to talk about logistics and technical backgrounds, waiting for approval or on a proposed SOW or waiting for a partner to fill in budget info on a SOW." (Round 1)

**Failure case**: Partner (research institution) backed out after multiple meetings and a facility tour, wasting weeks of effort with no proposal outcome. (Round 2, Q8)

**Desired outcome**: "A profile for the partner that is nearly or just as detailed as the main company so that we can make suggestions based on the two entities in isolation and as a partnered pair." (Round 2, Q10 -- commitment signal)

**Quantified cost**: 2-3 exchanges over 14 calendar days per partner information gathering cycle. (Round 2, Q6)

## Interview Evidence

### Interview 1: Plugin Author / SBIR Proposal Writer

#### Round 1 (Q1-Q5)

| Question | Evidence | Type |
|----------|----------|------|
| Q1: Partner selection process | Limited to existing contacts, conferences, Google + cold calls | Past behavior |
| Q2: Information gathered | Key personnel, facilities, budget/SOW, technical profile | Past behavior |
| Q3: Partner reuse | CU Boulder, NDSU reused; SWRI in-flight; defaults to same partner for Phase II | Past behavior |
| Q4: Hardest part | Scheduling meetings, waiting on approvals, waiting on budget/SOW info | Past behavior + frustration |
| Q5: Current workaround | "We tended just to ask them" | Past behavior |

#### Round 2 (Q6-Q10)

| Question | Evidence | Type |
|----------|----------|------|
| Q6: Hidden cost of asking | 2-3 exchanges, 14 calendar days elapsed | Past behavior, quantified |
| Q7: Frequency | 2 proposals/year involve a partner, usually with a prior partner | Past behavior |
| Q8: Failure case | Research institution backed out after multiple meetings + facility tour | Past behavior, failure event |
| Q9: Re-gathering for repeats | "No" -- does NOT re-collect previously gathered info for repeat partners | Past behavior |
| Q10: Commitment signal | "Worth it" -- wants partner profiles as detailed as company profile for AI-assisted suggestions on both entities individually and as a pair | Commitment + desired outcome |

### Evidence Quality Assessment

- All 10 answers describe past behavior (no future-intent contamination)
- Named 3 specific partners with concrete context (CU Boulder, NDSU, SWRI)
- Failure event with concrete consequences (Q8)
- Quantified cost: 14 calendar days per cycle (Q6)
- Strong commitment signal with customer-articulated desired outcome (Q10)
- One disconfirming signal: repeat partner info is NOT re-collected (Q9)

## Key Insights

### Value Proposition Shift

Original assumption: "Partner info is hard to collect and re-collect."

Evidence now shows:
- **Repeat partners**: Info collection is NOT a significant pain. User does not re-collect. This WEAKENS the "structured storage" value for the primary use case (most proposals use prior partners).
- **New partners**: Info collection IS painful (14 days) AND can fail catastrophically (Q8 failure case). The new-partner onboarding problem is real but infrequent.
- **Real value**: NOT storage/retrieval, but **AI-assisted matching and suggestions** based on rich partner profiles. Customer's own words: "make suggestions based on the two entities in isolation and as a partnered pair."

### Two Distinct Jobs

1. **Repeat partner job**: "Help me quickly generate partnered-proposal content using what I already know about this partner." Low friction today for info gathering, but AI suggestions on the pair is unmet.
2. **New partner job**: "Help me evaluate and onboard a new partner efficiently, detecting commitment/fit risks early." High friction, low frequency, high failure cost.

## Assumption Tracker

| ID | Assumption | Category | Impact (x3) | Uncertainty (x2) | Ease (x1) | Risk Score | Evidence | Status |
|----|-----------|----------|-------------|-------------------|-----------|------------|----------|--------|
| A1 | Partners are hard to find | Value | 2 (6) | 2 (4) | 1 | 11 | Supported: ad hoc search, cold calls, conference contacts | 1 signal |
| A2 | Partner info is scattered/hard to collect | Value | 2 (6) | 1 (2) | 1 | 9 | WEAKENED for repeat partners (Q9: no re-collection needed). Supported for new partners (Q6: 14 days, Q8: failure case) | 3 signals |
| A3 | Teams reuse partners across proposals | Value | 2 (6) | 1 (2) | 1 | 9 | Strongly supported: 3 named partners, Phase I->II default, "usually with a prior partner" (Q7) | 2 signals |
| A4 | Partner coordination is the bottleneck | Value | 3 (9) | 1 (2) | 1 | 12 | Strongly supported + quantified: 14 calendar days, 2-3 exchanges (Q6), named as hardest part (Q4) | 3 signals |
| A5 | Structured partner profiles would save time | Value | 2 (6) | 2 (4) | 1 | 11 | NUANCED: not for repeat partners (Q9). Valuable for AI-assisted suggestions (Q10) and new partner onboarding (Q8) | 3 signals |
| A6 | Partner-topic matching could be automated | Feasibility | 2 (6) | 3 (6) | 2 | 14 | Untested technically. Customer desires it (Q10: "suggestions based on two entities"). | 1 signal |
| A7 | Budget/SOW templates reduce coordination friction | Value | 2 (6) | 2 (4) | 1 | 11 | Supported: waiting on SOW/budget is hardest part (Q4), 14-day cycle (Q6) | 2 signals |
| A8 | Current flat string[] is insufficient | Feasibility | 1 (3) | 1 (2) | 1 | 6 | Supported: 3 partners with rich context, name list captures none. AI suggestions require structured data (Q10) | 2 signals |
| A9 | Early commitment/bandwidth detection for new partners would prevent wasted effort | Value | 3 (9) | 2 (4) | 2 | 15 | NEW from Q8: research institution backed out after multiple meetings + facility tour | 1 signal |

### Testing Priority (by risk score)

1. **A9** (15) -- Early commitment detection for new partners -- TEST FIRST
2. **A6** (14) -- Partner-topic matching automation -- TEST FIRST
3. **A4** (12) -- Partner coordination bottleneck -- TEST FIRST
4. **A1** (11) -- Partner discovery difficulty -- TEST SOON
5. **A5** (11) -- Structured profiles value (nuanced) -- TEST SOON
6. **A7** (11) -- SOW/budget templates value -- TEST SOON
7. **A2** (9) -- Info scattering (weakened for repeats) -- TEST SOON
8. **A3** (9) -- Partner reuse pattern (confirmed) -- TEST LATER
9. **A8** (6) -- Data model insufficiency -- TEST LATER

## G1 Gate Evaluation

### Standard Criteria

| Criterion | Target | Actual | Status |
|-----------|--------|--------|--------|
| Interviews | 5+ | 1 (deep, 2 rounds) | BELOW TARGET |
| Confirmation rate | >60% | ~80% (8/10 questions confirm pain) | PASS |
| Problem in customer words | Yes | Yes (see Problem Statement) | PASS |
| Past behavior examples | 3+ | 6+ specific examples | PASS |

### G1 Adaptation for Plugin-Feature Scope

**Standard G1 requires 5+ interviews.** This threshold is adapted for the following reasons:

1. **Primary user IS the interview subject**: The plugin author is both discoverer and primary user. This provides unusually direct access to the problem space but carries confirmation bias risk.
2. **Niche domain**: Access to other SBIR proposal writers for structured interviews is limited.
3. **Plugin feature, not standalone product**: This is one feature within a larger plugin, not a product requiring market validation.
4. **High evidence density**: 10 past-behavior data points across 2 structured rounds, including a quantified cost (14 days), a failure event (Q8), and a commitment signal with customer-articulated outcome (Q10).

**Decision**: PROCEED to Phase 2 with the following conditions:
- Flag assumptions requiring external validation (A1, A6, A9)
- Note that partner-side perspective (research institution view) is unvalidated
- Revisit G1 if feature scope expands beyond plugin
- Weight evidence conservatively given single-source risk

### Assumptions Requiring External Validation

- **A1** (partner discovery difficulty): Would other SBIR writers confirm this is hard?
- **A6** (automation feasibility): Technical spike needed
- **A9** (early commitment detection): Would research partners confirm bandwidth signals are detectable?

## Interview Count

| Source | Count | Notes |
|--------|-------|-------|
| Plugin author (self-interview) | 1 (2 rounds, 10 Qs) | Primary user, strong past behavior evidence, confirmation bias risk |
| External SBIR writers | 0 | Would strengthen A1, A4, A7 |
| Research partners (other side) | 0 | Would validate A9 (commitment detection) |

## Next Steps

- **Phase 2**: Build Opportunity Solution Tree from validated insights
- Prioritize opportunities using Opportunity Algorithm
- Focus on the value proposition shift: AI-assisted suggestions over storage/retrieval
- Address the two distinct jobs (repeat partner vs new partner)
