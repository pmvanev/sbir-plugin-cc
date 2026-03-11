"""Debrief domain model -- parsed debrief results, critique mappings, and ingestion outcomes."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ReviewerScore:
    """A single reviewer score from the debrief."""

    category: str
    score: float
    max_score: float


@dataclass(frozen=True)
class CritiqueMapping:
    """A critique mapped to a specific proposal section and page."""

    section: str
    page: int
    comment: str
    flagged_weakness: str | None = None


@dataclass(frozen=True)
class DebriefParseResult:
    """Raw output from the debrief parser adapter."""

    scores: list[ReviewerScore] = field(default_factory=list)
    critiques: list[CritiqueMapping] = field(default_factory=list)
    freeform_text: str | None = None
    parsing_confidence: float = 0.0
    is_structured: bool = False


@dataclass(frozen=True)
class DebriefIngestionResult:
    """Result of ingesting a debrief through DebriefService."""

    scores: list[ReviewerScore] = field(default_factory=list)
    critique_map: list[CritiqueMapping] = field(default_factory=list)
    flagged_weaknesses: list[str] = field(default_factory=list)
    freeform_text: str | None = None
    parsing_confidence: float = 0.0
    artifact_path: str | None = None
    message: str = ""
