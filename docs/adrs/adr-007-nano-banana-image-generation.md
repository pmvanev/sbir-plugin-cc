# ADR-007: Google Gemini Nano Banana for Proposal Figure Generation

## Status

Accepted

## Context

SBIR proposals benefit from visual assets: system architecture diagrams, deployment scenario illustrations, concept figures, and technical infographics. The plugin's formatter agent (Wave 5) generates these figures.

For structural diagrams (flowcharts, architecture, timelines), local tools like Mermaid, Graphviz, and inline SVG work well. However, concept figures, technical illustrations, and operational scenario visualizations require richer image generation that boxes-and-arrows cannot provide.

The original design punted these to "external briefs" — specification files the user would take to Napkin.ai or Canva and generate manually, breaking the CLI workflow.

## Decision

Use Google Gemini's Nano Banana image generation API for concept figures, technical illustrations, and infographics.

**Integration approach:**
- A shell script (`scripts/nano-banana-generate.sh`) wraps the Gemini REST API
- The formatter agent invokes it via the Bash tool with a crafted prompt
- API key read from `GEMINI_API_KEY` environment variable
- Model: `gemini-3.1-flash-image-preview` (speed-optimized, supports aspect ratio and resolution control)
- Output: PNG files written to `./artifacts/wave-5-visuals/`

**Method selection hierarchy for the formatter:**
1. SVG/Mermaid/Graphviz — structural diagrams (preferred for precision)
2. Nano Banana — concept figures, illustrations, infographics
3. External brief — fallback when no tools/API available

## Consequences

### Positive

- Eliminates the "external brief" workflow break for most concept figures
- Keeps the user in the CLI throughout Wave 5
- Free tier allows 500 images/day — sufficient for proposal work
- Aspect ratio and resolution control matches proposal formatting needs
- SynthID watermarking provides provenance tracking

### Negative

- Introduces an external API dependency (first network dependency in the plugin)
- Requires user to obtain and configure a Google API key
- Image quality depends on prompt engineering — the skill file must encode good prompting patterns
- Generated images may need manual refinement for highly technical or agency-specific visuals

### Mitigations

- **Optional dependency:** If `GEMINI_API_KEY` is not set, the formatter falls back to external briefs. No functionality is lost — the workflow just requires manual figure generation.
- **Prompt engineering in skill:** The `visual-asset-generator` skill includes SBIR-specific prompt templates and guidance for the formatter agent.
- **Local-first principle preserved:** The API key is the only credential. No proposal content is sent to the API — only figure prompts (descriptive text, not proposal prose).
- **No vendor lock-in:** The shell script is a thin wrapper. Swapping to a different image generation API requires only changing the script, not the agent or skill.

## Alternatives Considered

### 1. DALL-E (OpenAI)
- Similar capability but requires a separate OpenAI API key
- No free tier for image generation
- Less control over aspect ratio and resolution

### 2. Stable Diffusion (local)
- No API dependency — runs locally
- Requires significant GPU resources and setup
- Not practical for the target user (small business engineer, CLI-native)

### 3. SVG-only (no AI generation)
- No external dependency
- Cannot produce concept figures, illustrations, or realistic visualizations
- Already used for structural diagrams — this decision adds to it, not replaces

### 4. Keep external briefs only
- No dependency, no API key
- Breaks the CLI workflow — user must leave Claude Code to generate figures
- Adds friction that discourages visual assets in proposals
