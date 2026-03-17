---
name: quality-discovery-domain
description: Domain knowledge for quality discovery -- feedback taxonomy, auto-categorization keywords, confidence thresholds, and artifact schemas for all 4 phases
---

# Quality Discovery Domain Knowledge

## Artifact Locations

All quality artifacts live at `~/.sbir/`:
- `quality-preferences.json` -- writing style preferences (Phase 2)
- `winning-patterns.json` -- proposal ratings and win patterns (Phase 1 + Phase 4)
- `writing-quality-profile.json` -- categorized evaluator feedback (Phase 3 + Phase 4)

## Quality Rating Scale

Ratings for past proposals:
- **weak** -- significant issues identified, would not use as a template
- **adequate** -- acceptable quality, some areas for improvement
- **strong** -- high quality, represents best practices to replicate

## Confidence Thresholds

Based on total win count in the analyzed corpus:
- **low** -- fewer than 10 wins analyzed
- **medium** -- 10 to 19 wins analyzed
- **high** -- 20 or more wins analyzed

Confidence affects how strongly downstream agents weight discovered patterns.

## Feedback Taxonomy

### Categories

Each evaluator comment is categorized into exactly one category:

| Category | Description | Applies To |
|----------|-------------|------------|
| `organization_clarity` | Document structure, readability, flow | Meta-writing |
| `persuasiveness` | Convincing arguments, compelling narrative | Meta-writing |
| `tone` | Voice, formality, accessibility | Meta-writing |
| `specificity` | Level of detail, precision, evidence depth | Content |

### Sentiment

Each comment has exactly one sentiment:
- **positive** -- evaluator praised this aspect
- **negative** -- evaluator flagged this as a weakness

### Section Tags

Comments are tagged with the proposal section they apply to:
- `technical_approach`
- `sow` (statement of work)
- `commercialization`
- `general` (cross-cutting or section not identified)

## Auto-Categorization Keywords

### Meta-Writing Keywords

These keywords trigger auto-categorization as meta-writing feedback:

**organization_clarity**: "difficult to follow", "hard to read", "well-organized", "clear", "confusing", "unclear", "verbose", "concise", "wordy", "dense", "readable", "scattered", "disjointed"

**persuasiveness**: "persuasive", "compelling", "convincing", "unconvincing", "weak argument", "strong case", "not supported"

**tone**: "too informal", "too formal", "appropriate tone", "professional", "casual", "academic"

### Content Keywords

These keywords trigger auto-categorization as content feedback:

**specificity**: "lacked data", "insufficient detail", "TRL gap", "no evidence", "missing milestones", "cost justification", "market analysis", "competitive landscape", "risk mitigation", "vague", "unsubstantiated"

### Auto-Categorization Rules

1. Scan comment text for keyword matches (case-insensitive)
2. If meta-writing keyword found, assign matching category
3. If content keyword found, assign `specificity`
4. If both types match, prefer meta-writing (more actionable for writing style)
5. If no keywords match, set `auto_categorized: false` and prompt user
6. All auto-categorizations require user confirmation (`user_confirmed` field)

## Artifact Schemas

### quality-preferences.json

```json
{
  "schema_version": "1.0",
  "updated_at": "ISO-8601",
  "tone": "formal_authoritative | direct_data_driven | conversational_accessible | custom",
  "tone_custom_description": "string (required when tone is custom)",
  "detail_level": "high_level | moderate | deep_technical",
  "evidence_style": "inline_quantitative | narrative_supporting | table_heavy",
  "organization": "short_paragraphs | medium_paragraphs | long_flowing",
  "practices_to_replicate": ["string"],
  "practices_to_avoid": ["string"]
}
```

**Field descriptions**:
- `tone` -- overall voice. Enum values or custom with description.
- `detail_level` -- how deep the technical explanations go
- `evidence_style` -- how data and evidence are presented
- `organization` -- paragraph length and text flow preference
- `practices_to_replicate` -- specific writing habits the user wants to keep
- `practices_to_avoid` -- specific writing habits the user wants to eliminate

### winning-patterns.json

```json
{
  "schema_version": "1.0",
  "updated_at": "ISO-8601",
  "confidence_level": "low | medium | high",
  "win_count": 0,
  "proposal_ratings": [
    {
      "topic_id": "string",
      "agency": "string",
      "topic_area": "string",
      "outcome": "WIN | LOSS | ONGOING",
      "quality_rating": "weak | adequate | strong",
      "winning_practices": ["string"],
      "evaluator_praise": ["string"],
      "rated_at": "ISO-8601"
    }
  ],
  "patterns": [
    {
      "pattern": "string",
      "frequency": 0,
      "agencies": ["string"],
      "source_proposals": ["string"],
      "universal": false,
      "first_seen": "ISO-8601",
      "last_seen": "ISO-8601"
    }
  ]
}
```

**Field descriptions**:
- `confidence_level` -- derived from `win_count` using confidence thresholds
- `proposal_ratings` -- individual proposal assessments from Phase 1
- `patterns` -- cross-proposal patterns detected in Phase 4
- `universal` -- true if pattern appears across multiple agencies

### writing-quality-profile.json

```json
{
  "schema_version": "1.0",
  "updated_at": "ISO-8601",
  "entries": [
    {
      "comment": "string",
      "topic_id": "string",
      "agency": "string",
      "outcome": "WIN | LOSS | ONGOING",
      "category": "organization_clarity | persuasiveness | tone | specificity",
      "sentiment": "positive | negative",
      "section": "technical_approach | sow | commercialization | general",
      "auto_categorized": true,
      "user_confirmed": true,
      "added_at": "ISO-8601"
    }
  ],
  "agency_patterns": [
    {
      "agency": "string",
      "discriminators": ["string"],
      "positive_count": 0,
      "negative_count": 0
    }
  ]
}
```

**Field descriptions**:
- `entries` -- individual categorized evaluator comments from Phase 3
- `auto_categorized` -- true if keywords matched, false if user provided category
- `user_confirmed` -- true after user confirms or overrides auto-categorization
- `agency_patterns` -- cross-proposal patterns per agency, detected in Phase 4

## Atomic Write Protocol

All artifact writes follow the same atomic protocol:
1. Write to `{artifact}.tmp`
2. If existing file, backup to `{artifact}.bak`
3. Rename `.tmp` to target filename
4. Verify write by reading back

This prevents partial corruption if the process is interrupted.

## Incremental Update Protocol

When updating existing artifacts:
1. Read existing artifact
2. Merge new data additively (append to arrays, update scalars)
3. Deduplicate array entries by key field (`topic_id` for ratings, `comment` for entries)
4. Recalculate derived fields (`confidence_level`, `win_count`, `agency_patterns`)
5. Update `updated_at` timestamp
6. Write atomically

## Downstream Consumers

| Artifact | Consumer Agent | How Used |
|----------|---------------|----------|
| `winning-patterns.json` | sbir-strategist | Filters patterns by current agency, cites in strategy brief |
| `quality-preferences.json` | sbir-writer | Applies tone, detail, organization to draft output |
| `writing-quality-profile.json` | sbir-writer | Surfaces quality alerts for matching agency/section |
| `winning-patterns.json` | sbir-reviewer | Checks proposal against winning practices |
| `writing-quality-profile.json` | sbir-reviewer | Flags practices-to-avoid violations |

All downstream consumption is graceful -- missing artifacts produce informational notes, never errors.
