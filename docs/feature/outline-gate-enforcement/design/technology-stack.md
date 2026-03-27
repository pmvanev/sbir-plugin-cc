# Outline Gate Enforcement -- Technology Stack

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
| `scripts/pes/domain/outline_gate.py` | OutlineGateEvaluator domain class |

## Modified Production Files

| File | Change |
|---|---|
| `scripts/pes/domain/engine.py` | Register 1 evaluator (`outline_gate` -> `OutlineGateEvaluator`) |
| `scripts/pes/adapters/hook_adapter.py` | Cross-directory resolution: derive wave-3-outline/ from wave-4-drafting/, check proposal-outline.md, pass `outline_artifacts_present` in tool_context |
| `templates/pes-config.json` | Add 1 rule (`drafting-requires-outline`, type `outline_gate`) |
