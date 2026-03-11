"""Outcome domain model -- debrief request letter results, skip records, and outcome records."""

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
