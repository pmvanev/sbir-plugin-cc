# ADR-027: Separate Partner-Builder Agent

## Status

Accepted

## Context

Partnership management requires a profile-building capability for research institution partners. The existing `sbir-profile-builder` agent handles company profiles through a conversational interview with web research pre-population. The partner profile shares the same UX pattern (mode select, research, gather, preview, validate and save) but has different domain knowledge:

- 6 sections (basics, capabilities, personnel, **facilities**, **past collaborations**, **STTR eligibility**) vs. company profile's 6 sections (basics, capabilities, personnel, **certifications**, **past performance**, **research partners**)
- Combined capability analysis (company + partner) in the preview phase
- Screening mode (lightweight readiness assessment before full profile creation)
- Partner management operations (list, update, delete across multiple partner files)

The nWave agent convention limits agents to 200-400 lines. The existing profile-builder is ~300 lines. Adding partner-specific sections, screening mode, and combined preview would exceed this limit.

ADR-005 establishes the principle: one agent per domain role.

## Decision

Create a new `sbir-partner-builder` agent with its own `partner-domain` skill, separate from the existing `sbir-profile-builder`.

## Alternatives Considered

### Alternative 1: Extend sbir-profile-builder to handle both entity types

- **Evaluation**: Shares code/pattern. But adds ~150 lines for partner-specific sections, ~50 for screening mode, ~50 for combined preview. Total ~550 lines, exceeding the 400-line limit.
- **Rejection**: Violates nWave agent size convention and ADR-005 (one agent per domain role). Company profiles and partner profiles are different domain concepts with different consumers.

### Alternative 2: Abstract base pattern with two thin agents

- **Evaluation**: Extract common interview pattern into a shared skill, create two thin agent wrappers.
- **Rejection**: Over-engineering. The agents share a UX pattern but not domain logic. The skill system already provides knowledge sharing. Two independent agents with independent skills is simpler and more maintainable.

## Consequences

- **Positive**: Each agent stays within size limits. Domain knowledge is cleanly separated. Screening mode lives naturally in the partner agent.
- **Positive**: Familiar pattern for the developer -- partner-builder is modeled on profile-builder.
- **Negative**: Some structural duplication (mode select, research, preview phases). Acceptable because the domain content within each phase differs.
