"""TPOC answer ingestion domain models -- answers matched to questions, delta analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class AnswerStatus(Enum):
    """Status of an answer match."""

    ANSWERED = "answered"
    UNANSWERED = "unanswered"


@dataclass
class TpocAnswer:
    """A TPOC answer matched to an original question."""

    question_id: int
    question_text: str
    answer_text: str | None
    status: AnswerStatus

    @property
    def is_answered(self) -> bool:
        return self.status == AnswerStatus.ANSWERED


@dataclass
class DeltaItem:
    """A single delta between TPOC answer and solicitation requirement."""

    question_id: int
    answer_summary: str
    solicitation_text: str
    delta: str


@dataclass
class DeltaAnalysis:
    """Comparison of TPOC answers against solicitation requirements."""

    items: list[DeltaItem] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.items)


@dataclass
class TpocIngestionResult:
    """Result of ingesting TPOC call notes."""

    answers: list[TpocAnswer] = field(default_factory=list)
    delta_analysis: DeltaAnalysis = field(default_factory=DeltaAnalysis)
    compliance_updates: list[str] = field(default_factory=list)

    @property
    def answered_count(self) -> int:
        return sum(1 for a in self.answers if a.is_answered)

    @property
    def unanswered_count(self) -> int:
        return sum(1 for a in self.answers if not a.is_answered)
