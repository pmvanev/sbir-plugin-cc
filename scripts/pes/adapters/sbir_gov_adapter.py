"""SBIR.gov Company and Awards API adapter.

Implements company name search with disambiguation support and award
history fetch with agency, topic, and phase mapping. No authentication
required.

Uses httpx.Client for HTTP transport, injected via constructor for
testability.
"""

from __future__ import annotations

from datetime import datetime, timezone

import httpx

from pes.domain.enrichment import CompanyCandidate, EnrichedField, FieldSource, SourceError
from pes.ports.enrichment_port import SourceResult

SBIR_GOV_COMPANY_URL = "https://api.www.sbir.gov/public/api/company"
SBIR_GOV_AWARDS_URL = "https://api.www.sbir.gov/public/api/awards"


class SbirGovCompanyResult:
    """Return type for SBIR.gov company name search.

    Either fields are populated (single match + awards fetched),
    candidates are populated (multiple matches needing disambiguation),
    or an error is set (failure).
    """

    __slots__ = ("fields", "candidates", "error", "found")

    def __init__(
        self,
        fields: list[EnrichedField] | None = None,
        candidates: list[CompanyCandidate] | None = None,
        error: SourceError | None = None,
        found: bool = True,
    ) -> None:
        self.fields = fields or []
        self.candidates = candidates
        self.error = error
        self.found = found


class SbirGovAdapter:
    """SBIR.gov Company and Awards API enrichment source."""

    def __init__(self, client: httpx.Client, timeout: float = 10.0) -> None:
        self._client = client
        self._timeout = timeout

    @property
    def source_name(self) -> str:
        return "SBIR.gov"

    def _safe_get(self, url: str, params: dict) -> httpx.Response | SbirGovCompanyResult:
        """Execute GET with error handling. Returns Response on success or SbirGovCompanyResult on failure."""
        try:
            resp = self._client.get(url, params=params, timeout=self._timeout)
            resp.raise_for_status()
            return resp
        except httpx.TimeoutException:
            return SbirGovCompanyResult(
                error=SourceError(
                    api_name="SBIR.gov",
                    error_type="timeout",
                    message=f"Connection timed out after {self._timeout}s",
                ),
            )
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            return SbirGovCompanyResult(
                error=SourceError(
                    api_name="SBIR.gov",
                    error_type="server_error",
                    message=f"HTTP {status} from SBIR.gov",
                    http_status=status,
                ),
            )

    def fetch_by_company_name(self, company_name: str) -> SbirGovCompanyResult:
        """Search SBIR.gov by company name and fetch award history.

        Single match: fetches awards and returns EnrichedField objects.
        Multiple matches: returns CompanyCandidate list for disambiguation.
        Timeout/error: returns SourceError without raising.
        """
        resp = self._safe_get(SBIR_GOV_COMPANY_URL, {"keyword": company_name})
        if isinstance(resp, SbirGovCompanyResult):
            return resp

        firms = resp.json()

        if not firms:
            return SbirGovCompanyResult(found=False)

        # Multiple matches -> disambiguation needed
        if len(firms) > 1:
            candidates = [
                CompanyCandidate(
                    company_name=f.get("company_name", ""),
                    city=f.get("city", ""),
                    state=f.get("state", ""),
                    award_count=f.get("number_awards", 0),
                    firm_id=f.get("firm_nid", ""),
                )
                for f in firms
            ]
            return SbirGovCompanyResult(candidates=candidates)

        # Single match -> fetch awards
        firm = firms[0]
        firm_name = firm.get("company_name", company_name)
        return self._fetch_awards(firm_name)

    def _fetch_awards(self, firm_name: str) -> SbirGovCompanyResult:
        """Fetch award history for a specific firm name."""
        resp = self._safe_get(SBIR_GOV_AWARDS_URL, {"firm": firm_name})
        if isinstance(resp, SbirGovCompanyResult):
            return resp

        awards_data = resp.json()
        accessed_at = datetime.now(timezone.utc).isoformat()
        source = FieldSource(
            api_name="SBIR.gov",
            api_url=f"{SBIR_GOV_AWARDS_URL}?firm={firm_name}",
            accessed_at=accessed_at,
        )

        mapped_awards = [
            {
                "agency": a.get("agency", ""),
                "phase": a.get("phase", ""),
                "topic_area": a.get("research_keywords", ""),
                "program": a.get("program", ""),
                "year": a.get("award_year", ""),
                "amount": a.get("award_amount", 0),
                "title": a.get("award_title", ""),
            }
            for a in awards_data
        ]

        fields = [
            EnrichedField(
                field_path="sbir_awards",
                value=mapped_awards,
                source=source,
                confidence="high",
            ),
        ]

        return SbirGovCompanyResult(fields=fields)
