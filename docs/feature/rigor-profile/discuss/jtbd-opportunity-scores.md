# JTBD Opportunity Scoring -- Rigor Profile

Feature: rigor-profile
Date: 2026-03-23
Phase: 1 -- Deep Discovery (JTBD Analysis)

---

## Scoring Method

- **Importance**: Estimated % of target users rating outcome 4+ on 5-point scale
- **Satisfaction**: Estimated % of target users rating current solution 4+ on 5-point scale
- **Score**: Importance + max(0, Importance - Satisfaction)
- **Priority**: Extremely Underserved (15+), Underserved (12-15), Appropriately Served (10-12), Overserved (<10)

### Data Quality Notes

- **Source**: Team estimates based on plugin architecture analysis, user persona research, and nWave `/nw:rigor` precedent
- **Sample size**: N/A (no direct user survey -- estimates derived from domain analysis of small business SBIR workflow)
- **Confidence**: Medium (team estimates, informed by real plugin usage patterns and SBIR proposal lifecycle constraints)
- **Recommendation**: Re-score after beta release with actual user feedback

---

## Outcome Statements by Job Map Step

### Step 1: Define -- Determine appropriate quality level

| # | Outcome Statement | Imp. | Sat. | Score | Priority |
|---|-------------------|------|------|-------|----------|
| 1 | Minimize the time to determine the right quality/cost tradeoff for a given proposal | 85% | 10% | 16.0 | Extremely Underserved |
| 2 | Minimize the likelihood of over-investing in a low-priority proposal | 80% | 15% | 14.5 | Underserved |
| 3 | Minimize the likelihood of under-investing in a must-win proposal | 90% | 20% | 16.0 | Extremely Underserved |
| 4 | Minimize the time to understand what each quality level actually configures | 75% | 5% | 14.5 | Underserved |

### Step 2: Locate -- Find rigor controls

| # | Outcome Statement | Imp. | Sat. | Score | Priority |
|---|-------------------|------|------|-------|----------|
| 5 | Minimize the time to find and invoke the rigor configuration command | 60% | 10% | 11.0 | Appropriately Served |
| 6 | Minimize the likelihood of not knowing the rigor feature exists | 70% | 5% | 13.5 | Underserved |

### Step 3: Prepare -- Select or customize a profile

| # | Outcome Statement | Imp. | Sat. | Score | Priority |
|---|-------------------|------|------|-------|----------|
| 7 | Minimize the time to select a profile for a new proposal | 80% | 10% | 15.0 | Extremely Underserved |
| 8 | Minimize the number of decisions required to start a proposal with appropriate rigor | 85% | 10% | 16.0 | Extremely Underserved |
| 9 | Maximize the likelihood that a custom profile correctly maps models to agent roles | 55% | 5% | 10.5 | Appropriately Served |

### Step 4: Confirm -- Verify profile before applying

| # | Outcome Statement | Imp. | Sat. | Score | Priority |
|---|-------------------|------|------|-------|----------|
| 10 | Minimize the likelihood of applying the wrong rigor level to a proposal | 75% | 10% | 14.0 | Underserved |
| 11 | Minimize the time to preview what a profile will change before committing | 65% | 5% | 12.5 | Underserved |

### Step 5: Execute -- Profile applies to agent invocations

| # | Outcome Statement | Imp. | Sat. | Score | Priority |
|---|-------------------|------|------|-------|----------|
| 12 | Minimize the likelihood of an agent ignoring the configured rigor level | 90% | 15% | 16.5 | Extremely Underserved |
| 13 | Minimize the time to apply a rigor profile across all agents in a wave | 80% | 5% | 15.5 | Extremely Underserved |
| 14 | Minimize the likelihood that rigor settings produce inconsistent quality across sections | 70% | 20% | 12.0 | Appropriately Served |

### Step 6: Monitor -- See rigor in status displays

| # | Outcome Statement | Imp. | Sat. | Score | Priority |
|---|-------------------|------|------|-------|----------|
| 15 | Minimize the time to see the current rigor level for the active proposal | 70% | 5% | 13.5 | Underserved |
| 16 | Minimize the likelihood of losing track of which rigor level is active | 65% | 10% | 12.0 | Appropriately Served |
| 17 | Minimize the time to see cumulative cost impact of the chosen rigor level | 60% | 5% | 11.5 | Appropriately Served |

### Step 7: Modify -- Change rigor mid-proposal

| # | Outcome Statement | Imp. | Sat. | Score | Priority |
|---|-------------------|------|------|-------|----------|
| 18 | Minimize the time to change rigor level for an in-progress proposal | 70% | 5% | 13.5 | Underserved |
| 19 | Minimize the likelihood of losing work when changing rigor mid-proposal | 85% | 15% | 15.5 | Extremely Underserved |
| 20 | Minimize the time to apply a targeted rigor override to a single section or figure | 50% | 5% | 9.5 | Overserved |

### Step 8: Conclude -- Assess quality/cost outcome

| # | Outcome Statement | Imp. | Sat. | Score | Priority |
|---|-------------------|------|------|-------|----------|
| 21 | Minimize the time to review what rigor settings were used for a completed proposal | 55% | 5% | 10.5 | Appropriately Served |
| 22 | Maximize the likelihood that debrief feedback informs future rigor choices | 60% | 10% | 11.0 | Appropriately Served |

---

## Ranked Opportunity Scores

| Rank | # | Outcome Statement | Score | Priority |
|------|---|-------------------|-------|----------|
| 1 | 12 | Minimize the likelihood of an agent ignoring the configured rigor level | 16.5 | Extremely Underserved |
| 2 | 1 | Minimize the time to determine the right quality/cost tradeoff | 16.0 | Extremely Underserved |
| 3 | 3 | Minimize the likelihood of under-investing in a must-win proposal | 16.0 | Extremely Underserved |
| 4 | 8 | Minimize the number of decisions required to start with appropriate rigor | 16.0 | Extremely Underserved |
| 5 | 13 | Minimize the time to apply a rigor profile across all agents in a wave | 15.5 | Extremely Underserved |
| 6 | 19 | Minimize the likelihood of losing work when changing rigor mid-proposal | 15.5 | Extremely Underserved |
| 7 | 7 | Minimize the time to select a profile for a new proposal | 15.0 | Extremely Underserved |
| 8 | 2 | Minimize the likelihood of over-investing in a low-priority proposal | 14.5 | Underserved |
| 9 | 4 | Minimize the time to understand what each quality level actually configures | 14.5 | Underserved |
| 10 | 10 | Minimize the likelihood of applying the wrong rigor level | 14.0 | Underserved |
| 11 | 6 | Minimize the likelihood of not knowing the rigor feature exists | 13.5 | Underserved |
| 12 | 15 | Minimize the time to see current rigor level for active proposal | 13.5 | Underserved |
| 13 | 18 | Minimize the time to change rigor level for in-progress proposal | 13.5 | Underserved |
| 14 | 11 | Minimize the time to preview what a profile will change | 12.5 | Underserved |
| 15 | 14 | Minimize the likelihood of inconsistent quality across sections | 12.0 | Appropriately Served |
| 16 | 16 | Minimize the likelihood of losing track of active rigor level | 12.0 | Appropriately Served |
| 17 | 17 | Minimize the time to see cumulative cost impact | 11.5 | Appropriately Served |
| 18 | 5 | Minimize the time to find the rigor configuration command | 11.0 | Appropriately Served |
| 19 | 22 | Maximize the likelihood that debrief informs future rigor choices | 11.0 | Appropriately Served |
| 20 | 9 | Maximize the likelihood that custom profile maps models correctly | 10.5 | Appropriately Served |
| 21 | 21 | Minimize the time to review rigor settings for completed proposal | 10.5 | Appropriately Served |
| 22 | 20 | Minimize the time to apply targeted rigor override to single section | 9.5 | Overserved |

---

## Top Opportunities (Score >= 15) -- Must Address

| # | Outcome | Score | Maps to Job | Story Direction |
|---|---------|-------|-------------|-----------------|
| 12 | Agent ignoring configured rigor level | 16.5 | J1, J2, J4 | Rigor enforcement mechanism -- agents MUST respect the active profile. This is the foundational technical requirement. |
| 1 | Time to determine right quality/cost tradeoff | 16.0 | J1, J2, J6 | Named profiles with clear descriptions and cost implications. Sensible defaults based on proposal metadata. |
| 3 | Under-investing in must-win proposal | 16.0 | J1, J4 | "Thorough" profile with maximum quality settings. Integration with fit score to suggest appropriate level. |
| 8 | Decisions required to start with appropriate rigor | 16.0 | J6, J1 | Suggest a profile during `/proposal new` based on fit score and contract value. One-click acceptance. |
| 13 | Time to apply profile across all agents | 15.5 | J1, J2 | Single command sets rigor for all agents. No per-agent configuration required for standard profiles. |
| 19 | Losing work when changing rigor mid-proposal | 15.5 | J4, J5 | Rigor change is a metadata update, not a re-run. Existing artifacts are preserved. |
| 7 | Time to select a profile for a new proposal | 15.0 | J2, J6 | 3-5 named profiles selectable by name. No configuration file editing required. |

## Underserved Opportunities (Score 12-15) -- Should Address

| # | Outcome | Score | Maps to Job | Story Direction |
|---|---------|-------|-------------|-----------------|
| 2 | Over-investing in low-priority proposal | 14.5 | J2, J4 | "Lean" profile with cost-optimized settings. Dashboard shows rigor per proposal for portfolio view. |
| 4 | Understand what each quality level configures | 14.5 | J6 | Comparison table available via `/proposal rigor show`. Progressive disclosure: summary then detail. |
| 10 | Applying wrong rigor level | 14.0 | J6 | Confirmation prompt when setting rigor. Rigor level visible in status output. |
| 6 | Not knowing rigor feature exists | 13.5 | J6 | Mention rigor option during `/proposal new`. First-run hint. |
| 15 | See current rigor level for active proposal | 13.5 | J4, J6 | Rigor level displayed in `/proposal status` output. |
| 18 | Change rigor for in-progress proposal | 13.5 | J4, J5 | `/proposal rigor set <profile>` works at any point. No wave restrictions. |
| 11 | Preview profile changes before committing | 12.5 | J6 | Show diff of what the new profile changes relative to current settings. |

## Appropriately Served (Score 10-12) -- Maintain

Outcomes 5, 9, 14, 16, 17, 21, 22 are adequately served by baseline design decisions (standard CLI patterns, status displays, debrief integration). No special investment needed -- these are covered by doing the basics well.

## Overserved (Score < 10) -- Simplify or Defer

| # | Outcome | Score | Simplification |
|---|---------|-------|---------------|
| 20 | Per-section rigor override | 9.5 | Defer to future phase. Power-user feature with low demand. Job 5 (Recover Quality) is the least urgent job by force analysis. |

---

## Strategic Implications

### MVP Scope (Jobs 1 + 2 + 6)

The top 7 outcomes cluster around three capabilities:
1. **Named profiles** with transparent configuration (outcomes 1, 4, 7, 8)
2. **Enforcement mechanism** ensuring agents respect the profile (outcomes 12, 13)
3. **Safe mutability** so rigor can change without losing work (outcome 19)

This maps to: a `/proposal rigor` command with 3-5 named profiles, agent frontmatter integration for model/settings resolution, and rigor as per-proposal metadata in `.sbir/proposals/{topic-id}/`.

### Phase 2 Scope (Job 4)

Multi-proposal rigor differentiation (outcomes 2, 15) builds on the MVP by integrating rigor into the existing multi-proposal workspace dashboard and `/proposal switch` command.

### Deferred (Jobs 3 + 5)

Per-section overrides (outcome 20) and granular iteration-level rigor control (Job 3) are power-user refinements. Defer until post-MVP user feedback confirms demand.

### Key Design Constraint

Outcome 12 (agents must respect rigor) scored highest at 16.5. This is the foundational technical requirement. Without enforcement, profiles are advisory labels with no effect. The design must include a mechanism where agents resolve their model and behavior settings from the active rigor profile, not from hardcoded frontmatter alone.
