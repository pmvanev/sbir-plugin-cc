# ADR-011: Visual Asset Generation -- Local-First with API Fallback

## Status

Accepted

## Context

Wave 5 requires generating figures from outline placeholders. Figure types include block diagrams, flow charts, Gantt charts, data charts, concept illustrations, and photographs. Some types are amenable to local generation (diagrams), others require image generation APIs (concept illustrations), and some cannot be generated at all (photographs).

The system already integrates with Google Gemini Nano Banana API for concept figures (ADR-007). The question is how to handle the broader spectrum of figure types.

## Decision

Tiered generation strategy:

1. **Mermaid** (local, via Claude Code's native Mermaid rendering) for block diagrams, flow charts, Gantt charts, sequence diagrams
2. **Graphviz** (local, DOT language) for network topologies and complex relationship graphs
3. **SVG generation** (local, Python) for simple data charts and comparison tables
4. **Gemini API** (remote, existing) for concept illustrations and infographics
5. **External brief** (fallback) for photographs and figures that cannot be generated

All generated figures exported as SVG or PNG. The VisualAssetPort abstracts generation method; the adapter routes to the appropriate tool based on `generation_method` from figure classification.

## Alternatives Considered

### Alternative 1: All figures via Gemini API
- **What**: Send all figure descriptions to Gemini for image generation
- **Expected impact**: Unified approach, one integration point
- **Why rejected**: Diagrams (architecture, flow, Gantt) are better described structurally via Mermaid/Graphviz. API-generated diagrams lack precision for technical proposals. Network dependency for every figure. Cost per API call at 3-5 figures per proposal.

### Alternative 2: matplotlib/seaborn for all charts
- **What**: Python chart library for data visualizations
- **Expected impact**: Publication-quality charts
- **Why rejected**: Adds heavyweight dependencies. Most SBIR figures are structural diagrams, not data visualizations. The few data charts can be handled by SVG generation. If matplotlib is needed later, it can be added as another adapter behind the same port.

### Alternative 3: Claude Code artifact rendering only
- **What**: Rely entirely on Claude Code's ability to render Mermaid and create SVG artifacts
- **Expected impact**: Zero additional dependencies
- **Why rejected**: Claude Code can render Mermaid but cannot produce Graphviz natively. SVG generation for charts requires programmatic control. Limiting to Claude Code's built-in capabilities covers ~60% of figure types.

## Consequences

- **Positive**: Local-first means most figures generated without network dependency.
- **Positive**: Mermaid is already supported by Claude Code -- no new tooling for the majority of figures.
- **Positive**: External brief fallback ensures no figure type blocks progress.
- **Negative**: Graphviz requires `graphviz` system package. Graceful degradation: if not installed, Graphviz figures fall back to external brief.
- **Negative**: Multiple generation methods add complexity to the VisualAssetPort adapter. Mitigated by clear classification in FigurePlaceholder.generation_method.
