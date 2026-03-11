"""Unit tests for OutcomeService (driving port) -- debrief request letter generation,
outcome recording, pattern analysis, and lessons learned.

Test Budget: 12 behaviors x 2 = 24 unit tests max.
Tests enter through driving port (OutcomeService).
Driven ports (TemplateLoader, ArtifactWriter) faked at port boundary.
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

import json

import pytest

from pes.domain.outcome_service import OutcomeService
from pes.ports.artifact_writer_port import ArtifactWriter
from pes.ports.template_loader_port import TemplateLoader

# ---------------------------------------------------------------------------
# Fake driven ports -- mock at port boundary only
# ---------------------------------------------------------------------------


class FakeTemplateLoader(TemplateLoader):
    """Fake template loader returning pre-configured templates."""

    def __init__(self, templates: dict[str, str] | None = None) -> None:
        self._templates: dict[str, str] = templates or {}

    def add_template(self, name: str, content: str) -> None:
        self._templates[name] = content

    def load_template(self, name: str) -> str:
        if name not in self._templates:
            raise FileNotFoundError(f"Template not found: {name}")
        return self._templates[name]


class FakeArtifactWriter(ArtifactWriter):
    """Fake artifact writer capturing written artifacts in memory."""

    def __init__(self) -> None:
        self.written_artifacts: dict[str, str] = {}
        self.written_json: dict[str, dict[str, object]] = {}

    def write_artifact(self, path: str, content: str) -> None:
        self.written_artifacts[path] = content

    def write_json(self, path: str, data: dict[str, object]) -> None:
        self.written_json[path] = data
        # Also store as text for content assertions
        self.written_artifacts[path] = json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_DOD_TEMPLATE = (
    "Subject: Debrief Request for {topic_id}\n"
    "Confirmation: {confirmation_number}\n"
    "Per FAR 15.505(a)(1), we request a post-award debrief.\n"
)

_NASA_TEMPLATE = (
    "Subject: NASA Debrief Request for {topic_id}\n"
    "Confirmation: {confirmation_number}\n"
    "Per NASA debrief procedures, we request feedback.\n"
)


def _make_template_loader() -> FakeTemplateLoader:
    loader = FakeTemplateLoader()
    loader.add_template("dod-far-15-505.md", _DOD_TEMPLATE)
    loader.add_template("nasa-debrief.md", _NASA_TEMPLATE)
    return loader


def _make_service(
    template_loader: FakeTemplateLoader | None = None,
    artifact_writer: FakeArtifactWriter | None = None,
) -> tuple[OutcomeService, FakeArtifactWriter]:
    loader = template_loader or _make_template_loader()
    writer = artifact_writer or FakeArtifactWriter()
    service = OutcomeService(template_loader=loader, artifact_writer=writer)
    return service, writer


# ---------------------------------------------------------------------------
# Behavior 1: DoD letter references topic and confirmation number
# ---------------------------------------------------------------------------


class TestDodLetterReferences:
    def test_letter_contains_topic_id(self):
        service, _ = _make_service()

        result = service.generate_debrief_letter(
            topic_id="AF243-001",
            agency="Air Force",
            confirmation_number="DSIP-2026-AF243-001-7842",
            artifacts_dir="/artifacts",
        )

        assert "AF243-001" in result.content

    def test_letter_contains_confirmation_number(self):
        service, _ = _make_service()

        result = service.generate_debrief_letter(
            topic_id="AF243-001",
            agency="Air Force",
            confirmation_number="DSIP-2026-AF243-001-7842",
            artifacts_dir="/artifacts",
        )

        assert "DSIP-2026-AF243-001-7842" in result.content


# ---------------------------------------------------------------------------
# Behavior 2: DoD letter cites FAR 15.505(a)(1)
# ---------------------------------------------------------------------------


class TestDodLetterRegulation:
    def test_dod_letter_cites_far_15_505(self):
        service, _ = _make_service()

        result = service.generate_debrief_letter(
            topic_id="AF243-001",
            agency="Air Force",
            confirmation_number="DSIP-2026-AF243-001-7842",
            artifacts_dir="/artifacts",
        )

        assert "FAR 15.505(a)(1)" in result.content


# ---------------------------------------------------------------------------
# Behavior 3: NASA letter uses NASA-specific procedures
# ---------------------------------------------------------------------------


class TestNasaLetter:
    def test_nasa_letter_uses_nasa_procedures(self):
        service, _ = _make_service()

        result = service.generate_debrief_letter(
            topic_id="N244-012",
            agency="NASA",
            confirmation_number="NSPIRES-2026-N244-012",
            artifacts_dir="/artifacts",
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
        service, _ = _make_service()

        record = service.skip_debrief_request(topic_id="AF243-001")

        assert record.status == "debrief not requested"
        assert record.letter_created is False

    def test_skip_preserves_topic_id(self):
        service, _ = _make_service()

        record = service.skip_debrief_request(topic_id="AF243-001")

        assert record.topic_id == "AF243-001"


# ---------------------------------------------------------------------------
# Behavior 5: Letter written to learning artifacts directory
# ---------------------------------------------------------------------------


class TestLetterArtifactWritten:
    def test_letter_written_to_artifacts_dir(self):
        service, writer = _make_service()

        result = service.generate_debrief_letter(
            topic_id="AF243-001",
            agency="Air Force",
            confirmation_number="DSIP-2026-AF243-001-7842",
            artifacts_dir="/artifacts",
        )

        assert result.file_path in writer.written_artifacts
        assert "/artifacts" in result.file_path

    @pytest.mark.parametrize(
        "agency,expected_in_filename",
        [
            ("Air Force", "debrief-request"),
            ("NASA", "debrief-request"),
        ],
    )
    def test_letter_filename_identifies_debrief_request(
        self, agency: str, expected_in_filename: str
    ):
        service, _ = _make_service()

        result = service.generate_debrief_letter(
            topic_id="AF243-001",
            agency=agency,
            confirmation_number="CONF-001",
            artifacts_dir="/artifacts",
        )

        assert expected_in_filename in result.file_path


# ---------------------------------------------------------------------------
# Behavior 6: Awarded proposals archived with outcome tag and discriminators
# ---------------------------------------------------------------------------


class TestAwardedProposalArchiving:
    def test_awarded_outcome_archives_with_tag_and_discriminators(self):
        service, _ = _make_service()

        result = service.record_outcome(
            topic_id="AF243-001",
            outcome="awarded",
            artifacts_dir="/artifacts",
        )

        assert result.outcome_tag == "awarded"
        assert result.archived is True
        assert result.discriminators is not None
        assert "Phase II" in result.message

    def test_awarded_outcome_writes_archive_artifact(self):
        service, writer = _make_service()

        result = service.record_outcome(
            topic_id="AF243-001",
            outcome="awarded",
            artifacts_dir="/artifacts",
        )

        assert result.archive_path in writer.written_json
        assert "AF243-001" in result.archive_path


# ---------------------------------------------------------------------------
# Behavior 7: Outcome without debrief is valid terminal state
# ---------------------------------------------------------------------------


class TestOutcomeWithoutDebrief:
    def test_not_selected_without_debrief_is_valid_terminal_state(self):
        service, _ = _make_service()

        result = service.record_outcome(
            topic_id="AF243-001",
            outcome="not_selected",
            artifacts_dir="/artifacts",
        )

        assert result.outcome_tag == "not_selected"
        assert result.debrief_artifacts_created is False
        assert "Debrief can be ingested later if received" in result.message

    def test_not_selected_preserves_topic_id(self):
        service, _ = _make_service()

        result = service.record_outcome(
            topic_id="AF243-001",
            outcome="not_selected",
            artifacts_dir="/artifacts",
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
    def test_identifies_recurring_weaknesses(self):
        service, _ = _make_service()
        corpus = _build_corpus_outcomes(losses=4)

        result = service.update_pattern_analysis(
            corpus_outcomes=corpus,
            artifacts_dir="/artifacts",
        )

        assert len(result.recurring_weaknesses) > 0
        weakness_names = [w["pattern"] for w in result.recurring_weaknesses]
        assert "cost realism" in weakness_names


# ---------------------------------------------------------------------------
# Behavior 9: Pattern analysis identifies recurring strengths across wins
# ---------------------------------------------------------------------------


class TestPatternAnalysisStrengths:
    def test_identifies_recurring_strengths(self):
        service, _ = _make_service()
        corpus = _build_corpus_outcomes(wins=3)

        result = service.update_pattern_analysis(
            corpus_outcomes=corpus,
            artifacts_dir="/artifacts",
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
        self, total_proposals: int, expected_confidence: str
    ):
        service, _ = _make_service()
        wins = total_proposals // 3
        losses = total_proposals - wins
        corpus = _build_corpus_outcomes(wins=wins, losses=losses)

        result = service.update_pattern_analysis(
            corpus_outcomes=corpus,
            artifacts_dir="/artifacts",
        )

        assert result.confidence_level == expected_confidence


# ---------------------------------------------------------------------------
# Behavior 11: Pattern analysis written to learning artifacts directory
# ---------------------------------------------------------------------------


class TestPatternAnalysisArtifact:
    def test_writes_pattern_analysis_to_artifacts_dir(self):
        service, writer = _make_service()
        corpus = _build_corpus_outcomes()

        result = service.update_pattern_analysis(
            corpus_outcomes=corpus,
            artifacts_dir="/artifacts",
        )

        assert result.artifact_path in writer.written_json
        assert "/artifacts" in result.artifact_path


# ---------------------------------------------------------------------------
# Behavior 12: Lessons learned require human acknowledgment checkpoint
# ---------------------------------------------------------------------------


class TestLessonsLearnedCheckpoint:
    def test_lessons_require_human_acknowledgment(self):
        service, _ = _make_service()

        result = service.present_lessons_learned(
            artifacts_dir="/artifacts",
        )

        assert result.requires_human_acknowledgment is True
        assert result.status == "pending_review"
