# JTBD Analysis: Writing Style Gate Enforcement

## Job Classification

**Job Type**: Brownfield Improvement (Job 2)
**Rationale**: PES enforcement system already exists with 7 evaluators (including the recently delivered figure pipeline gate). The writer agent and quality discovery artifacts exist. Problem is identified (writer agent drafted sections in SF25D-T1201 without style discussion). Scope is clear (1 new PES evaluator + writer agent markdown changes). No discovery phase needed -- enter execution loop.

## Job Stories

### JS-1: Writing Style Enforcement (PES Layer)

**When** the writer agent begins Wave 4 drafting and quality-preferences.json does not exist at ~/.sbir/ (and the user has not explicitly skipped style selection for this proposal),
**I want to** be blocked from writing draft sections to wave-4-drafting/,
**so I can** trust that every proposal section reflects a conscious writing style choice rather than falling back to generic defaults.

#### Functional Job
Prevent the writer agent from writing section drafts to wave-4-drafting/ before quality preferences exist (or are consciously skipped). Gate operates at the PES hook layer where the agent cannot override it.

#### Emotional Job
Feel confident that the proposal's writing voice was a deliberate decision -- the user either ran quality discovery, chose a style, or explicitly opted out. No proposal silently defaults to generic prose.

#### Social Job
Present a proposal with a consistent, intentional writing voice that reflects the PI's expertise and the target agency's expectations. Evaluators notice when a proposal reads like it was carefully crafted versus auto-generated.

#### Forces Analysis
- **Push**: During the SF25D-T1201 test proposal, the writer agent drafted all sections without any style discussion. Quality discovery artifacts existed as a system capability but were never consulted. Elements of Style skill was never loaded. Winning proposal patterns were never surfaced. The result was generic prose that did not match Dr. Moreno's preferred concise, data-driven style.
- **Pull**: PES hooks are Python code that physically BLOCK non-compliant tool invocations. The figure pipeline gate (FigurePipelineGateEvaluator) proved this pattern works -- the formatter agent can no longer bypass figure planning. The same pattern applied to the writer ensures the style conversation cannot be skipped.
- **Anxiety**: What if quality discovery is genuinely unnecessary for a quick draft? The gate needs an explicit skip mechanism (writing_style_selection_skipped in per-proposal state) so users are not forced through quality discovery when they consciously choose not to.
- **Habit**: The writer agent's markdown instructions already say "when available" for quality artifacts -- graceful degradation means the agent never blocks on missing artifacts. This soft guidance is ignored because the agent prioritizes being helpful and generating content immediately.

### JS-2: Style Discussion Before Drafting (Writer Agent Layer)

**When** I start drafting a new proposal and reach Wave 4 for the first time,
**I want to** be walked through my writing style options (Strunk & White, winning proposal patterns, academic, custom) with recommendations based on my quality discovery data and the target agency,
**so I can** make an informed choice about how this proposal should read before any section is drafted.

#### Functional Job
Present available writing styles with context-aware recommendations at Wave 4 entry. Let the user choose, adjust, or skip. Record the choice in per-proposal state so it persists and informs all subsequent section drafting.

#### Emotional Job
Feel that writing style is a first-class concern, not an afterthought. The system treats tone and voice as deliberate decisions worthy of a guided conversation, just like the visual style analysis in the formatter.

#### Social Job
Demonstrate to stakeholders and reviewers that the proposal was written with intentional voice calibration -- not a random default. The PI can say "I chose concise, evidence-heavy prose matching our winning Navy proposals" rather than "it wrote whatever it wanted."

#### Forces Analysis
- **Push**: In the SF25D-T1201 session, the writer never asked about tone, whether to apply Elements of Style, whether to use winning patterns, or how to handle detail level. Dr. Moreno had no opportunity to say "write like our winning Navy proposals" or "use Strunk & White rules."
- **Pull**: A mandatory style checkpoint at Wave 4 entry (parallel to the formatter's visual style analysis) ensures the user is consulted before any drafting begins. The system recommends based on available data (quality-preferences.json, winning-patterns.json, agency match).
- **Anxiety**: Will this add friction to every proposal? The checkpoint should be quick (2-3 questions) and remember choices. If quality-preferences.json already exists and the user confirms, it takes seconds.
- **Habit**: The writer agent currently loads quality artifacts passively ("when available"). Changing to mandatory discussion at Wave 4 entry requires updating the agent's Phase 3 workflow to add a gated checkpoint before any section drafting.

## Outcome Statements

1. Minimize the likelihood that the writer agent drafts sections without a conscious writing style choice
2. Minimize the likelihood that quality discovery artifacts (tone, winning patterns, evaluator feedback) go unused during drafting
3. Maximize the confidence that every proposal section reflects the user's preferred writing style and agency-appropriate tone
4. Minimize the number of proposals drafted with generic prose when the user has strong style preferences

## Personas

### Persona 1: Dr. Rafael Moreno -- SBIR Principal Investigator

Rafael is the founder and PI at a small defense tech company (8 employees). He is writing a DoD Phase I SBIR proposal for SF25D-T1201 (autonomous sensor fusion, Air Force). He has strong opinions about writing style -- prefers concise, data-driven prose following Strunk & White principles. He was frustrated when his last proposal was drafted in generic academic style without consulting him. He wants to be asked about style preferences for each proposal. He ran quality discovery once and has quality-preferences.json at ~/.sbir/ with tone: "direct", detail_level: "high", evidence_style: "inline".

### Persona 2: Phil -- Plugin Maintainer

Phil maintains the SBIR proposal plugin and observed the writer agent ignoring quality discovery artifacts during the SF25D-T1201 test. He needs hard enforcement at the PES layer (same as figure pipeline gate) plus mandatory interactive checkpoint in the writer agent. He wants the evaluator to follow the established hexagonal architecture pattern exactly (pure domain, no infrastructure imports).

### Persona 3: Dr. Amara Okafor -- First-Time User

Dr. Okafor is a university researcher submitting her first SBIR proposal through a small spinoff. She has never run quality discovery and has no quality-preferences.json at ~/.sbir/. When the writer starts Wave 4, the style checkpoint should present sensible defaults and let her choose quickly. She should not be blocked indefinitely -- the skip option must be accessible and guilt-free. She might choose "standard" style and move on in under a minute.
