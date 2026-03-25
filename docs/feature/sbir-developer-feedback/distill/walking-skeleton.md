# Walking Skeleton — sbir-developer-feedback

## Definition

The walking skeleton is the thinnest vertical slice that validates the end-to-end pipeline: user submits quality feedback → CLI assembles snapshot → feedback file written → file contains correct data.

## Walking Skeleton 1 (Active — implement first)

**Scenario**: Proposal writer submits a quality issue and feedback is persisted with context snapshot

**What it proves**:
- `FeedbackSnapshotService.build_snapshot()` correctly reads proposal state, rigor, company profile, and finder results
- `FeedbackEntry` serializes to JSON correctly
- `FilesystemFeedbackAdapter.write()` creates the file at the right path
- `sbir_feedback_cli.py save` wires all of the above end-to-end
- Context snapshot contains the 7 most critical fields (proposal_id, current_wave, completed_waves, rigor_profile, company_name, company_profile_age_days, finder_results_age_days)

**Implementation requires** (in order):
1. `scripts/pes/domain/feedback.py` — domain model
2. `scripts/pes/domain/feedback_service.py` — snapshot assembly
3. `scripts/pes/ports/feedback_port.py` — writer port
4. `scripts/pes/adapters/filesystem_feedback_adapter.py` — file write
5. `scripts/sbir_feedback_cli.py` — CLI wiring

## Walking Skeleton 2 (Skip until WS-1 passes)

**Scenario**: User submits feedback with no active proposal and feedback is still saved

**What it adds**: Validates the graceful degradation path. All proposal fields null, feedback still written.

**Requires**: WS-1 + graceful null handling in snapshot service and CLI.

## Confidence Checklist Before DELIVER

- [ ] Walking Skeleton 1 passes with production code (not fakes)
- [ ] Walking Skeleton 2 passes
- [ ] All M01-M04 scenarios unblocked (no @skip remaining after implementation)
- [ ] `pytest tests/acceptance/sbir_developer_feedback/ -v` exits 0
- [ ] No real `.sbir/` directory modified during test run
