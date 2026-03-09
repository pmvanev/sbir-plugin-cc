"""TPOC question domain model -- questions generated from solicitation gaps."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class QuestionCategory(Enum):
    """Category of TPOC question by source."""

    AMBIGUITY = "ambiguity"
    COMPLIANCE_GAP = "compliance_gap"
    STRATEGIC_PROBE = "strategic_probe"


# Priority ordering: lower number = higher priority
CATEGORY_PRIORITY: dict[QuestionCategory, int] = {
    QuestionCategory.AMBIGUITY: 1,
    QuestionCategory.COMPLIANCE_GAP: 2,
    QuestionCategory.STRATEGIC_PROBE: 3,
}


@dataclass
class TpocQuestion:
    """A single TPOC question derived from solicitation analysis."""

    question_id: int
    text: str
    category: QuestionCategory
    source_item_id: int | None = None
    rationale: str | None = None

    @property
    def priority(self) -> int:
        """Priority based on category. Lower = more important."""
        return CATEGORY_PRIORITY.get(self.category, 99)


@dataclass
class TpocQuestionSet:
    """Collection of TPOC questions, ordered by strategic priority."""

    questions: list[TpocQuestion] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.questions)

    def sorted_by_priority(self) -> list[TpocQuestion]:
        """Return questions ordered by strategic priority."""
        return sorted(self.questions, key=lambda q: (q.priority, q.question_id))

    def by_category(self, category: QuestionCategory) -> list[TpocQuestion]:
        """Return questions filtered by category."""
        return [q for q in self.questions if q.category == category]
