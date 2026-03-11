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

## Mutation Testing Strategy

- **Strategy**: per-feature
- **Scope**: `scripts/pes/` (Python PES code only)
- **Tool**: mutmut 2.4.x (configured in `pyproject.toml`)
- **When**: After each feature delivery, scoped to modified Python files
- **Kill rate gate**: >= 80%
- **Rationale**: Under 50k LOC project with per-feature delivery cadence. PES enforces proposal invariants -- mutation testing validates that enforcement logic is meaningfully tested, not just covered.

### Running mutmut (Windows / Git Bash)

mutmut does not run natively on Windows (`please use WSL` error). Use Docker instead.
mutmut 3.x has a bug traversing `/proc` in Docker containers — use **2.4.x only**.

**Single file (recommended for per-feature scoping):**
```bash
MSYS_NO_PATHCONV=1 docker run --rm \
  -v "C:/Users/PhilVanEvery/Git/github/pmvanev/sbir-plugin-cc:/app" \
  -w /app python:3.12-slim sh -c "
pip install -q 'mutmut>=2.4,<2.5' pytest pytest-bdd jsonschema 2>/dev/null
rm -f .mutmut-cache
export PYTHONPATH=scripts
python -m mutmut run \
  --paths-to-mutate scripts/pes/domain/TARGET_FILE.py \
  --tests-dir tests/ \
  --runner 'python -m pytest tests/ -x -q' \
  --no-progress
python -m mutmut results
"
```

**Key details:**
- `MSYS_NO_PATHCONV=1` prevents Git Bash from mangling `/app` paths
- `PYTHONPATH=scripts` must be set as an **env var before mutmut**, not inside `--runner` (mutmut 2.x passes runner to `subprocess.Popen` which doesn't parse shell env vars)
- Scope to individual files for faster feedback; full `scripts/pes/` runs are slow in Docker
- Results are stored in `.mutmut-cache` inside the container (ephemeral with `--rm`)

## CI/CD

- **Platform**: GitHub Actions
- **Workflows**: `.github/workflows/ci.yml` (PR/push), `.github/workflows/release.yml` (tag push)
- **Branch strategy**: Trunk-based development. Short-lived feature branches, PR to main, CI gates required.
- **Release**: Semantic versioning via git tags (`vMAJOR.MINOR.PATCH`)
- **Branch protection**: PR required, status checks required, linear history enforced
- **Quality gates**: lint (ruff), type check (mypy), test (pytest >= 80% coverage), security (bandit)
- **Design docs**: `docs/design/sbir-proposal-plugin/`
