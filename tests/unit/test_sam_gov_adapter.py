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

from pes.adapters.sam_gov_adapter import BUSINESS_TYPE_MAP, SAM_GOV_BASE_URL, SamGovAdapter
from pes.domain.enrichment import EnrichedField, FieldSource, SourceError


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


# ---------- Mutation-killing tests ----------


class TestSamGovMutationKillers:
    """Targeted tests to kill surviving mutants in sam_gov_adapter.py."""

    def test_source_name_property_exact_value(self, adapter):
        """Kill mutant: source_name string literal mutation."""
        assert adapter.source_name == "SAM.gov"

    def test_base_url_constant_exact_value(self):
        """Kill mutant: SAM_GOV_BASE_URL string mutation."""
        assert SAM_GOV_BASE_URL == "https://api.sam.gov/entity-information/v3/entities"

    def test_business_type_map_exact_entries(self):
        """Kill mutant: BUSINESS_TYPE_MAP key/value mutations."""
        assert BUSINESS_TYPE_MAP["A8"] == "8(a)"
        assert BUSINESS_TYPE_MAP["QF"] == "HUBZone"
        assert BUSINESS_TYPE_MAP["A5"] == "WOSB"
        assert BUSINESS_TYPE_MAP["QE"] == "SDVOSB"
        assert BUSINESS_TYPE_MAP["A9"] == "VOSB"
        assert BUSINESS_TYPE_MAP["27"] == "SDB"
        assert BUSINESS_TYPE_MAP["LJ"] == "EDWOSB"
        assert len(BUSINESS_TYPE_MAP) == 7

    def test_field_source_immutability(self, adapter, mock_client):
        """Kill mutant: frozen=True -> frozen=False on FieldSource."""
        source = FieldSource(api_name="SAM.gov", api_url="https://test", accessed_at="2026-01-01")
        with pytest.raises(AttributeError):
            source.api_name = "Other"

    def test_enriched_field_immutability(self, adapter, mock_client):
        """Kill mutant: frozen=True -> frozen=False on EnrichedField."""
        source = FieldSource(api_name="SAM.gov", api_url="https://test", accessed_at="2026-01-01")
        field = EnrichedField(field_path="test", value="val", source=source, confidence="high")
        with pytest.raises(AttributeError):
            field.field_path = "other"

    def test_source_error_immutability(self):
        """Kill mutant: frozen=True -> frozen=False on SourceError."""
        error = SourceError(api_name="SAM.gov", error_type="timeout", message="test")
        with pytest.raises(AttributeError):
            error.api_name = "Other"

    def test_source_error_default_http_status_is_none(self):
        """Kill mutant: default http_status=None -> other value."""
        error = SourceError(api_name="SAM.gov", error_type="timeout", message="test")
        assert error.http_status is None

    def test_timeout_default_value(self, mock_client):
        """Kill mutant: default timeout=10.0 mutation."""
        adapter = SamGovAdapter(client=mock_client)
        assert adapter._timeout == 10.0

    def test_api_url_in_source_contains_uei(self, adapter, mock_client):
        """Kill mutant: api_url format string mutation."""
        mock_client.get.return_value = _mock_response(200, _sam_entity_response())
        result = adapter.fetch_fields("DKJF84NXLE73", api_key="test-key")
        name_field = next(f for f in result.fields if f.field_path == "company_name")
        assert "ueiSAM=DKJF84NXLE73" in name_field.source.api_url
        assert name_field.source.api_url.startswith(SAM_GOV_BASE_URL)

    def test_uei_field_exact_field_path(self, adapter, mock_client):
        """Kill mutant: field_path string mutations for UEI field."""
        mock_client.get.return_value = _mock_response(200, _sam_entity_response())
        result = adapter.fetch_fields("DKJF84NXLE73", api_key="test-key")
        uei_field = next(f for f in result.fields if f.field_path == "certifications.sam_gov.uei")
        assert uei_field.value == "DKJF84NXLE73"
        assert uei_field.confidence == "high"

    def test_inactive_registration_status_maps_to_false(self, adapter, mock_client):
        """Kill mutant: == 'Active' -> != 'Active' comparison."""
        mock_client.get.return_value = _mock_response(
            200, _sam_entity_response(registration_status="Inactive")
        )
        result = adapter.fetch_fields("DKJF84NXLE73", api_key="test-key")
        active_field = next(f for f in result.fields if f.field_path == "certifications.sam_gov.active")
        assert active_field.value is False

    def test_naics_secondary_is_not_primary(self, adapter, mock_client):
        """Kill mutant: isPrimary default False mutation."""
        mock_client.get.return_value = _mock_response(200, _sam_entity_response())
        result = adapter.fetch_fields("DKJF84NXLE73", api_key="test-key")
        naics_field = next(f for f in result.fields if f.field_path == "naics_codes")
        assert naics_field.value[1]["primary"] is False
        assert naics_field.value[1]["code"] == "541715"

    def test_no_entity_data_key_returns_not_found(self, adapter, mock_client):
        """Kill mutant: entityData key name mutation."""
        mock_client.get.return_value = _mock_response(200, {"totalRecords": 1})
        result = adapter.fetch_fields("DKJF84NXLE73", api_key="test-key")
        assert result.found is False

    def test_total_records_zero_but_entities_present_returns_not_found(self, adapter, mock_client):
        """Kill mutant: 'and' -> 'or' in not-found condition (total==0 OR not entities)."""
        mock_client.get.return_value = _mock_response(
            200, {"totalRecords": 0, "entityData": [{"entityRegistration": {}}]}
        )
        result = adapter.fetch_fields("DKJF84NXLE73", api_key="test-key")
        # totalRecords==0 should trigger not_found even with entities present
        assert result.found is False

    def test_http_401_returns_auth_failed_error_type(self, adapter, mock_client):
        """Kill mutant: auth_failed error_type on 401."""
        mock_client.get.return_value = _mock_response(401)
        result = adapter.fetch_fields("DKJF84NXLE73", api_key="test-key")
        assert result.error.error_type == "auth_failed"

    def test_http_403_returns_auth_failed_error_type(self, adapter, mock_client):
        """Kill mutant: auth_failed for 403 (boundary of 'in (401, 403)')."""
        mock_client.get.return_value = _mock_response(403)
        result = adapter.fetch_fields("DKJF84NXLE73", api_key="test-key")
        assert result.error.error_type == "auth_failed"

    def test_http_500_returns_server_error_type(self, adapter, mock_client):
        """Kill mutant: server_error for non-auth status codes."""
        mock_client.get.return_value = _mock_response(500)
        result = adapter.fetch_fields("DKJF84NXLE73", api_key="test-key")
        assert result.error.error_type == "server_error"

    def test_http_error_message_contains_status_and_api_name(self, adapter, mock_client):
        """Kill mutant: error message format string mutations."""
        mock_client.get.return_value = _mock_response(503)
        result = adapter.fetch_fields("DKJF84NXLE73", api_key="test-key")
        assert "503" in result.error.message
        assert "SAM.gov" in result.error.message

    def test_timeout_message_contains_timeout_value(self, adapter, mock_client):
        """Kill mutant: timeout message format string mutation."""
        mock_client.get.side_effect = httpx.TimeoutException("timeout")
        result = adapter.fetch_fields("DKJF84NXLE73", api_key="test-key")
        assert "10.0" in result.error.message

    def test_api_key_none_sends_empty_string(self, adapter, mock_client):
        """Kill mutant: api_key or '' -> other default."""
        mock_client.get.return_value = _mock_response(200, {"totalRecords": 0, "entityData": []})
        adapter.fetch_fields("DKJF84NXLE73", api_key=None)
        call_kwargs = mock_client.get.call_args
        assert call_kwargs[1]["params"]["api_key"] == ""

    def test_unrecognized_business_type_code_ignored(self, adapter, mock_client):
        """Kill mutant: 'in BUSINESS_TYPE_MAP' check removal."""
        mock_client.get.return_value = _mock_response(
            200, _sam_entity_response(business_types=["ZZ"])
        )
        result = adapter.fetch_fields("DKJF84NXLE73", api_key="test-key")
        cert_field = next(
            (f for f in result.fields if f.field_path == "certifications.socioeconomic"),
            None,
        )
        assert cert_field is None

    def test_missing_registration_fields_skipped(self, adapter, mock_client):
        """Kill mutant: walrus operator / get() return None path."""
        entity_data = {
            "totalRecords": 1,
            "entityData": [
                {
                    "entityRegistration": {},
                    "assertions": {"goodsAndServices": {}},
                }
            ],
        }
        mock_client.get.return_value = _mock_response(200, entity_data)
        result = adapter.fetch_fields("DKJF84NXLE73", api_key="test-key")
        assert result.found is True
        assert result.fields == []

    def test_exact_field_count_with_full_entity(self, adapter, mock_client):
        """Kill mutant: ensure all 6 expected fields are produced for full entity."""
        mock_client.get.return_value = _mock_response(
            200, _sam_entity_response(business_types=["A8"])
        )
        result = adapter.fetch_fields("DKJF84NXLE73", api_key="test-key")
        # company_name, cage_code, uei, active, registration_expiration, naics_codes, socioeconomic
        assert len(result.fields) == 7
