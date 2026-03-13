"""Targeted mutation-killing tests for KeywordPreFilter.

Kills surviving mutants by asserting on exact values, edge cases,
and behaviors that loose assertions miss.
"""

from __future__ import annotations

from pes.domain.keyword_prefilter import FilterResult, KeywordPreFilter


def _t(topic_id: str, title: str, topic_code: str = "") -> dict:
    return {"topic_id": topic_id, "topic_code": topic_code or topic_id, "title": title}


class TestFilterResultDefaults:
    """Kill mutants on dataclass defaults."""

    def test_default_candidates_is_empty_list(self) -> None:
        r = FilterResult()
        assert r.candidates == []
        assert isinstance(r.candidates, list)

    def test_default_eliminated_count_is_zero(self) -> None:
        r = FilterResult()
        assert r.eliminated_count == 0

    def test_default_warnings_is_empty_list(self) -> None:
        r = FilterResult()
        assert r.warnings == []


class TestTopicCodeMatching:
    """Kill mutants: pre-filter also matches against topic_code, not just title."""

    def test_matches_topic_code_when_title_does_not_match(self) -> None:
        pf = KeywordPreFilter()
        topic = _t("RF-001", "Generic Systems Research", topic_code="rf power module")
        result = pf.filter([topic], ["rf power"])
        assert len(result.candidates) == 1

    def test_searchable_combines_title_and_code(self) -> None:
        """Mutant: removing code from searchable string."""
        pf = KeywordPreFilter()
        # Code has "laser" but title doesn't
        topic = _t("LASER-001", "Advanced Optics", topic_code="laser beam control")
        result = pf.filter([topic], ["laser"])
        assert len(result.candidates) == 1
        assert result.eliminated_count == 0


class TestExactWarningMessages:
    """Kill mutants on warning message content."""

    def test_empty_capabilities_exact_warning(self) -> None:
        pf = KeywordPreFilter()
        result = pf.filter([_t("T-1", "Anything")], [])
        assert result.warnings == [
            "No capability keywords in profile -- all topics passed"
        ]

    def test_zero_matches_exact_warnings(self) -> None:
        pf = KeywordPreFilter()
        result = pf.filter([_t("T-1", "Unrelated Topic")], ["quantum teleportation"])
        assert result.warnings == [
            "No topics matched your company profile",
            "Review your profile capabilities or broaden your filters",
        ]

    def test_match_found_warning_format(self) -> None:
        pf = KeywordPreFilter()
        topics = [_t("T-1", "Directed Energy"), _t("T-2", "Biology")]
        result = pf.filter(topics, ["directed energy"])
        assert len(result.warnings) == 1
        assert result.warnings[0] == "Keyword match: 1 candidate topics (1 eliminated)"


class TestEliminatedCountExact:
    """Kill mutants on eliminated_count increment."""

    def test_three_eliminated_two_matched(self) -> None:
        pf = KeywordPreFilter()
        topics = [
            _t("T-1", "Directed Energy System"),
            _t("T-2", "Marine Biology"),
            _t("T-3", "RF Power Amplifier"),
            _t("T-4", "Underwater Research"),
            _t("T-5", "Food Safety"),
        ]
        result = pf.filter(topics, ["directed energy", "rf power"])
        assert result.eliminated_count == 3
        assert len(result.candidates) == 2

    def test_all_eliminated(self) -> None:
        pf = KeywordPreFilter()
        topics = [_t("T-1", "A"), _t("T-2", "B"), _t("T-3", "C")]
        result = pf.filter(topics, ["xyz"])
        assert result.eliminated_count == 3
        assert len(result.candidates) == 0


class TestCandidateIsCopy:
    """Kill mutants on dict(topic) creating a copy."""

    def test_candidate_is_separate_dict_from_original(self) -> None:
        pf = KeywordPreFilter()
        original = _t("T-1", "Directed Energy")
        result = pf.filter([original], ["directed energy"])
        candidate = result.candidates[0]
        assert "matched_keywords" in candidate
        assert "matched_keywords" not in original

    def test_matched_keywords_exact_values(self) -> None:
        pf = KeywordPreFilter()
        topics = [_t("T-1", "Directed Energy and RF Power")]
        result = pf.filter(topics, ["directed energy", "rf power", "quantum"])
        assert result.candidates[0]["matched_keywords"] == ["directed energy", "rf power"]


class TestEmptyCapabilitiesReturnsCopy:
    """Kill mutants on list(topics) in empty capabilities path."""

    def test_empty_caps_returns_all_topics(self) -> None:
        pf = KeywordPreFilter()
        topics = [_t("T-1", "A"), _t("T-2", "B")]
        result = pf.filter(topics, [])
        assert len(result.candidates) == 2
        assert result.eliminated_count == 0

    def test_empty_caps_candidates_are_original_objects(self) -> None:
        """With empty capabilities, list(topics) is used (shallow copy of list)."""
        pf = KeywordPreFilter()
        topics = [_t("T-1", "A")]
        result = pf.filter(topics, [])
        # Should be same objects (list() copies list, not items)
        assert result.candidates[0] is topics[0]


class TestMissingFields:
    """Kill mutants on .get() defaults for missing fields."""

    def test_topic_missing_title_does_not_crash(self) -> None:
        pf = KeywordPreFilter()
        result = pf.filter([{"topic_id": "T-1", "topic_code": "T-1"}], ["energy"])
        assert len(result.candidates) == 0

    def test_topic_missing_topic_code_does_not_crash(self) -> None:
        pf = KeywordPreFilter()
        result = pf.filter([{"topic_id": "T-1", "title": "Energy"}], ["energy"])
        assert len(result.candidates) == 1
