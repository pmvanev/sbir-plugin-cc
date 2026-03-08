# SBIR Proposal Plugin -- Project Instructions

## What This Is

A Claude Code plugin for the SBIR/STTR proposal lifecycle. Multi-agent system with markdown agents, skills, and commands. PES (Proposal Enforcement System) is Python code invoked via Claude Code hooks.

## Architecture

- Architecture document: `docs/architecture/architecture.md`
- ADRs: `docs/adrs/`
- User stories: `docs/feature/sbir-proposal-plugin/discuss/user-stories.md`
- Specification: `sbir-proposal-plugin.md`

## Development Paradigm

**OOP with Ports and Adapters** for the PES Python code (`scripts/pes/`).

- Domain rules are pure Python objects with no infrastructure imports
- Ports are abstract interfaces in `scripts/pes/ports/`
- Adapters implement ports for specific infrastructure (file system, Claude Code hooks)
- Dependencies point inward: adapters -> application -> domain

**Markdown convention** for agents, commands, skills, and rules:
- Follow nWave plugin structure exactly
- Agents: YAML frontmatter + behavioral specification, 200-400 lines max
- Commands: YAML frontmatter + dispatch to agent, context files listed
- Skills: domain knowledge loaded on demand by agents

## Project Layout

```
sbir-plugin-cc/
  .claude-plugin/plugin.json     -- Plugin metadata
  agents/                        -- Agent markdown files (sbir-*.md)
  commands/                      -- Slash command markdown files
  hooks/hooks.json               -- PES hook event mappings
  scripts/pes/                   -- PES Python code (ports-and-adapters)
  skills/                        -- Domain knowledge per agent
  templates/                     -- JSON/Markdown templates
  rules/                         -- Auto-loaded Claude Code rules
  docs/architecture/             -- Architecture document
  docs/adrs/                     -- Architecture Decision Records
```

## Key Conventions

- State lives in `.sbir/` subdirectory of the user's project
- Company profile is global at `~/.sbir/company-profile.json`
- Artifacts written to `./artifacts/wave-N-name/`
- PES hook protocol: JSON stdin/stdout, exit codes 0=allow, 1=block, 2=reject
- Atomic state writes: write to .tmp, backup to .bak, rename .tmp to target

## Testing

- PES Python code: TDD with pytest, ports-and-adapters enables isolated testing
- Agents/commands/skills: validated via nWave forge checklist (no unit tests for markdown)
- Integration: end-to-end scenarios from user stories (39 scenarios in Phase C1)
