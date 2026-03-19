"""Targeted unit tests for topic_enrichment domain logic -- mutation coverage.

Test Budget: 4 behaviors x 2 = 8 max unit tests.

These are pure domain functions with stable public interfaces (Mandate 2 exception).
Tests target mutant survival gaps identified by mutmut: field merging, skip logic,
conditional report lines, and error formatting.

Behaviors tested:
1. combine_topics_with_enrichment: merges enrichment fields into matching candidates
2. combine_topics_with_enrichment: skips candidates without enrichment match
3. completeness_report: conditional inclusion of instructions/QA lines
4. completeness_report: error message formatting with topic IDs
"""

from __future__ import annotations

import pytest

from pes.domain.topic_enrichment import combine_topics_with_enrichment, completeness_report


# ---------------------------------------------------------------------------
# Behavior 1: Merge enrichment fields into matching candidates
# ---------------------------------------------------------------------------


class TestCombineMergesFields:
    """combine_topics_with_enrichment merges specific enrichment fields."""

    def test_merges_all_enrichment_fields_into_candidate(self) -> None:
        """Each enrichment field (description, instructions, component_instructions,
        qa_entries, enrichment_status) is merged into the candidate dict."""
        candidates = [{"topic_id": "T-001", "title": "Original Title"}]
        enriched = [{
            "topic_id": "T-001",
            "description": "Topic description text",
            "instructions": "Submit by Friday",
            "component_instructions": "Component A details",
            "qa_entries": [{"question": "Q1", "answer": "A1"}],
        }]

        result = combine_topics_with_enrichment(candidates, enriched)

        assert len(result) == 1
        merged = result[0]
        # Original fields preserved
        assert merged["title"] == "Original Title"
        # Enrichment fields merged
        assert merged["description"] == "Topic description text"
        assert merged["instructions"] == "Submit by Friday"
        assert merged["component_instructions"] == "Component A details"
        assert merged["qa_entries"] == [{"question": "Q1", "answer": "A1"}]
        assert merged["enrichment_status"] == "ok"

    def test_missing_enrichment_fields_default_to_empty(self) -> None:
        """When enrichment dict lacks optional fields, defaults are applied."""
        candidates = [{"topic_id": "T-001"}]
        enriched = [{"topic_id": "T-001"}]  # No description, instructions, etc.

        result = combine_topics_with_enrichment(candidates, enriched)

        assert len(result) == 1
        merged = result[0]
        assert merged["description"] == ""
        assert merged["instructions"] is None
        assert merged["component_instructions"] is None
        assert merged["qa_entries"] == []
        assert merged["enrichment_status"] == "ok"


# ---------------------------------------------------------------------------
# Behavior 2: Skip candidates without enrichment match
# ---------------------------------------------------------------------------


class TestCombineSkipsMissingEnrichment:
    """Candidates without matching enrichment entry are excluded from output."""

    def test_skips_candidate_without_matching_enrichment(self) -> None:
        """Only candidates with a matching enrichment entry appear in result."""
        candidates = [
            {"topic_id": "T-001", "title": "Matched"},
            {"topic_id": "T-002", "title": "Unmatched"},
            {"topic_id": "T-003", "title": "Also Matched"},
        ]
        enriched = [
            {"topic_id": "T-001", "description": "Desc 1"},
            {"topic_id": "T-003", "description": "Desc 3"},
        ]

        result = combine_topics_with_enrichment(candidates, enriched)

        assert len(result) == 2
        result_ids = [r["topic_id"] for r in result]
        assert "T-001" in result_ids
        assert "T-003" in result_ids
        assert "T-002" not in result_ids

    def test_empty_enrichment_returns_empty_list(self) -> None:
        """When no enrichment data provided, no candidates are returned."""
        candidates = [{"topic_id": "T-001"}, {"topic_id": "T-002"}]

        result = combine_topics_with_enrichment(candidates, [])

        assert result == []

    def test_candidate_without_topic_id_key_uses_empty_default(self) -> None:
        """Candidate missing topic_id key defaults to empty string for lookup."""
        candidates = [{"title": "No ID topic"}]
        # Enrichment keyed by empty string should match the default
        enriched = [{"topic_id": "", "description": "Matched by empty default"}]

        result = combine_topics_with_enrichment(candidates, enriched)

        assert len(result) == 1
        assert result[0]["description"] == "Matched by empty default"


# ---------------------------------------------------------------------------
# Behavior 3: Conditional report lines for instructions and QA
# ---------------------------------------------------------------------------


class TestCompletenessReportConditionalLines:
    """completeness_report conditionally includes instructions/QA lines."""

    @pytest.mark.parametrize(
        "completeness,expected_messages",
        [
            # Only descriptions (instructions=0, qa=0): 1 line
            (
                {"descriptions": 3, "instructions": 0, "qa": 0, "total": 5},
                ["Descriptions: 3/5"],
            ),
            # Descriptions + instructions=1 (boundary for > 0 vs > 1): 2 lines
            (
                {"descriptions": 3, "instructions": 1, "qa": 0, "total": 5},
                ["Descriptions: 3/5", "Instructions: 1/5"],
            ),
            # Descriptions + QA=1 (boundary for > 0 vs > 1): 2 lines
            (
                {"descriptions": 3, "instructions": 0, "qa": 1, "total": 5},
                ["Descriptions: 3/5", "Q&A: 1/5"],
            ),
            # All three present: 3 lines
            (
                {"descriptions": 5, "instructions": 3, "qa": 2, "total": 5},
                ["Descriptions: 5/5", "Instructions: 3/5", "Q&A: 2/5"],
            ),
        ],
        ids=["desc-only", "desc+instr-boundary", "desc+qa-boundary", "all-three"],
    )
    def test_conditional_lines_based_on_counts(
        self,
        completeness: dict[str, int],
        expected_messages: list[str],
    ) -> None:
        """Instructions and Q&A lines only appear when their count > 0."""
        messages = completeness_report(completeness, errors=[])

        assert messages == expected_messages

    def test_missing_keys_default_to_zero(self) -> None:
        """When completeness dict lacks keys, defaults produce 0/0 output."""
        messages = completeness_report({}, errors=[])

        assert messages == ["Descriptions: 0/0"]


# ---------------------------------------------------------------------------
# Behavior 4: Error message formatting
# ---------------------------------------------------------------------------


class TestCompletenessReportErrors:
    """completeness_report formats error messages with topic IDs."""

    def test_errors_appended_with_exact_format(self) -> None:
        """When errors present, message has exact format with count and comma-joined IDs."""
        completeness = {"descriptions": 2, "instructions": 0, "qa": 0, "total": 4}
        errors = [
            {"topic_id": "T-002", "error": "download failed"},
            {"topic_id": "T-004", "error": "timeout"},
        ]

        messages = completeness_report(completeness, errors)

        assert len(messages) == 2
        assert messages[0] == "Descriptions: 2/4"
        assert messages[1] == "Enrichment failed for 2 topics: T-002, T-004"

    def test_error_without_topic_id_uses_unknown_default(self) -> None:
        """Error dict missing topic_id defaults to 'unknown'."""
        completeness = {"descriptions": 0, "instructions": 0, "qa": 0, "total": 1}
        errors = [{"error": "some failure"}]

        messages = completeness_report(completeness, errors)

        error_msg = messages[-1]
        assert error_msg == "Enrichment failed for 1 topics: unknown"

    def test_no_errors_produces_no_failure_message(self) -> None:
        """When errors list is empty, no failure message is appended."""
        completeness = {"descriptions": 3, "instructions": 0, "qa": 0, "total": 3}

        messages = completeness_report(completeness, errors=[])

        assert not any("failed" in m.lower() for m in messages)

    def test_zero_total_produces_zero_denominators(self) -> None:
        """Edge case: total=0 produces 0/0 denominators without error."""
        completeness = {"descriptions": 0, "instructions": 0, "qa": 0, "total": 0}

        messages = completeness_report(completeness, errors=[])

        assert len(messages) == 1
        assert "0/0" in messages[0]
