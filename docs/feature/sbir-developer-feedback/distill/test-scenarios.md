# Test Scenarios — sbir-developer-feedback

## Coverage Map

| User Story | Milestone | Scenario Count | Coverage |
|-----------|-----------|---------------|---------|
| Story 1 (capture in-context) | Walking Skeleton, M03-CLI | 2 WS + 4 CLI | ✅ |
| Story 2 (quality ratings) | Walking Skeleton, M01-domain | 1 WS + 2 domain | ✅ |
| Story 3 (no active proposal) | Walking Skeleton WS-2, M03-CLI | 1 WS + 1 CLI | ✅ |
| Story 4 (developer reads structured) | M01-domain, M03-CLI | 2 domain + 3 CLI | ✅ |
| Story 5 (persists across sessions) | M02-adapter | 2 adapter | ✅ |
| Story 6 (privacy boundary) | M04-privacy | 5 privacy | ✅ |
| Story 7 (empty submission guard) | M04-privacy (agent concern) | Agent-level only | ⚠️ |

**Story 7 note**: The empty submission guard is handled by the markdown agent (`sbir-feedback-collector`) using `AskUserQuestion`. It is not testable at the Python acceptance level. Coverage is via agent scenario walkthroughs.

---

## Feature Files

| File | Scenarios | Tags | Milestone |
|------|-----------|------|-----------|
| `walking-skeleton.feature` | 2 | `@walking_skeleton`, `@skip` | Skeleton |
| `milestone-01-domain-model.feature` | 5 | `@skip` | M01 |
| `milestone-02-adapter.feature` | 5 | `@skip` | M02 |
| `milestone-03-cli.feature` | 8 | `@skip` | M03 |
| `milestone-04-privacy-and-guards.feature` | 5 | `@skip` | M04 |

**Total**: 25 scenarios (2 walking skeleton active, 23 `@skip` for one-at-a-time implementation)

---

## Implementation Order (Outside-In TDD)

```
Walking Skeleton 1  →  M01 domain model  →  M02 adapter  →  M03 CLI  →  M04 privacy
       ↓                     ↓                   ↓              ↓             ↓
  Full pipeline         FeedbackEntry      FilesystemFb    sbir_feedback   Privacy
  smoke test           FeedbackSnapshot    Adapter write   _cli.py save    boundary
                       FeedbackService     atomic + name   full wiring     enforcement
```

**Rule**: Remove `@skip` from each scenario only after the production code it exercises is written and the scenario passes. Never skip forward.

---

## Driving Port Strategy

All acceptance tests drive through **driving ports only**:

| Boundary | How Tested |
|----------|-----------|
| `FeedbackSnapshotService` | Called directly with dict arguments (no adapter injection) |
| `FilesystemFeedbackAdapter` | Called directly via `FeedbackWriterPort` interface |
| `sbir_feedback_cli.py` | Invoked via subprocess (same as agent Bash call) |

No test imports from `scripts/pes/adapters/` except `filesystem_feedback_adapter`. All state files are written to `tmp_path` directories, never to real `.sbir/`.

---

## Fixture Strategy

All filesystem state is controlled via `pytest.tmp_path`:

| State File | Written By | Path |
|------------|-----------|------|
| `proposal-state.json` | `active_proposal_with_rigor` step | `tmp_path/.sbir/proposals/{id}/` |
| `rigor-profile.json` | `active_proposal_with_rigor` step | `tmp_path/.sbir/proposals/{id}/` |
| `company-profile.json` | `company_profile_with_age` step | `tmp_path/home_sbir/` |
| `finder-results.json` | `finder_results_with_age` step | `tmp_path/.sbir/` |
| `active-proposal.json` | `active_proposal_with_rigor` step | `tmp_path/.sbir/` |
| feedback output | `FilesystemFeedbackAdapter` | `tmp_path/.sbir/feedback/` |
