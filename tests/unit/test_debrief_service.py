"""Unit tests for DebriefService (driving port) -- debrief ingestion and critique mapping.

Test Budget: 6 behaviors x 2 = 12 unit tests max.
Tests enter through driving port (DebriefService).
Driven ports (DebriefParser, ArtifactWriter) faked at port boundary.
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

import json

from pes.domain.debrief import (
    CritiqueMapping,
    DebriefParseResult,
    ReviewerScore,
)
from pes.domain.debrief_service import DebriefService
from pes.ports.artifact_writer_port import ArtifactWriter
from pes.ports.debrief_parser_port import DebriefParser

# ---------------------------------------------------------------------------
# Fake driven ports -- mock at port boundary only
# ---------------------------------------------------------------------------


class FakeDebriefParser(DebriefParser):
    """Fake parser returning pre-configured parse results."""

    def __init__(self, result: DebriefParseResult) -> None:
        self._result = result

    def parse(self, text: str) -> DebriefParseResult:
        return self._result


class FakeArtifactWriter(ArtifactWriter):
    """Fake artifact writer capturing written artifacts in memory."""

    def __init__(self) -> None:
        self.written_artifacts: dict[str, str] = {}
        self.written_json: dict[str, dict[str, object]] = {}

    def write_artifact(self, path: str, content: str) -> None:
        self.written_artifacts[path] = content

    def write_json(self, path: str, data: dict[str, object]) -> None:
        self.written_json[path] = data
        self.written_artifacts[path] = json.dumps(data, indent=2)


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


def _make_service(
    parse_result: DebriefParseResult | None = None,
) -> tuple[DebriefService, FakeArtifactWriter]:
    """Wire DebriefService with fake driven ports."""
    parser = FakeDebriefParser(parse_result or _structured_parse_result())
    writer = FakeArtifactWriter()
    service = DebriefService(parser=parser, artifact_writer=writer)
    return service, writer


# ---------------------------------------------------------------------------
# Behavior 1: Parse structured debrief with scores and confidence
# ---------------------------------------------------------------------------


class TestParseStructuredDebrief:
    def test_returns_scores_from_structured_debrief(self):
        service, _ = _make_service()

        result = service.ingest_debrief(
            debrief_text="structured debrief content",
            known_weaknesses=[],
            artifacts_dir="/artifacts",
        )

        assert len(result.scores) == 3
        assert result.scores[0].category == "Technical Merit"
        assert result.parsing_confidence > 0.0

    def test_reports_parsing_confidence(self):
        service, _ = _make_service()

        result = service.ingest_debrief(
            debrief_text="structured debrief content",
            known_weaknesses=[],
            artifacts_dir="/artifacts",
        )

        assert result.parsing_confidence == 0.85


# ---------------------------------------------------------------------------
# Behavior 2: Map critiques to proposal sections and pages
# ---------------------------------------------------------------------------


class TestCritiqueMapping:
    def test_maps_critiques_to_sections_and_pages(self):
        service, _ = _make_service()

        result = service.ingest_debrief(
            debrief_text="structured debrief content",
            known_weaknesses=[],
            artifacts_dir="/artifacts",
        )

        assert len(result.critique_map) == 3
        assert result.critique_map[0].section == "3.1"
        assert result.critique_map[0].page == 5

    def test_each_critique_has_comment(self):
        service, _ = _make_service()

        result = service.ingest_debrief(
            debrief_text="structured debrief content",
            known_weaknesses=[],
            artifacts_dir="/artifacts",
        )

        for critique in result.critique_map:
            assert critique.comment is not None
            assert len(critique.comment) > 0


# ---------------------------------------------------------------------------
# Behavior 3: Flag known weaknesses from past debriefs
# ---------------------------------------------------------------------------


class TestFlagKnownWeaknesses:
    def test_flags_critiques_matching_known_weaknesses(self):
        service, _ = _make_service()

        result = service.ingest_debrief(
            debrief_text="structured debrief content",
            known_weaknesses=["thermal management", "cost realism"],
            artifacts_dir="/artifacts",
        )

        assert len(result.flagged_weaknesses) > 0
        # "thermal management" should match critique about thermal management
        assert any("thermal" in w.lower() for w in result.flagged_weaknesses)

    def test_no_flags_when_no_known_weaknesses(self):
        service, _ = _make_service()

        result = service.ingest_debrief(
            debrief_text="structured debrief content",
            known_weaknesses=[],
            artifacts_dir="/artifacts",
        )

        assert len(result.flagged_weaknesses) == 0


# ---------------------------------------------------------------------------
# Behavior 4: Write structured debrief artifact
# ---------------------------------------------------------------------------


class TestWriteDebriefArtifact:
    def test_writes_artifact_to_artifacts_directory(self):
        service, writer = _make_service()

        result = service.ingest_debrief(
            debrief_text="structured debrief content",
            known_weaknesses=[],
            artifacts_dir="/artifacts",
        )

        assert result.artifact_path is not None
        assert result.artifact_path in writer.written_json
        assert "/artifacts" in result.artifact_path

    def test_artifact_contains_structured_data(self):
        service, writer = _make_service()

        result = service.ingest_debrief(
            debrief_text="structured debrief content",
            known_weaknesses=[],
            artifacts_dir="/artifacts",
        )

        content = writer.written_artifacts[result.artifact_path]
        assert "Technical Merit" in content


# ---------------------------------------------------------------------------
# Behavior 5: Preserve unstructured debrief as freeform text
# ---------------------------------------------------------------------------


class TestUnstructuredDebriefFallback:
    def test_preserves_freeform_text(self):
        service, _ = _make_service(_unstructured_parse_result())

        result = service.ingest_debrief(
            debrief_text="unstructured paragraph",
            known_weaknesses=[],
            artifacts_dir="/artifacts",
        )

        assert result.freeform_text is not None
        assert len(result.freeform_text) > 0

    def test_reports_parsing_limitation_message(self):
        service, _ = _make_service(_unstructured_parse_result())

        result = service.ingest_debrief(
            debrief_text="unstructured paragraph",
            known_weaknesses=[],
            artifacts_dir="/artifacts",
        )

        assert "Structured scores could not be extracted" in result.message


# ---------------------------------------------------------------------------
# Behavior 6: Freeform text available for keyword-based pattern matching
# ---------------------------------------------------------------------------


class TestFreeformKeywordMatching:
    def test_freeform_text_contains_searchable_content(self):
        service, _ = _make_service(_unstructured_parse_result())

        result = service.ingest_debrief(
            debrief_text="unstructured paragraph",
            known_weaknesses=[],
            artifacts_dir="/artifacts",
        )

        # Freeform text should be the full original text, searchable
        assert "cost justification" in result.freeform_text.lower()
