"""Unit tests for OutcomeService (driving port) -- debrief request letter generation.

Test Budget: 5 behaviors x 2 = 10 unit tests max.
Tests enter through driving port (OutcomeService).
Domain objects (DebriefLetterResult, DebriefSkipRecord) are real collaborators.

Behaviors (step 06-01):
1. Generate DoD debrief request letter with topic reference and confirmation number
2. Generate DoD letter citing FAR 15.505(a)(1) regulation
3. Generate NASA debrief request letter with NASA-specific procedures
4. Skip debrief request records status without creating letter
5. Letter written to learning artifacts directory
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
