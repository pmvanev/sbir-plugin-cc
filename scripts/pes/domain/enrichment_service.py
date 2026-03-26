"""Enrichment service -- orchestrates three-API cascade.

SAM.gov is queried first (provides company name from UEI). Then SBIR.gov
and USASpending are queried by company name. Results are merged into a
single EnrichmentResult. Per-source success/failure is tracked.

Pure domain orchestration. No infrastructure imports.
"""

from __future__ import annotations

from pes.domain.enrichment import (
    EnrichedField,
    EnrichmentResult,
    SourceError,
)
from pes.ports.enrichment_port import EnrichmentSourcePort


class EnrichmentService:
    """Orchestrates the three-API enrichment cascade."""

    def __init__(
        self,
        sam_adapter: EnrichmentSourcePort,
        sbir_adapter: object,
        usa_spending_adapter: object,
        required_fields: list[str] | None = None,
    ) -> None:
        self._sam = sam_adapter
        self._sbir = sbir_adapter
        self._usa = usa_spending_adapter
        self._required_fields = required_fields or []

    def enrich(self, uei: str, api_key: str | None = None) -> EnrichmentResult:
        """Run the three-API cascade and return merged EnrichmentResult."""
        all_fields: list[EnrichedField] = []
        errors: list[SourceError] = []
        sources_attempted: list[str] = []
        sources_succeeded: list[str] = []

        # Step 1: SAM.gov (provides company name for downstream lookups)
        company_name = ""
        sources_attempted.append("SAM.gov")
        sam_result = self._sam.fetch_fields(uei, api_key=api_key)

        if sam_result.error:
            errors.append(sam_result.error)
        elif sam_result.found and sam_result.fields:
            all_fields.extend(sam_result.fields)
            sources_succeeded.append("SAM.gov")
            # Extract company name for downstream queries
            for f in sam_result.fields:
                if f.field_path == "company_name":
                    company_name = f.value
                    break

        # Step 2: SBIR.gov (by company name)
        sources_attempted.append("SBIR.gov")
        sbir_result = self._sbir.fetch_by_company_name(company_name)

        if sbir_result.error:
            errors.append(sbir_result.error)
        elif sbir_result.fields:
            all_fields.extend(sbir_result.fields)
            sources_succeeded.append("SBIR.gov")

        # Step 3: USASpending (by company name)
        sources_attempted.append("USASpending.gov")
        usa_result = self._usa.fetch_by_company_name(company_name)

        if usa_result.error:
            errors.append(usa_result.error)
        elif usa_result.fields:
            all_fields.extend(usa_result.fields)
            sources_succeeded.append("USASpending.gov")

        return EnrichmentResult.with_missing_fields(
            uei=uei,
            fields=all_fields,
            required_fields=self._required_fields,
            sources_attempted=sources_attempted,
            sources_succeeded=sources_succeeded,
            errors=errors,
        )
