# ADR-036: Rigor Model Resolution Mechanism

## Status

Accepted

## Context

The rigor profile feature introduces per-proposal quality/cost configuration across all 18 agents. The highest-scored opportunity outcome (16.5) is "minimize the likelihood of an agent ignoring the configured rigor level." All 18 agents use `model: inherit` in YAML frontmatter -- they do not specify their own model. The question is: how does a rigor profile (e.g., "thorough" = strongest model for the writer) mechanically control which model an agent uses at runtime?

Three options were evaluated:

### Option A: Orchestrator passes model override via Task tool

The orchestrator reads rigor-profile.json, looks up the agent's role in rigor-profiles.json, and passes the resolved model tier to the Task tool's `model` parameter when dispatching. The orchestrator skill (wave-agent-mapping) includes the rigor resolution logic.

- **Pros**: Single enforcement point in orchestrator. Agent markdown files unchanged. Clear audit trail (orchestrator logs which model it selected).
- **Cons**: Claude Code's Task tool does not expose a `model` parameter for overriding the subagent's model. The `model` field in agent frontmatter is the only model selection mechanism in the Claude Code plugin protocol. This option is architecturally impossible within the current runtime.

### Option B: PES hook intercepts agent dispatch and injects model

A PES PreToolUse hook detects when an agent is being dispatched and modifies the event to inject a model override based on the active rigor profile.

- **Pros**: Centralized enforcement at the platform level. Agents and orchestrator unchanged.
- **Cons**: The Claude Code hook protocol allows hooks to allow/block/reject actions but does not support modifying tool parameters. Hooks return exit codes and optional messages -- they cannot rewrite the dispatching payload. This option is architecturally impossible within the current runtime.

### Option C: Orchestrator reads rigor config and instructs agents via prompt context

The orchestrator reads rigor-profile.json and rigor-profiles.json, resolves the model tier and behavioral parameters (review passes, critique iterations, iteration cap) for each agent role, and includes this as structured context in the Task tool prompt when dispatching. The agent receives its behavioral parameters as part of the task instruction. For model tier, the orchestrator instructs itself to use the appropriate model name when invoking the Task tool -- since `model: inherit` means "use the caller's model," the orchestrator is the caller and can set the model field in the Task tool invocation (the `model` parameter exists on Task tool invocations in Claude Code).

**Correction on Task tool model parameter**: The Claude Code Task tool DOES accept a `model` parameter that overrides the agent's frontmatter `model` field. When frontmatter says `model: inherit`, the agent inherits the caller's model. But the Task tool invocation can explicitly set `model: "claude-sonnet-4-20250514"` (or any valid model ID) to override. This is the mechanism.

- **Pros**: Works within the existing Claude Code runtime. No changes to the hook protocol. Agents remain `model: inherit`. Behavioral parameters (review depth, critique iterations) naturally flow as task context. Model override is explicit and auditable in the Task tool invocation.
- **Cons**: Requires orchestrator skill update to include rigor resolution. Orchestrator must map model tiers (basic/standard/strongest) to concrete model IDs. Model ID mapping needs a configuration source.

## Decision

**Option C: Orchestrator reads rigor config and passes model + behavioral parameters when dispatching agents via Task tool.**

The resolution chain:
1. Orchestrator loads `.sbir/proposals/{topic-id}/rigor-profile.json` to get active profile name
2. Orchestrator loads `config/rigor-profiles.json` to get profile definition
3. For each agent dispatch, orchestrator looks up the agent's role in the profile definition
4. Orchestrator resolves model tier (basic/standard/strongest) to concrete model ID via `config/model-tiers.json`
5. Orchestrator passes `model: "<resolved-model-id>"` to Task tool invocation
6. Orchestrator includes behavioral parameters (review passes, critique iterations, iteration cap) in the task prompt

If rigor-profile.json is missing (pre-rigor proposal), orchestrator defaults to "standard" profile behavior.

## Consequences

### Positive

- Works within existing Claude Code plugin protocol -- no runtime changes needed
- Single enforcement point: orchestrator is the only agent that dispatches others
- Behavioral parameters (not just model) are configurable per profile
- Model tier abstraction (basic/standard/strongest) decouples from specific model names
- Backward compatible: missing rigor-profile.json defaults to standard

### Negative

- Orchestrator becomes responsible for rigor resolution (increased complexity)
- Model ID mapping (tier -> concrete model name) needs maintenance as Anthropic releases new models
- If a user bypasses the orchestrator and invokes an agent directly, rigor is not enforced (mitigation: PES could warn on direct agent invocation without rigor context, but this is a Phase 2 concern)
