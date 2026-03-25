# Data Models — sbir-developer-feedback

## Domain Models (`scripts/pes/domain/feedback.py`)

### FeedbackType
```python
class FeedbackType(str, Enum):
    BUG = "bug"
    SUGGESTION = "suggestion"
    QUALITY = "quality"
```

### QualityRatings
```python
@dataclass
class QualityRatings:
    past_performance: int | None  # 1–5 or None (N/A)
    image_quality: int | None
    writing_quality: int | None
    topic_scoring: int | None
```
All fields nullable. A fully null QualityRatings is valid (ratings were not applicable).

### FeedbackSnapshot
```python
@dataclass
class FeedbackSnapshot:
    # Environment
    plugin_version: str                    # git short SHA or "unknown"

    # Proposal identity
    proposal_id: str | None
    topic_id: str | None
    topic_title: str | None
    topic_agency: str | None
    topic_deadline: str | None             # ISO date string or None
    topic_phase: str | None

    # Wave progress
    current_wave: int | None
    completed_waves: list[int]             # never None, may be empty
    skipped_waves: list[int]               # never None, may be empty

    # Configuration
    rigor_profile: str | None              # "lean"|"standard"|"thorough"|"exhaustive"
    company_name: str | None
    company_profile_age_days: int | None
    finder_results_age_days: int | None
    top_scored_topics: list[dict]          # [{topic_id, composite_score, recommendation}]

    # Artifacts
    generated_artifacts: list[str]         # alphabetical filenames
```

**Privacy enforcement in `build_snapshot()`**:
- From company profile: extract only `company_name`. Do NOT extract capabilities, past_performance, key_personnel, certifications details.
- From proposal state: extract only id, title, agency, deadline, phase, current_wave, wave statuses. Do NOT extract draft content or corpus matches.
- From finder results: extract only top 5 `{topic_id, composite_score, recommendation}`. Do NOT extract full topic descriptions.

### FeedbackEntry
```python
@dataclass
class FeedbackEntry:
    feedback_id: str          # UUID v4
    timestamp: str            # ISO-8601 UTC, e.g. "2026-03-25T18:30:00Z"
    type: FeedbackType
    ratings: QualityRatings
    free_text: str | None
    context_snapshot: FeedbackSnapshot

    def to_dict(self) -> dict:
        """Serialize to JSON-compatible dict."""
        ...
```

---

## JSON Output Schema (`.sbir/feedback/feedback-{ts}.json`)

```json
{
  "feedback_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-03-25T18:30:00Z",
  "type": "quality",
  "ratings": {
    "past_performance": 2,
    "image_quality": null,
    "writing_quality": null,
    "topic_scoring": null
  },
  "free_text": "Past performance selection missed the mark — radar topic got GPS project",
  "context_snapshot": {
    "plugin_version": "6ee8407",
    "proposal_id": "proposal-a254-049",
    "topic_id": "A254-049",
    "topic_title": "Ka-Band Metamaterial Array for T&E",
    "topic_agency": "ARMY",
    "topic_deadline": "2025-11-15",
    "topic_phase": "I",
    "current_wave": 3,
    "completed_waves": [0, 1, 2],
    "skipped_waves": [],
    "rigor_profile": "standard",
    "company_name": "Acme Defense Systems",
    "company_profile_age_days": 14,
    "finder_results_age_days": 3,
    "top_scored_topics": [
      {"topic_id": "A254-049", "composite_score": 0.72, "recommendation": "GO"},
      {"topic_id": "A254-051", "composite_score": 0.58, "recommendation": "EVALUATE"}
    ],
    "generated_artifacts": [
      "strategy.md",
      "outline.md",
      "section-technical-approach.md"
    ]
  }
}
```

---

## Filename Convention

```
.sbir/feedback/feedback-{UTC-ISO-timestamp-colons-replaced}.json
```

Example: `feedback-2026-03-25T18-30-00Z.json`

Colons in ISO timestamps are replaced with hyphens for Windows filesystem compatibility. If two entries arrive within the same second (extremely unlikely), a short UUID suffix is appended: `feedback-2026-03-25T18-30-00Z-a3f2.json`.

---

## Wave Number Extraction

From `proposal-state.json`, wave numbers with status "completed" populate `completed_waves`; "skipped" populates `skipped_waves`. Wave numbers 0–9 (the plugin's 10-wave lifecycle).

```python
# In FeedbackSnapshotService.build_snapshot():
waves = state.get("waves", {})
completed_waves = [int(k) for k, v in waves.items() if v.get("status") == "completed"]
skipped_waves = [int(k) for k, v in waves.items() if v.get("status") == "skipped"]
```
