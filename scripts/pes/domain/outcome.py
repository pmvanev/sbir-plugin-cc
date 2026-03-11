"""Outcome domain model -- debrief request letter results and skip records."""

from __future__ import annotations

from dataclasses import dataclass


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
