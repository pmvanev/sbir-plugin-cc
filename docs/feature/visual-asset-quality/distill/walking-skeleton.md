# Visual Asset Quality -- Walking Skeletons

## Walking Skeleton Identification

Three walking skeletons covering the three testable domain surfaces:

### WS-1: TikZ Generation Routed and Tracked

**User goal**: Phil generates a block diagram as TikZ and gets a result with audit trail.

**Observable outcome**: Result indicates TikZ format, carries prompt hash and iteration count.

**Driving port**: VisualAssetService.generate_figure()

**What it proves**: The service correctly routes "tikz" generation method to the TikZ handler and produces a result with the new tracking fields. This is the first test the software crafter should make pass.

### WS-2: Style Profile Loaded and Validated

**User goal**: Phil's approved style profile is loaded from disk with all fields present.

**Observable outcome**: Profile contains agency, domain, palette with required colors, and valid detail level.

**Driving port**: Style profile YAML parser (new domain utility)

**What it proves**: Style profiles round-trip through YAML correctly and contain all required fields. Enables downstream prompt engineering to inject style data.

### WS-3: Critique Ratings Identify Refinement Targets

**User goal**: Phil's critique identifies which categories need refinement.

**Observable outcome**: Categories below threshold are flagged; average rating computed.

**Driving port**: Critique rating model (new domain utility)

**What it proves**: The critique model correctly flags low-rated categories and computes averages. Enables the refinement loop to target specific prompt adjustments.

## Implementation Sequence

1. **WS-1 first** -- requires adding `_generate_tikz()` to VisualAssetService and `prompt_hash`/`iteration_count` fields to FigureGenerationResult. Roadmap step 01-01.

2. **WS-2 second** -- requires style profile parsing/validation utility. Roadmap step 02-01.

3. **WS-3 third** -- requires critique rating model with flagging and averaging. Roadmap step 03-02.

After walking skeletons pass, enable milestone scenarios one at a time following the milestone order.

## Stakeholder Demo Script

Each walking skeleton is demo-able:

- **WS-1**: "When Phil asks to generate a TikZ block diagram, the system routes to TikZ and produces a result with an audit hash and iteration count."
- **WS-2**: "When Phil loads his approved Navy style profile, it contains the right colors, tone, and detail level."
- **WS-3**: "When Phil rates a figure with labels 2/5, the system flags labels for refinement and computes an overall 3.6 average."
