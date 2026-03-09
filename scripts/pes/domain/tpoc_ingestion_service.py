"""TPOC ingestion service -- driving port for TPOC answer ingestion and delta analysis.

Orchestrates: note parsing, answer-to-question matching,
delta analysis generation, and compliance matrix updates.
"""

from __future__ import annotations

import re
from pathlib import Path

from pes.domain.compliance import ComplianceMatrix
from pes.domain.tpoc import TpocQuestionSet
from pes.domain.tpoc_ingestion import (
    AnswerStatus,
    DeltaAnalysis,
    DeltaItem,
    TpocAnswer,
    TpocIngestionResult,
)


class NotesFileNotFoundError(Exception):
    """Raised when the notes file path does not exist."""


# Pattern: "Q1 Answer: ..." or "Q12 Answer: ..."
_ANSWER_PATTERN = re.compile(r"Q(\d+)\s+Answer:\s*(.+)")


class TpocIngestionService:
    """Driving port: ingests TPOC call notes and produces delta analysis."""

    def ingest_notes(
        self,
        notes_path: Path,
        questions: TpocQuestionSet,
        matrix: ComplianceMatrix,
    ) -> TpocIngestionResult:
        """Ingest TPOC call notes and match answers to questions.

        Parses structured notes, matches answers to original questions,
        generates delta analysis comparing answers to solicitation text,
        and identifies compliance matrix updates.

        Raises NotesFileNotFoundError if notes_path does not exist.
        """
        if not notes_path.exists():
            raise NotesFileNotFoundError(
                f"Notes file not found: {notes_path}. "
                "Verify the file path and try again."
            )

        raw_answers = self._parse_notes(notes_path)
        answers = self._match_answers(questions, raw_answers)
        delta_analysis = self._build_delta(answers, matrix)
        compliance_updates = self._build_compliance_updates(answers, matrix)

        return TpocIngestionResult(
            answers=answers,
            delta_analysis=delta_analysis,
            compliance_updates=compliance_updates,
        )

    def _parse_notes(self, notes_path: Path) -> dict[int, str]:
        """Parse structured notes into question_id -> answer_text mapping."""
        text = notes_path.read_text()
        answers: dict[int, str] = {}
        for match in _ANSWER_PATTERN.finditer(text):
            question_num = int(match.group(1))
            answer_text = match.group(2).strip()
            answers[question_num] = answer_text
        return answers

    def _match_answers(
        self,
        questions: TpocQuestionSet,
        raw_answers: dict[int, str],
    ) -> list[TpocAnswer]:
        """Match parsed answers to original questions."""
        results: list[TpocAnswer] = []
        for question in questions.questions:
            answer_text = raw_answers.get(question.question_id)
            status = AnswerStatus.ANSWERED if answer_text else AnswerStatus.UNANSWERED
            results.append(TpocAnswer(
                question_id=question.question_id,
                question_text=question.text,
                answer_text=answer_text,
                status=status,
            ))
        return results

    def _build_delta(
        self,
        answers: list[TpocAnswer],
        matrix: ComplianceMatrix,
    ) -> DeltaAnalysis:
        """Build delta analysis comparing answered info to solicitation requirements."""
        items_by_id = {item.item_id: item for item in matrix.items}
        delta_items: list[DeltaItem] = []

        for answer in answers:
            if not answer.is_answered:
                continue
            source_item = items_by_id.get(answer.question_id)
            solicitation_text = source_item.text if source_item else "No matching requirement"
            delta_items.append(DeltaItem(
                question_id=answer.question_id,
                answer_summary=answer.answer_text or "",
                solicitation_text=solicitation_text,
                delta=self._compute_delta(answer.answer_text or "", solicitation_text),
            ))

        return DeltaAnalysis(items=delta_items)

    def _compute_delta(self, answer: str, solicitation_text: str) -> str:
        """Compute a textual delta between answer and solicitation requirement."""
        return f"TPOC clarified: {answer} (vs. requirement: {solicitation_text})"

    def _build_compliance_updates(
        self,
        answers: list[TpocAnswer],
        matrix: ComplianceMatrix,
    ) -> list[str]:
        """Generate compliance update notes for answered questions."""
        items_by_id = {item.item_id: item for item in matrix.items}
        updates: list[str] = []

        for answer in answers:
            if not answer.is_answered:
                continue
            source_item = items_by_id.get(answer.question_id)
            item_ref = f"item {source_item.item_id}" if source_item else f"Q{answer.question_id}"
            updates.append(
                f"TPOC clarification for {item_ref}: {answer.answer_text}"
            )

        return updates
