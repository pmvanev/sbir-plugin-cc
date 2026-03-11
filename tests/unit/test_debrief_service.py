"""Unit tests for DebriefService (driving port) -- debrief ingestion and critique mapping.

Test Budget: 6 behaviors x 2 = 12 unit tests max.
Tests enter through driving port (DebriefService).
Driven port (DebriefParser) mocked at port boundary.
Domain objects (DebriefIngestionResult, CritiqueMapping, etc.) are real collaborators.

Behaviors (step 07-01):
1. Parse structured debrief with scores and confidence reported
2. Map critiques to proposal sections and pages
3. Flag known weaknesses from past debriefs matching critiques
4. Write structured debrief artifact to learning artifacts directory
5. Preserve unstructured debrief as freeform text with parsing note
6. Freeform text available for keyword-based pattern matching
"""

from __future__ import annotations

from pathlib import Path

from pes.domain.debrief import (
    CritiqueMapping,
    DebriefParseResult,
    ReviewerScore,
)
from pes.domain.debrief_service import DebriefService
from pes.ports.debrief_parser_port import DebriefParser

# ---------------------------------------------------------------------------
# Fake driven port -- mock at port boundary only
# ---------------------------------------------------------------------------


class FakeDebriefParser(DebriefParser):
    """Fake parser returning pre-configured parse results."""

    def __init__(self, result: DebriefParseResult) -> None:
        self._result = result

    def parse(self, text: str) -> DebriefParseResult:
        return self._result


# ---------------------------------------------------------------------------
# Test data builders
# ---------------------------------------------------------------------------


def _structured_parse_result() -> DebriefParseResult:
    """Parse result simulating a well-structured debrief."""
    return DebriefParseResult(
        scores=[
            ReviewerScore(category="Technical Merit", score=3.5, max_score=5.0),
            ReviewerScore(category="Team Qualifications", score=4.0, max_score=5.0),
            ReviewerScore(category="Cost Realism", score=2.5, max_score=5.0),
        ],
        critiques=[
            CritiqueMapping(
                section="3.1",
                page=5,
                comment="Beam-steering mechanism lacks thermal management detail.",
            ),
            CritiqueMapping(
                section="4.2",
                page=12,
                comment="Timeline aggressive for TRL advancement.",
            ),
            CritiqueMapping(
                section="2.1",
                page=3,
                comment="Risk mitigation for manufacturing scalability insufficient.",
            ),
        ],
        parsing_confidence=0.85,
        is_structured=True,
    )


def _unstructured_parse_result() -> DebriefParseResult:
    """Parse result simulating an unstructured debrief (no scores, no sections)."""
    return DebriefParseResult(
        scores=[],
        critiques=[],
        freeform_text=(
            "Thank you for your submission. After careful review, your proposal "
            "was not selected for award. The evaluation panel noted that while "
            "the concept showed promise, several areas needed improvement "
            "including cost justification and timeline feasibility."
        ),
        parsing_confidence=0.2,
        is_structured=False,
    )


# ---------------------------------------------------------------------------
# Behavior 1: Parse structured debrief with scores and confidence
# ---------------------------------------------------------------------------


class TestParseStructuredDebrief:
    def test_returns_scores_from_structured_debrief(self, tmp_path: Path):
        parser = FakeDebriefParser(_structured_parse_result())
        service = DebriefService(parser=parser)

        result = service.ingest_debrief(
            debrief_text="structured debrief content",
            known_weaknesses=[],
            artifacts_dir=str(tmp_path),
        )

        assert len(result.scores) == 3
        assert result.scores[0].category == "Technical Merit"
        assert result.parsing_confidence > 0.0

    def test_reports_parsing_confidence(self, tmp_path: Path):
        parser = FakeDebriefParser(_structured_parse_result())
        service = DebriefService(parser=parser)

        result = service.ingest_debrief(
            debrief_text="structured debrief content",
            known_weaknesses=[],
            artifacts_dir=str(tmp_path),
        )

        assert result.parsing_confidence == 0.85


# ---------------------------------------------------------------------------
# Behavior 2: Map critiques to proposal sections and pages
# ---------------------------------------------------------------------------


class TestCritiqueMapping:
    def test_maps_critiques_to_sections_and_pages(self, tmp_path: Path):
        parser = FakeDebriefParser(_structured_parse_result())
        service = DebriefService(parser=parser)

        result = service.ingest_debrief(
            debrief_text="structured debrief content",
            known_weaknesses=[],
            artifacts_dir=str(tmp_path),
        )

        assert len(result.critique_map) == 3
        assert result.critique_map[0].section == "3.1"
        assert result.critique_map[0].page == 5

    def test_each_critique_has_comment(self, tmp_path: Path):
        parser = FakeDebriefParser(_structured_parse_result())
        service = DebriefService(parser=parser)

        result = service.ingest_debrief(
            debrief_text="structured debrief content",
            known_weaknesses=[],
            artifacts_dir=str(tmp_path),
        )

        for critique in result.critique_map:
            assert critique.comment is not None
            assert len(critique.comment) > 0


# ---------------------------------------------------------------------------
# Behavior 3: Flag known weaknesses from past debriefs
# ---------------------------------------------------------------------------


class TestFlagKnownWeaknesses:
    def test_flags_critiques_matching_known_weaknesses(self, tmp_path: Path):
        parser = FakeDebriefParser(_structured_parse_result())
        service = DebriefService(parser=parser)

        result = service.ingest_debrief(
            debrief_text="structured debrief content",
            known_weaknesses=["thermal management", "cost realism"],
            artifacts_dir=str(tmp_path),
        )

        assert len(result.flagged_weaknesses) > 0
        # "thermal management" should match critique about thermal management
        assert any("thermal" in w.lower() for w in result.flagged_weaknesses)

    def test_no_flags_when_no_known_weaknesses(self, tmp_path: Path):
        parser = FakeDebriefParser(_structured_parse_result())
        service = DebriefService(parser=parser)

        result = service.ingest_debrief(
            debrief_text="structured debrief content",
            known_weaknesses=[],
            artifacts_dir=str(tmp_path),
        )

        assert len(result.flagged_weaknesses) == 0


# ---------------------------------------------------------------------------
# Behavior 4: Write structured debrief artifact
# ---------------------------------------------------------------------------


class TestWriteDebriefArtifact:
    def test_writes_artifact_to_artifacts_directory(self, tmp_path: Path):
        parser = FakeDebriefParser(_structured_parse_result())
        service = DebriefService(parser=parser)

        result = service.ingest_debrief(
            debrief_text="structured debrief content",
            known_weaknesses=[],
            artifacts_dir=str(tmp_path),
        )

        assert result.artifact_path is not None
        written = Path(result.artifact_path)
        assert written.exists()
        assert str(written).startswith(str(tmp_path))

    def test_artifact_contains_structured_data(self, tmp_path: Path):
        parser = FakeDebriefParser(_structured_parse_result())
        service = DebriefService(parser=parser)

        result = service.ingest_debrief(
            debrief_text="structured debrief content",
            known_weaknesses=[],
            artifacts_dir=str(tmp_path),
        )

        content = Path(result.artifact_path).read_text(encoding="utf-8")
        assert "Technical Merit" in content


# ---------------------------------------------------------------------------
# Behavior 5: Preserve unstructured debrief as freeform text
# ---------------------------------------------------------------------------


class TestUnstructuredDebriefFallback:
    def test_preserves_freeform_text(self, tmp_path: Path):
        parser = FakeDebriefParser(_unstructured_parse_result())
        service = DebriefService(parser=parser)

        result = service.ingest_debrief(
            debrief_text="unstructured paragraph",
            known_weaknesses=[],
            artifacts_dir=str(tmp_path),
        )

        assert result.freeform_text is not None
        assert len(result.freeform_text) > 0

    def test_reports_parsing_limitation_message(self, tmp_path: Path):
        parser = FakeDebriefParser(_unstructured_parse_result())
        service = DebriefService(parser=parser)

        result = service.ingest_debrief(
            debrief_text="unstructured paragraph",
            known_weaknesses=[],
            artifacts_dir=str(tmp_path),
        )

        assert "Structured scores could not be extracted" in result.message


# ---------------------------------------------------------------------------
# Behavior 6: Freeform text available for keyword-based pattern matching
# ---------------------------------------------------------------------------


class TestFreeformKeywordMatching:
    def test_freeform_text_contains_searchable_content(self, tmp_path: Path):
        parser = FakeDebriefParser(_unstructured_parse_result())
        service = DebriefService(parser=parser)

        result = service.ingest_debrief(
            debrief_text="unstructured paragraph",
            known_weaknesses=[],
            artifacts_dir=str(tmp_path),
        )

        # Freeform text should be the full original text, searchable
        assert "cost justification" in result.freeform_text.lower()
