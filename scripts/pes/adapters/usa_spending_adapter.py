"""USASpending.gov Recipient API adapter.

Two-step resolution: POST autocomplete by company name to get recipient ID,
then GET recipient detail by ID to retrieve total awards and business types.
No authentication required.

Uses httpx.Client for HTTP transport, injected via constructor for
testability.
"""

from __future__ import annotations

from datetime import datetime, timezone

import httpx

from pes.domain.enrichment import EnrichedField, FieldSource, SourceError

USA_SPENDING_AUTOCOMPLETE_URL = (
    "https://api.usaspending.gov/api/v2/autocomplete/recipient/"
)
USA_SPENDING_RECIPIENT_URL = (
    "https://api.usaspending.gov/api/v2/recipient/"
)


class UsaSpendingResult:
    """Return type for USASpending.gov company name lookup.

    Either fields are populated (success) or an error is set (failure).
    found=False with empty fields means no autocomplete match.
    """

    __slots__ = ("fields", "error", "found")

    def __init__(
        self,
        fields: list[EnrichedField] | None = None,
        error: SourceError | None = None,
        found: bool = True,
    ) -> None:
        self.fields = fields or []
        self.error = error
        self.found = found


class UsaSpendingAdapter:
    """USASpending.gov Recipient API enrichment source."""

    def __init__(self, client: httpx.Client, timeout: float = 10.0) -> None:
        self._client = client
        self._timeout = timeout

    @property
    def source_name(self) -> str:
        return "USASpending.gov"

    def _make_error(self, error_type: str, message: str, http_status: int | None = None) -> UsaSpendingResult:
        """Build a UsaSpendingResult with a SourceError."""
        return UsaSpendingResult(
            error=SourceError(
                api_name="USASpending.gov",
                error_type=error_type,
                message=message,
                http_status=http_status,
            ),
        )

    def fetch_by_company_name(self, company_name: str) -> UsaSpendingResult:
        """Search USASpending.gov by company name via two-step resolution.

        Step 1: POST autocomplete to find recipient ID.
        Step 2: GET recipient detail for total awards and business types.
        """
        # Step 1: Autocomplete
        try:
            autocomplete_resp = self._client.post(
                USA_SPENDING_AUTOCOMPLETE_URL,
                json={"search_text": company_name},
                timeout=self._timeout,
            )
            autocomplete_resp.raise_for_status()
        except httpx.TimeoutException:
            return self._make_error("timeout", f"Connection timed out after {self._timeout}s")
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            return self._make_error("server_error", f"HTTP {status} from USASpending.gov", status)

        results = autocomplete_resp.json().get("results", [])
        if not results:
            return UsaSpendingResult(found=False)

        recipient = results[0]
        recipient_id = recipient.get("recipient_id", "")

        # Step 2: Recipient detail
        detail_url = f"{USA_SPENDING_RECIPIENT_URL}{recipient_id}/"
        try:
            detail_resp = self._client.get(
                detail_url,
                params={"year": "all"},
                timeout=self._timeout,
            )
            detail_resp.raise_for_status()
        except httpx.TimeoutException:
            return self._make_error("timeout", f"Connection timed out after {self._timeout}s")
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            return self._make_error("server_error", f"HTTP {status} from USASpending.gov", status)

        detail = detail_resp.json()
        accessed_at = datetime.now(timezone.utc).isoformat()
        source = FieldSource(
            api_name="USASpending.gov",
            api_url=detail_url,
            accessed_at=accessed_at,
        )

        fields = self._map_detail_to_fields(detail, source)
        return UsaSpendingResult(fields=fields)

    def _map_detail_to_fields(
        self, detail: dict, source: FieldSource
    ) -> list[EnrichedField]:
        """Map USASpending recipient detail to EnrichedField objects."""
        fields: list[EnrichedField] = []

        total_amount = detail.get("total_transaction_amount")
        if total_amount is not None:
            fields.append(
                EnrichedField(
                    field_path="federal_awards.total_amount",
                    value=total_amount,
                    source=source,
                    confidence="high",
                )
            )

        total_transactions = detail.get("total_transactions")
        if total_transactions is not None:
            fields.append(
                EnrichedField(
                    field_path="federal_awards.transaction_count",
                    value=total_transactions,
                    source=source,
                    confidence="high",
                )
            )

        business_types = detail.get("business_types")
        if business_types:
            fields.append(
                EnrichedField(
                    field_path="federal_awards.business_types",
                    value=business_types,
                    source=source,
                    confidence="high",
                )
            )

        return fields
