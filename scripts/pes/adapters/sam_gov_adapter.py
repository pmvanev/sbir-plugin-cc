"""SAM.gov Entity API v3 adapter.

Implements EnrichmentSourcePort for SAM.gov. Queries the Entity
Management API by UEI and maps registration fields to EnrichedField
value objects with source attribution.

Uses httpx.Client for HTTP transport, injected via constructor for
testability.
"""

from __future__ import annotations

from datetime import datetime, timezone

import httpx

from pes.domain.enrichment import EnrichedField, FieldSource, SourceError
from pes.ports.enrichment_port import EnrichmentSourcePort, SourceResult

SAM_GOV_BASE_URL = "https://api.sam.gov/entity-information/v3/entities"

# SAM.gov business type code -> human-readable certification name
BUSINESS_TYPE_MAP: dict[str, str] = {
    "A8": "8(a)",
    "QF": "HUBZone",
    "A5": "WOSB",
    "QE": "SDVOSB",
    "A9": "VOSB",
    "27": "SDB",
    "LJ": "EDWOSB",
}


class SamGovAdapter(EnrichmentSourcePort):
    """SAM.gov Entity API v3 enrichment source."""

    def __init__(self, client: httpx.Client, timeout: float = 10.0) -> None:
        self._client = client
        self._timeout = timeout

    @property
    def source_name(self) -> str:
        return "SAM.gov"

    def fetch_fields(self, uei: str, api_key: str | None = None) -> SourceResult:
        """Fetch entity data from SAM.gov for the given UEI."""
        url = SAM_GOV_BASE_URL
        params = {"ueiSAM": uei, "api_key": api_key or ""}

        try:
            response = self._client.get(url, params=params, timeout=self._timeout)
            response.raise_for_status()
        except httpx.TimeoutException:
            return SourceResult.failure(
                SourceError(
                    api_name="SAM.gov",
                    error_type="timeout",
                    message=f"Connection timed out after {self._timeout}s",
                )
            )
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            error_type = "auth_failed" if status in (401, 403) else "server_error"
            return SourceResult.failure(
                SourceError(
                    api_name="SAM.gov",
                    error_type=error_type,
                    message=f"HTTP {status} from SAM.gov",
                    http_status=status,
                )
            )

        data = response.json()
        total = data.get("totalRecords", 0)
        entities = data.get("entityData", [])

        if total == 0 or not entities:
            return SourceResult.not_found()

        entity = entities[0]
        accessed_at = datetime.now(timezone.utc).isoformat()
        api_url = f"{url}?ueiSAM={uei}"
        source = FieldSource(
            api_name="SAM.gov",
            api_url=api_url,
            accessed_at=accessed_at,
        )

        fields = self._map_entity_to_fields(entity, source)
        return SourceResult.success(fields)

    def _map_entity_to_fields(
        self, entity: dict, source: FieldSource
    ) -> list[EnrichedField]:
        """Map SAM.gov entity data to EnrichedField objects."""
        fields: list[EnrichedField] = []
        reg = entity.get("entityRegistration", {})
        assertions = entity.get("assertions", {})
        goods = assertions.get("goodsAndServices", {})

        # Legal name
        if legal_name := reg.get("legalBusinessName"):
            fields.append(
                EnrichedField(
                    field_path="company_name",
                    value=legal_name,
                    source=source,
                    confidence="high",
                )
            )

        # CAGE code
        if cage_code := reg.get("cageCode"):
            fields.append(
                EnrichedField(
                    field_path="certifications.sam_gov.cage_code",
                    value=cage_code,
                    source=source,
                    confidence="high",
                )
            )

        # UEI
        if uei_val := reg.get("ueiSAM"):
            fields.append(
                EnrichedField(
                    field_path="certifications.sam_gov.uei",
                    value=uei_val,
                    source=source,
                    confidence="high",
                )
            )

        # Registration status -> active boolean
        status = reg.get("registrationStatus")
        if status is not None:
            fields.append(
                EnrichedField(
                    field_path="certifications.sam_gov.active",
                    value=status == "Active",
                    source=source,
                    confidence="high",
                )
            )

        # Registration expiration
        if exp_date := reg.get("registrationExpirationDate"):
            fields.append(
                EnrichedField(
                    field_path="certifications.sam_gov.registration_expiration",
                    value=exp_date,
                    source=source,
                    confidence="high",
                )
            )

        # NAICS codes
        naics_list = goods.get("naicsList", [])
        if naics_list:
            mapped_naics = [
                {
                    "code": n.get("naicsCode", ""),
                    "primary": n.get("isPrimary", False),
                }
                for n in naics_list
            ]
            fields.append(
                EnrichedField(
                    field_path="naics_codes",
                    value=mapped_naics,
                    source=source,
                    confidence="high",
                )
            )

        # Business type codes -> socioeconomic certifications
        biz_types = goods.get("businessTypeList", [])
        certs = []
        for bt in biz_types:
            code = bt.get("businessTypeCode", "")
            if code in BUSINESS_TYPE_MAP:
                certs.append(BUSINESS_TYPE_MAP[code])
        if certs:
            fields.append(
                EnrichedField(
                    field_path="certifications.socioeconomic",
                    value=certs,
                    source=source,
                    confidence="high",
                )
            )

        return fields
