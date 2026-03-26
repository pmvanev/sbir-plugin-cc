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
