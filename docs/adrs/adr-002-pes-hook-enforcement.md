# ADR-002: PES as Python Hook-Based Enforcement

## Status

Accepted

## Context

The Proposal Enforcement System (PES) must guarantee invariants: wave ordering, compliance matrix existence gates, session startup integrity. The question is whether enforcement should be implemented as agent instructions (markdown), Python code invoked via hooks, or a hybrid.

nWave's DES (Delivery Enforcement System) provides a proven precedent: Python code invoked via Claude Code hooks, using the `PreToolUse`, `PostToolUse`, and `SessionStart` events with JSON stdin/stdout and exit codes.

## Decision

PES is implemented as Python code in `scripts/pes/`, invoked via Claude Code hooks defined in `hooks/hooks.json`. PES follows ports-and-adapters internally:

- **Hook adapter** (driver): Translates Claude Code hook JSON protocol to PES domain commands
- **Enforcement engine** (application): Evaluates rules against state, returns allow/block/warn
- **Rule registry** (application): Loads rules from `pes-config.json`, supports dynamic rule addition
- **State reader** (driven port): Reads `proposal-state.json`
- **Audit writer** (driven port): Appends to audit log

Exit codes: 0 = allow, 1 = block with message, 2 = reject (invalid input).

## Alternatives Considered

### Agent instructions only
- What: Tell agents in their markdown definitions "do not proceed if go_no_go is pending"
- Expected Impact: Would handle ~60% of enforcement cases
- Why Rejected: Agent instructions are advisory, not enforceable. An agent told "check wave ordering" can still skip the check. The spec explicitly states: "guardrails belong at the execution layer, not just in the instructions given to agents."

### Hybrid (agent instructions + hooks for critical rules)
- What: Use hooks for wave ordering and compliance gate; use agent instructions for softer checks
- Expected Impact: Would handle ~85% of cases
- Why Rejected: Creates two enforcement mechanisms with different reliability guarantees. Engineers would not know which rules are enforceable and which are advisory. Single mechanism is simpler to reason about and extend.

## Consequences

- **Positive:** Enforcement is structural, not advisory. PES physically prevents forbidden actions.
- **Positive:** Rule registry supports Phase C2/C3 extension without engine changes.
- **Positive:** Audit trail is automatic -- every enforcement decision logged.
- **Negative:** Python dependency. Plugin requires Python 3.12+ on the user's machine.
- **Negative:** Hook invocation adds latency to every tool use (~50-100ms). Acceptable for CLI tool.
- **Negative:** More complex to develop and test than agent instructions.
