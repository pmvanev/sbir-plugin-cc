"""Strategy brief domain model -- strategy sections and brief for Wave 1 checkpoint."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class StrategyStatus(Enum):
    """Status of strategy brief lifecycle."""

    NOT_STARTED = "not_started"
    GENERATED = "generated"
    APPROVED = "approved"
    REVISION_REQUESTED = "revision_requested"


class CheckpointDecision(Enum):
    """Human checkpoint decision for strategy alignment."""

    APPROVE = "approve"
    REVISE = "revise"
    SKIP = "skip"


REQUIRED_SECTION_KEYS = [
    "technical_approach",
    "trl",
    "teaming",
    "phase_iii",
    "budget",
    "risks",
]


@dataclass
class StrategySection:
    """A single section of the strategy brief."""

    key: str
    title: str
    content: str


@dataclass
class StrategyBrief:
    """Complete strategy brief covering all required dimensions."""

    sections: list[StrategySection] = field(default_factory=list)
    tpoc_available: bool = False
    revision_feedback: str | None = None

    @property
    def section_keys(self) -> set[str]:
        """Return set of section keys present in the brief."""
        return {s.key for s in self.sections}

    @property
    def covers_required_sections(self) -> bool:
        """Check whether all required sections are present."""
        return all(k in self.section_keys for k in REQUIRED_SECTION_KEYS)

    def get_section(self, key: str) -> StrategySection | None:
        """Return section by key, or None if not found."""
        for s in self.sections:
            if s.key == key:
                return s
        return None
