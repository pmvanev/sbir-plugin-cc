---
name: debrief-domain-knowledge
description: Domain knowledge for post-submission debrief processing -- loss categorization, debrief request letter format, lessons-learned generation, and feedback distribution to downstream agents
---

# Debrief Domain Knowledge

## Loss Categorization Taxonomy

Classify every loss into one or more root cause categories. A single loss may have multiple contributing factors, but identify the primary category.

| Category | Indicators | Typical Debrief Language |
|----------|-----------|------------------------|
| Technical | Low scores on technical approach, innovation, feasibility | "approach lacks detail", "TRL gap not addressed", "methodology unclear" |
| Cost | Budget concerns, unrealistic pricing, rate issues | "cost not commensurate", "labor hours excessive", "indirect rates high" |
| Strategic | Poor fit, weak teaming, commercialization gaps, wrong agency | "limited relevant experience", "Phase III path unclear", "team lacks key expertise" |
| Past Performance | Weak or missing citations, poor relevance mapping | "insufficient relevant past performance", "citations not directly applicable" |
| Compliance | Missing requirements, format violations, incomplete sections | "did not address requirement X", "exceeded page limit", "missing required section" |

When debrief feedback is ambiguous, categorize as the most specific applicable category. "Technical" is the default only when no other category fits.

## Debrief Request Letter Template

Use when outcome is LOSS and no debrief has been provided. Draft for human review -- never send automatically.

Required elements:
1. **Solicitation reference**: Topic number, solicitation ID, proposal title
2. **Submission date**: When the proposal was submitted
3. **Request statement**: Polite, professional request for evaluator feedback
4. **Specific asks**: Scores per criterion, strengths, weaknesses, adjectival ratings
5. **Contact information**: Company POC name and contact details (from company profile)
6. **Timeline reference**: Note any agency-specific debrief request deadlines

Agency-specific notes:
- **DoD (DSIP portal)**: Debrief requests typically go through the contracting officer listed in the notification letter
- **NSF**: Uses panel review summaries; request through program officer
- **NASA**: SBIR program office handles debriefs; reference SBIR.gov submission ID
- **DOE**: Contact the program manager listed in the solicitation

## Lessons-Learned Output Format

Generate a structured lessons-learned summary at the end of every Wave 9 cycle:

```yaml
lessons_learned:
  proposal_id: "{proposal_id}"
  outcome: "{WIN|LOSS|NO_DECISION|WITHDRAWN}"
  date: "{ISO date}"

  # What worked -- replicate in future proposals
  strengths:
    - section: "{proposal section}"
      feedback: "{evaluator comment or internal observation}"
      action: "Replicate: {specific element to keep}"

  # What failed -- address before next submission
  weaknesses:
    - section: "{proposal section}"
      feedback: "{evaluator comment or internal observation}"
      root_cause: "{technical|cost|strategic|past_performance|compliance}"
      action: "Improve: {specific corrective action}"

  # Strategic adjustments for next cycle
  strategic_adjustments:
    - area: "{agency targeting|teaming|pricing|technical approach|...}"
      observation: "{what the data shows}"
      recommendation: "{specific change for next cycle}"

  # Updated metrics
  metrics:
    overall_win_rate: "{N wins / M total}"
    agency_win_rates:
      "{agency}": "{n/m}"
    trend: "{improving|stable|declining}"
```

## Feedback Distribution Map

After generating lessons learned, distribute specific insights to downstream agents:

| Recipient Agent | What to Feed | State Location |
|----------------|-------------|----------------|
| `fit-scorer` | Updated win rate by agency and topic area | `.sbir/proposal-state.json` -> `analytics.win_rates` |
| `strategist` | New weakness profile entries, agency preference updates | `.sbir/proposal-state.json` -> `analytics.weakness_profile` |
| `writer` | Winning section exemplars flagged, debrief praise patterns | Corpus outcome tags (via corpus-librarian) |
| `reviewer` | New weakness checklist items from debrief critiques | `.sbir/proposal-state.json` -> `analytics.weakness_profile` |

Feedback is written to state and corpus -- downstream agents read it on their next invocation. The debrief-analyst does not invoke other agents directly.

## Award Path: Phase II Pre-Planning

When outcome is WIN on a Phase I proposal:
1. Archive the winning proposal with outcome tag `WIN` in corpus
2. Extract winning discriminators (what evaluators praised)
3. Create a Phase II pre-planning scaffold:
   - Key technical milestones achieved in Phase I
   - Phase II scope expansion areas (from solicitation)
   - Team augmentation needs identified during Phase I
   - Commercialization evidence to strengthen
4. Write scaffold to `./artifacts/wave-9-debrief/{proposal_id}-phase2-preplanning.md`

## Notification Timeline Tracking

Track expected notification dates and actual receipt:

| Field | Source |
|-------|--------|
| `expected_notification_date` | Solicitation document (typical: 90-180 days post-close) |
| `actual_notification_date` | When outcome is received |
| `debrief_requested_date` | When debrief request was sent (if applicable) |
| `debrief_received_date` | When debrief feedback was received |
| `lessons_learned_date` | When Wave 9 lessons-learned was completed |

Write notification tracking to `.sbir/proposal-state.json` -> `wave9.timeline`.
