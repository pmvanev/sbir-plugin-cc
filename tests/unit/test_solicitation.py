"""Unit tests for solicitation parsing through TextSolicitationAdapter.

Test Budget: 3 behaviors x 2 = 6 unit tests max.
The adapter is tested as an integration test (real text parsing),
but since this is a pure text parser with no infrastructure,
it can be tested as a unit.

Tests verify:
1. Extracts all metadata fields from well-formed text
2. Returns error for unparseable content
3. Returns warnings for missing optional fields
"""

from __future__ import annotations

import pytest

from pes.adapters.text_solicitation_adapter import TextSolicitationAdapter


@pytest.fixture()
def parser():
    return TextSolicitationAdapter()


WELL_FORMED_SOLICITATION = """
SBIR/STTR Topic Information
Topic ID: AF243-001
Agency: Air Force
Phase: I
Deadline: 2026-04-15
Title: Compact Directed Energy for Maritime UAS Defense

Description: This topic seeks innovative approaches to compact directed
energy systems for defense against unmanned aerial systems in maritime
environments.
"""


# ---------------------------------------------------------------------------
# Behavior 1: Extracts metadata from well-formed solicitation
# ---------------------------------------------------------------------------


class TestExtractMetadata:
    def test_extracts_all_fields_from_well_formed_text(self, parser):
        result = parser.parse(WELL_FORMED_SOLICITATION)

        assert result.success
        assert result.topic.topic_id == "AF243-001"
        assert result.topic.agency == "Air Force"
        assert result.topic.phase == "I"
        assert result.topic.deadline == "2026-04-15"
        assert result.topic.title == "Compact Directed Energy for Maritime UAS Defense"

    @pytest.mark.parametrize("field_line,field_name,expected", [
        ("Topic ID: N241-001", "topic_id", "N241-001"),
        ("Agency: Navy", "agency", "Navy"),
        ("Phase: II", "phase", "II"),
        ("Deadline: 2026-06-30", "deadline", "2026-06-30"),
    ])
    def test_extracts_individual_fields(self, parser, field_line, field_name, expected):
        text = """
Topic ID: N241-001
Agency: Navy
Phase: II
Deadline: 2026-06-30
Title: Advanced Sonar Processing
"""
        result = parser.parse(text)
        assert result.success
        assert getattr(result.topic, field_name) == expected


# ---------------------------------------------------------------------------
# Behavior 2: Returns error for unparseable content
# ---------------------------------------------------------------------------


class TestUnparseableContent:
    def test_returns_error_for_no_extractable_fields(self, parser):
        result = parser.parse("BINARY_IMAGE_CONTENT_NO_TEXT")

        assert not result.success
        assert result.error is not None
        assert "could not parse" in result.error.lower()


# ---------------------------------------------------------------------------
# Behavior 3: Returns warnings for missing fields
# ---------------------------------------------------------------------------


class TestMissingFields:
    def test_missing_deadline_produces_warning(self, parser):
        text = """
Topic ID: AF243-003
Agency: Air Force
Phase: I
Title: Some Research Topic
"""
        result = parser.parse(text)

        assert result.success
        assert result.warnings is not None
        assert any("deadline" in w.lower() for w in result.warnings)
