# ADR-001: Plugin Architecture Follows nWave Conventions

## Status

Accepted

## Context

The SBIR Proposal Plugin must integrate with Claude Code as a first-class plugin. Claude Code has a defined plugin protocol (agents, commands, hooks, skills as files in a specific directory structure). nWave is a mature, production-tested Claude Code plugin that has established conventions for this protocol.

We need to decide whether to follow nWave's conventions, invent our own structure, or use a hybrid approach.

## Decision

Follow nWave's plugin structure exactly:

- `.claude-plugin/plugin.json` for plugin metadata
- `agents/` for agent markdown files with YAML frontmatter
- `commands/` for slash command markdown files
- `hooks/hooks.json` for event-to-command mappings
- `scripts/` for Python enforcement code
- `skills/` for domain knowledge per agent
- `rules/` for auto-loaded Claude Code rules

Agent files prefixed with `sbir-` to namespace within Claude Code's agent registry.

## Alternatives Considered

### Custom directory structure
- What: Invent a different layout (e.g., `src/agents/`, `config/hooks/`)
- Why Rejected: No benefit. Claude Code expects specific paths. Custom structure would require additional mapping configuration and confuse developers familiar with nWave.

### Monolithic plugin file
- What: Single large plugin configuration file instead of per-agent files
- Why Rejected: Violates Claude Code plugin protocol. Agents must be individual markdown files. A single file would exceed size limits and prevent independent agent evolution.

## Consequences

- **Positive:** Developers familiar with nWave can immediately navigate the codebase. Plugin installation and discovery work out of the box. Agent, command, and skill patterns are proven.
- **Positive:** Phase C2/C3 agents can be added by dropping new files into existing directories.
- **Negative:** Locked to Claude Code's plugin protocol. If the protocol changes, we adapt.
- **Negative:** `sbir-` prefix on every agent file adds visual noise but prevents namespace collisions.
