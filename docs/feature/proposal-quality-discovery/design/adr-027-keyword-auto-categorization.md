# ADR-027: Keyword-Based Auto-Categorization for Evaluator Feedback

## Status

Accepted

## Context

US-QD-003 requires auto-categorization of evaluator comments into meta-writing (organization, clarity, tone, persuasiveness) vs content (technical merit, data gaps, cost issues). The user confirms or overrides each categorization.

Options range from simple keyword matching in the agent skill to NLP libraries to LLM-based classification.

Quality attributes: usability (fast, accurate-enough default with human override), maintainability (no new dependencies), simplicity (solo developer).

## Decision

Use keyword matching defined in the quality-discovery-domain skill. The agent applies keyword rules from the skill to suggest a category, then presents the categorization for user confirmation with override option.

## Alternatives Considered

### Alternative 1: NLP library (spaCy, NLTK) for semantic classification

- **Evaluation**: Higher accuracy for ambiguous comments. Could handle nuanced language ("risk table was hard to parse" = writing quality, not content). Requires Python dependency, model download (~50MB), and Docker or WSL for some processing.
- **Rejection**: Over-engineered for the use case. Evaluator comments are typically short (1-2 sentences) and use recognizable keywords. The human confirmation step catches misclassifications. Adding an NLP dependency violates the simplest-solution principle for a feature that processes 1-10 comments per session.

### Alternative 2: LLM-based classification via Claude Code

- **Evaluation**: Highest accuracy. Could understand subtle context. No new dependencies since Claude Code is already running.
- **Rejection**: Auto-categorization happens within the agent's conversation flow -- the agent IS the LLM. The agent naturally categorizes based on its understanding of the comment text and the keyword guidance from the skill. This is the actual implementation: the agent reads the keyword list from the skill and uses LLM reasoning to apply it. Framing it as "keyword matching" describes the guidance; the agent's LLM reasoning provides the actual categorization.

### Alternative 3: No auto-categorization -- user categorizes everything manually

- **Evaluation**: Simplest implementation. No misclassification risk. User has full control.
- **Rejection**: Poor usability. The interview should feel like the system understands the domain. Making the user manually classify each comment as "writing quality" or "content" adds friction and time to a flow that targets under 10 minutes. The auto-suggestion with override is the right UX trade-off.

## Consequences

### Positive

- No new Python dependencies or libraries
- Keyword list is human-readable and maintainable in the skill file
- Human override catches all misclassifications
- Agent's LLM reasoning naturally handles nuanced cases better than pure keyword matching
- Consistent with the plugin's markdown-first approach

### Negative

- Pure keyword matching would miss nuanced comments; mitigated by LLM reasoning and user override
- Keyword list needs maintenance as new evaluator language patterns emerge; mitigated by the incremental learning flow (US-QD-008) which processes real debrief language

### Keyword Categories (defined in skill)

| Category | Positive Keywords | Negative Keywords |
|----------|------------------|-------------------|
| organization_clarity | "well-organized", "clear structure", "easy to follow", "logical flow" | "difficult to follow", "hard to read", "confusing structure", "disorganized" |
| persuasiveness | "compelling", "convincing", "well-argued" | "not convincing", "unconvincing", "weak argument" |
| tone | "professional", "appropriate tone" | "too informal", "too academic", "inconsistent voice" |
| specificity | "specific", "detailed", "quantitative" | "vague", "generic", "lacked specifics" |
| content (route to weakness profile) | N/A | "lacked data", "insufficient detail", "TRL gap", "missing requirement", "cost not commensurate" |
