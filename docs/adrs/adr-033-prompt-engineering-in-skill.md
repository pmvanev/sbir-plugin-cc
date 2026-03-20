# ADR-033: Prompt Engineering Knowledge in Skill File, Not Python Code

## Status

Accepted

## Context

The visual-asset-quality feature requires engineered prompts for Nano Banana image generation. Prompts need structured sections (COMPOSITION, STYLE, LABELS, AVOID, RESOLUTION), per-figure-type templates, and style profile injection. The question is where this prompt construction logic lives.

## Decision

Prompt engineering knowledge lives in the `visual-asset-generator` skill file (markdown). The formatter agent constructs prompts by following skill templates and injecting figure-specific content. No Python code constructs prompts.

## Alternatives Considered

### Alternative 1: Python prompt builder service
- **What**: A Python class `PromptBuilder` in `scripts/pes/domain/` that takes a FigurePlaceholder and style profile, returns a structured prompt string.
- **Expected impact**: Testable via pytest, type-safe template composition.
- **Why rejected**: Prompt construction is an LLM-mediated activity -- the agent uses its reasoning to fill templates with context-appropriate content. A rigid Python template cannot adapt to solicitation-specific nuances. The agent reads the skill, reads the solicitation, and synthesizes -- this is fundamentally agent behavior, not deterministic code. Also, the agent cannot call Python directly; it would need a hook, which is unnecessary complexity.

### Alternative 2: JSON prompt templates with variable substitution
- **What**: JSON files with `{{variable}}` placeholders, agent fills in values.
- **Expected impact**: More structured than markdown, parseable.
- **Why rejected**: Over-constrains the agent. Prompt engineering benefits from LLM reasoning about what composition directive fits a specific figure. JSON templates make substitution mechanical when it should be intelligent. Markdown skill guidance is the right level of structure.

## Consequences

- **Positive**: Prompt templates easy to iterate (edit markdown, no code changes, no tests to update)
- **Positive**: Agent applies LLM reasoning to template application -- adapts to solicitation context
- **Positive**: Consistent with existing plugin architecture (skills = domain knowledge for agents)
- **Negative**: Not unit-testable. Validated through forge checklist and end-to-end usage.
- **Negative**: Prompt quality depends on skill file quality. Mitigated by structured template format with clear sections.
