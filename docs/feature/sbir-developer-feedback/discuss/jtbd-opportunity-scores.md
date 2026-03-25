# JTBD Opportunity Scores — sbir-developer-feedback

Scoring: Importance (1–10) × (10 − Current Satisfaction) = Opportunity Score. Higher = stronger unmet need.

| Job | Importance | Current Satisfaction | Opportunity Score | Priority |
|-----|-----------|---------------------|-------------------|----------|
| Job 1: Capture friction in-context | 9 | 1 (no mechanism exists) | 81 | **Critical** |
| Job 2: Receive actionable developer feedback | 8 | 2 (only vague reports today) | 64 | **High** |
| Job 3: Rate specific AI output quality | 7 | 1 (no mechanism exists) | 63 | **High** |

**Recommendation**: All three jobs are worth solving in one command. Job 1 drives the happy path (user flow); Job 2 drives the output schema (developer value); Job 3 drives the structured ratings UI.

The feature should deliver all three in a single `/sbir:developer-feedback` interaction.
