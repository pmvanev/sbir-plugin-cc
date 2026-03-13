# Opportunity Scoring -- Solution Shaper

## Scoring Method

- **Importance**: 1-10 scale based on impact on approach selection quality
- **Satisfaction**: 1-10 scale based on current state (no agent owns approach selection)
- **Score**: Importance + Max(0, Importance - Satisfaction)
- **Max score**: 20

## Data Quality Note

Source: Codebase structural analysis + user-described workflow gap + discovery phase evidence (5 sources). Single user (Phil). Confidence: MEDIUM -- strong behavioral signals from the user who built the plugin.

---

## Outcome Statements and Scores

| # | Outcome Statement | Imp | Sat | Score | Category | Traces To |
|---|-------------------|-----|-----|-------|----------|-----------|
| O1 | Minimize the time to extract actionable requirements, objectives, and evaluation criteria from a solicitation | 9 | 5 | 13 | Underserved | JS-1 |
| O2 | Minimize the likelihood of missing a strong candidate technical approach | 10 | 2 | 18 | Extremely Underserved | JS-2 |
| O3 | Minimize the uncertainty about which approach best leverages company-specific strengths | 10 | 1 | 19 | Extremely Underserved | JS-3 |
| O4 | Minimize the risk of selecting an approach with weak Phase III commercialization pathway | 8 | 2 | 14 | Underserved | JS-4 |
| O5 | Minimize the time from scored approaches to a documented, defensible selection | 9 | 1 | 17 | Extremely Underserved | JS-5 |
| O6 | Minimize the likelihood of approach discrimination angles being undiscovered before Wave 3 | 8 | 3 | 13 | Underserved | JS-5 |
| O7 | Minimize information loss between approach selection and strategy brief generation | 7 | 3 | 11 | Appropriately Served | JS-6 |
| O8 | Minimize the effort to revise approach selection when new information arrives | 7 | 2 | 12 | Underserved | JS-5 |

---

## Ranked by Score

| Rank | # | Outcome | Score | Action |
|------|---|---------|-------|--------|
| 1 | O3 | Company-specific approach scoring | 19 | Must Have -- core differentiator |
| 2 | O2 | Candidate approach generation | 18 | Must Have -- foundational capability |
| 3 | O5 | Documented approach convergence | 17 | Must Have -- the output artifact |
| 4 | O4 | Early commercialization assessment | 14 | Should Have -- informs scoring |
| 5 | O1 | Solicitation deep-read | 13 | Should Have -- prerequisite for generation |
| 6 | O6 | Discrimination angle discovery | 13 | Should Have -- feeds Wave 3 |
| 7 | O8 | Approach revision support | 12 | Could Have -- handles change of information |
| 8 | O7 | Strategy handoff fidelity | 11 | Could Have -- we control both agents |

---

## Prioritization Summary

### Extremely Underserved (Score 15+) -- Must Have

- **O3 (19)**: Company-specific approach scoring. This is the highest-scoring outcome because no tool, agent, or process currently evaluates approaches against Phil's specific personnel, past performance, and IP. The topic-scout scores company-level fit; nobody scores approach-level fit.

- **O2 (18)**: Candidate approach generation. The second-highest because the option space is never systematically explored. Phil defaults to his first idea, which works for core expertise but fails for adjacent topics where growth happens.

- **O5 (17)**: Documented approach convergence. The third-highest because the approach decision is currently implicit. No artifact records why this approach was chosen. The strategy brief assumes the approach; the discrimination table compares it against alternatives without recording the selection process.

### Underserved (Score 12-15) -- Should Have

- **O4 (14)**: Early commercialization. Currently assessed in Wave 2 after the approach is set. Moving a lightweight assessment forward gives approach selection a commercialization dimension.

- **O1 (13)**: Solicitation deep-read. Partially served by topic-scout parsing, but the deep-read needed for approach generation goes beyond title/summary. Requirement extraction at the level needed for approach evaluation.

- **O6 (13)**: Discrimination angle discovery. The discrimination table in Wave 3 would be sharper with deliberate approach selection feeding it. Early discrimination thinking during approach scoring.

- **O8 (12)**: Approach revision. Edge case for when TPOC feedback or research changes the picture. The approach brief should be revisable, not write-once.

### Appropriately Served (Score 10-12) -- Could Have

- **O7 (11)**: Strategy handoff fidelity. We control both the solution-shaper and the strategist agent. The approach-brief.md schema can be designed to match what the strategist needs. Low risk of integration failure.

---

## MoSCoW Summary

| Priority | Outcomes | Story Coverage |
|----------|----------|----------------|
| Must Have | O2, O3, O5 | US-SS-001 (approach generation + scoring + convergence) |
| Should Have | O1, O4, O6 | US-SS-001 (deep-read, commercialization as scoring dimension, discrimination angles in brief) |
| Could Have | O7, O8 | US-SS-002 (approach revision), US-SS-001 (handoff artifact) |
| Won't Have | -- | -- |
