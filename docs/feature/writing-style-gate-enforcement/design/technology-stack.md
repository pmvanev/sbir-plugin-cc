# Writing Style Gate Enforcement -- Technology Stack

All technology reused from existing PES enforcement system. No new dependencies.

## Reused Stack

| Component | Technology | Version | License | Rationale |
|---|---|---|---|---|
| Runtime | Python | 3.12+ | PSF | Existing PES runtime |
| Testing | pytest | 8.x | MIT | Existing test framework |
| Testing | pytest-bdd | 7.x | MIT | Existing BDD acceptance tests |
| Linting | ruff | 0.x | MIT | Existing CI lint gate |
| Type checking | mypy | 1.x | MIT | Existing CI type gate |
| Security | bandit | 1.x | Apache 2.0 | Existing CI security gate |
| Mutation | mutmut | 2.4.x | BSD | Existing per-feature mutation testing |
| Config format | JSON | -- | -- | pes-config.json, existing format |
| State format | JSON | -- | -- | proposal-state.json, existing format |

## New Production Files

| File | Purpose |
|---|---|
| `scripts/pes/domain/writing_style_gate.py` | WritingStyleGateEvaluator domain class |

## Modified Production Files

| File | Change |
|---|---|
| `scripts/pes/domain/engine.py` | Register WritingStyleGateEvaluator in _evaluators dict |
| `scripts/pes/adapters/hook_adapter.py` | Add wave-4-drafting/ detection + global artifact resolution at ~/.sbir/ |
| `templates/pes-config.json` | Add 1 rule (writing_style_gate) |

## Modified Markdown Files

| File | Change |
|---|---|
| `agents/sbir-writer.md` | Add style checkpoint before first section draft in Phase 3 |
| `commands/proposal-draft.md` | Update prerequisites to include style checkpoint |
