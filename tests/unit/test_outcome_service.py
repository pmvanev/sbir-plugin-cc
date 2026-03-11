"""Unit tests for OutcomeService (driving port) -- debrief request letter generation,
outcome recording, pattern analysis, and lessons learned.

Test Budget: 12 behaviors x 2 = 24 unit tests max.
Tests enter through driving port (OutcomeService).
Domain objects (DebriefLetterResult, DebriefSkipRecord, OutcomeRecord,
PatternAnalysisResult, LessonsLearnedResult) are real collaborators.

Behaviors (step 06-01):
1. Generate DoD debrief request letter with topic reference and confirmation number
2. Generate DoD letter citing FAR 15.505(a)(1) regulation
3. Generate NASA debrief request letter with NASA-specific procedures
4. Skip debrief request records status without creating letter
5. Letter written to learning artifacts directory

Behaviors (step 06-02):
6. Awarded proposals archived with outcome tag and discriminators extracted
7. Outcome without debrief is valid terminal state

Behaviors (step 07-02):
8. Pattern analysis identifies recurring weaknesses across losses
9. Pattern analysis identifies recurring strengths across wins
10. Pattern analysis notes confidence level for small corpus
11. Pattern analysis written to learning artifacts directory
12. Lessons learned require human acknowledgment checkpoint
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pes.domain.outcome_service import OutcomeService

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_service() -> OutcomeService:
    return OutcomeService()


# ---------------------------------------------------------------------------
# Behavior 1: DoD letter references topic and confirmation number
# ---------------------------------------------------------------------------


class TestDodLetterReferences:
    def test_letter_contains_topic_id(self, tmp_path: Path):
        service = _make_service()
        artifacts_dir = str(tmp_path)

        result = service.generate_debrief_letter(
            topic_id="AF243-001",
            agency="Air Force",
            confirmation_number="DSIP-2026-AF243-001-7842",
            artifacts_dir=artifacts_dir,
        )

        assert "AF243-001" in result.content

    def test_letter_contains_confirmation_number(self, tmp_path: Path):
        service = _make_service()
        artifacts_dir = str(tmp_path)

        result = service.generate_debrief_letter(
            topic_id="AF243-001",
            agency="Air Force",
            confirmation_number="DSIP-2026-AF243-001-7842",
            artifacts_dir=artifacts_dir,
        )

        assert "DSIP-2026-AF243-001-7842" in result.content


# ---------------------------------------------------------------------------
# Behavior 2: DoD letter cites FAR 15.505(a)(1)
# ---------------------------------------------------------------------------


class TestDodLetterRegulation:
    def test_dod_letter_cites_far_15_505(self, tmp_path: Path):
        service = _make_service()
        artifacts_dir = str(tmp_path)

        result = service.generate_debrief_letter(
            topic_id="AF243-001",
            agency="Air Force",
            confirmation_number="DSIP-2026-AF243-001-7842",
            artifacts_dir=artifacts_dir,
        )

        assert "FAR 15.505(a)(1)" in result.content


# ---------------------------------------------------------------------------
# Behavior 3: NASA letter uses NASA-specific procedures
# ---------------------------------------------------------------------------


class TestNasaLetter:
    def test_nasa_letter_uses_nasa_procedures(self, tmp_path: Path):
        service = _make_service()
        artifacts_dir = str(tmp_path)

        result = service.generate_debrief_letter(
            topic_id="N244-012",
            agency="NASA",
            confirmation_number="NSPIRES-2026-N244-012",
            artifacts_dir=artifacts_dir,
        )

        # NASA letters should reference NASA-specific debrief procedures
        assert "NASA" in result.content
        # Should NOT cite DoD FAR regulation
        assert "FAR 15.505" not in result.content


# ---------------------------------------------------------------------------
# Behavior 4: Skip debrief request records status without letter
# ---------------------------------------------------------------------------


class TestSkipDebriefRequest:
    def test_skip_records_debrief_not_requested(self):
        service = _make_service()

        record = service.skip_debrief_request(topic_id="AF243-001")

        assert record.status == "debrief not requested"
        assert record.letter_created is False

    def test_skip_preserves_topic_id(self):
        service = _make_service()

        record = service.skip_debrief_request(topic_id="AF243-001")

        assert record.topic_id == "AF243-001"


# ---------------------------------------------------------------------------
# Behavior 5: Letter written to learning artifacts directory
# ---------------------------------------------------------------------------


class TestLetterArtifactWritten:
    def test_letter_written_to_artifacts_dir(self, tmp_path: Path):
        service = _make_service()
        artifacts_dir = str(tmp_path)

        result = service.generate_debrief_letter(
            topic_id="AF243-001",
            agency="Air Force",
            confirmation_number="DSIP-2026-AF243-001-7842",
            artifacts_dir=artifacts_dir,
        )

        written = Path(result.file_path)
        assert written.exists()
        assert str(written).startswith(str(tmp_path))

    @pytest.mark.parametrize(
        "agency,expected_in_filename",
        [
            ("Air Force", "debrief-request"),
            ("NASA", "debrief-request"),
        ],
    )
    def test_letter_filename_identifies_debrief_request(
        self, tmp_path: Path, agency: str, expected_in_filename: str
    ):
        service = _make_service()
        artifacts_dir = str(tmp_path)

        result = service.generate_debrief_letter(
            topic_id="AF243-001",
            agency=agency,
            confirmation_number="CONF-001",
            artifacts_dir=artifacts_dir,
        )

        filename = Path(result.file_path).name
        assert expected_in_filename in filename


# ---------------------------------------------------------------------------
# Behavior 6: Awarded proposals archived with outcome tag and discriminators
# ---------------------------------------------------------------------------


class TestAwardedProposalArchiving:
    def test_awarded_outcome_archives_with_tag_and_discriminators(self, tmp_path: Path):
        service = _make_service()
        artifacts_dir = str(tmp_path)

        result = service.record_outcome(
            topic_id="AF243-001",
            outcome="awarded",
            artifacts_dir=artifacts_dir,
        )

        assert result.outcome_tag == "awarded"
        assert result.archived is True
        assert result.discriminators is not None
        assert "Phase II" in result.message

    def test_awarded_outcome_writes_archive_artifact(self, tmp_path: Path):
        service = _make_service()
        artifacts_dir = str(tmp_path)

        result = service.record_outcome(
            topic_id="AF243-001",
            outcome="awarded",
            artifacts_dir=artifacts_dir,
        )

        archive_path = Path(result.archive_path)
        assert archive_path.exists()
        assert "AF243-001" in archive_path.name


# ---------------------------------------------------------------------------
# Behavior 7: Outcome without debrief is valid terminal state
# ---------------------------------------------------------------------------


class TestOutcomeWithoutDebrief:
    def test_not_selected_without_debrief_is_valid_terminal_state(self, tmp_path: Path):
        service = _make_service()
        artifacts_dir = str(tmp_path)

        result = service.record_outcome(
            topic_id="AF243-001",
            outcome="not_selected",
            artifacts_dir=artifacts_dir,
        )

        assert result.outcome_tag == "not_selected"
        assert result.debrief_artifacts_created is False
        assert "Debrief can be ingested later if received" in result.message

    def test_not_selected_preserves_topic_id(self, tmp_path: Path):
        service = _make_service()
        artifacts_dir = str(tmp_path)

        result = service.record_outcome(
            topic_id="AF243-001",
            outcome="not_selected",
            artifacts_dir=artifacts_dir,
        )

        assert result.topic_id == "AF243-001"


# ---------------------------------------------------------------------------
# Helpers for corpus outcomes (step 07-02)
# ---------------------------------------------------------------------------


def _build_corpus_outcomes(
    wins: int = 3,
    losses: int = 4,
    win_strengths: list[str] | None = None,
    loss_weaknesses: list[str] | None = None,
) -> list[dict[str, object]]:
    """Build corpus outcome entries for pattern analysis tests."""
    strengths = win_strengths or ["strong technical approach", "experienced team"]
    weaknesses = loss_weaknesses or ["cost realism", "schedule risk"]
    outcomes: list[dict[str, object]] = []
    for i in range(wins):
        outcomes.append(
            {
                "topic_id": f"WIN-{i + 1:03d}",
                "outcome": "awarded",
                "strengths": strengths,
                "weaknesses": [],
            }
        )
    for i in range(losses):
        outcomes.append(
            {
                "topic_id": f"LOSS-{i + 1:03d}",
                "outcome": "not_selected",
                "strengths": [],
                "weaknesses": weaknesses,
            }
        )
    return outcomes


# ---------------------------------------------------------------------------
# Behavior 8: Pattern analysis identifies recurring weaknesses across losses
# ---------------------------------------------------------------------------


class TestPatternAnalysisWeaknesses:
    def test_identifies_recurring_weaknesses(self, tmp_path: Path):
        service = _make_service()
        corpus = _build_corpus_outcomes(losses=4)

        result = service.update_pattern_analysis(
            corpus_outcomes=corpus,
            artifacts_dir=str(tmp_path),
        )

        assert len(result.recurring_weaknesses) > 0
        weakness_names = [w["pattern"] for w in result.recurring_weaknesses]
        assert "cost realism" in weakness_names


# ---------------------------------------------------------------------------
# Behavior 9: Pattern analysis identifies recurring strengths across wins
# ---------------------------------------------------------------------------


class TestPatternAnalysisStrengths:
    def test_identifies_recurring_strengths(self, tmp_path: Path):
        service = _make_service()
        corpus = _build_corpus_outcomes(wins=3)

        result = service.update_pattern_analysis(
            corpus_outcomes=corpus,
            artifacts_dir=str(tmp_path),
        )

        assert len(result.recurring_strengths) > 0
        strength_names = [s["pattern"] for s in result.recurring_strengths]
        assert "strong technical approach" in strength_names


# ---------------------------------------------------------------------------
# Behavior 10: Pattern analysis notes confidence level for small corpus
# ---------------------------------------------------------------------------


class TestPatternAnalysisConfidence:
    @pytest.mark.parametrize(
        "total_proposals,expected_confidence",
        [
            (3, "low"),
            (10, "medium"),
            (25, "high"),
        ],
    )
    def test_confidence_level_scales_with_corpus_size(
        self, tmp_path: Path, total_proposals: int, expected_confidence: str
    ):
        service = _make_service()
        wins = total_proposals // 3
        losses = total_proposals - wins
        corpus = _build_corpus_outcomes(wins=wins, losses=losses)

        result = service.update_pattern_analysis(
            corpus_outcomes=corpus,
            artifacts_dir=str(tmp_path),
        )

        assert result.confidence_level == expected_confidence


# ---------------------------------------------------------------------------
# Behavior 11: Pattern analysis written to learning artifacts directory
# ---------------------------------------------------------------------------


class TestPatternAnalysisArtifact:
    def test_writes_pattern_analysis_to_artifacts_dir(self, tmp_path: Path):
        service = _make_service()
        corpus = _build_corpus_outcomes()

        result = service.update_pattern_analysis(
            corpus_outcomes=corpus,
            artifacts_dir=str(tmp_path),
        )

        written = Path(result.artifact_path)
        assert written.exists()
        assert str(written).startswith(str(tmp_path))


# ---------------------------------------------------------------------------
# Behavior 12: Lessons learned require human acknowledgment checkpoint
# ---------------------------------------------------------------------------


class TestLessonsLearnedCheckpoint:
    def test_lessons_require_human_acknowledgment(self, tmp_path: Path):
        service = _make_service()

        result = service.present_lessons_learned(
            artifacts_dir=str(tmp_path),
        )

        assert result.requires_human_acknowledgment is True
        assert result.status == "pending_review"
