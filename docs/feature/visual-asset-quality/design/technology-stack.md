# Visual Asset Quality -- Technology Stack

## Stack Decisions

All technologies are already in use by the project. This feature introduces no new dependencies.

| Technology | Version | License | Purpose | Status |
|-----------|---------|---------|---------|--------|
| Python | 3.12+ | PSF (MIT-like) | PES domain model extension (TikZ routing, FigureGenerationResult fields) | Existing |
| pytest | 8.x | MIT | TDD for Python domain model changes | Existing |
| Google Gemini API | gemini-3.1-flash-image-preview | API ToS (free tier) | Nano Banana image generation (unchanged) | Existing |
| pdflatex/xelatex/lualatex | System-installed | LPPL / GPL | TikZ compilation and verification | Existing (detected by setup wizard) |
| YAML | 1.2 | N/A (data format) | Style profile persistence | New usage, no new library (agent writes YAML as text) |
| SHA-256 | N/A | N/A (algorithm) | Prompt hash for audit traceability | New usage, Python stdlib `hashlib` |
| Markdown | N/A | N/A (format) | Agent specs, skill files, quality summary | Existing |

## No New Dependencies Rationale

| Considered | Decision | Rationale |
|-----------|----------|-----------|
| PyYAML library | Not needed | Agent writes YAML as formatted text via Write tool. No Python parsing needed -- style profile is consumed by the agent, not Python code. |
| Pillow/PIL for image analysis | Not needed | Critique is human-driven (user rates). No automated image quality analysis. |
| TikZ Python wrapper | Not needed | Agent generates TikZ code via LLM, compiles via subprocess. No Python TikZ library needed. |
| Prompt template library (Jinja2, etc.) | Not needed | Prompt construction is agent behavior using skill templates. String formatting in markdown, not code. |

## Delivery Method Summary

| Method | Count | Technologies Used |
|--------|-------|-------------------|
| `skill/edit` | 1 | Markdown (visual-asset-generator enhancement) |
| `forge/skill` | 1 | Markdown (visual-style-intelligence new skill) |
| `agent/edit` | 1 | Markdown (sbir-formatter enhancement) |
| `command/edit` | 2 | Markdown (wave visuals + draft figure commands) |
| `code/tdd` | 3 | Python 3.12, pytest (domain model, service, adapter) |
