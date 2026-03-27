# PES Figure Pipeline Enforcement -- Technology Stack

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
| `scripts/pes/domain/figure_pipeline_gate.py` | FigurePipelineGateEvaluator domain class |
| `scripts/pes/domain/style_profile_gate.py` | StyleProfileGateEvaluator domain class |

## Modified Production Files

| File | Change |
|---|---|
| `scripts/pes/domain/engine.py` | Register 2 evaluators, add `tool_context` to `evaluate()` and `_rule_triggers()` |
| `scripts/pes/adapters/hook_adapter.py` | Extract file_path, resolve artifact existence, pass tool_context |
| `templates/pes-config.json` | Add 2 rules (figure_pipeline_gate, style_profile_gate) |
