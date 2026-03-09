"""Unit tests for strategy brief through StrategyService (driving port).

Test Budget: 7 behaviors x 2 = 14 unit tests max.
Tests enter through driving port (StrategyService).
Domain objects (ComplianceMatrix, StrategyBrief, TpocIngestionResult) are real collaborators.
"""

from __future__ import annotations

import pytest

from pes.domain.compliance import (
    ComplianceItem,
    ComplianceMatrix,
    RequirementType,
)
from pes.domain.strategy import REQUIRED_SECTION_KEYS
from pes.domain.strategy_service import (
    ComplianceMatrixRequiredError,
    StrategyBriefNotFoundError,
    StrategyService,
)
from pes.domain.tpoc_ingestion import (
    AnswerStatus,
    TpocAnswer,
    TpocIngestionResult,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SAMPLE_MATRIX = ComplianceMatrix(
    items=[
        ComplianceItem(
            item_id=i,
            text=f"Requirement {i}: system shall do thing {i}",
            requirement_type=RequirementType.SHALL,
            proposal_section="Technical Volume",
        )
        for i in range(1, 11)
    ]
)

SAMPLE_TPOC_RESULT = TpocIngestionResult(
    answers=[
        TpocAnswer(
            question_id=1,
            question_text="What does compact mean?",
            answer_text="Less than 50 lbs.",
            status=AnswerStatus.ANSWERED,
        ),
        TpocAnswer(
            question_id=2,
            question_text="What is Phase III target?",
            answer_text="PMS 501 integration.",
            status=AnswerStatus.ANSWERED,
        ),
    ],
)


def _make_service() -> StrategyService:
    """Wire StrategyService (no driven ports needed)."""
    return StrategyService()


# ---------------------------------------------------------------------------
# Behavior 1: Brief covers all required sections
# ---------------------------------------------------------------------------


class TestBriefCoversRequiredSections:
    def test_brief_contains_trl_teaming_phase_iii_budget_risks(self):
        service = _make_service()

        brief = service.generate_brief(SAMPLE_MATRIX)

        assert brief.covers_required_sections
        for key in REQUIRED_SECTION_KEYS:
            section = brief.get_section(key)
            assert section is not None, f"Missing section: {key}"
            assert len(section.content) > 0, f"Empty content for section: {key}"

    def test_each_section_has_descriptive_title(self):
        service = _make_service()

        brief = service.generate_brief(SAMPLE_MATRIX)

        for key in REQUIRED_SECTION_KEYS:
            section = brief.get_section(key)
            assert section is not None
            assert len(section.title) > 0


# ---------------------------------------------------------------------------
# Behavior 2: Brief generated without TPOC answers notes absence
# ---------------------------------------------------------------------------


class TestBriefWithoutTpocAnswers:
    def test_generates_brief_without_tpoc_data(self):
        service = _make_service()

        brief = service.generate_brief(SAMPLE_MATRIX, tpoc_result=None)

        assert brief.covers_required_sections
        assert brief.tpoc_available is False

    def test_notes_tpoc_absence_in_brief(self):
        service = _make_service()

        brief = service.generate_brief(SAMPLE_MATRIX, tpoc_result=None)

        # The brief should contain a note about TPOC absence somewhere
        all_content = " ".join(s.content for s in brief.sections)
        assert "tpoc" in all_content.lower()
        assert "not available" in all_content.lower()


# ---------------------------------------------------------------------------
# Behavior 3: Brief with TPOC insights references them
# ---------------------------------------------------------------------------


class TestBriefWithTpocInsights:
    def test_marks_tpoc_as_available(self):
        service = _make_service()

        brief = service.generate_brief(SAMPLE_MATRIX, tpoc_result=SAMPLE_TPOC_RESULT)

        assert brief.tpoc_available is True

    def test_references_tpoc_insights_in_content(self):
        service = _make_service()

        brief = service.generate_brief(SAMPLE_MATRIX, tpoc_result=SAMPLE_TPOC_RESULT)

        all_content = " ".join(s.content for s in brief.sections)
        assert "tpoc" in all_content.lower()
        # Should reference actual answer content
        assert "50 lbs" in all_content or "PMS 501" in all_content


# ---------------------------------------------------------------------------
# Behavior 4: Approve brief records approval and unlocks Wave 2
# ---------------------------------------------------------------------------


class TestApproveBrief:
    def test_approval_returns_state_update_with_approval(self):
        service = _make_service()
        brief = service.generate_brief(SAMPLE_MATRIX)

        result = service.approve_brief(brief)

        assert result["strategy_brief_status"] == "approved"
        assert result["approved_at"] is not None

    def test_approval_unlocks_wave_2(self):
        service = _make_service()
        brief = service.generate_brief(SAMPLE_MATRIX)

        result = service.approve_brief(brief)

        assert result["wave_2_unlocked"] is True


# ---------------------------------------------------------------------------
# Behavior 5: Revise brief incorporates feedback
# ---------------------------------------------------------------------------


class TestReviseBrief:
    def test_revised_brief_records_feedback(self):
        service = _make_service()
        original = service.generate_brief(SAMPLE_MATRIX)

        revised = service.revise_brief(
            original, SAMPLE_MATRIX, "Change approach from solid-state laser to fiber laser"
        )

        assert revised.revision_feedback is not None
        assert "fiber laser" in revised.revision_feedback

    def test_revised_brief_still_covers_all_sections(self):
        service = _make_service()
        original = service.generate_brief(SAMPLE_MATRIX)

        revised = service.revise_brief(
            original, SAMPLE_MATRIX, "Adjust budget to $150K"
        )

        assert revised.covers_required_sections


# ---------------------------------------------------------------------------
# Behavior 6: Error -- no compliance matrix raises error
# ---------------------------------------------------------------------------


class TestNoComplianceMatrix:
    def test_none_matrix_raises_compliance_required_error(self):
        service = _make_service()

        with pytest.raises(ComplianceMatrixRequiredError) as exc_info:
            service.generate_brief(None)  # type: ignore[arg-type]

        assert "compliance matrix" in str(exc_info.value).lower()


# ---------------------------------------------------------------------------
# Behavior 7: Error -- approve without brief raises error
# ---------------------------------------------------------------------------


class TestApproveWithoutBrief:
    def test_none_brief_raises_not_found_error(self):
        service = _make_service()

        with pytest.raises(StrategyBriefNotFoundError) as exc_info:
            service.approve_brief(None)

        assert "no strategy brief" in str(exc_info.value).lower()
