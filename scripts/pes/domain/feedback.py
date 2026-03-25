"""Feedback domain model -- value objects for developer feedback capture.

Pure domain module. No infrastructure imports.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class FeedbackType(Enum):
    BUG = "bug"
    SUGGESTION = "suggestion"
    QUALITY = "quality"


@dataclass(frozen=True)
class QualityRatings:
    """Immutable value object holding per-dimension quality ratings (1-5 or None)."""

    past_performance: int | None = None
    image_quality: int | None = None
    writing_quality: int | None = None
    topic_scoring: int | None = None

    def to_dict(self) -> dict[str, int | None]:
        return {
            "past_performance": self.past_performance,
            "image_quality": self.image_quality,
            "writing_quality": self.writing_quality,
            "topic_scoring": self.topic_scoring,
        }


@dataclass(frozen=True)
class FeedbackSnapshot:
    """Immutable context snapshot captured at feedback submission time."""

    plugin_version: str
    proposal_id: str | None
    topic_id: str | None
    topic_title: str | None
    topic_agency: str | None
    topic_deadline: str | None
    topic_phase: str | None
    current_wave: int | None
    completed_waves: list[int] = field(default_factory=list)
    skipped_waves: list[int] = field(default_factory=list)
    rigor_profile: str | None = None
    company_name: str | None = None
    company_profile_age_days: int | None = None
    finder_results_age_days: int | None = None
    top_scored_topics: list[dict[str, Any]] = field(default_factory=list)
    generated_artifacts: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "plugin_version": self.plugin_version,
            "proposal_id": self.proposal_id,
            "topic_id": self.topic_id,
            "topic_title": self.topic_title,
            "topic_agency": self.topic_agency,
            "topic_deadline": self.topic_deadline,
            "topic_phase": self.topic_phase,
            "current_wave": self.current_wave,
            "completed_waves": list(self.completed_waves),
            "skipped_waves": list(self.skipped_waves),
            "rigor_profile": self.rigor_profile,
            "company_name": self.company_name,
            "company_profile_age_days": self.company_profile_age_days,
            "finder_results_age_days": self.finder_results_age_days,
            "top_scored_topics": list(self.top_scored_topics),
            "generated_artifacts": list(self.generated_artifacts),
        }


@dataclass(frozen=True)
class FeedbackEntry:
    """Immutable record of a single developer feedback submission."""

    feedback_id: str
    timestamp: str
    type: FeedbackType
    ratings: QualityRatings
    free_text: str | None
    context_snapshot: FeedbackSnapshot

    def to_dict(self) -> dict[str, Any]:
        return {
            "feedback_id": self.feedback_id,
            "timestamp": self.timestamp,
            "type": self.type.value,
            "ratings": self.ratings.to_dict(),
            "free_text": self.free_text,
            "context_snapshot": self.context_snapshot.to_dict(),
        }
