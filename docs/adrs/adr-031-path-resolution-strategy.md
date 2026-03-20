# ADR-031: Path Resolution Strategy

## Status

Proposed

## Context

The hook adapter currently hardcodes `state_dir = os.path.join(os.getcwd(), ".sbir")`. Multi-proposal support requires deriving `state_dir` and `artifact_base` from the active proposal. The resolution must support three layouts: fresh workspace, multi-proposal, and legacy single-proposal. Every consumer (hook adapter, agent dispatch, commands) must resolve identically.

## Decision

Centralized path resolution service in the adapter layer. Single function/class that:

1. Checks `.sbir/proposals/` existence (multi-proposal indicator)
2. If present: reads `.sbir/active-proposal`, validates proposal directory exists, returns namespaced paths
3. If absent but `.sbir/proposal-state.json` exists: returns root paths (legacy mode)
4. If neither: returns fresh workspace indicator

The hook adapter `main()` calls this service instead of hardcoding paths. Agents receive resolved paths from the orchestrator dispatch context.

## Alternatives Considered

### Alternative 1: Environment variable injection

- **What**: Hook command in `hooks.json` includes a shell script that resolves the active proposal and sets `SBIR_STATE_DIR` env var before invoking Python.
- **Evaluation**: Keeps Python code simple. Resolution happens in shell.
- **Why rejected**: Shell-based resolution is harder to test, harder to maintain, and platform-dependent (bash vs cmd). Resolution logic should be testable Python code.

### Alternative 2: Per-consumer resolution (no centralization)

- **What**: Each consumer (hook adapter, agent, command) independently reads `.sbir/active-proposal` and derives paths.
- **Evaluation**: No new module needed. Each consumer owns its path logic.
- **Why rejected**: Violates DRY. Risk of inconsistent resolution across consumers. Bug in one consumer could read wrong proposal state while another reads correctly. Centralization eliminates this class of bugs.

### Alternative 3: Resolution in domain layer

- **What**: Path resolution as a domain service with a port interface.
- **Evaluation**: Maximum testability via port mocking.
- **Why rejected**: Path resolution is infrastructure (filesystem structure detection), not domain logic. Placing it in domain would violate the ports-and-adapters principle that domain is infrastructure-free. The adapter layer is the correct location.

## Consequences

### Positive
- Single point of truth for path resolution -- all consumers guaranteed consistent
- Testable: resolution function takes CWD as input, returns path strings
- Backward-compatible: legacy detection is the fallback path, not a special case
- Hook adapter change is minimal: replace one line (`os.path.join(os.getcwd(), ".sbir")`) with a function call

### Negative
- New module to maintain (mitigated by small size -- ~50-80 lines of production code)
- All consumers gain a dependency on the resolution service (acceptable: it replaces ad-hoc path construction)
