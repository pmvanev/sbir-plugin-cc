"""Tests for SbirGovAdapter -- SBIR.gov Company and Awards API enrichment.

Tests exercise the adapter through its public methods with mocked HTTP
transport (httpx.Client constructor injection). Follows same pattern as
test_sam_gov_adapter.py.

Test Budget: 4 distinct behaviors x 2 = 8 max unit tests. Using 5.
Behaviors:
  B1: Single company match fetches award history as EnrichedField objects
  B2: Multiple firm matches returns CompanyCandidate list for disambiguation
  B3: Timeout returns SourceError without exception propagation
  B4: Award data mapping includes agency, topic area, and phase
  B5: HTTP error returns SourceError with status details
"""

from __future__ import annotations

from unittest.mock import MagicMock

import httpx
import pytest

from pes.adapters.sbir_gov_adapter import SbirGovAdapter
from pes.domain.enrichment import CompanyCandidate, SourceError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_client() -> MagicMock:
    """Mock httpx.Client for HTTP transport mocking."""
    return MagicMock(spec=httpx.Client)


@pytest.fixture()
def adapter(mock_client: MagicMock) -> SbirGovAdapter:
    """SbirGovAdapter with injected mock HTTP client."""
    return SbirGovAdapter(client=mock_client, timeout=10.0)


def _company_response(firms: list[dict] | None = None) -> dict:
    """Build an SBIR.gov company API response."""
    if firms is None:
        firms = [
            {
                "company_name": "Radiant Defense Systems, LLC",
                "city": "Arlington",
                "state": "VA",
                "number_awards": 12,
                "firm_nid": "firm-001",
                "uei": "DKJF84NXLE73",
            }
        ]
    return firms


def _awards_response(awards: list[dict] | None = None) -> dict:
    """Build an SBIR.gov awards API response."""
    if awards is None:
        awards = [
            {
                "agency": "DOD",
                "branch": "Army",
                "award_title": "Sensor Fusion for UAVs",
                "award_year": "2024",
                "phase": "Phase I",
                "program": "SBIR",
                "award_amount": 150000,
                "abstract": "Develop next-gen sensor fusion.",
                "research_keywords": "sensor fusion, UAV, defense",
            },
            {
                "agency": "DOE",
                "branch": "",
                "award_title": "Grid Storage Optimization",
                "award_year": "2023",
                "phase": "Phase II",
                "program": "STTR",
                "award_amount": 750000,
                "abstract": "Optimize grid-scale battery storage.",
                "research_keywords": "energy storage, grid, optimization",
            },
        ]
    return awards


def _mock_response(status_code: int = 200, json_data=None) -> MagicMock:
    """Create a mock httpx.Response."""
    response = MagicMock(spec=httpx.Response)
    response.status_code = status_code
    response.json.return_value = json_data if json_data is not None else {}
    response.raise_for_status = MagicMock()
    if status_code >= 400:
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            f"{status_code} Error",
            request=MagicMock(),
            response=response,
        )
    return response


# ---------- B1: Single match returns award history as EnrichedField objects ----------


def test_single_company_match_returns_award_fields(adapter, mock_client):
    """Given a company name matching one SBIR.gov firm, when fetched, then
    award history is returned as EnrichedField objects with per-award
    agency and phase."""
    # First call: company search returns single match
    # Second call: awards fetch returns award list
    mock_client.get.side_effect = [
        _mock_response(200, _company_response()),
        _mock_response(200, _awards_response()),
    ]

    result = adapter.fetch_by_company_name("Radiant Defense Systems")

    assert result.found is True
    assert result.error is None
    assert len(result.fields) > 0

    # Should have sbir_award_history field
    field_paths = {f.field_path for f in result.fields}
    assert "sbir_awards" in field_paths

    awards_field = next(f for f in result.fields if f.field_path == "sbir_awards")
    assert len(awards_field.value) == 2
    assert awards_field.value[0]["agency"] == "DOD"
    assert awards_field.value[0]["phase"] == "Phase I"
    assert awards_field.value[1]["agency"] == "DOE"
    assert awards_field.value[1]["phase"] == "Phase II"
    assert awards_field.source.api_name == "SBIR.gov"
    assert awards_field.confidence == "high"


# ---------- B2: Multiple firm matches returns CompanyCandidate list ----------


def test_multiple_matches_returns_candidates(adapter, mock_client):
    """Given a company name matching multiple SBIR.gov firms, when fetched,
    then a CompanyCandidate list is returned for caller disambiguation."""
    firms = [
        {
            "company_name": "Radiant Defense Systems, LLC",
            "city": "Arlington",
            "state": "VA",
            "number_awards": 12,
            "firm_nid": "firm-001",
            "uei": "DKJF84NXLE73",
        },
        {
            "company_name": "Radiant Defense Corp",
            "city": "San Diego",
            "state": "CA",
            "number_awards": 3,
            "firm_nid": "firm-002",
            "uei": "ABCD12345678",
        },
    ]
    mock_client.get.return_value = _mock_response(200, _company_response(firms))

    result = adapter.fetch_by_company_name("Radiant Defense")

    assert result.candidates is not None
    assert len(result.candidates) == 2
    assert result.candidates[0].company_name == "Radiant Defense Systems, LLC"
    assert result.candidates[0].city == "Arlington"
    assert result.candidates[0].state == "VA"
    assert result.candidates[0].award_count == 12
    assert result.candidates[0].firm_id == "firm-001"
    assert result.candidates[1].company_name == "Radiant Defense Corp"
    assert result.candidates[1].firm_id == "firm-002"
    assert result.fields == []


# ---------- B3: Timeout returns SourceError ----------


def test_timeout_returns_source_error(adapter, mock_client):
    """Given a timeout on SBIR.gov, when the adapter call fails, then a
    SourceError is returned without blocking other adapters."""
    mock_client.get.side_effect = httpx.TimeoutException("Connection timed out")

    result = adapter.fetch_by_company_name("Radiant Defense Systems")

    assert result.error is not None
    assert result.error.error_type == "timeout"
    assert result.error.api_name == "SBIR.gov"
    assert "timed out" in result.error.message.lower()
    assert result.fields == []


# ---------- B4: Award data mapping includes agency, topic area, and phase ----------


def test_award_mapping_includes_agency_topic_and_phase(adapter, mock_client):
    """Given award data, when mapped, then each award includes agency,
    topic area (research_keywords), and phase."""
    awards = [
        {
            "agency": "NASA",
            "branch": "GSFC",
            "award_title": "Lunar Comms",
            "award_year": "2025",
            "phase": "Phase I",
            "program": "SBIR",
            "award_amount": 125000,
            "abstract": "Lunar communication relay.",
            "research_keywords": "lunar, communications, relay",
        },
    ]
    mock_client.get.side_effect = [
        _mock_response(200, _company_response()),
        _mock_response(200, _awards_response(awards)),
    ]

    result = adapter.fetch_by_company_name("Radiant Defense Systems")

    awards_field = next(f for f in result.fields if f.field_path == "sbir_awards")
    award = awards_field.value[0]
    assert award["agency"] == "NASA"
    assert award["phase"] == "Phase I"
    assert award["topic_area"] == "lunar, communications, relay"
    assert award["program"] == "SBIR"
    assert award["year"] == "2025"
    assert award["amount"] == 125000


# ---------- B5: HTTP error returns SourceError ----------


def test_http_error_returns_source_error(adapter, mock_client):
    """Given an HTTP error status from SBIR.gov, when the adapter call fails,
    then a SourceError with the HTTP status is returned."""
    mock_client.get.return_value = _mock_response(503)

    result = adapter.fetch_by_company_name("Radiant Defense Systems")

    assert result.error is not None
    assert result.error.api_name == "SBIR.gov"
    assert result.error.http_status == 503
    assert result.fields == []
