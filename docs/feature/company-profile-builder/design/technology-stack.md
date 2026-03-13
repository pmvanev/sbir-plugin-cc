# Company Profile Builder -- Technology Stack

## Stack Overview

No new technologies introduced. All choices reuse existing project patterns and dependencies.

| Component | Technology | Version | License | Rationale |
|-----------|-----------|---------|---------|-----------|
| Profile agent | Markdown (Claude Code agent) | N/A | N/A | Plugin convention per ADR-001. All agents are markdown. |
| Profile skill | Markdown | N/A | N/A | Plugin convention. Domain knowledge loaded on demand. |
| Profile commands | Markdown (Claude Code command) | N/A | N/A | Plugin convention per ADR-001. |
| Validation service | Python | 3.12+ | PSF (OSS) | Consistent with all PES code. Team expertise. |
| Schema definition | JSON Schema | Draft 2020-12 | N/A | Standard schema language. Machine-readable validation. |
| Schema validation | `jsonschema` | 4.x | MIT | Already a project dependency (used by PES). |
| JSON I/O | Python `json` stdlib | 3.12+ | PSF (OSS) | No additional dependency. |
| File operations | Python `pathlib` stdlib | 3.12+ | PSF (OSS) | Consistent with `JsonStateAdapter`. |
| Document reading (local) | Claude Code Read tool | N/A | Proprietary (Anthropic) | Required -- agent tool for file reading. |
| Document reading (URL) | Bash `curl` | System | MIT-like | Agent Bash tool for HTTP fetch. Already used in project. |

## Technology Decisions

### Why Python for validation (not agent-only)

LLM-based validation is probabilistic. A CAGE code of "7X2K" might pass LLM validation in edge cases. Profile data feeds into fit scoring that drives Go/No-Go decisions worth 10-15 hours of proposal effort. Deterministic validation via `jsonschema` + custom rules eliminates this risk.

See ADR-013 for full alternatives analysis.

### Why not a separate validation library

Considered `pydantic` (MIT) for schema validation as an alternative to `jsonschema`. Rejected because:
- `jsonschema` is already a project dependency
- Adding `pydantic` increases dependency surface for a single feature
- `jsonschema` + custom validation functions are sufficient for this scope

### Why no database

Profile is a single JSON file per user. No query requirements, no relational structure, no concurrent access. JSON on disk is the simplest option. Consistent with ADR-004 (JSON files for state persistence).
