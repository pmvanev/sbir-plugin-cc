"""Status report domain model -- structured output from /proposal status."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class WaveDetail:
    """Status detail for a single wave."""

    wave_number: int
    name: str
    status: str
    detail: str | None = None
    completion_pct: float = 0.0


@dataclass
class AsyncEvent:
    """A pending async event requiring user action."""

    name: str
    status: str
    description: str
    days_since: int | None = None


@dataclass
class SubmissionDetail:
    """Submission status for a submitted proposal."""

    confirmation_number: str
    archive_path: str
    read_only: bool


@dataclass
class StatusReport:
    """Complete status report for a proposal."""

    current_wave: str
    progress: str
    deadline_countdown: str
    next_action: str
    waves: list[WaveDetail] = field(default_factory=list)
    async_events: list[AsyncEvent] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    error: str | None = None
    suggestion: str | None = None
    submission: SubmissionDetail | None = None
