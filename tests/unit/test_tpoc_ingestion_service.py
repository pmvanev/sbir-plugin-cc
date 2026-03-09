"""Unit tests for TPOC answer ingestion through TpocIngestionService (driving port).

Test Budget: 6 behaviors x 2 = 12 unit tests max.
Tests enter through driving port (TpocIngestionService).
Domain objects (TpocQuestionSet, ComplianceMatrix, TpocIngestionResult) are real collaborators.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pes.domain.compliance import (
    ComplianceItem,
    ComplianceMatrix,
    RequirementType,
)
from pes.domain.tpoc import QuestionCategory, TpocQuestion, TpocQuestionSet
from pes.domain.tpoc_ingestion import AnswerStatus
from pes.domain.tpoc_ingestion_service import (
    NotesFileNotFoundError,
    TpocIngestionService,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_questions(count: int = 3) -> TpocQuestionSet:
    """Build a TpocQuestionSet with numbered questions."""
    return TpocQuestionSet(questions=[
        TpocQuestion(
            question_id=i + 1,
            text=f"Question {i + 1}?",
            category=QuestionCategory.AMBIGUITY,
            source_item_id=i + 1,
        )
        for i in range(count)
    ])


def _make_matrix(count: int = 3) -> ComplianceMatrix:
    """Build a ComplianceMatrix with items matching question source IDs."""
    return ComplianceMatrix(items=[
        ComplianceItem(
            item_id=i + 1,
            text=f"Requirement {i + 1}: system shall do thing {i + 1}",
            requirement_type=RequirementType.SHALL,
            ambiguity=f"Unclear scope for requirement {i + 1}",
        )
        for i in range(count)
    ])


def _write_notes(tmp_path: Path, answers: dict[int, str]) -> Path:
    """Write structured call notes with Q/A pairs."""
    notes_path = tmp_path / "tpoc-call-notes.txt"
    lines = ["TPOC Call Notes\n\n"]
    for qnum, answer_text in sorted(answers.items()):
        lines.append(f"Q{qnum} Answer: {answer_text}\n")
    notes_path.write_text("".join(lines))
    return notes_path


def _make_service() -> TpocIngestionService:
    """Wire TpocIngestionService (no driven ports needed)."""
    return TpocIngestionService()


# ---------------------------------------------------------------------------
# Behavior 1: Matches answers to original questions
# ---------------------------------------------------------------------------


class TestMatchAnswersToQuestions:
    def test_matches_answers_by_question_number(self, tmp_path):
        questions = _make_questions(count=3)
        matrix = _make_matrix(count=3)
        answers = {1: "Answer one.", 2: "Answer two.", 3: "Answer three."}
        notes_path = _write_notes(tmp_path, answers)
        service = _make_service()

        result = service.ingest_notes(notes_path, questions, matrix)

        answered = [a for a in result.answers if a.status == AnswerStatus.ANSWERED]
        assert len(answered) == 3
        assert answered[0].answer_text == "Answer one."
        assert answered[0].question_id == 1

    def test_each_answer_includes_original_question_text(self, tmp_path):
        questions = _make_questions(count=2)
        matrix = _make_matrix(count=2)
        notes_path = _write_notes(tmp_path, {1: "Answer one."})
        service = _make_service()

        result = service.ingest_notes(notes_path, questions, matrix)

        answered = [a for a in result.answers if a.status == AnswerStatus.ANSWERED]
        assert answered[0].question_text == "Question 1?"


# ---------------------------------------------------------------------------
# Behavior 2: Marks unanswered questions
# ---------------------------------------------------------------------------


class TestMarkUnansweredQuestions:
    def test_unanswered_questions_marked_with_unanswered_status(self, tmp_path):
        questions = _make_questions(count=3)
        matrix = _make_matrix(count=3)
        notes_path = _write_notes(tmp_path, {1: "Answer one."})
        service = _make_service()

        result = service.ingest_notes(notes_path, questions, matrix)

        unanswered = [a for a in result.answers if a.status == AnswerStatus.UNANSWERED]
        assert len(unanswered) == 2
        unanswered_ids = {a.question_id for a in unanswered}
        assert unanswered_ids == {2, 3}

    def test_unanswered_questions_have_no_answer_text(self, tmp_path):
        questions = _make_questions(count=2)
        matrix = _make_matrix(count=2)
        notes_path = _write_notes(tmp_path, {1: "Answer one."})
        service = _make_service()

        result = service.ingest_notes(notes_path, questions, matrix)

        unanswered = [a for a in result.answers if a.status == AnswerStatus.UNANSWERED]
        assert unanswered[0].answer_text is None


# ---------------------------------------------------------------------------
# Behavior 3: Generates delta analysis from answers
# ---------------------------------------------------------------------------


class TestDeltaAnalysis:
    def test_generates_delta_for_each_answered_question(self, tmp_path):
        questions = _make_questions(count=3)
        matrix = _make_matrix(count=3)
        notes_path = _write_notes(tmp_path, {1: "Answer one.", 2: "Answer two."})
        service = _make_service()

        result = service.ingest_notes(notes_path, questions, matrix)

        assert result.delta_analysis.count == 2

    def test_delta_includes_answer_and_solicitation_text(self, tmp_path):
        questions = _make_questions(count=1)
        matrix = _make_matrix(count=1)
        notes_path = _write_notes(tmp_path, {1: "Compact means less than 50 lbs."})
        service = _make_service()

        result = service.ingest_notes(notes_path, questions, matrix)

        delta_item = result.delta_analysis.items[0]
        assert "less than 50 lbs" in delta_item.answer_summary
        assert "Requirement 1" in delta_item.solicitation_text


# ---------------------------------------------------------------------------
# Behavior 4: Updates compliance matrix with clarifications
# ---------------------------------------------------------------------------


class TestComplianceMatrixUpdates:
    def test_generates_compliance_updates_for_answered_questions(self, tmp_path):
        questions = _make_questions(count=2)
        matrix = _make_matrix(count=2)
        notes_path = _write_notes(tmp_path, {1: "Answer one.", 2: "Answer two."})
        service = _make_service()

        result = service.ingest_notes(notes_path, questions, matrix)

        assert len(result.compliance_updates) == 2

    def test_compliance_update_references_question_and_answer(self, tmp_path):
        questions = _make_questions(count=1)
        matrix = _make_matrix(count=1)
        notes_path = _write_notes(tmp_path, {1: "Compact means less than 50 lbs."})
        service = _make_service()

        result = service.ingest_notes(notes_path, questions, matrix)

        update = result.compliance_updates[0]
        assert "1" in update
        assert "50 lbs" in update or "compact" in update.lower()


# ---------------------------------------------------------------------------
# Behavior 5: File not found raises error
# ---------------------------------------------------------------------------


class TestNotesFileNotFound:
    def test_nonexistent_path_raises_not_found_error(self):
        service = _make_service()
        questions = _make_questions(count=1)
        matrix = _make_matrix(count=1)

        with pytest.raises(NotesFileNotFoundError) as exc_info:
            service.ingest_notes(Path("/nonexistent/notes.txt"), questions, matrix)

        assert "not found" in str(exc_info.value).lower()

    def test_error_includes_file_path_guidance(self):
        service = _make_service()
        questions = _make_questions(count=1)
        matrix = _make_matrix(count=1)

        with pytest.raises(NotesFileNotFoundError) as exc_info:
            service.ingest_notes(Path("/nonexistent/notes.txt"), questions, matrix)

        message = str(exc_info.value).lower()
        assert "file" in message or "path" in message


# ---------------------------------------------------------------------------
# Behavior 6: Partial answer ingestion
# ---------------------------------------------------------------------------


class TestPartialIngestion:
    @pytest.mark.parametrize("total,answered_count", [
        (10, 3),
        (23, 8),
        (5, 0),
    ])
    def test_partial_notes_match_subset_and_mark_rest_unanswered(
        self, tmp_path, total, answered_count
    ):
        questions = _make_questions(count=total)
        matrix = _make_matrix(count=total)
        answers = {i + 1: f"Answer {i + 1}." for i in range(answered_count)}
        notes_path = _write_notes(tmp_path, answers)
        service = _make_service()

        result = service.ingest_notes(notes_path, questions, matrix)

        assert result.answered_count == answered_count
        assert result.unanswered_count == total - answered_count
        assert len(result.answers) == total
