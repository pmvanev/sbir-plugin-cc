# ADR-006: Per-Project State with Global Plugin Installation

## Status

Accepted

## Context

The plugin installs globally (Claude Code plugin registry). But proposal state is per-proposal, and users may work on multiple proposals over time. We need to decide where state lives: globally in `~/.sbir/`, locally in the project directory, or a hybrid.

## Decision

- **Plugin code:** Global. Installed via `claude plugin install`. Lives in Claude Code's plugin cache.
- **Proposal state:** Per-project. Created in the directory where the user runs `/proposal new`. State lives in `.sbir/` subdirectory of the working directory.
- **PES config:** Per-project. Copied from template on `/proposal new`. Lives in `.sbir/pes-config.json`.
- **Audit logs:** Per-project. Written to `.sbir/audit/`.
- **Corpus:** Flexible. User points at any directory. Corpus paths stored in proposal state (can be absolute or relative).
- **Company profile:** User-global. Lives at `~/.sbir/company-profile.json`. Shared across proposals.
- **Proposal artifacts:** Per-project. Written to `./artifacts/` in the working directory.

### Directory Layout (per project)

```
my-proposal-project/
├── .sbir/
│   ├── proposal-state.json
│   ├── proposal-state.json.bak
│   ├── pes-config.json
│   └── audit/
│       └── audit-2026-03-07.log
├── artifacts/
│   └── wave-1-strategy/
│       ├── compliance-matrix.md
│       ├── tpoc-questions.md
│       ├── tpoc-qa-log.md
│       └── strategy-brief.md
└── solicitations/
    └── AF243-001.pdf
```

## Alternatives Considered

### All state global (~/.sbir/)
- What: All proposals share a global state directory. State files keyed by proposal_id.
- Expected Impact: Single location for all proposal data.
- Why Rejected: Mixes proposal data across projects. Git cannot track proposal artifacts alongside proposal source material. User cannot use standard directory navigation to find their work.

### State in project root (no .sbir/ subdirectory)
- What: `proposal-state.json` directly in project root alongside other files.
- Expected Impact: Slightly simpler paths.
- Why Rejected: Pollutes the project root with state files, backup files, and audit logs. `.sbir/` subdirectory keeps plugin state contained and `.gitignore`-able if desired.

## Consequences

- **Positive:** Each proposal is a self-contained directory. Easy to archive, backup, share.
- **Positive:** Git tracks artifacts alongside proposal source material.
- **Positive:** Company profile shared across proposals (write once, use everywhere).
- **Positive:** `.sbir/` subdirectory keeps plugin internals separate from user artifacts.
- **Negative:** User must navigate to the correct directory for each proposal. Mitigated by `/proposal status` showing current state.
- **Negative:** Company profile requires separate setup step on first use. Mitigated by `/proposal new` prompting if missing.
