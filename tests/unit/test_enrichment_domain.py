"""Unit tests for enrichment domain types and UEI validation.

Test budget: 4 distinct behaviors x 2 = 8 max unit tests.
Behaviors:
  1. Valid UEI accepted (12 alphanumeric)
  2. Invalid UEI rejected with descriptive message
  3. EnrichmentResult retains source attribution per field
  4. Missing fields = unpopulated required schema fields
"""

import pytest

from pes.domain.enrichment import (
    CompanyCandidate,
    EnrichedField,
    EnrichmentResult,
    FieldSource,
    SourceError,
    validate_uei,
)


# ---------- Behavior 1: Valid UEI accepted ----------


@pytest.mark.parametrize("uei", [
    "DKJF84NXLE73",  # mixed alpha-digit
    "AAAAAAAAAAAA",  # all alpha
    "123456789012",  # all digits
    "abcdef123456",  # lowercase alpha
])
def test_valid_uei_accepted(uei):
    result = validate_uei(uei)
    assert result.is_valid is True
    assert result.error is None


# ---------- Behavior 2: Invalid UEI rejected with message ----------


@pytest.mark.parametrize("uei,expected_substring", [
    ("SHORT", "12"),              # too short -- message mentions 12
    ("TOOLONGSTRING123", "12"),   # too long -- message mentions 12
    ("", "12"),                   # empty
    ("DKJF84NX-E73", "alphanumeric"),  # hyphen
    ("DKJF84NX LE7", "alphanumeric"),  # space
    ("DKJF!4NXLE73", "alphanumeric"),  # special char
])
def test_invalid_uei_rejected_with_descriptive_message(uei, expected_substring):
    result = validate_uei(uei)
    assert result.is_valid is False
    assert result.error is not None
    assert expected_substring.lower() in result.error.lower()


# ---------- Behavior 3: EnrichmentResult retains source attribution ----------


def test_enrichment_result_retains_source_per_field():
    sam_source = FieldSource(
        api_name="SAM.gov",
        api_url="https://api.sam.gov/entity-information/v3/entities?ueiSAM=DKJF84NXLE73",
        accessed_at="2026-03-26T14:00:00Z",
    )
    sbir_source = FieldSource(
        api_name="SBIR.gov",
        api_url="https://api.sbir.gov/company?keyword=Radiant",
        accessed_at="2026-03-26T14:01:00Z",
    )
    fields = [
        EnrichedField(
            field_path="company_name",
            value="Radiant Defense Systems, LLC",
            source=sam_source,
            confidence="high",
        ),
        EnrichedField(
            field_path="past_performance",
            value=[{"agency": "Air Force"}],
            source=sbir_source,
            confidence="high",
        ),
    ]
    result = EnrichmentResult(
        uei="DKJF84NXLE73",
        fields=fields,
        missing_fields=[],
        sources_attempted=["SAM.gov", "SBIR.gov"],
        sources_succeeded=["SAM.gov", "SBIR.gov"],
    )
    assert result.fields[0].source.api_name == "SAM.gov"
    assert result.fields[1].source.api_name == "SBIR.gov"
    assert result.fields[0].field_path == "company_name"
    assert result.fields[1].field_path == "past_performance"


# ---------- Behavior 4: Missing fields = unpopulated required fields ----------


def test_missing_fields_lists_only_unpopulated_required_fields():
    sam_source = FieldSource(
        api_name="SAM.gov",
        api_url="https://api.sam.gov/v3/entities",
        accessed_at="2026-03-26T14:00:00Z",
    )
    enriched = [
        EnrichedField(field_path="company_name", value="Acme", source=sam_source, confidence="high"),
        EnrichedField(field_path="certifications", value={"sam_gov": {"active": True}}, source=sam_source, confidence="high"),
    ]
    required_fields = [
        "company_name",
        "capabilities",
        "certifications",
        "employee_count",
        "key_personnel",
        "past_performance",
        "research_institution_partners",
    ]
    result = EnrichmentResult.with_missing_fields(
        uei="DKJF84NXLE73",
        fields=enriched,
        required_fields=required_fields,
        sources_attempted=["SAM.gov"],
        sources_succeeded=["SAM.gov"],
    )
    # company_name and certifications are populated -- should NOT be in missing
    assert "company_name" not in result.missing_fields
    assert "certifications" not in result.missing_fields
    # These are unpopulated -- should be in missing
    assert "capabilities" in result.missing_fields
    assert "employee_count" in result.missing_fields
    assert "key_personnel" in result.missing_fields
    assert "past_performance" in result.missing_fields
    assert "research_institution_partners" in result.missing_fields


# ---------- Supporting types: SourceError and CompanyCandidate ----------


def test_source_error_captures_api_failure_details():
    error = SourceError(
        api_name="SBIR.gov",
        error_type="timeout",
        message="Request timed out after 10 seconds",
        http_status=None,
    )
    assert error.api_name == "SBIR.gov"
    assert error.error_type == "timeout"
    assert error.message == "Request timed out after 10 seconds"
    assert error.http_status is None


def test_company_candidate_captures_disambiguation_fields():
    candidate = CompanyCandidate(
        company_name="Radiant Defense Systems, LLC",
        city="Huntsville",
        state="AL",
        award_count=3,
        firm_id="FIRM-12345",
    )
    assert candidate.company_name == "Radiant Defense Systems, LLC"
    assert candidate.award_count == 3
    assert candidate.firm_id == "FIRM-12345"


# ---------- Mutation kill: immutability, defaults, factory defaults ----------


def test_domain_value_objects_are_immutable():
    """Kill frozen=True→False mutations on all domain dataclasses."""
    source = FieldSource(api_name="SAM.gov", api_url="https://api.sam.gov", accessed_at="2026-01-01")
    with pytest.raises(AttributeError):
        source.api_name = "changed"

    field = EnrichedField(field_path="x", value="v", source=source, confidence="high")
    with pytest.raises(AttributeError):
        field.value = "changed"

    error = SourceError(api_name="X", error_type="timeout", message="msg")
    with pytest.raises(AttributeError):
        error.message = "changed"

    candidate = CompanyCandidate(company_name="X", city="Y", state="Z", award_count=0, firm_id="F")
    with pytest.raises(AttributeError):
        candidate.city = "changed"

    result = validate_uei("DKJF84NXLE73")
    with pytest.raises(AttributeError):
        result.is_valid = False


def test_source_error_default_http_status_is_none():
    """Kill http_status default None→'' mutation."""
    error = SourceError(api_name="X", error_type="t", message="m")
    assert error.http_status is None


def test_enrichment_result_default_lists_are_empty():
    """Kill default_factory=list→None mutations on disambiguation_needed and errors."""
    result = EnrichmentResult(
        uei="DKJF84NXLE73",
        fields=[],
        missing_fields=[],
        sources_attempted=[],
        sources_succeeded=[],
    )
    assert result.disambiguation_needed == []
    assert result.errors == []


def test_with_missing_fields_handles_none_disambiguation():
    """Kill 'or []' → 'and []' mutation on disambiguation_needed parameter."""
    result = EnrichmentResult.with_missing_fields(
        uei="DKJF84NXLE73",
        fields=[],
        required_fields=["company_name"],
        sources_attempted=[],
        sources_succeeded=[],
        disambiguation_needed=None,
    )
    assert result.disambiguation_needed == []
