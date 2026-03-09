"""TPOC service -- driving port for TPOC question generation.

Orchestrates: ambiguity extraction from compliance matrix,
strategic probe generation, question prioritization, and
output to editable markdown.
"""

from __future__ import annotations

from pes.domain.compliance import ComplianceMatrix
from pes.domain.tpoc import QuestionCategory, TpocQuestion, TpocQuestionSet


class ComplianceMatrixRequiredError(Exception):
    """Raised when generating questions without a compliance matrix."""


# Standard strategic probes applicable to any SBIR solicitation
STRATEGIC_PROBES = [
    "What evaluation criteria carry the most weight in scoring?",
    "Are there preferred technologies or approaches for this topic?",
    "What does a successful Phase I outcome look like to the TPOC?",
]


class TpocService:
    """Driving port: generates TPOC questions from solicitation gaps."""

    def generate_questions(self, matrix: ComplianceMatrix) -> TpocQuestionSet:
        """Generate prioritized TPOC questions from compliance matrix.

        Extracts questions from ambiguities and generates strategic probes.
        Returns TpocQuestionSet ordered by strategic priority.

        Raises ComplianceMatrixRequiredError if matrix is None.
        """
        if matrix is None:
            raise ComplianceMatrixRequiredError(
                "Compliance matrix required before generating TPOC questions. "
                "Run the strategy wave command first."
            )

        questions: list[TpocQuestion] = []
        question_id = 1

        # Generate questions from ambiguous items
        for item in matrix.items:
            if item.ambiguity:
                questions.append(TpocQuestion(
                    question_id=question_id,
                    text=f"Can you clarify: {item.ambiguity}",
                    category=QuestionCategory.AMBIGUITY,
                    source_item_id=item.item_id,
                    rationale=f"Flagged ambiguity in requirement {item.item_id}",
                ))
                question_id += 1

        # Add standard strategic probes
        for probe_text in STRATEGIC_PROBES:
            questions.append(TpocQuestion(
                question_id=question_id,
                text=probe_text,
                category=QuestionCategory.STRATEGIC_PROBE,
                rationale="Standard strategic probe for SBIR TPOC calls",
            ))
            question_id += 1

        return TpocQuestionSet(questions=questions)
