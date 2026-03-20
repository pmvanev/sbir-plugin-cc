---
name: visual-style-intelligence
description: Domain-aware visual style intelligence for SBIR proposals -- agency style database, style profile schema, recommendation workflow, and prompt integration guidance
---

# Visual Style Intelligence

## Purpose

Provides domain-specific visual style recommendations based on the target agency and technical domain. The formatter agent loads this skill at the start of Wave 5 to recommend a style profile that applies consistently to all Nano Banana prompts in the proposal.

## Agency-Domain Style Database

Each entry defines the visual language that resonates with evaluators in that domain.

### Navy

```yaml
agency: Navy
domains:
  - maritime
  - naval
  - undersea warfare
  - directed energy (naval)
  - shipboard systems
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
  - "land-centric imagery in maritime context"
notes: "Naval evaluators expect precise technical illustrations with clear component labeling. Use clean sightlines and structured layouts. Ship silhouettes and maritime operational environments are familiar visual anchors."
```

### Air Force

```yaml
agency: Air Force
domains:
  - aerospace
  - space-based ISR
  - satellite systems
  - avionics
  - directed energy (airborne)
  - cyber operations
palette:
  primary: "#191970"      # Midnight blue
  secondary: "#C0C0C0"    # Silver
  accent: "#0047AB"       # Electric blue
  highlight: "#FFD700"    # Accent gold
tone: "precision-aerospace"
detail_level: "high"
avoid:
  - "ground-centric imagery for space topics"
  - "atmospheric effects in orbital scenes"
  - "cluttered backgrounds"
  - "rounded/organic shapes for technical systems"
notes: "Air Force evaluators value precision and clean geometry. For space topics, dark backgrounds are acceptable for operational context scenes but white backgrounds are safer for technical diagrams. Aerospace color language emphasizes blues, silvers, and golds."
```

### Army

```yaml
agency: Army
domains:
  - ground systems
  - soldier systems
  - C4ISR
  - logistics
  - rotary wing
  - ground vehicles
palette:
  primary: "#2D4A1E"      # Army olive
  secondary: "#5C4033"    # Earth brown
  accent: "#C19A6B"       # Desert tan
  highlight: "#8B0000"    # Signal red
tone: "operational-practical"
detail_level: "medium"
avoid:
  - "overly abstract representations"
  - "complex layered compositions"
  - "non-standard military symbology"
  - "decorative flourishes"
notes: "Army evaluators favor straightforward, operationally grounded illustrations. Show systems in field context. Use MIL-STD symbology where applicable. Practical, no-nonsense visual language. Diagrams should emphasize ruggedness and operational readiness."
```

### DARPA

```yaml
agency: DARPA
domains:
  - advanced research
  - breakthrough technology
  - AI/ML
  - quantum
  - biotechnology
  - hypersonics
palette:
  primary: "#1B1B3A"      # Deep indigo
  secondary: "#4A90D9"    # Bright blue
  accent: "#00CED1"       # Cyan
  highlight: "#FF4500"    # Innovation orange-red
tone: "cutting-edge-technical"
detail_level: "high"
avoid:
  - "conventional/dated visual styles"
  - "clip art or stock imagery"
  - "low-information-density layouts"
  - "incremental/evolutionary framing"
notes: "DARPA evaluators expect visuals that convey technological ambition and scientific rigor. High information density is acceptable. Diagrams should communicate novelty -- show what is new, not what is standard. Concept figures should feel forward-looking without being speculative."
```

### NASA

```yaml
agency: NASA
domains:
  - space exploration
  - earth science
  - aeronautics
  - life support systems
  - propulsion
  - planetary science
palette:
  primary: "#0B3D91"      # NASA blue
  secondary: "#FC3D21"    # NASA red
  accent: "#FFFFFF"       # White (space context)
  highlight: "#FF8C00"    # Deep orange
tone: "scientific-precise"
detail_level: "high"
avoid:
  - "science fiction aesthetic"
  - "artistic license with physics"
  - "unlabeled or ambiguous components"
  - "low-resolution or pixelated elements"
notes: "NASA evaluators value scientific accuracy and clear data presentation. Diagrams should reflect engineering precision. Use NASA visual identity colors where appropriate. Label everything. Data visualizations should cite sources and include units."
```

### Generic (Fallback)

```yaml
agency: generic
domains:
  - default
  - unknown agency
  - multi-agency
palette:
  primary: "#2563EB"      # Professional blue
  secondary: "#4B5563"    # Neutral gray
  accent: "#D97706"       # Amber
  highlight: "#059669"    # Green
tone: "professional-neutral"
detail_level: "medium"
avoid:
  - "cartoon/sketch style"
  - "excessive decoration"
  - "agency-specific branding"
  - "photorealistic people"
notes: "Generic fallback for agencies not in the style database (e.g., NIST, DOE, DHS, NIH). Clean, professional aesthetic. The user should be prompted to provide domain-specific preferences. This profile is a starting point, not a final recommendation."
```

## Style Profile Schema

The style profile is a YAML file persisted at `{artifact_base}/wave-5-visuals/style-profile.yaml`.

### Schema Definition

```yaml
# Required fields
solicitation_id: string    # e.g., "N241-033"
agency: string             # e.g., "Navy", "Air Force", "DARPA"
domain: string             # e.g., "maritime/naval", "aerospace/space-based ISR"
created_at: string         # ISO 8601 timestamp

# Required: palette (minimum primary + secondary)
palette:
  primary: string          # Hex color, required
  secondary: string        # Hex color, required
  accent: string           # Hex color, optional
  highlight: string        # Hex color, optional

# Required
tone: string               # Free text, agent-inferred from solicitation
detail_level: string       # One of: "low", "medium", "high"

# Optional
avoid: list[string]        # Zero or more style directives to avoid
notes: string              # Agent rationale or domain-specific guidance

# Populated after user review
user_adjustments: list[string]  # Audit trail of user changes
```

### Validation Rules

| Field | Rule |
|-------|------|
| `solicitation_id` | Required, non-empty string |
| `agency` | Required, non-empty string |
| `domain` | Required, non-empty string |
| `created_at` | Required, valid ISO 8601 |
| `palette.primary` | Required, valid hex color (`#RRGGBB`) |
| `palette.secondary` | Required, valid hex color (`#RRGGBB`) |
| `palette.accent` | Optional, valid hex color if present |
| `palette.highlight` | Optional, valid hex color if present |
| `tone` | Required, non-empty string |
| `detail_level` | Required, one of `low`, `medium`, `high` |
| `avoid` | Optional, list of strings |
| `user_adjustments` | Optional, list of strings, append-only |

### Hex Color Validation

Valid: `#003366`, `#FF6B35`, `#0B3D91`
Invalid: `003366` (no hash), `#GG0000` (non-hex), `blue` (named color), `#333` (shorthand)

## Recommendation Workflow

The formatter agent follows this sequence at the start of Wave 5:

### Step 1: Read Solicitation Context

Extract from the solicitation and proposal state:
- Agency name (from `solicitation-id` prefix or solicitation metadata)
- Topic area / domain keywords
- Any explicit format or branding requirements in the solicitation

### Step 2: Match Agency-Domain

1. Match `agency` against the style database entries above (case-insensitive).
2. If matched, use that entry as the baseline recommendation.
3. If no match, use the **Generic** entry and inform the user: "Agency {name} not in style database. Recommending generic professional style."

### Step 3: Present Recommendation

Display to the user:
- Recommended palette with color swatches (hex codes)
- Tone description
- Detail level
- Avoid list
- Agent notes explaining why this style was selected

### Step 4: User Review and Adjustment

The user can:
- **Approve as-is**: Profile saved immediately
- **Adjust palette**: Change individual colors (record in `user_adjustments`)
- **Adjust tone**: Modify tone text
- **Adjust detail level**: Change between low/medium/high
- **Add avoid items**: Append to avoid list
- **Provide custom preferences**: Free text merged into notes

Every user adjustment is recorded in `user_adjustments` for audit trail.

### Step 5: Persist Profile

Write the finalized profile to `{artifact_base}/wave-5-visuals/style-profile.yaml`.

### Step 6: Skip Option

If no Nano Banana figures are planned (all figures use SVG, Mermaid, Graphviz, or TikZ), style analysis is **optional**. Inform the user: "No Nano Banana figures planned. Style analysis is optional. Proceed without style profile? [yes / create profile anyway]"

## Prompt Integration

When constructing engineered prompts (see `visual-asset-generator` skill), inject style profile values into the STYLE section:

```
STYLE: {tone} illustration, {palette.primary} and {palette.secondary} color scheme.
White background. Clean outlines. Labels in {palette.primary} with high contrast.
```

If `palette.accent` or `palette.highlight` are defined, include them for emphasis elements:

```
Use {palette.accent} for callout arrows and emphasis markers.
Use {palette.highlight} for secondary groupings or status indicators.
```

Append the `avoid` list to the prompt's AVOID section:

```
AVOID: {style_profile.avoid joined by ", "}, {figure-type-specific avoids}
```

## Style Consistency Checking

At Wave 5 conclusion (quality summary step), verify consistency:

1. For each Nano Banana figure, extract the palette colors used in its prompt (from `prompt_hash` lookup or stored prompt metadata).
2. Compare against the approved `style-profile.yaml` palette.
3. If any figure's prompt palette deviates from the approved profile:
   - Flag as **WARN** in the quality summary
   - Identify the specific figure and the deviant color
   - Offer to regenerate with the approved palette

A deviation occurs when a prompt uses a hex color not in the approved palette for a style-significant element (primary, secondary, accent, highlight).
