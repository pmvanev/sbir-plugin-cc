"""Unit tests for TPOC question generation through TpocService (driving port).

Test Budget: 5 behaviors x 2 = 10 unit tests max.
Tests enter through driving port (TpocService).
Domain objects (ComplianceMatrix, TpocQuestion, TpocQuestionSet) are real collaborators.
"""

from __future__ import annotations

import pytest

from pes.domain.compliance import (
    ComplianceItem,
    ComplianceMatrix,
    RequirementType,
)
from pes.domain.tpoc import QuestionCategory
from pes.domain.tpoc_service import ComplianceMatrixRequiredError, TpocService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_matrix(
    ambiguity_count: int = 3, clear_count: int = 5
) -> ComplianceMatrix:
    """Build a compliance matrix with ambiguous and clear items."""
    items: list[ComplianceItem] = []
    for i in range(ambiguity_count):
        items.append(ComplianceItem(
            item_id=i + 1,
            text=f"Requirement {i + 1}",
            requirement_type=RequirementType.SHALL,
            ambiguity=f"Ambiguous: unclear scope for requirement {i + 1}",
        ))
    for i in range(clear_count):
        items.append(ComplianceItem(
            item_id=ambiguity_count + i + 1,
            text=f"Clear requirement {ambiguity_count + i + 1}",
            requirement_type=RequirementType.SHALL,
        ))
    return ComplianceMatrix(items=items)


def _make_service() -> TpocService:
    """Wire TpocService (no driven ports needed)."""
    return TpocService()


# ---------------------------------------------------------------------------
# Behavior 1: Generates questions from ambiguities
# ---------------------------------------------------------------------------


class TestGenerateQuestionsFromAmbiguities:
    def test_generates_questions_from_flagged_ambiguities(self):
        matrix = _make_matrix(ambiguity_count=3)
        service = _make_service()

        result = service.generate_questions(matrix)

        ambiguity_questions = result.by_category(QuestionCategory.AMBIGUITY)
        assert len(ambiguity_questions) == 3

    def test_each_ambiguity_question_references_source_item(self):
        matrix = _make_matrix(ambiguity_count=2)
        service = _make_service()

        result = service.generate_questions(matrix)

        ambiguity_questions = result.by_category(QuestionCategory.AMBIGUITY)
        source_ids = {q.source_item_id for q in ambiguity_questions}
        assert source_ids == {1, 2}


# ---------------------------------------------------------------------------
# Behavior 2: Questions are categorized by type
# ---------------------------------------------------------------------------


class TestQuestionCategorization:
    def test_includes_strategic_probes_alongside_ambiguities(self):
        matrix = _make_matrix(ambiguity_count=2)
        service = _make_service()

        result = service.generate_questions(matrix)

        categories = {q.category for q in result.questions}
        assert QuestionCategory.AMBIGUITY in categories
        assert QuestionCategory.STRATEGIC_PROBE in categories

    def test_all_questions_have_valid_category(self):
        matrix = _make_matrix(ambiguity_count=3)
        service = _make_service()

        result = service.generate_questions(matrix)

        assert all(
            isinstance(q.category, QuestionCategory) for q in result.questions
        )


# ---------------------------------------------------------------------------
# Behavior 3: Questions ordered by strategic priority
# ---------------------------------------------------------------------------


class TestPriorityOrdering:
    def test_ambiguities_appear_before_strategic_probes(self):
        matrix = _make_matrix(ambiguity_count=2)
        service = _make_service()

        result = service.generate_questions(matrix)

        sorted_qs = result.sorted_by_priority()
        priorities = [q.priority for q in sorted_qs]
        assert priorities == sorted(priorities)
        # Ambiguity priority (1) should come before strategic probe (3)
        assert sorted_qs[0].category == QuestionCategory.AMBIGUITY


# ---------------------------------------------------------------------------
# Behavior 4: No compliance matrix raises error
# ---------------------------------------------------------------------------


class TestNoComplianceMatrix:
    def test_none_matrix_raises_compliance_matrix_required(self):
        service = _make_service()

        with pytest.raises(ComplianceMatrixRequiredError) as exc_info:
            service.generate_questions(None)

        assert "compliance matrix" in str(exc_info.value).lower()

    def test_error_message_includes_guidance(self):
        service = _make_service()

        with pytest.raises(ComplianceMatrixRequiredError) as exc_info:
            service.generate_questions(None)

        message = str(exc_info.value).lower()
        assert "required" in message or "strategy" in message


# ---------------------------------------------------------------------------
# Behavior 5: Matrix with no ambiguities still produces strategic probes
# ---------------------------------------------------------------------------


class TestNoAmbiguities:
    def test_generates_strategic_probes_with_no_ambiguities(self):
        matrix = _make_matrix(ambiguity_count=0, clear_count=5)
        service = _make_service()

        result = service.generate_questions(matrix)

        assert result.count > 0
        assert all(
            q.category == QuestionCategory.STRATEGIC_PROBE
            for q in result.questions
        )
