# /proposal wave final-review

Run simulated government evaluator review with red team analysis, debrief cross-check, and sign-off gate. Supports max 2 iteration rounds before forced sign-off.

## Usage

```
/proposal wave final-review             # Run full review cycle
/proposal wave final-review iterate     # Submit feedback for re-review
/proposal wave final-review sign-off    # Approve final sign-off
```

## Prerequisites

- Wave 6 complete (formatted proposal assembled in `./artifacts/wave-6-formatted/`)
- Current wave is 7 (Wave 7 active)

## Flow

1. **Reviewer simulation** -- Simulate government technical evaluator scoring against solicitation evaluation criteria
2. **Red team** -- Identify 3-5 strongest objections a skeptical reviewer could raise
3. **Debrief cross-check** -- Check proposal against known weakness patterns from past debriefs (if available)
4. **Scorecard presentation** -- Present reviewer simulation scorecard with strengths, weaknesses, and red team findings
5. **Iteration loop** (max 2 rounds) -- User provides feedback, reviewer updates findings, re-presents scorecard
6. **Forced sign-off** -- If max iterations reached, remaining findings documented and sign-off required
7. **Human checkpoint** -- Approve final sign-off or request revisions

## Context Files Required

- `./artifacts/wave-6-formatted/` -- Formatted proposal volumes for review
- `.sbir/proposal-state.json` -- Current wave and proposal context
- `.sbir/compliance-matrix.md` -- Requirement coverage status
- Solicitation file (path from proposal state) -- Evaluation criteria for persona construction

## Agent Invocation

Dispatch to `sbir-reviewer` agent for Wave 7 full review.

The reviewer agent handles: evaluator persona construction from solicitation criteria | full proposal scoring | red team analysis | debrief cross-check | jargon and cross-reference audits | iteration tracking with 2-round max | sign-off gate.

SKILL_LOADING: The reviewer agent MUST load its skills from `skills/reviewer/` and `skills/corpus-librarian/` before beginning work. Skills contain government evaluator simulation methodology, scoring rubrics, red team technique, and debrief pattern matching.

## Implementation

This command invokes `FinalReviewService` (driving port):

| Method | Purpose |
|--------|---------|
| `run_reviewer_simulation()` | Simulate government evaluator scoring against criteria |
| `run_red_team()` | Identify strongest objections by severity |
| `run_debrief_cross_check()` | Check against known debrief weaknesses from corpus |
| `re_review()` | Re-review after fixes; returns `ForcedSignOffResult` if max iterations reached |
| `sign_off()` | Record human sign-off with timestamp and unresolved issues |

Domain models: `ReviewerScorecard`, `RedTeamFinding`, `RedTeamResult`, `DebriefCrossCheckResult`, `ReReviewResult`, `ForcedSignOffResult`, `SignOffRecord` (from `pes.domain.final_review`).

## Success Criteria

- [ ] Reviewer scorecard written to `./artifacts/wave-7-review/reviewer-scorecard.md`
- [ ] Red team findings written to `./artifacts/wave-7-review/red-team-findings.md`
- [ ] Debrief cross-check completed (or noted as unavailable)
- [ ] All compliance matrix items verified as COVERED or WAIVED
- [ ] Human sign-off recorded (approved or forced after 2 iterations)

## Next Wave

**Handoff To**: Wave 8 (Submission preparation)
**Deliverables**: Reviewer scorecard | Red team findings | Sign-off record

## Expected outputs

- `./artifacts/wave-7-review/reviewer-scorecard.md`
- `./artifacts/wave-7-review/red-team-findings.md`
- `./artifacts/wave-7-review/sign-off-record.md`
