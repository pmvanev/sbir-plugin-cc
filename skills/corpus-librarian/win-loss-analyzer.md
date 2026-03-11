---
name: win-loss-analyzer
description: Domain knowledge for analyzing outcome-tagged proposals and debrief feedback -- pattern extraction, weakness profiling, confidence thresholds, and agency-specific debrief handling
---

# Win/Loss Analyzer

## Domain Models

### Outcome Models (pes.domain.outcome)

| Model | Purpose | Key Fields |
|-------|---------|------------|
| `OutcomeRecord` | Records a proposal outcome | `topic_id`, `outcome_tag` (awarded/not_selected), `archived`, `discriminators`, `archive_path` |
| `PatternAnalysisResult` | Cumulative pattern analysis | `recurring_weaknesses`, `recurring_strengths`, `confidence_level`, `corpus_size`, `artifact_path` |
| `LessonsLearnedResult` | Human review checkpoint | `requires_human_acknowledgment` (always True), `status` (pending_review), `lessons`, `artifact_path` |
| `DebriefLetterResult` | Generated debrief request letter | `topic_id`, `agency`, `confirmation_number`, `content`, `file_path` |
| `DebriefSkipRecord` | User declined debrief request | `topic_id`, `status` ("debrief not requested"), `letter_created` (False) |

### Debrief Models (pes.domain.debrief)

| Model | Purpose | Key Fields |
|-------|---------|------------|
| `ReviewerScore` | Single evaluator score | `category`, `score`, `max_score` |
| `CritiqueMapping` | Critique mapped to proposal location | `section`, `page`, `comment`, `flagged_weakness` (optional) |
| `DebriefParseResult` | Raw parser output | `scores`, `critiques`, `freeform_text`, `parsing_confidence`, `is_structured` |
| `DebriefIngestionResult` | Full ingestion result | `scores`, `critique_map`, `flagged_weaknesses`, `freeform_text`, `parsing_confidence`, `artifact_path` |

## Outcome Recording

OutcomeService handles two outcome paths:

**Awarded**: Archives the proposal with outcome tag, writes `outcome-{topic_id}.json` to artifacts directory containing `{topic_id, outcome: "awarded", discriminators: []}`. Returns message suggesting Phase II pre-planning.

**Not selected**: Records as valid terminal state without archiving. Debrief can be ingested later. No archive file is created.

Outcome tags are plain strings ("awarded", "not_selected"), not enums. The `discriminators` field is initialized empty and populated later from debrief analysis.

## Agency-Specific Debrief Letter Templates

OutcomeService maps agencies to letter templates:

| Agency | Template |
|--------|----------|
| Air Force | `dod-far-15-505.md` |
| Army | `dod-far-15-505.md` |
| Navy | `dod-far-15-505.md` |
| NASA | `nasa-debrief.md` |
| Unknown agency | `dod-far-15-505.md` (default fallback) |

Letter generation substitutes `{topic_id}` and `{confirmation_number}` placeholders in the template. Output file: `debrief-request-{topic_id}.md` in the artifacts directory.

Users can skip the debrief request, which produces a `DebriefSkipRecord` with no letter artifact.

## Pattern Analysis

### Tally Algorithm

`OutcomeService._tally_patterns()` counts recurring patterns across corpus outcomes:

1. Iterates all corpus outcome entries
2. Extracts items from either the "weaknesses" or "strengths" key
3. Counts frequency of each unique string pattern
4. Returns list of `{pattern, count}` dicts sorted by count descending

This means higher-frequency patterns appear first -- the most recurring issues surface at the top.

### Confidence Thresholds

Confidence level is determined by corpus size:

| Corpus Size | Confidence Level |
|-------------|-----------------|
| >= 20 outcomes | high |
| >= 10 outcomes | medium |
| < 10 outcomes | low |

Pattern analysis writes `pattern-analysis.json` to artifacts containing: `corpus_size`, `confidence_level`, `recurring_weaknesses`, `recurring_strengths`.

Low confidence should trigger a caveat when presenting results -- patterns from fewer than 10 proposals are suggestive, not reliable.

## Debrief Ingestion

### Parsing Pipeline

DebriefService orchestrates debrief processing:

1. Delegate to `DebriefParser` port (adapter handles format-specific extraction)
2. Parser returns `DebriefParseResult` with `is_structured` flag
3. If structured: scores and critique mappings are available
4. If unstructured: only `freeform_text` is populated

### Known Weakness Flagging

When `is_structured` is True and `known_weaknesses` list is provided:

1. For each critique in the parse result:
   - Lowercase the critique comment
   - Check if any known weakness string (also lowercased) is a substring
   - If match found: create a flagged `CritiqueMapping` with `flagged_weakness` set
   - First matching weakness wins (break after first match per critique)
2. Build final critique map: flagged critiques replace their originals

This is case-insensitive substring matching, not exact match. A known weakness of "TRL gap" will flag a critique containing "the trl gap was not addressed".

### Debrief Artifact

Writes `debrief-analysis.json` containing:
- `parsing_confidence` and `is_structured` (always present)
- If structured: `scores` (category/score/max_score arrays), `critique_map`, `flagged_weaknesses`
- If unstructured: `freeform_text` only

## Known Weakness Profile

The weakness profile is built cumulatively from debrief feedback across all proposals. Structure:

```yaml
weakness_profile:
  - category: "technical_approach"
    pattern: "Insufficient detail on TRL advancement methodology"
    frequency: 3
    agencies: ["Air Force", "Navy"]
    mitigation: "Include explicit TRL entry/exit criteria with milestones"
  - category: "past_performance"
    pattern: "Weak connection between cited past work and proposed effort"
    frequency: 2
    agencies: ["DARPA"]
    mitigation: "Map each past performance citation to a specific proposal task"
```

Update rules:
- Add new weakness on first appearance in a debrief
- Increment frequency on repeat appearances in different debriefs
- Track which agencies raised the weakness (agency-specific patterns are high value)
- Include suggested mitigation based on winning proposals that addressed similar concerns

## Lessons Learned Checkpoint

`OutcomeService.present_lessons_learned()` returns a result with:
- `requires_human_acknowledgment`: always True
- `status`: "pending_review"
- `lessons`: empty list (populated by the calling agent)
- `artifact_path`: set to the artifacts directory

The corpus update does not complete until the human acknowledges the lessons. This is a hard gate -- no automated bypass.

## Loss Categorization Taxonomy

Classify losses into root cause categories:

| Category | Debrief Language Indicators |
|----------|---------------------------|
| Technical | "approach lacks detail", "TRL gap not addressed", "methodology unclear" |
| Cost | "cost not commensurate", "labor hours excessive", "indirect rates high" |
| Strategic | "limited relevant experience", "Phase III path unclear", "team lacks key expertise" |
| Past Performance | "insufficient relevant past performance", "citations not directly applicable" |
| Compliance | "did not address requirement X", "exceeded page limit", "missing required section" |

A single loss may have multiple root causes. Identify the primary category; "Technical" is the default only when no other category fits.

## Integration Points

| Consumer Agent | What It Needs | When |
|---------------|--------------|------|
| `fit-scorer` | Win rate by agency + topic area | Wave 0 -- informs Go/No-Go |
| `strategist` | Known weakness profile + agency preferences | Wave 1 -- informs strategy brief |
| `writer` | Winning section exemplars + debrief praise patterns | Wave 3-4 -- informs drafting |
| `reviewer` | Known weakness checklist + debrief critique patterns | Wave 4-7 -- review checklist |
| `debrief-analyst` | Raw debrief data + historical comparison | Wave 9 -- debrief processing |

## Artifacts Summary

| Artifact | Written By | Location |
|----------|-----------|----------|
| `outcome-{topic_id}.json` | OutcomeService.record_outcome | artifacts dir (awarded only) |
| `debrief-request-{topic_id}.md` | OutcomeService.generate_debrief_letter | artifacts dir |
| `pattern-analysis.json` | OutcomeService.update_pattern_analysis | artifacts dir |
| `debrief-analysis.json` | DebriefService._write_artifact | artifacts dir |
