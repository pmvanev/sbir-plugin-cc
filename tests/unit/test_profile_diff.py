"""Unit tests for ProfileDiff -- comparing EnrichmentResult against existing profile.

Tests exercise the diff_profile function directly. ProfileDiff is a pure domain
value object with standalone diff algorithm -- qualifies for direct testing per
Mandate 2 exception (complex standalone algorithm with stable public interface).

Test Budget: 5 distinct behaviors x 2 = 10 max unit tests. Using 5.
Behaviors:
  B1: New enriched values not in existing profile -> additions
  B2: Same array values in different order -> no change (order-independent)
  B3: User-entered fields absent from API -> api_missing, preserved
  B4: Enrichment matching all existing fields -> no changes
  B5: Changed scalar field -> appears in changes with old and new value
"""

from __future__ import annotations

import pytest

from pes.domain.enrichment import EnrichedField, EnrichmentResult, FieldSource
from pes.domain.profile_diff import diff_profile, ProfileDiff, DiffEntry


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TIMESTAMP = "2026-03-26T14:00:00Z"


def _source(api: str = "SAM.gov") -> FieldSource:
    return FieldSource(api_name=api, api_url=f"https://{api}/test", accessed_at=_TIMESTAMP)


def _field(path: str, value, api: str = "SAM.gov") -> EnrichedField:
    return EnrichedField(field_path=path, value=value, source=_source(api), confidence="high")


def _enrichment(*fields: EnrichedField) -> EnrichmentResult:
    return EnrichmentResult(
        uei="DKJF84NXLE73",
        fields=list(fields),
        missing_fields=[],
        sources_attempted=["SAM.gov"],
        sources_succeeded=["SAM.gov"],
    )


# ---------------------------------------------------------------------------
# B1: New enriched values not in existing profile -> additions
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "field_path,new_value,existing_profile",
    [
        (
            "certifications.sam_gov.naics_codes",
            ["334511", "541715", "334220"],
            {"certifications": {"sam_gov": {"naics_codes": ["334511", "541715"]}}},
        ),
        (
            "past_performance",
            [
                {"agency": "Navy", "topic_area": "Shipboard Power Conditioning", "outcome": "Phase I"},
                {"agency": "Army", "topic_area": "Sensors", "outcome": "Phase II"},
                {"agency": "DoE", "topic_area": "Solar", "outcome": "Phase I"},
            ],
            {
                "past_performance": [
                    {"agency": "Army", "topic_area": "Sensors", "outcome": "Phase II"},
                    {"agency": "DoE", "topic_area": "Solar", "outcome": "Phase I"},
                ]
            },
        ),
    ],
    ids=["new-naics-code", "new-sbir-award"],
)
def test_new_enriched_values_appear_as_additions(field_path, new_value, existing_profile):
    enrichment = _enrichment(_field(field_path, new_value))
    diff = diff_profile(enrichment, existing_profile)

    assert isinstance(diff, ProfileDiff)
    assert len(diff.additions) == 1
    assert diff.additions[0].field_path == field_path


# ---------------------------------------------------------------------------
# B2: Same array values in different order -> no change
# ---------------------------------------------------------------------------


def test_same_values_different_order_no_change():
    existing = {"certifications": {"sam_gov": {"naics_codes": ["541715", "334511"]}}}
    enrichment = _enrichment(
        _field("certifications.sam_gov.naics_codes", ["334511", "541715"])
    )

    diff = diff_profile(enrichment, existing)

    naics_additions = [a for a in diff.additions if a.field_path == "certifications.sam_gov.naics_codes"]
    naics_changes = [c for c in diff.changes if c.field_path == "certifications.sam_gov.naics_codes"]
    assert naics_additions == []
    assert naics_changes == []
    assert any(m.field_path == "certifications.sam_gov.naics_codes" for m in diff.matches)


# ---------------------------------------------------------------------------
# B3: User-entered fields not in API -> api_missing
# ---------------------------------------------------------------------------


def test_user_entered_fields_not_in_api_flagged_as_api_missing():
    existing = {
        "capabilities": ["radar systems", "signal processing"],
        "key_personnel": [{"name": "Alice", "role": "PI", "expertise": ["RF"]}],
        "company_name": "Acme Corp",
    }
    # Enrichment only has company_name -- capabilities and key_personnel not from API
    enrichment = _enrichment(_field("company_name", "Acme Corp"))

    diff = diff_profile(enrichment, existing)

    api_missing_paths = [m.field_path for m in diff.api_missing]
    assert "capabilities" in api_missing_paths
    assert "key_personnel" in api_missing_paths
    # company_name IS in API, so not api_missing
    assert "company_name" not in api_missing_paths


# ---------------------------------------------------------------------------
# B4: Enrichment matching all existing -> no changes
# ---------------------------------------------------------------------------


def test_enrichment_matching_existing_shows_no_changes():
    existing = {
        "company_name": "Acme Corp",
        "certifications": {"sam_gov": {"naics_codes": ["334511", "541715"]}},
    }
    enrichment = _enrichment(
        _field("company_name", "Acme Corp"),
        _field("certifications.sam_gov.naics_codes", ["334511", "541715"]),
    )

    diff = diff_profile(enrichment, existing)

    assert diff.additions == []
    assert diff.changes == []
    assert len(diff.matches) == 2
    assert diff.has_changes is False


# ---------------------------------------------------------------------------
# B5: Changed scalar value -> appears in changes
# ---------------------------------------------------------------------------


def test_changed_scalar_appears_in_changes():
    existing = {"employee_count": 45}
    enrichment = _enrichment(_field("employee_count", 50))

    diff = diff_profile(enrichment, existing)

    assert len(diff.changes) == 1
    assert diff.changes[0].field_path == "employee_count"
    assert diff.changes[0].old_value == 45
    assert diff.changes[0].new_value == 50
    assert diff.has_changes is True


# ---------------------------------------------------------------------------
# Mutation kill: immutability, defaults, path resolution, normalization
# ---------------------------------------------------------------------------


def test_diff_entry_and_profile_diff_are_immutable():
    """Kill frozen=True→False mutations."""
    entry = DiffEntry(field_path="x", new_value="v")
    with pytest.raises(AttributeError):
        entry.field_path = "changed"

    diff = ProfileDiff()
    with pytest.raises(AttributeError):
        diff.additions = []


def test_diff_entry_defaults():
    """Kill default value mutations on DiffEntry fields."""
    entry = DiffEntry(field_path="x")
    assert entry.new_value is None
    assert entry.old_value is None
    assert entry.source == ""


def test_profile_diff_defaults_are_empty_lists():
    """Kill default_factory=list→None mutations."""
    diff = ProfileDiff()
    assert diff.additions == []
    assert diff.changes == []
    assert diff.matches == []
    assert diff.api_missing == []


def test_has_changes_true_with_additions_only():
    """Kill 'additions or changes' → 'additions and changes' mutation."""
    diff = ProfileDiff(additions=[DiffEntry(field_path="x", new_value="v")])
    assert diff.has_changes is True


def test_resolve_path_stops_at_non_dict():
    """Kill isinstance(current, dict) mutation in _resolve_path."""
    existing = {"a": "not_a_dict"}
    enrichment = _enrichment(_field("a.b", "value"))
    diff = diff_profile(enrichment, existing)
    assert len(diff.additions) == 1
    assert diff.additions[0].field_path == "a.b"


def test_field_not_in_existing_is_addition():
    """Kill 'not found' → 'found' inversion in diff_profile."""
    existing = {}
    enrichment = _enrichment(_field("brand_new_field", "value"))
    diff = diff_profile(enrichment, existing)
    assert len(diff.additions) == 1
    assert diff.additions[0].new_value == "value"
    assert diff.additions[0].source == "SAM.gov"


def test_source_attribution_preserved_in_diff_entries():
    """Kill source assignment mutation (source = ef.source.api_name)."""
    enrichment = _enrichment(_field("company_name", "Acme", "SBIR.gov"))
    diff = diff_profile(enrichment, {"company_name": "Acme"})
    assert diff.matches[0].source == "SBIR.gov"


def test_list_length_mismatch_is_not_equal():
    """Kill len(old_list) != len(new_list) boundary in _sets_equal."""
    existing = {"tags": ["a", "b"]}
    enrichment = _enrichment(_field("tags", ["a", "b", "c"]))
    diff = diff_profile(enrichment, existing)
    # new has more items -> addition (via _list_has_additions)
    assert len(diff.additions) == 1


def test_nested_path_collect_api_missing():
    """Kill prefix/path construction in _collect_api_missing."""
    existing = {"level1": {"level2": "value"}}
    enrichment = _enrichment(_field("other_field", "x"))
    diff = diff_profile(enrichment, existing)
    missing_paths = [m.field_path for m in diff.api_missing]
    assert "level1" in missing_paths


def test_enriched_child_prevents_api_missing():
    """Kill has_enriched_child check in _collect_api_missing."""
    existing = {"certifications": {"sam_gov": {"cage_code": "ABC"}}}
    enrichment = _enrichment(_field("certifications.sam_gov.cage_code", "ABC"))
    diff = diff_profile(enrichment, existing)
    missing_paths = [m.field_path for m in diff.api_missing]
    # certifications should NOT be in api_missing because it has an enriched child
    assert "certifications" not in missing_paths
