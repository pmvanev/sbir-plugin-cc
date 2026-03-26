"""Unit tests for EnrichmentService -- three-API cascade orchestration.

Tests exercise the enrichment service through its public enrich() method.
Adapters are fakes implementing the port interfaces at the hexagonal boundary.

Test Budget: 4 distinct behaviors x 2 = 8 max unit tests. Using 5.
Behaviors:
  B1: All three APIs succeed -> merged result with fields from all sources
  B2: One secondary API fails -> partial result, failed source in errors list
  B3: SAM.gov fails -> other APIs still attempted, SAM.gov in errors
  B4: Missing fields = required schema fields minus populated fields
  B5: SAM.gov not-found -> still attempts secondary APIs with empty company name
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from pes.domain.enrichment import (
    EnrichedField,
    EnrichmentResult,
    FieldSource,
    SourceError,
)
from pes.domain.enrichment_service import EnrichmentService
from pes.ports.enrichment_port import EnrichmentSourcePort, SourceResult


# ---------------------------------------------------------------------------
# Fakes -- port boundary test doubles
# ---------------------------------------------------------------------------

_TIMESTAMP = "2026-03-26T14:00:00Z"


def _make_source(api_name: str) -> FieldSource:
    return FieldSource(api_name=api_name, api_url=f"https://{api_name}/test", accessed_at=_TIMESTAMP)


def _make_field(path: str, value: str, api_name: str) -> EnrichedField:
    return EnrichedField(field_path=path, value=value, source=_make_source(api_name), confidence="high")


class FakeSamAdapter(EnrichmentSourcePort):
    """Fake SAM.gov adapter returning canned SourceResult."""

    def __init__(self, result: SourceResult) -> None:
        self._result = result

    @property
    def source_name(self) -> str:
        return "SAM.gov"

    def fetch_fields(self, uei: str, api_key: str | None = None) -> SourceResult:
        return self._result


@dataclass
class FakeSbirAdapter:
    """Fake SBIR.gov adapter returning canned result."""

    fields: list[EnrichedField] = field(default_factory=list)
    error: SourceError | None = None
    called: bool = False

    @property
    def source_name(self) -> str:
        return "SBIR.gov"

    def fetch_by_company_name(self, company_name: str):
        from pes.adapters.sbir_gov_adapter import SbirGovCompanyResult

        self.called = True
        if self.error:
            return SbirGovCompanyResult(error=self.error)
        return SbirGovCompanyResult(fields=self.fields)


@dataclass
class FakeUsaSpendingAdapter:
    """Fake USASpending adapter returning canned result."""

    fields: list[EnrichedField] = field(default_factory=list)
    error: SourceError | None = None
    called: bool = False

    @property
    def source_name(self) -> str:
        return "USASpending.gov"

    def fetch_by_company_name(self, company_name: str):
        from pes.adapters.usa_spending_adapter import UsaSpendingResult

        self.called = True
        if self.error:
            return UsaSpendingResult(error=self.error)
        return UsaSpendingResult(fields=self.fields)


# ---------------------------------------------------------------------------
# Required fields for missing-fields computation
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = [
    "company_name",
    "certifications.sam_gov.cage_code",
    "sbir_awards",
    "federal_awards.total_amount",
    "capabilities",
    "security_clearance",
    "key_personnel",
]


# ---------------------------------------------------------------------------
# B1: All three APIs succeed -> merged result
# ---------------------------------------------------------------------------


def test_all_three_apis_succeed_returns_merged_result():
    sam_fields = [
        _make_field("company_name", "Acme Corp", "SAM.gov"),
        _make_field("certifications.sam_gov.cage_code", "ABC12", "SAM.gov"),
    ]
    sbir_fields = [_make_field("sbir_awards", "[awards]", "SBIR.gov")]
    usa_fields = [_make_field("federal_awards.total_amount", "1000000", "USASpending.gov")]

    sam = FakeSamAdapter(SourceResult.success(sam_fields))
    sbir = FakeSbirAdapter(fields=sbir_fields)
    usa = FakeUsaSpendingAdapter(fields=usa_fields)

    service = EnrichmentService(
        sam_adapter=sam,
        sbir_adapter=sbir,
        usa_spending_adapter=usa,
        required_fields=REQUIRED_FIELDS,
    )

    result = service.enrich(uei="DKJF84NXLE73", api_key="test-key")

    assert isinstance(result, EnrichmentResult)
    assert len(result.fields) == 4
    source_names = {f.source.api_name for f in result.fields}
    assert source_names == {"SAM.gov", "SBIR.gov", "USASpending.gov"}
    assert result.sources_attempted == ["SAM.gov", "SBIR.gov", "USASpending.gov"]
    assert result.sources_succeeded == ["SAM.gov", "SBIR.gov", "USASpending.gov"]
    assert result.errors == []


# ---------------------------------------------------------------------------
# B2: SBIR.gov fails -> partial result with SBIR.gov in errors
# ---------------------------------------------------------------------------


def test_sbir_fails_returns_partial_result_with_error():
    sam_fields = [_make_field("company_name", "Acme Corp", "SAM.gov")]
    usa_fields = [_make_field("federal_awards.total_amount", "1000000", "USASpending.gov")]
    sbir_error = SourceError(api_name="SBIR.gov", error_type="timeout", message="Timed out")

    sam = FakeSamAdapter(SourceResult.success(sam_fields))
    sbir = FakeSbirAdapter(error=sbir_error)
    usa = FakeUsaSpendingAdapter(fields=usa_fields)

    service = EnrichmentService(
        sam_adapter=sam,
        sbir_adapter=sbir,
        usa_spending_adapter=usa,
        required_fields=REQUIRED_FIELDS,
    )

    result = service.enrich(uei="DKJF84NXLE73", api_key="test-key")

    assert len(result.fields) == 2
    assert len(result.errors) == 1
    assert result.errors[0].api_name == "SBIR.gov"
    assert "SBIR.gov" not in result.sources_succeeded
    assert "SBIR.gov" in result.sources_attempted


# ---------------------------------------------------------------------------
# B3: SAM.gov fails -> other APIs still attempted, SAM.gov in errors
# ---------------------------------------------------------------------------


def test_sam_fails_other_apis_still_attempted():
    sam_error = SourceError(api_name="SAM.gov", error_type="auth_failed", message="HTTP 403")
    sbir_fields = [_make_field("sbir_awards", "[awards]", "SBIR.gov")]
    usa_fields = [_make_field("federal_awards.total_amount", "500000", "USASpending.gov")]

    sam = FakeSamAdapter(SourceResult.failure(sam_error))
    sbir = FakeSbirAdapter(fields=sbir_fields)
    usa = FakeUsaSpendingAdapter(fields=usa_fields)

    service = EnrichmentService(
        sam_adapter=sam,
        sbir_adapter=sbir,
        usa_spending_adapter=usa,
        required_fields=REQUIRED_FIELDS,
    )

    result = service.enrich(uei="DKJF84NXLE73", api_key="test-key")

    assert sbir.called is True
    assert usa.called is True
    assert len(result.errors) == 1
    assert result.errors[0].api_name == "SAM.gov"
    assert "SAM.gov" not in result.sources_succeeded
    assert "SBIR.gov" in result.sources_succeeded
    assert "USASpending.gov" in result.sources_succeeded


# ---------------------------------------------------------------------------
# B4: Missing fields = required minus populated
# ---------------------------------------------------------------------------


def test_missing_fields_reflects_unpopulated_required_fields():
    sam_fields = [
        _make_field("company_name", "Acme Corp", "SAM.gov"),
        _make_field("certifications.sam_gov.cage_code", "ABC12", "SAM.gov"),
    ]

    sam = FakeSamAdapter(SourceResult.success(sam_fields))
    sbir = FakeSbirAdapter()
    usa = FakeUsaSpendingAdapter()

    service = EnrichmentService(
        sam_adapter=sam,
        sbir_adapter=sbir,
        usa_spending_adapter=usa,
        required_fields=REQUIRED_FIELDS,
    )

    result = service.enrich(uei="DKJF84NXLE73", api_key="test-key")

    assert "company_name" not in result.missing_fields
    assert "certifications.sam_gov.cage_code" not in result.missing_fields
    assert "capabilities" in result.missing_fields
    assert "security_clearance" in result.missing_fields
    assert "key_personnel" in result.missing_fields


# ---------------------------------------------------------------------------
# B5: SAM.gov not-found -> secondary APIs still attempted
# ---------------------------------------------------------------------------


def test_sam_not_found_still_attempts_secondary_apis():
    sbir_fields = [_make_field("sbir_awards", "[awards]", "SBIR.gov")]

    sam = FakeSamAdapter(SourceResult.not_found())
    sbir = FakeSbirAdapter(fields=sbir_fields)
    usa = FakeUsaSpendingAdapter()

    service = EnrichmentService(
        sam_adapter=sam,
        sbir_adapter=sbir,
        usa_spending_adapter=usa,
        required_fields=REQUIRED_FIELDS,
    )

    result = service.enrich(uei="DKJF84NXLE73", api_key="test-key")

    assert sbir.called is True
    assert usa.called is True
    assert "SAM.gov" not in result.sources_succeeded
