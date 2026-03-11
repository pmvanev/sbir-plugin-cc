"""Outcome domain model -- debrief request letter results, skip records, outcome records,
pattern analysis results, and lessons learned results."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DebriefLetterResult:
    """Result of generating a debrief request letter."""

    topic_id: str
    agency: str
    confirmation_number: str
    content: str
    file_path: str


@dataclass(frozen=True)
class DebriefSkipRecord:
    """Record of a skipped debrief request."""

    topic_id: str
    status: str
    letter_created: bool


@dataclass(frozen=True)
class OutcomeRecord:
    """Result of recording a proposal outcome (awarded or not_selected)."""

    topic_id: str
    outcome_tag: str
    archived: bool
    discriminators: list[str] = field(default_factory=list)
    debrief_artifacts_created: bool = False
    archive_path: str = ""
    message: str = ""


@dataclass(frozen=True)
class PatternAnalysisResult:
    """Result of cumulative win/loss pattern analysis across corpus."""

    recurring_weaknesses: list[dict[str, object]] = field(default_factory=list)
    recurring_strengths: list[dict[str, object]] = field(default_factory=list)
    confidence_level: str = "low"
    corpus_size: int = 0
    artifact_path: str = ""


@dataclass(frozen=True)
class LessonsLearnedResult:
    """Result of presenting lessons learned for human review checkpoint."""

    requires_human_acknowledgment: bool = True
    status: str = "pending_review"
    lessons: list[str] = field(default_factory=list)
    artifact_path: str = ""
