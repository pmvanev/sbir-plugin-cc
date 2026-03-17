# Shared Artifacts Registry: PES Enforcement Wiring

## Artifacts

### pes-config.json rules array
- **Source of truth**: `templates/pes-config.json`
- **Consumers**: `JsonRuleAdapter.load_rules()`, `EnforcementEngine.evaluate()`, all 4 evaluators
- **Owner**: PES enforcement system
- **Integration risk**: HIGH -- if rule_type values in config do not match engine dispatch strings, evaluator never fires
- **Validation**: Each rule's `rule_type` must be one of: `wave_ordering`, `pdc_gate`, `deadline_blocking`, `submission_immutability`, `corpus_integrity`

### proposal-state.json
- **Source of truth**: `.sbir/proposal-state.json` (per project)
- **Consumers**: All evaluators read specific fields; `JsonStateAdapter.load()` deserializes
- **Owner**: Proposal state management
- **Integration risk**: HIGH -- evaluators read specific field paths; missing fields must degrade gracefully (not crash)
- **Validation**: Each evaluator must handle missing/empty state fields without raising exceptions

### State Field Map by Evaluator

| Evaluator | State Field | Type | Graceful Default |
|-----------|------------|------|-----------------|
| PDC Gate | `pdc_status` | dict of section dicts | Empty dict -- returns False (no block) |
| PDC Gate | `pdc_status.{id}.tier_1` | string "RED"/"GREEN" | Not checked if missing |
| PDC Gate | `pdc_status.{id}.tier_2` | string "RED"/"GREEN" | Not checked if missing |
| PDC Gate | `pdc_status.{id}.red_items` | list of strings | Empty list -- no items in message |
| Deadline Blocking | `current_wave` | int | Not in non_essential_waves -- no block |
| Deadline Blocking | `topic.deadline` | ISO date string | Missing -- returns False (no block) |
| Submission Immutability | `submission.status` | string | Not "submitted" -- no block |
| Submission Immutability | `submission.immutable` | bool | Not True -- no block |
| Submission Immutability | `topic.id` | string | Falls back to rule.message |
| Corpus Integrity | `learning.outcome` | string or None | None -- no existing tag -- no block |
| Corpus Integrity | `requested_outcome_change` | string or None | None -- no change requested -- no block |

### Rule Condition Field Map

| Evaluator | Config Condition Field | Type | Purpose |
|-----------|----------------------|------|---------|
| PDC Gate | `target_wave` | int | Which wave this gate protects |
| PDC Gate | `requires_pdc_green` | bool | Activates PDC check |
| Deadline Blocking | `critical_days` | int | Days-before-deadline threshold |
| Deadline Blocking | `non_essential_waves` | list[int] | Which waves get blocked |
| Submission Immutability | `requires_immutable` | bool | Activates immutability check |
| Corpus Integrity | `append_only_tags` | bool | Activates tag protection |

### hook exit codes
- **Source of truth**: `scripts/pes/adapters/hook_adapter.py` (lines 80-86)
- **Consumers**: Claude Code runtime
- **Owner**: Hook adapter
- **Integration risk**: MEDIUM -- exit code semantics must match Claude Code protocol
- **Validation**: 0=allow, 1=block with message, 2=reject (invalid input)
