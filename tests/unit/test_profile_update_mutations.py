"""Targeted tests for profile_update.py mutation coverage.

Tests deepcopy isolation and append-to-non-list fallback.
"""

from __future__ import annotations

from pes.domain.profile_update import apply_section_update


class TestDeepCopyIsolation:
    def test_original_profile_not_mutated_by_append(self):
        """apply_section_update must not mutate the original profile dict."""
        profile = {
            "past_performance": [{"agency": "DoD"}],
            "certifications": {"sam_gov": {"active": True}},
        }
        original_pp = profile["past_performance"].copy()
        original_certs_active = profile["certifications"]["sam_gov"]["active"]

        update = {
            "section": "past_performance",
            "action": "append",
            "value": {"agency": "NASA"},
        }
        result = apply_section_update(profile, update)

        # Result has new entry
        assert len(result["past_performance"]) == 2
        # Original is untouched (deep copy, not shallow)
        assert profile["past_performance"] == original_pp
        assert len(profile["past_performance"]) == 1

    def test_nested_dict_not_shared_after_update(self):
        """Nested dicts in the result must not share references with original."""
        profile = {"certifications": {"sam_gov": {"active": True, "cage_code": "1A2B3"}}}
        update = {
            "section": "certifications.sam_gov.cage_code",
            "action": "replace",
            "value": "XXXXX",
        }
        result = apply_section_update(profile, update)
        assert result["certifications"]["sam_gov"]["cage_code"] == "XXXXX"
        assert profile["certifications"]["sam_gov"]["cage_code"] == "1A2B3"


class TestAppendToNonList:
    def test_append_to_non_list_field_creates_list(self):
        """Appending to a field that is not a list should create a new list."""
        profile = {"capabilities": "not-a-list"}
        update = {
            "section": "capabilities",
            "action": "append",
            "value": "AI",
        }
        result = apply_section_update(profile, update)
        assert result["capabilities"] == ["AI"]
        assert isinstance(result["capabilities"], list)
