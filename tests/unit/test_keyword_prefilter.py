"""Unit tests for KeywordPreFilter -- pure domain logic.

Test Budget: 3 behaviors x 2 = 6 max unit tests.
Behaviors:
  1. Matches topic titles against capability keywords (case-insensitive)
  2. Zero matches returns empty candidates with suggestion warning
  3. Empty capabilities returns all topics with warning
"""

from __future__ import annotations

import pytest

from pes.domain.keyword_prefilter import KeywordPreFilter


def _make_topic(topic_id: str, title: str) -> dict:
    """Minimal topic dict for pre-filter testing."""
    return {"topic_id": topic_id, "topic_code": topic_id, "title": title}


class TestKeywordPreFilterMatching:
    """Behavior 1: Filter matches topics by capability keywords in title."""

    @pytest.mark.parametrize(
        "title,capabilities,should_match",
        [
            # Exact keyword in title
            ("Compact Directed Energy for C-UAS", ["directed energy"], True),
            # Case-insensitive: uppercase title, lowercase capability
            ("DIRECTED ENERGY Systems for Defense", ["directed energy"], True),
            # Case-insensitive: mixed case capability
            ("RF Power Amplifier Design", ["rf power"], True),
            # No match
            ("Biodefense Pathogen Detection", ["directed energy"], False),
            # Partial keyword match within title
            ("Advanced Thermal Management Systems", ["thermal management"], True),
        ],
        ids=[
            "exact-keyword",
            "case-insensitive-upper",
            "case-insensitive-mixed",
            "no-match",
            "partial-phrase",
        ],
    )
    def test_matches_topics_by_capability_keywords(
        self, title: str, capabilities: list[str], should_match: bool
    ):
        prefilter = KeywordPreFilter()
        topics = [_make_topic("T-001", title)]
        result = prefilter.filter(topics, capabilities)

        if should_match:
            assert len(result.candidates) == 1
            assert result.eliminated_count == 0
        else:
            assert len(result.candidates) == 0
            assert result.eliminated_count == 1

    def test_annotates_matched_keywords_on_candidates(self):
        """Candidates should have matched_keywords field."""
        prefilter = KeywordPreFilter()
        topics = [_make_topic("T-001", "Directed Energy Laser System")]
        result = prefilter.filter(topics, ["directed energy", "quantum computing"])

        assert len(result.candidates) == 1
        candidate = result.candidates[0]
        assert "matched_keywords" in candidate
        assert "directed energy" in candidate["matched_keywords"]
        assert "quantum computing" not in candidate["matched_keywords"]

    def test_multiple_topics_filters_correctly(self):
        """Given many topics, only matching ones pass."""
        prefilter = KeywordPreFilter()
        topics = [
            _make_topic("T-001", "Directed Energy Application"),
            _make_topic("T-002", "Biodefense Research"),
            _make_topic("T-003", "RF Power Systems Design"),
        ]
        result = prefilter.filter(topics, ["directed energy", "RF power"])

        assert len(result.candidates) == 2
        assert result.eliminated_count == 1
        candidate_ids = [c["topic_id"] for c in result.candidates]
        assert "T-001" in candidate_ids
        assert "T-003" in candidate_ids


class TestKeywordPreFilterZeroMatches:
    """Behavior 2: Zero matches returns empty with suggestion."""

    def test_no_matches_returns_empty_with_warning(self):
        prefilter = KeywordPreFilter()
        topics = [
            _make_topic("T-001", "Biodefense Pathogen Detection"),
            _make_topic("T-002", "Marine Biology Research"),
        ]
        result = prefilter.filter(topics, ["underwater basket weaving"])

        assert len(result.candidates) == 0
        assert result.eliminated_count == 2
        assert any("no topics matched" in w.lower() for w in result.warnings)


class TestKeywordPreFilterEmptyCapabilities:
    """Behavior 3: Empty capabilities returns all topics with warning."""

    def test_empty_capabilities_passes_all_with_warning(self):
        prefilter = KeywordPreFilter()
        topics = [
            _make_topic("T-001", "Topic A"),
            _make_topic("T-002", "Topic B"),
        ]
        result = prefilter.filter(topics, [])

        assert len(result.candidates) == 2
        assert result.eliminated_count == 0
        assert any(
            "no capability keywords in profile" in w.lower()
            for w in result.warnings
        )
