# ADR-025: Dedicated Quality Discoverer Agent

## Status

Accepted

## Context

Proposal quality discovery requires a guided Q&A flow (4 steps: past proposal review, style interview, evaluator feedback extraction, artifact assembly) plus an incremental update mode after proposal cycles. This workflow needs a home in the agent ecosystem.

Three candidate locations exist: extend the setup wizard, extend the corpus librarian, or create a new dedicated agent.

Quality attributes driving this decision: maintainability (agent line limits, single-responsibility), usability (independent invocation at any lifecycle point), extensibility (update mode separate from initial discovery).

## Decision

Create a new `sbir-quality-discoverer` agent with a dedicated skill (`quality-discovery-domain`), three commands (`quality discover`, `quality update`, `quality status`), and additive extensions to five existing agents for downstream consumption.

## Alternatives Considered

### Alternative 1: Extend setup wizard with quality discovery phases

- **Evaluation**: Setup wizard is ~180 lines. Adding 4 discovery steps (past proposal review with per-entry iteration, style interview with 6 dimensions, evaluator feedback extraction with auto-categorization, artifact assembly) would add ~200 lines, exceeding the 400-line agent limit. The update mode (US-QD-008) has no logical home in setup.
- **Rejection**: Violates line limit. Setup wizard is for one-time configuration; quality discovery is a recurring lifecycle activity invokable at any time.

### Alternative 2: Extend corpus librarian with quality tagging

- **Evaluation**: Corpus librarian manages document indexing, search, and outcome tracking. Quality discovery is a guided user interview producing structured preferences and ratings -- fundamentally different from corpus operations. Librarian is already ~200 lines with image reuse functionality.
- **Rejection**: Violates single-responsibility. Interview-based knowledge capture is a different domain from document indexing. Would create a "god agent" anti-pattern.

### Alternative 3: Embed in profile builder as "quality profile" extension

- **Evaluation**: Profile builder manages company-profile.json. Quality artifacts are separate files with different schemas and different consumers. Quality discovery reads the company profile (read-only) but writes to different artifacts.
- **Rejection**: Different data ownership. Quality artifacts have different lifecycle (updated per proposal cycle, not per company setup). Would conflate two distinct concerns.

## Consequences

### Positive

- Each agent remains under 400 lines with clear single responsibility
- Quality discovery invokable independently: `/sbir:proposal quality discover`, `/sbir:proposal quality update`
- Update mode naturally fits as an agent mode flag, not a grafted-on setup wizard phase
- Setup wizard can delegate to quality discoverer via Task tool (same pattern as profile builder delegation)
- Consistent with ADR-005 (one agent per domain role)

### Negative

- One more agent file to maintain (total agents: 13 -> 14)
- Downstream agents require additive modifications (~10-15 lines each for 3 agents)
- New skill file and 3 new command files added to plugin

### Trade-offs

- Agent count increases by 1, but each agent stays focused and within line limits
- Five existing agents modified, but all changes are additive (new skill loading rows, new artifact reads) with no existing behavior removed
