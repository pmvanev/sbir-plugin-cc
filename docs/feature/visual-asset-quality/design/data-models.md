# Visual Asset Quality -- Data Models

## Style Profile

**Location**: `{artifact_base}/wave-5-visuals/style-profile.yaml`
**Owner**: sbir-formatter agent (created during style analysis)
**Consumers**: Prompt engineering (injected into STYLE section), quality summary (consistency check)

```yaml
# Style Profile Schema
solicitation_id: "N241-033"
agency: "Navy"
domain: "maritime/naval"
created_at: "2026-03-20T10:30:00Z"

palette:
  primary: "#003366"      # Navy blue
  secondary: "#6B7B8D"    # Steel gray
  accent: "#FF6B35"       # Signal orange
  highlight: "#2B7A8C"    # Ocean teal

tone: "technical-authoritative"
detail_level: "high"

avoid:
  - "cartoon/sketch style"
  - "excessive gradients"
  - "decorative elements"

notes: "Naval evaluators expect precise technical illustrations with clear component labeling"
user_adjustments:
  - "Changed highlight from #2B7A8C to #1A5F6D"
```

**Validation rules**:
- `palette` requires at least `primary` and `secondary` hex colors
- `tone` is free text (agent inference from solicitation)
- `detail_level` is one of: "low", "medium", "high"
- `avoid` is a list of strings (zero or more)

## Engineered Prompt Template Structure

**Location**: In-memory, constructed by agent from skill templates + style profile + figure spec
**Persisted as**: `prompt_hash` (SHA-256) in figure log entry

```
{figure_type_intro}

COMPOSITION: {composition_directive}
{per-figure-type layout guidance from skill}

STYLE: {tone} illustration, {palette.primary} and {palette.secondary} color scheme.
{background_directive}. {outline_directive}. {label_style}.

LABELS: {comma-separated list from figure description and compliance items}

AVOID: {avoid_list from style profile + figure-type-specific avoids from skill}

RESOLUTION: {resolution}, {aspect_ratio} aspect ratio.
```

**Template variables**:
| Variable | Source |
|----------|--------|
| `figure_type_intro` | Skill: per-type opening (e.g., "Technical illustration of...") |
| `composition_directive` | Skill: per-type composition (e.g., "Exploded isometric view") |
| `palette.*` | style-profile.yaml |
| `tone` | style-profile.yaml |
| `label list` | Figure spec description + compliance matrix items |
| `avoid_list` | style-profile.yaml avoid + skill per-type avoids |
| `resolution` | Figure spec or default "2K" |
| `aspect_ratio` | Figure spec or default "16:9" |

## Critique/Rating Model

**Location**: Recorded in figure log entry per figure
**Owner**: User provides ratings; agent records them

```yaml
# Per-figure critique entry (appended to figure-log.md)
figure_number: 3
ratings:
  composition: 4
  labels: 2
  accuracy: 4
  style_match: 5
  scale_proportion: 3
notes: "Labels too small and overlapping. Power bus connection not prominent enough."
iteration: 1          # 0 = initial, 1-3 = refinement rounds
prompt_hash: "a1b2c3..." # SHA-256 of the prompt used for this generation
flagged_categories:
  - "labels"          # Categories rated below 3
```

**Critique categories**:
| Category | Description | Rating Scale |
|----------|-------------|-------------|
| Composition | Layout clarity, hierarchy readability | 1-5 |
| Labels | All components labeled, text readability | 1-5 |
| Accuracy | Technical content correctness | 1-5 |
| Style Match | Consistency with proposal domain style | 1-5 |
| Scale/Proportion | Elements sized appropriately | 1-5 |

**Refinement threshold**: Categories rated below 3 are flagged for prompt adjustment.

**Prompt adjustment patterns** (per category, in skill):
| Flagged Category | Typical Additions | Typical Removals |
|------------------|-------------------|------------------|
| Composition | Layout directives, spacing, hierarchy cues | Conflicting layout instructions |
| Labels | Font size minimums, no-overlap, contrast backgrounds | Small font references |
| Accuracy | Specific technical corrections from user notes | Incorrect element descriptions |
| Style Match | Reinforce palette, tone, domain cues | Generic style references |
| Scale/Proportion | Relative sizing directives, prominence cues | Ambiguous sizing |

## TikZ Generation Metadata

**Location**: Figure log entry + artifact files
**Files produced**: `{artifact_base}/wave-5-visuals/{figure-name}.tex` (source) + `{figure-name}.pdf` (preview)

```yaml
# TikZ-specific figure log entry
figure_number: 2
title: "System Block Diagram"
method: "tikz"
compilation:
  compiler: "pdflatex"     # or xelatex, lualatex
  exit_code: 0
  warnings: 0
  errors: 0
source_file: "system-block-diagram.tex"
preview_file: "system-block-diagram.pdf"
status: "approved"
```

**TikZ availability conditions** (all must be true):
1. `proposal-state.json` field `output_format` == "latex"
2. LaTeX compiler detected (pdflatex, xelatex, or lualatex)
3. Figure type is diagram-compatible (system-diagram, block-diagram, process-flow, comparison)

**TikZ NOT offered for**: concept images, charts with data, timeline/Gantt

## Extended Figure Log Format

Current figure log gains new columns for quality tracking:

```markdown
# Figure Log

| # | Title | Type | Method | Iterations | Avg Rating | Prompt Hash | Status | File |
|---|-------|------|--------|-----------|------------|-------------|--------|------|
| 1 | Operational Scenario | concept | nano-banana | 2 | 4.2 | a1b2c3 | approved | op-scenario.png |
| 2 | System Block Diagram | block-diagram | tikz | 1 | 4.6 | d4e5f6 | approved | system-block.tex |
| 3 | System Architecture | system-diagram | nano-banana | 2 | 4.2 | g7h8i9 | approved | sys-arch.png |
```

New columns: `Iterations`, `Avg Rating`, `Prompt Hash`

## Quality Summary Format

**Location**: `{artifact_base}/wave-5-visuals/quality-summary.md`
**Produced**: Automatically after last figure approved, before Wave 5 checkpoint

```markdown
# Wave 5 Quality Summary

- **Proposal**: N241-033 (Compact DE System)
- **Style**: Maritime/Naval (approved)
- **Figures**: 6 total

| # | Title | Method | Iterations | Quality | Status |
|---|-------|--------|-----------|---------|--------|
| 1 | Operational Scenario | NB | 2 | 4.2/5 | OK |
| 2 | System Block Diagram | TikZ | 1 | 4.6/5 | OK |
...

- **Style Consistency**: PASS / WARN (details if WARN)
- **Cross-References**: PASS (6/6 cited)
- **Average Quality**: 4.2/5
- **Outliers**: None / Figure N flagged (category X rated Y, average Z)
```
