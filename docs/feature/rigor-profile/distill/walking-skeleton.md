# Walking Skeleton -- Rigor Profile

Feature: rigor-profile
Date: 2026-03-23
Phase: 5 -- DISTILL (Acceptance Test Design)

---

## Walking Skeletons (3)

### WS-1: Author sets rigor profile and it persists

**User Goal**: Elena wants to tell the plugin "this proposal is a must-win, use more capable models."

**Observable Outcome**: After setting thorough rigor, the rigor profile file reflects "thorough" and records the change in history.

**Resolution Chain Exercised**: Profile validation -> state write -> history append.

**Driving Port**: `RigorService.set_profile()`

**Implementation Sequence**: First skeleton -- enable this test first.

### WS-2: Pre-rigor proposal defaults to standard without error

**User Goal**: Phil has a proposal from before the rigor feature existed. He expects it to continue working normally.

**Observable Outcome**: Reading the rigor profile returns "standard" with no error, even though no rigor-profile.json exists.

**Resolution Chain Exercised**: Missing file detection -> default fallback.

**Driving Port**: `RigorService.get_active_profile()`

**Implementation Sequence**: Second skeleton -- tests backward compatibility.

### WS-3: Agent model tier resolves from rigor profile

**User Goal**: Elena set "thorough" rigor and expects the writer agent to use the strongest model.

**Observable Outcome**: Resolving the writer role returns "strongest" model tier.

**Resolution Chain Exercised**: Per-proposal profile read -> definition lookup -> agent role -> model tier.

**Driving Port**: `RigorService.resolve_model_tier()`

**Implementation Sequence**: Third skeleton -- tests the full resolution chain.

---

## Litmus Test Results

All three walking skeletons pass the litmus test:

1. **Title describes user goal**: "Elena sets thorough rigor", "Phil opens pre-rigor proposal", "writer resolves model tier" -- all user-focused.
2. **Given/When describe user actions**: "Elena sets the rigor to thorough", "Phil reads the active rigor profile" -- not "database row inserted."
3. **Then describe user observations**: "active rigor profile is thorough", "rigor profile resolves to standard" -- not "JSON file contains key."
4. **Non-technical stakeholder can confirm**: A PI would say "yes, I need to set quality level, it should default to standard, and agents should use the level I set."

---

## Implementation Sequence

| Order | Skeleton/Milestone | Scenarios | Focus |
|-------|-------------------|-----------|-------|
| 1 | WS-1 (set profile) | 1 | Core write path |
| 2 | WS-2 (default fallback) | 1 | Backward compatibility |
| 3 | WS-3 (model resolution) | 1 | Resolution chain |
| 4 | M-01 (validation) | 7 | Profile name validation, definition completeness |
| 5 | M-02 (selection) | 7 | Set/diff/history/no-op/error paths |
| 6 | M-03 (resolution) | 13 | All roles, behavioral params, property tests |
| 7 | M-04 (suggestion) | 9 | Contextual suggestion thresholds |
| 8 | M-05 (diff) | 6 | Diff computation, edge cases |
