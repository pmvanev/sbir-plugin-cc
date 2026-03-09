---
name: win-loss-analyzer
description: Domain knowledge for analyzing outcome-tagged proposals and debrief feedback -- pattern extraction, weakness profiling, and agency preference modeling
---

# Win/Loss Analyzer

## Outcome Tracking Schema

Track per proposal in `.sbir/proposal-state.json` or corpus metadata:

| Field | Type | Source |
|-------|------|--------|
| `proposal_id` | str | State-generated (e.g., `proposal-af243-001`) |
| `agency` | str | Extracted from solicitation (e.g., Air Force, Navy, DARPA) |
| `topic_number` | str | Solicitation topic ID |
| `phase` | str | I, II, or Direct-to-Phase-II |
| `outcome` | enum | WIN, LOSS, NO_DECISION, WITHDRAWN |
| `debrief_available` | bool | Whether debrief document has been ingested |
| `debrief_path` | str/null | Path to debrief document in corpus |
| `strengths` | list[str] | Extracted from debrief (if available) |
| `weaknesses` | list[str] | Extracted from debrief (if available) |
| `submitted_at` | ISO datetime | Submission date |
| `outcome_recorded_at` | ISO datetime | When outcome was recorded |

## Debrief Parsing

When a debrief document is ingested, extract structured data:

1. **Evaluator scores**: Numeric scores per evaluation criterion (if present)
2. **Strength comments**: Positive evaluator feedback, mapped to proposal sections
3. **Weakness comments**: Negative evaluator feedback, mapped to proposal sections
4. **Adjectival ratings**: Outstanding/Good/Acceptable/Marginal/Unacceptable per criterion
5. **Overall recommendation**: Award/No-award with rationale summary

Mapping to sections: Match each comment to the proposal section it references by looking for section names, topic keywords, or explicit section references in the evaluator text.

## Known Weakness Profile

The weakness profile is a living document built from debrief feedback across all proposals. It serves as an active checklist for the reviewer agent.

Structure:
```
weakness_profile:
  - category: "technical_approach"
    pattern: "Insufficient detail on TRL advancement methodology"
    frequency: 3  # seen in 3 separate debriefs
    agencies: ["Air Force", "Navy"]
    mitigation: "Include explicit TRL entry/exit criteria with milestones"
  - category: "past_performance"
    pattern: "Weak connection between cited past work and proposed effort"
    frequency: 2
    agencies: ["DARPA"]
    mitigation: "Map each past performance citation to a specific proposal task"
```

Update rules:
- Add new weakness when it appears in a debrief for the first time
- Increment frequency when same pattern appears in a different debrief
- Track which agencies raised the weakness -- agency-specific patterns are high value
- Include suggested mitigation based on winning proposals that addressed similar concerns

## Pattern Analysis

Over time, the win/loss database reveals actionable patterns:

### Agency-Specific Success Factors
- Which agencies the company wins at most (and least)
- Topic areas with highest win rates
- Phase I vs Phase II win rate differences by agency
- Whether certain evaluator scoring tendencies repeat by agency

### Common Weakness Themes
- Recurring debrief criticisms across multiple proposals
- Section-specific weaknesses (e.g., commercialization plans consistently weak)
- Agency-specific expectations not met (e.g., Navy expects more schedule detail)

### Trend Analysis
- Win rate trend over time (improving or declining)
- Impact of specific strategy changes on outcomes
- Correlation between corpus size (more exemplars) and win rate

## Outcome Recording Workflow

1. Receive outcome notification (win, loss, no-decision, withdrawn)
2. Update proposal state with outcome and timestamp
3. Tag the submitted proposal in corpus with outcome
4. If debrief available:
   a. Ingest debrief document into corpus
   b. Parse for structured feedback (scores, strengths, weaknesses)
   c. Map feedback to proposal sections
   d. Update known weakness profile
   e. Update agency preference model
5. Generate lessons-learned summary:
   - What worked (strengths to replicate)
   - What failed (weaknesses to address)
   - Strategic adjustments for next cycle
6. Present lessons-learned at human checkpoint (Wave 9 exit gate)

## Integration Points

| Consumer Agent | What It Needs | When |
|---------------|--------------|------|
| `fit-scorer` | Win rate by agency + topic area | Wave 0 -- informs Go/No-Go |
| `strategist` | Known weakness profile + agency preferences | Wave 1 -- informs strategy brief |
| `writer` | Winning section exemplars + debrief praise patterns | Wave 3-4 -- informs drafting |
| `reviewer` | Known weakness checklist + debrief critique patterns | Wave 4-7 -- review checklist |
| `debrief-analyst` | Raw debrief data + historical comparison | Wave 9 -- debrief processing |
