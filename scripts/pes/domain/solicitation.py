"""Solicitation domain model -- parsed metadata from solicitation documents."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TopicInfo:
    """Parsed solicitation metadata."""

    topic_id: str
    agency: str
    phase: str
    deadline: str
    title: str


@dataclass
class SolicitationParseResult:
    """Outcome of parsing a solicitation document."""

    topic: TopicInfo | None = None
    error: str | None = None
    warnings: list[str] | None = None

    @property
    def success(self) -> bool:
        return self.topic is not None and self.error is None
