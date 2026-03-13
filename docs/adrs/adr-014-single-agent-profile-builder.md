# ADR-014: Single Agent for Setup and Update Flows

## Status

Accepted

## Context

The Company Profile Builder has two entry flows: initial setup (create from scratch via interview/documents) and selective update (modify one section of existing profile). These could be implemented as one agent handling both flows or two separate agents.

Quality attributes: **maintainability** (minimize agent count), **usability** (consistent interaction patterns).

## Decision

A single `sbir-profile-builder` agent handles both setup and update flows. The dispatching command passes mode context (setup vs. update). The agent's workflow branches based on mode.

## Alternatives Considered

### Alternative 1: Two agents (sbir-profile-creator + sbir-profile-updater)

- **Pros**: Smaller per-agent files. Clear separation of concerns.
- **Cons**: Shared domain knowledge duplicated or cross-referenced. Two agents to maintain for closely related functionality. User mental model splits an atomic concept (profile management) across two agents.
- **Rejected because**: Both flows share validation, preview, atomic write, and schema knowledge. The combined agent stays within 200-400 line limit. Two agents would duplicate shared behavior or require a shared skill that contains flow logic (violating skill-as-knowledge convention).

### Alternative 2: Extend sbir-topic-scout with inline profile creation

- **Pros**: No new agent. Profile creation triggered naturally when profile is missing.
- **Cons**: Mixes scoring responsibility with profile management. Topic scout already has substantial behavior. Does not support standalone profile update. Would exceed 400-line agent limit.
- **Rejected because**: Violates single-responsibility. Topic scout should read profiles, not create them. ADR-005 established one agent per domain role.

## Consequences

- **Positive**: Single agent for all profile operations. Consistent user experience. Shared validation/preview/save logic without duplication.
- **Positive**: Stays within 200-400 line agent limit (estimated ~300 lines).
- **Negative**: Agent has branching logic (setup vs update mode). Slightly more complex than a single-flow agent.
- **Trade-off**: Minor internal complexity vs. significant reduction in agent count and knowledge duplication.
