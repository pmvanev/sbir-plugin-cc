"""Tests for SamGovAdapter -- SAM.gov Entity API enrichment through port boundary.

Tests exercise EnrichmentSourcePort via SamGovAdapter. HTTP calls are mocked
at the transport layer (httpx.Client) -- the adapter is tested with fake HTTP
responses, not real API calls.

Test Budget: 4 distinct behaviors x 2 = 8 max unit tests. Using 5.
Behaviors:
  B1: Valid UEI returns mapped EnrichedField objects (name, CAGE, NAICS, certs, status)
  B2: UEI with no matching entity returns not-found indicator
  B3: Network timeout returns SourceError with type 'timeout'
  B4: Business type codes map to human-readable certification names
  B5: HTTP error status returns SourceError with details
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest

from pes.adapters.sam_gov_adapter import SamGovAdapter
from pes.domain.enrichment import EnrichedField, SourceError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_client() -> MagicMock:
    """Mock httpx.Client for HTTP transport mocking."""
    return MagicMock(spec=httpx.Client)


@pytest.fixture()
def adapter(mock_client: MagicMock) -> SamGovAdapter:
    """SamGovAdapter with injected mock HTTP client."""
    return SamGovAdapter(client=mock_client, timeout=10.0)


def _sam_entity_response(
    legal_name: str = "Radiant Defense Systems, LLC",
    cage_code: str = "7X2K9",
    uei: str = "DKJF84NXLE73",
    naics_code: str = "334511",
    naics_list: list[dict] | None = None,
    registration_status: str = "Active",
    expiration_date: str = "2027-01-15",
    business_types: list[str] | None = None,
) -> dict:
    """Build a SAM.gov API response matching the v3 entity format."""
    if naics_list is None:
        naics_list = [
            {"naicsCode": "334511", "isPrimary": True},
            {"naicsCode": "541715", "isPrimary": False},
            {"naicsCode": "334220", "isPrimary": False},
        ]
    return {
        "totalRecords": 1,
        "entityData": [
            {
                "entityRegistration": {
                    "legalBusinessName": legal_name,
                    "cageCode": cage_code,
                    "ueiSAM": uei,
                    "registrationStatus": registration_status,
                    "registrationExpirationDate": expiration_date,
                },
                "assertions": {
                    "goodsAndServices": {
                        "naicsCode": naics_code,
                        "naicsList": naics_list,
                        "businessTypeList": [
                            {"businessTypeCode": bt}
                            for bt in (business_types or [])
                        ],
                    },
                },
            },
        ],
    }


def _mock_response(status_code: int = 200, json_data: dict | None = None) -> MagicMock:
    """Create a mock httpx.Response."""
    response = MagicMock(spec=httpx.Response)
    response.status_code = status_code
    response.json.return_value = json_data or {}
    response.raise_for_status = MagicMock()
    if status_code >= 400:
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            f"{status_code} Error",
            request=MagicMock(),
            response=response,
        )
    return response


# ---------- B1: Valid UEI returns mapped EnrichedField objects ----------


def test_valid_uei_returns_mapped_fields(adapter, mock_client):
    """Given a valid UEI and API key, when SAM.gov returns entity data,
    then legal name, CAGE code, NAICS codes, certifications, and
    registration status are mapped to EnrichedField objects."""
    mock_client.get.return_value = _mock_response(
        200, _sam_entity_response()
    )

    result = adapter.fetch_fields("DKJF84NXLE73", api_key="test-key")

    assert result.found is True
    assert result.error is None
    assert len(result.fields) > 0

    # Check field paths present
    field_paths = {f.field_path for f in result.fields}
    assert "company_name" in field_paths
    assert "certifications.sam_gov.cage_code" in field_paths
    assert "naics_codes" in field_paths
    assert "certifications.sam_gov.active" in field_paths
    assert "certifications.sam_gov.registration_expiration" in field_paths

    # Check values
    name_field = next(f for f in result.fields if f.field_path == "company_name")
    assert name_field.value == "Radiant Defense Systems, LLC"
    assert name_field.source.api_name == "SAM.gov"
    assert name_field.confidence == "high"

    cage_field = next(f for f in result.fields if f.field_path == "certifications.sam_gov.cage_code")
    assert cage_field.value == "7X2K9"

    naics_field = next(f for f in result.fields if f.field_path == "naics_codes")
    assert len(naics_field.value) == 3
    assert naics_field.value[0]["code"] == "334511"
    assert naics_field.value[0]["primary"] is True

    active_field = next(f for f in result.fields if f.field_path == "certifications.sam_gov.active")
    assert active_field.value is True

    expiry_field = next(f for f in result.fields if f.field_path == "certifications.sam_gov.registration_expiration")
    assert expiry_field.value == "2027-01-15"


# ---------- B2: UEI with no match returns not-found ----------


def test_no_entity_returns_not_found(adapter, mock_client):
    """Given a UEI with no matching entity, when SAM.gov returns empty
    results, then a not-found indicator is returned with no fields."""
    mock_client.get.return_value = _mock_response(
        200, {"totalRecords": 0, "entityData": []}
    )

    result = adapter.fetch_fields("XYZABC123456", api_key="test-key")

    assert result.found is False
    assert result.fields == []
    assert result.error is None


# ---------- B3: Network timeout returns SourceError ----------


def test_timeout_returns_source_error(adapter, mock_client):
    """Given a network timeout, when the adapter call fails, then a
    SourceError with type 'timeout' is returned and no exception propagates."""
    mock_client.get.side_effect = httpx.TimeoutException("Connection timed out")

    result = adapter.fetch_fields("DKJF84NXLE73", api_key="test-key")

    assert result.error is not None
    assert result.error.error_type == "timeout"
    assert result.error.api_name == "SAM.gov"
    assert "timed out" in result.error.message.lower()
    assert result.fields == []


# ---------- B4: Business type codes map to readable certifications ----------


@pytest.mark.parametrize("codes,expected_certs", [
    (["A8"], ["8(a)"]),
    (["QF"], ["HUBZone"]),
    (["A5"], ["WOSB"]),
    (["QE"], ["SDVOSB"]),
    (["A9"], ["VOSB"]),
    (["27"], ["SDB"]),
    (["LJ"], ["EDWOSB"]),
    (["A8", "QF", "A5"], ["8(a)", "HUBZone", "WOSB"]),
    ([], []),
])
def test_business_type_codes_map_to_certifications(adapter, mock_client, codes, expected_certs):
    """Given business type codes in the response, when mapped, then codes
    produce human-readable certification names."""
    mock_client.get.return_value = _mock_response(
        200, _sam_entity_response(business_types=codes)
    )

    result = adapter.fetch_fields("DKJF84NXLE73", api_key="test-key")

    cert_field = next(
        (f for f in result.fields if f.field_path == "certifications.socioeconomic"),
        None,
    )
    if expected_certs:
        assert cert_field is not None
        assert cert_field.value == expected_certs
    else:
        # No certs field when no business type codes match
        assert cert_field is None or cert_field.value == []


# ---------- B5: HTTP error returns SourceError ----------


def test_http_error_returns_source_error(adapter, mock_client):
    """Given an HTTP error status, when the adapter call fails, then a
    SourceError with the HTTP status is returned."""
    mock_client.get.return_value = _mock_response(403)

    result = adapter.fetch_fields("DKJF84NXLE73", api_key="test-key")

    assert result.error is not None
    assert result.error.api_name == "SAM.gov"
    assert result.error.http_status == 403
    assert result.fields == []
