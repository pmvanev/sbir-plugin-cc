# Component Boundaries: Multi-Proposal Workspace

## Delivery Surface Distinction

This plugin has two delivery surfaces that must not be conflated:

| Surface | Location | Invoked by | Delivery method |
|---------|----------|-----------|-----------------|
| **Python (PES)** | `scripts/pes/` | Claude Code hooks via `hooks.json` | TDD with pytest (`/nw:execute`) |
| **Markdown agents** | `agents/` | Claude Code Task tool dispatch | `/nw:forge` (new) or direct edit (modify) |
| **Markdown commands** | `commands/` | User slash commands | `/nw:forge` (new) or direct edit (modify) |
| **Markdown skills** | `skills/` | Agent skill loading | `/nw:forge` (new) or direct edit (modify) |

**Key boundary**: Agents never call Python directly. They use Claude's tools (Read, Glob, Bash) to interact with the filesystem. Python code only runs via PES hooks. Therefore, "enumeration" is agent behavior (Glob + Read), not a Python service.

## New Components

### Path Resolution Module (Python -- PES only)

- **Location**: `scripts/pes/adapters/` (new module -- crafter decides exact name)
- **Responsibility**: Detect workspace layout, read active proposal pointer, derive state_dir and artifact_base paths for PES hook enforcement
- **Boundary type**: Infrastructure service (adapter layer)
- **Consumers**: Hook adapter `main()` only. Agents do their own path resolution via Read tool on `.sbir/active-proposal`.
- **Does NOT**: Read or write proposal state, enforce rules, make domain decisions

### Migration Module (Python)

- **Location**: `scripts/pes/adapters/` (new module -- crafter decides exact name)
- **Responsibility**: Move legacy state and artifacts into multi-proposal namespace, preserve originals as `.migrated`
- **Boundary type**: Infrastructure service (adapter layer)
- **Consumers**: Hook that validates migration, or agent-invoked via Bash. Design decision: if migration is a simple file copy/rename, it could be agent-driven (Bash tool) instead of Python. Crafter decides based on atomicity needs.
- **Does NOT**: Create new proposals, modify state content, enforce rules

### Proposal Switch Command (Markdown -- NEW)

- **Location**: `commands/proposal-switch.md`
- **Responsibility**: Dispatch `/sbir:proposal switch <topic-id>` to orchestrator agent
- **Boundary type**: Command entry point
- **Delivery**: `/nw:forge` to create command markdown
- **Pattern**: Same as existing `commands/proposal-status.md` -- YAML frontmatter + dispatch instructions

### Multi-Proposal Dashboard Skill (Markdown -- NEW)

- **Location**: `skills/continue/multi-proposal-dashboard.md`
- **Responsibility**: Encode dashboard enumeration patterns, display templates (table format, active/completed separation), corruption handling patterns, deadline sorting logic
- **Boundary type**: Domain knowledge (loaded by `sbir-continue` agent)
- **Delivery**: `/nw:forge` to create skill, or direct write if simple enough
- **Consumers**: `sbir-continue` agent loads this skill when multi-proposal layout detected

## Modified Components

### Python (PES) -- `code/tdd`

#### Hook Adapter (`scripts/pes/adapters/hook_adapter.py`)

- **Current**: Hardcodes `state_dir = os.path.join(os.getcwd(), ".sbir")` (line 200)
- **Change**: Call path resolution module to derive `state_dir`
- **Boundary preserved**: Still translates hook protocol to engine calls. Path resolution is delegated, not inlined.
- **Delivery**: `code/tdd` -- unit test path resolution, integration test hook adapter

#### Proposal Service (`scripts/pes/domain/proposal_service.py`)

- **Current**: Builds state and saves via `StateWriter`
- **Change**: Handle namespace collision detection, `--name` override if proposal creation has PES enforcement hooks
- **Boundary preserved**: Still owns proposal creation logic. Receives resolved `state_dir` from caller.
- **Delivery**: `code/tdd`

### Markdown Agents -- `agent/edit`

#### Continue Agent (`agents/sbir-continue.md`)

- **Current**: Reads single `.sbir/proposal-state.json`
- **Change**: Detect multi-proposal layout (check `.sbir/proposals/` via Glob). Enumerate proposals (Glob + Read each state file). Display table with active/completed separation. Deadline-driven suggestions. Load new `multi-proposal-dashboard` skill.
- **Boundary preserved**: Still read-only. Still single-turn completion.
- **Delivery**: `agent/edit` -- modify behavioral spec, add skill reference

#### Orchestrator Agent (`agents/sbir-orchestrator.md`)

- **Current**: Reads `.sbir/proposal-state.json`
- **Change**: Read `.sbir/active-proposal` to derive paths. Handle switch command routing. Auto-switch after submission. Pass resolved artifact base to specialist agents in dispatch context.
- **Boundary preserved**: Still coordinates, does not draft. Dispatches to specialists.
- **Delivery**: `agent/edit` -- modify behavioral spec

#### All Wave Agents (12 agents)

- **Current**: Reference `./artifacts/wave-N-name/` paths
- **Change**: Reference orchestrator-provided resolved artifact base path from dispatch context
- **Boundary preserved**: Agents still own their domain slice. Path is an input, not computed.
- **Delivery**: `agent/edit` (batch) -- identical substitution pattern across all 12

### Markdown Commands -- `command/edit`

#### Proposal New Command (`commands/proposal-new.md`)

- **Current**: Documents single-proposal prerequisites
- **Change**: Remove "no active proposal" prerequisite. Add `--name` flag documentation. Document multi-proposal creation context.
- **Delivery**: `command/edit`

### Markdown Skills -- `skill/edit`

#### Continue Detection Skill (`skills/continue/continue-detection.md`)

- **Current**: Detection priority assumes single `.sbir/proposal-state.json`
- **Change**: Insert multi-proposal detection priority above legacy checks. When `.sbir/proposals/` exists, route to dashboard behavior instead of single-proposal display.
- **Delivery**: `skill/edit`

#### Wave-Agent Mapping Skill (`skills/orchestrator/wave-agent-mapping.md`)

- **Current**: Command routing table has no switch command
- **Change**: Add `proposal switch` to routing table
- **Delivery**: `skill/edit`

#### Proposal State Patterns Skill (`skills/orchestrator/proposal-state-patterns.md`)

- **Current**: Documents root-level state paths
- **Change**: Document multi-proposal path conventions, active-proposal file, per-proposal namespacing
- **Delivery**: `skill/edit`

## Unchanged Components

| Component | Why Unchanged |
|-----------|---------------|
| `JsonStateAdapter` | Already parameterized with `state_dir` -- receives resolved path |
| `FileAuditAdapter` | Already parameterized with `audit_dir` -- receives resolved path |
| `FilesystemArtifactWriter` | Receives full path, creates directories as needed |
| `EnforcementEngine` | Operates on state dict, no path awareness |
| All domain services | Operate on data, not filesystem paths |
| All ports | Interface contracts unchanged |
| All existing domain rules | Evaluate state dict, path-agnostic |

## Dependency Direction

```
Commands (driving adapter)
    |
    v
Orchestrator Agent (application)
    |
    +-- Path Resolution Service (adapter layer)
    |       |
    |       +-- Filesystem (infrastructure)
    |
    +-- Domain Services (domain layer -- UNCHANGED)
    |       |
    |       +-- Ports (interfaces -- UNCHANGED)
    |               |
    |               +-- Adapters (implementations -- receive resolved paths)
```

Dependencies point inward. Path resolution is an adapter-layer concern. Domain layer remains pure.

## New Markdown Artifacts

| Type | File | Delivery | Description |
|------|------|----------|-------------|
| Command | `commands/proposal-switch.md` | `forge/command` | Dispatch switch to orchestrator |
| Skill | `skills/continue/multi-proposal-dashboard.md` | `forge/skill` | Dashboard enumeration patterns and display templates |

## Modified Slash Commands

| Command | Change | Delivery |
|---------|--------|----------|
| `/sbir:proposal new` | Multi-proposal namespace creation, collision detection, legacy migration prompt | `command/edit` |
| `/sbir:continue` | Multi-proposal dashboard with enumeration and table display | `agent/edit` + `skill/edit` |
| All wave commands | Path references use resolved paths (transparent change) | `batch/agent-edit` |
