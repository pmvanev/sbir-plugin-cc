# Acceptance Criteria — sbir-developer-feedback

## AC-01: Command is invokable (Story 1)
- [ ] `/sbir:developer-feedback` resolves to a command file in `commands/`
- [ ] Command can be invoked with no arguments from any Claude Code session
- [ ] Command works with no active proposal (no `.sbir/proposals/` directory)

## AC-02: Feedback type is required (Story 1)
- [ ] Agent asks user to select Bug, Suggestion, or Quality Issue before proceeding
- [ ] No feedback entry is written before type is selected
- [ ] All three types produce a valid output file

## AC-03: Quality ratings are presented for Quality Issue type (Story 2)
- [ ] When type = "Quality Issue", agent presents all four rating dimensions
- [ ] Each dimension is rated 1–5 or skipped (null)
- [ ] When type = "Bug" or "Suggestion", ratings step is skipped entirely
- [ ] A fully null ratings object (all skipped) is valid

## AC-04: Free text is optional for all types (Stories 1, 3)
- [ ] Agent offers free text field for all feedback types
- [ ] Submitting with null free_text is valid (no error, no retry)

## AC-05: Context snapshot captures proposal state (Story 1, 4)
- [ ] When active proposal exists, `proposal_id` matches `proposal-state.json`
- [ ] `current_wave` matches `proposal-state.json:current_wave`
- [ ] `completed_waves` contains wave numbers where `status == "completed"`
- [ ] `skipped_waves` contains wave numbers where `status == "skipped"`
- [ ] `topic.id`, `topic.title`, `topic.agency`, `topic.deadline`, `topic.phase` populated from state

## AC-06: Context snapshot captures configuration state (Story 4)
- [ ] `rigor_profile` matches `rigor-profile.json:profile_name`; null if file absent
- [ ] `company_name` from `~/.sbir/company-profile.json`; null if absent
- [ ] `company_profile_age_days` is integer days since file mtime; null if absent
- [ ] `finder_results_age_days` is integer days since `.sbir/finder-results.json` mtime; null if absent
- [ ] `top_scored_topics` is top 5 entries from finder results; empty list if absent

## AC-07: Context snapshot captures environment (Story 4)
- [ ] `plugin_version` is short git SHA (`git rev-parse --short HEAD`); "unknown" if git unavailable
- [ ] `generated_artifacts` is alphabetical list of filenames in artifacts dir; empty list if absent

## AC-08: Output file is written correctly (Stories 1, 5)
- [ ] File written to `.sbir/feedback/feedback-{UTC-ISO-timestamp}.json` (colons → hyphens)
- [ ] Directory created if absent
- [ ] Write uses atomic pattern (write tmp, rename)
- [ ] `feedback_id` is a valid UUID v4
- [ ] `timestamp` is ISO-8601 UTC

## AC-09: Graceful degradation (Story 3)
- [ ] Missing `proposal-state.json` → all proposal fields null, no crash
- [ ] Missing `rigor-profile.json` → `rigor_profile: null`, no crash
- [ ] Missing `~/.sbir/company-profile.json` → company fields null, no crash
- [ ] Missing `finder-results.json` → finder fields null/empty, no crash
- [ ] Git unavailable → `plugin_version: "unknown"`, no crash
- [ ] Feedback file is written in all above scenarios

## AC-10: Privacy boundary enforced (Story 6)
- [ ] Company profile capability text NOT in snapshot
- [ ] Past performance descriptions NOT in snapshot
- [ ] Proposal draft text NOT in snapshot
- [ ] Key personnel details NOT in snapshot
- [ ] Only metadata (names, ages, counts, scores, IDs) present

## AC-11: Empty submission guard (Story 7)
- [ ] When ratings all null AND free_text null, agent prompts: "Are you sure you want to submit with no details?"
- [ ] If user confirms → feedback saved, no error
- [ ] Prompt shown at most once per submission attempt

## AC-12: Confirmation message (Story 1)
- [ ] After save, agent displays: feedback ID (UUID) and full file path
- [ ] Message is shown even when snapshot had partial/null fields

## AC-13: Output schema validity
- [ ] All saved files parse as valid JSON
- [ ] Schema matches definition in `journey-feedback.yaml`
- [ ] No extra fields outside schema
- [ ] No required field missing (all non-nullable fields present)
