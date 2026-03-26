"""Port interface for enrichment source adapters.

Driven port: EnrichmentSourcePort
Defines the business contract for fetching company data from
a single external API source. Each adapter (SAM.gov, SBIR.gov,
USASpending.gov) implements this port independently.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from pes.domain.enrichment import EnrichedField, SourceError


class SourceResult:
    """Return type for EnrichmentSourcePort.fetch_fields().

    Either fields are populated (success) or an error is set (failure).
    found=False with empty fields means the entity was not found.
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

    @classmethod
    def success(cls, fields: list[EnrichedField]) -> SourceResult:
        return cls(fields=fields, found=True)

    @classmethod
    def not_found(cls) -> SourceResult:
        return cls(fields=[], found=False)

    @classmethod
    def failure(cls, error: SourceError) -> SourceResult:
        return cls(error=error, found=True)


class EnrichmentSourcePort(ABC):
    """Abstract interface for a single enrichment data source.

    Each implementation fetches company data from one external API
    and maps the response to EnrichedField value objects.
    """

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Human-readable name of this data source (e.g., 'SAM.gov')."""

    @abstractmethod
    def fetch_fields(self, uei: str, api_key: str | None = None) -> SourceResult:
        """Fetch enrichment fields for the given UEI.

        Args:
            uei: 12-character Unique Entity Identifier.
            api_key: API key if required by the source.

        Returns:
            SourceResult with enriched fields on success,
            not-found indicator if entity doesn't exist,
            or SourceError on failure (timeout, auth, etc.).
        """
