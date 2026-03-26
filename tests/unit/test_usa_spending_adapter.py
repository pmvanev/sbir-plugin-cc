"""Tests for UsaSpendingAdapter -- USASpending.gov recipient API enrichment.

Tests exercise the adapter through its public method with mocked HTTP
transport (httpx.Client constructor injection). Two-step resolution:
POST autocomplete by company name, GET recipient detail by ID.

Test Budget: 4 distinct behaviors x 2 = 8 max unit tests. Using 5.
Behaviors:
  B1: Autocomplete resolves recipient -> total award amount and transaction count returned
  B2: No autocomplete match -> empty result with not-found indicator
  B3: Timeout on either autocomplete or detail step -> SourceError returned gracefully
  B4: Business types in response available for cross-check against SAM.gov certs
"""

from __future__ import annotations

from unittest.mock import MagicMock

import httpx
import pytest

from pes.adapters.usa_spending_adapter import (
    USA_SPENDING_AUTOCOMPLETE_URL,
    USA_SPENDING_RECIPIENT_URL,
    UsaSpendingAdapter,
    UsaSpendingResult,
)
from pes.domain.enrichment import SourceError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_client() -> MagicMock:
    """Mock httpx.Client for HTTP transport mocking."""
    return MagicMock(spec=httpx.Client)


@pytest.fixture()
def adapter(mock_client: MagicMock) -> UsaSpendingAdapter:
    """UsaSpendingAdapter with injected mock HTTP client."""
    return UsaSpendingAdapter(client=mock_client, timeout=10.0)


def _autocomplete_response(
    results: list[dict] | None = None,
) -> dict:
    """Build a USASpending autocomplete response."""
    if results is None:
        results = [
            {
                "recipient_name": "RADIANT DEFENSE SYSTEMS LLC",
                "recipient_id": "abc123-R",
                "uei": "DKJF84NXLE73",
            }
        ]
    return {"results": results}


def _recipient_detail_response(
    name: str = "RADIANT DEFENSE SYSTEMS LLC",
    total_transaction_amount: float = 5_250_000.00,
    total_transactions: int = 14,
    business_types: list[str] | None = None,
) -> dict:
    """Build a USASpending recipient detail response."""
    if business_types is None:
        business_types = ["small_business", "minority_owned_business"]
    return {
        "name": name,
        "total_transaction_amount": total_transaction_amount,
        "total_transactions": total_transactions,
        "business_types": business_types,
    }


def _mock_response(status_code: int = 200, json_data: dict | None = None) -> MagicMock:
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


# ---------- B1: Autocomplete resolves -> returns award totals ----------


def test_resolved_recipient_returns_award_fields(adapter, mock_client):
    """Given a company name, when autocomplete resolves a recipient, then
    total award amount and transaction count are returned as EnrichedField
    objects with source attribution."""
    mock_client.post.return_value = _mock_response(
        200, _autocomplete_response()
    )
    mock_client.get.return_value = _mock_response(
        200, _recipient_detail_response()
    )

    result = adapter.fetch_by_company_name("Radiant Defense Systems")

    assert result.found is True
    assert result.error is None
    assert len(result.fields) > 0

    field_paths = {f.field_path for f in result.fields}
    assert "federal_awards.total_amount" in field_paths
    assert "federal_awards.transaction_count" in field_paths

    amount_field = next(
        f for f in result.fields if f.field_path == "federal_awards.total_amount"
    )
    assert amount_field.value == 5_250_000.00
    assert amount_field.source.api_name == "USASpending.gov"
    assert amount_field.confidence == "high"

    count_field = next(
        f for f in result.fields if f.field_path == "federal_awards.transaction_count"
    )
    assert count_field.value == 14


# ---------- B2: No autocomplete match -> not-found ----------


def test_no_autocomplete_match_returns_not_found(adapter, mock_client):
    """Given a company name with no autocomplete match, when fetched,
    then empty result returned with not-found indicator."""
    mock_client.post.return_value = _mock_response(
        200, _autocomplete_response(results=[])
    )

    result = adapter.fetch_by_company_name("Nonexistent Corp")

    assert result.found is False
    assert result.fields == []
    assert result.error is None


# ---------- B3: Timeout on either step -> SourceError ----------


@pytest.mark.parametrize("timeout_step", ["autocomplete", "detail"])
def test_timeout_returns_source_error(adapter, mock_client, timeout_step):
    """Given a timeout on either the autocomplete or recipient detail step,
    when the adapter call fails, then a SourceError is returned gracefully."""
    if timeout_step == "autocomplete":
        mock_client.post.side_effect = httpx.TimeoutException("timed out")
    else:
        mock_client.post.return_value = _mock_response(
            200, _autocomplete_response()
        )
        mock_client.get.side_effect = httpx.TimeoutException("timed out")

    result = adapter.fetch_by_company_name("Radiant Defense Systems")

    assert result.error is not None
    assert result.error.error_type == "timeout"
    assert result.error.api_name == "USASpending.gov"
    assert "timed out" in result.error.message.lower()
    assert result.fields == []


# ---------- B4: Business types available for cross-check ----------


def test_business_types_returned_for_crosscheck(adapter, mock_client):
    """Given business types in the response, when returned, then they are
    available as an EnrichedField for cross-check against SAM.gov certs."""
    biz_types = ["small_business", "woman_owned_business", "hubzone"]
    mock_client.post.return_value = _mock_response(
        200, _autocomplete_response()
    )
    mock_client.get.return_value = _mock_response(
        200, _recipient_detail_response(business_types=biz_types)
    )

    result = adapter.fetch_by_company_name("Radiant Defense Systems")

    field_paths = {f.field_path for f in result.fields}
    assert "federal_awards.business_types" in field_paths

    biz_field = next(
        f for f in result.fields if f.field_path == "federal_awards.business_types"
    )
    assert biz_field.value == ["small_business", "woman_owned_business", "hubzone"]
    assert biz_field.source.api_name == "USASpending.gov"


# ---------- B5: HTTP error returns SourceError ----------


def test_http_error_returns_source_error(adapter, mock_client):
    """Given an HTTP error status from USASpending.gov, when the adapter
    call fails, then a SourceError with the HTTP status is returned."""
    mock_client.post.return_value = _mock_response(500)

    result = adapter.fetch_by_company_name("Radiant Defense Systems")

    assert result.error is not None
    assert result.error.api_name == "USASpending.gov"
    assert result.error.http_status == 500
    assert result.fields == []


# ---------- Mutation-killing tests ----------


class TestUsaSpendingMutationKillers:
    """Targeted tests to kill surviving mutants in usa_spending_adapter.py."""

    def test_source_name_exact_value(self, adapter):
        """Kill mutant: source_name string literal mutation."""
        assert adapter.source_name == "USASpending.gov"

    def test_autocomplete_url_constant(self):
        """Kill mutant: URL string mutation."""
        assert USA_SPENDING_AUTOCOMPLETE_URL == "https://api.usaspending.gov/api/v2/autocomplete/recipient/"

    def test_recipient_url_constant(self):
        """Kill mutant: URL string mutation."""
        assert USA_SPENDING_RECIPIENT_URL == "https://api.usaspending.gov/api/v2/recipient/"

    def test_timeout_default_value(self, mock_client):
        """Kill mutant: default timeout=10.0 mutation."""
        adapter = UsaSpendingAdapter(client=mock_client)
        assert adapter._timeout == 10.0

    def test_result_defaults(self):
        """Kill mutant: UsaSpendingResult default value mutations."""
        result = UsaSpendingResult()
        assert result.fields == []
        assert result.error is None
        assert result.found is True

    def test_result_found_false(self):
        """Kill mutant: found=True default."""
        result = UsaSpendingResult(found=False)
        assert result.found is False

    def test_result_slots(self):
        """Kill mutant: __slots__ tuple mutation."""
        result = UsaSpendingResult()
        assert hasattr(result, "fields")
        assert hasattr(result, "error")
        assert hasattr(result, "found")

    def test_autocomplete_post_body_exact(self, adapter, mock_client):
        """Kill mutant: search_text key or company_name value mutation."""
        mock_client.post.return_value = _mock_response(200, _autocomplete_response(results=[]))
        adapter.fetch_by_company_name("Acme Corp")
        call_kwargs = mock_client.post.call_args
        assert call_kwargs[1]["json"] == {"search_text": "Acme Corp"}

    def test_empty_recipient_id_returns_not_found(self, adapter, mock_client):
        """Kill mutant: empty recipient_id check removal."""
        mock_client.post.return_value = _mock_response(
            200, _autocomplete_response(results=[{"recipient_name": "Test", "recipient_id": ""}])
        )
        result = adapter.fetch_by_company_name("Test")
        assert result.found is False
        assert result.fields == []

    def test_detail_url_contains_recipient_id(self, adapter, mock_client):
        """Kill mutant: detail_url format string mutation."""
        mock_client.post.return_value = _mock_response(200, _autocomplete_response())
        mock_client.get.return_value = _mock_response(200, _recipient_detail_response())
        adapter.fetch_by_company_name("Test")
        get_call = mock_client.get.call_args
        assert "abc123-R" in get_call[0][0]
        assert get_call[0][0].endswith("/")
        assert get_call[1]["params"] == {"year": "all"}

    def test_detail_timeout_returns_error(self, adapter, mock_client):
        """Kill mutant: timeout handling on detail step."""
        mock_client.post.return_value = _mock_response(200, _autocomplete_response())
        mock_client.get.side_effect = httpx.TimeoutException("timeout")
        result = adapter.fetch_by_company_name("Test")
        assert result.error.error_type == "timeout"
        assert result.error.api_name == "USASpending.gov"
        assert "10.0" in result.error.message

    def test_detail_http_error_returns_server_error(self, adapter, mock_client):
        """Kill mutant: detail step HTTP error handling."""
        mock_client.post.return_value = _mock_response(200, _autocomplete_response())
        mock_client.get.return_value = _mock_response(502)
        result = adapter.fetch_by_company_name("Test")
        assert result.error.error_type == "server_error"
        assert result.error.http_status == 502
        assert "502" in result.error.message
        assert "USASpending.gov" in result.error.message

    def test_autocomplete_http_error_message_format(self, adapter, mock_client):
        """Kill mutant: error message format for autocomplete step."""
        mock_client.post.return_value = _mock_response(503)
        result = adapter.fetch_by_company_name("Test")
        assert "503" in result.error.message
        assert "USASpending.gov" in result.error.message

    def test_field_path_exact_strings(self, adapter, mock_client):
        """Kill mutant: field_path string mutations."""
        mock_client.post.return_value = _mock_response(200, _autocomplete_response())
        mock_client.get.return_value = _mock_response(200, _recipient_detail_response())
        result = adapter.fetch_by_company_name("Test")
        paths = [f.field_path for f in result.fields]
        assert "federal_awards.total_amount" in paths
        assert "federal_awards.transaction_count" in paths
        assert "federal_awards.business_types" in paths

    def test_all_fields_have_high_confidence(self, adapter, mock_client):
        """Kill mutant: confidence string mutation."""
        mock_client.post.return_value = _mock_response(200, _autocomplete_response())
        mock_client.get.return_value = _mock_response(200, _recipient_detail_response())
        result = adapter.fetch_by_company_name("Test")
        for f in result.fields:
            assert f.confidence == "high"

    def test_source_api_url_is_detail_url(self, adapter, mock_client):
        """Kill mutant: source api_url should be the detail URL."""
        mock_client.post.return_value = _mock_response(200, _autocomplete_response())
        mock_client.get.return_value = _mock_response(200, _recipient_detail_response())
        result = adapter.fetch_by_company_name("Test")
        source = result.fields[0].source
        assert source.api_name == "USASpending.gov"
        assert "abc123-R" in source.api_url

    def test_missing_total_amount_omits_field(self, adapter, mock_client):
        """Kill mutant: 'is not None' check on total_transaction_amount."""
        detail = {"total_transactions": 5, "business_types": ["small"]}
        mock_client.post.return_value = _mock_response(200, _autocomplete_response())
        mock_client.get.return_value = _mock_response(200, detail)
        result = adapter.fetch_by_company_name("Test")
        paths = {f.field_path for f in result.fields}
        assert "federal_awards.total_amount" not in paths
        assert "federal_awards.transaction_count" in paths

    def test_missing_total_transactions_omits_field(self, adapter, mock_client):
        """Kill mutant: 'is not None' check on total_transactions."""
        detail = {"total_transaction_amount": 1000.0, "business_types": ["small"]}
        mock_client.post.return_value = _mock_response(200, _autocomplete_response())
        mock_client.get.return_value = _mock_response(200, detail)
        result = adapter.fetch_by_company_name("Test")
        paths = {f.field_path for f in result.fields}
        assert "federal_awards.total_amount" in paths
        assert "federal_awards.transaction_count" not in paths

    def test_empty_business_types_omits_field(self, adapter, mock_client):
        """Kill mutant: business_types truthy check."""
        detail = {"total_transaction_amount": 1000.0, "total_transactions": 5, "business_types": []}
        mock_client.post.return_value = _mock_response(200, _autocomplete_response())
        mock_client.get.return_value = _mock_response(200, detail)
        result = adapter.fetch_by_company_name("Test")
        paths = {f.field_path for f in result.fields}
        assert "federal_awards.business_types" not in paths

    def test_none_business_types_omits_field(self, adapter, mock_client):
        """Kill mutant: business_types None check."""
        detail = {"total_transaction_amount": 1000.0, "total_transactions": 5}
        mock_client.post.return_value = _mock_response(200, _autocomplete_response())
        mock_client.get.return_value = _mock_response(200, detail)
        result = adapter.fetch_by_company_name("Test")
        paths = {f.field_path for f in result.fields}
        assert "federal_awards.business_types" not in paths

    def test_zero_total_amount_still_included(self, adapter, mock_client):
        """Kill mutant: 'is not None' vs falsy check on total_transaction_amount=0."""
        detail = {"total_transaction_amount": 0, "total_transactions": 0}
        mock_client.post.return_value = _mock_response(200, _autocomplete_response())
        mock_client.get.return_value = _mock_response(200, detail)
        result = adapter.fetch_by_company_name("Test")
        paths = {f.field_path for f in result.fields}
        assert "federal_awards.total_amount" in paths
        assert "federal_awards.transaction_count" in paths
