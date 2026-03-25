# Definition of Ready Checklist — sbir-developer-feedback

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | **Problem validated**: we understand the pain, not just the feature request | ✅ | JTBD Four Forces: push = vague feedback without context, habit = silent workarounds or Slack messages |
| 2 | **User story format**: each story has As/I want/So that with clear benefit | ✅ | 7 stories in user-stories.md, each with job trace |
| 3 | **Acceptance criteria are testable**: each AC can be verified true/false | ✅ | AC-01 through AC-13, each phrased as observable assertion |
| 4 | **Scope is bounded**: clear out-of-scope list, no scope creep risk | ✅ | requirements.md §Out of Scope: no remote sending, no aggregation, no multi-user |
| 5 | **Dependencies identified**: external systems and interfaces listed | ✅ | Shared Artifacts Registry: all 14 state variables with source file and field path |
| 6 | **Privacy/security considered**: sensitive data boundaries defined | ✅ | NFR-02 + AC-10: capability text, past performance, draft text excluded |
| 7 | **Error paths designed**: failure modes handled, no happy-path-only spec | ✅ | Journey visual §Error Paths: 5 scenarios; AC-09: 5 graceful degradation assertions |
| 8 | **Size estimated**: stories sized, implementation approach is clear | ✅ | Stories 1-7: M, S, S, XS, XS, XS, XS — fits one delivery cycle |

**DoR Result**: ✅ READY — all 8 criteria pass with evidence.

---

## Handoff Note to DESIGN Wave

The implementation has two surfaces:

1. **Python (PES)** — `FeedbackSnapshotService` (domain) + `FilesystemFeedbackAdapter` (adapter) + `FeedbackPort` (port). Reads from `json_state_adapter`, `filesystem_rigor_adapter`, `json_profile_adapter`, `json_finder_results_adapter`. Writes atomic JSON. This gets TDD + mutation testing.

2. **Markdown (command)** — `commands/proposal-developer-feedback.md` dispatches to `agents/sbir-feedback-collector.md` (new lightweight agent, ~100 lines). The agent runs the interactive type/ratings/text flow via `AskUserQuestion`, calls the Python snapshot script via Bash, then confirms. This gets forge validation.

The snapshot assembly is pure Python (testable in isolation). The interactive UX is markdown agent behavior (validated by scenario walkthroughs).

Key design question for DESIGN wave: **Should the snapshot script be a standalone CLI** (`scripts/sbir_feedback_cli.py`) callable by the agent via Bash, matching the pattern established by `dsip_cli.py`? Recommended: yes — keeps agent behavior declarative and Python logic unit-testable.
