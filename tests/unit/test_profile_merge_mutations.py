"""Targeted tests for profile_merge.py mutation coverage.

Tests check_completeness with populated/empty drafts and
merge_extractions with overlapping list deduplication.
"""

from __future__ import annotations

from pes.domain.profile_merge import (
    check_completeness,
    merge_extractions,
)


class TestCheckCompleteness:
    def test_complete_draft_returns_empty(self):
        """A draft with all required sections populated returns no missing."""
        draft = {
            "capabilities": ["AI"],
            "certifications": {"sam_gov": {"active": True}},
            "key_personnel": [{"name": "Jane"}],
            "past_performance": [{"agency": "DoD"}],
            "research_institution_partners": [{"name": "MIT"}],
        }
        assert check_completeness(draft) == []

    def test_empty_list_is_missing(self):
        """An empty list counts as missing."""
        draft = {
            "capabilities": [],
            "certifications": {"sam_gov": {}},
            "key_personnel": [{"name": "Jane"}],
            "past_performance": [{"agency": "DoD"}],
            "research_institution_partners": [{"name": "MIT"}],
        }
        result = check_completeness(draft)
        assert "capabilities" in result

    def test_empty_dict_is_missing(self):
        """An empty dict counts as missing."""
        draft = {
            "capabilities": ["AI"],
            "certifications": {},
            "key_personnel": [{"name": "Jane"}],
            "past_performance": [{"agency": "DoD"}],
            "research_institution_partners": [{"name": "MIT"}],
        }
        result = check_completeness(draft)
        assert "certifications" in result

    def test_none_value_is_missing(self):
        """A None value counts as missing."""
        draft = {
            "capabilities": None,
            "certifications": {"sam_gov": {}},
            "key_personnel": [{"name": "Jane"}],
            "past_performance": [{"agency": "DoD"}],
            "research_institution_partners": [{"name": "MIT"}],
        }
        result = check_completeness(draft)
        assert "capabilities" in result

    def test_nonempty_list_not_missing(self):
        """A populated list is NOT missing."""
        draft = {
            "capabilities": ["AI"],
            "certifications": {"sam_gov": {}},
            "key_personnel": [{"name": "Jane"}],
            "past_performance": [{"agency": "DoD"}],
            "research_institution_partners": [{"name": "MIT"}],
        }
        result = check_completeness(draft)
        assert "capabilities" not in result
        assert "key_personnel" not in result


class TestMergeExtractionsDedupe:
    def test_list_deduplication_preserves_order(self):
        """Merging overlapping lists deduplicates preserving first-seen order."""
        ext1 = {"capabilities": ["AI", "ML"]}
        ext2 = {"capabilities": ["ML", "NLP"]}
        result = merge_extractions(ext1, ext2)
        assert result["capabilities"] == ["AI", "ML", "NLP"]

    def test_list_concat_without_duplicates(self):
        """Merging distinct lists concatenates them."""
        ext1 = {"capabilities": ["AI"]}
        ext2 = {"capabilities": ["NLP"]}
        result = merge_extractions(ext1, ext2)
        assert result["capabilities"] == ["AI", "NLP"]

    def test_list_merge_with_all_duplicates(self):
        """Merging identical lists deduplicates to single set."""
        ext1 = {"capabilities": ["AI", "ML"]}
        ext2 = {"capabilities": ["AI", "ML"]}
        result = merge_extractions(ext1, ext2)
        assert result["capabilities"] == ["AI", "ML"]

    def test_dict_list_deduplication(self):
        """Dict items in lists are deduplicated by sorted key-value pairs."""
        ext1 = {"key_personnel": [{"name": "Jane", "role": "PI"}]}
        ext2 = {"key_personnel": [{"name": "Jane", "role": "PI"}, {"name": "Bob", "role": "CoPI"}]}
        result = merge_extractions(ext1, ext2)
        assert len(result["key_personnel"]) == 2
        assert result["key_personnel"][0] == {"name": "Jane", "role": "PI"}
        assert result["key_personnel"][1] == {"name": "Bob", "role": "CoPI"}
