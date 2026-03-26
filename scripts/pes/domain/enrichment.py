"""Enrichment domain types -- value objects and UEI validation.

Pure domain module. No infrastructure imports.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


_UEI_PATTERN = re.compile(r"^[A-Za-z0-9]{12}$")


@dataclass(frozen=True)
class UeiValidationResult:
    """Result of UEI format validation."""

    is_valid: bool
    error: str | None = None


def validate_uei(uei: str) -> UeiValidationResult:
    """Validate UEI format: must be exactly 12 alphanumeric characters."""
    if len(uei) != 12:
        return UeiValidationResult(
            is_valid=False,
            error=f"UEI must be exactly 12 characters, got {len(uei)}",
        )
    if not _UEI_PATTERN.match(uei):
        return UeiValidationResult(
            is_valid=False,
            error="UEI must contain only alphanumeric characters",
        )
    return UeiValidationResult(is_valid=True)


@dataclass(frozen=True)
class FieldSource:
    """Provenance for a single enriched field."""

    api_name: str
    api_url: str
    accessed_at: str


@dataclass(frozen=True)
class EnrichedField:
    """A single profile field populated from an external API."""

    field_path: str
    value: Any
    source: FieldSource
    confidence: str


@dataclass(frozen=True)
class SourceError:
    """Per-API error information."""

    api_name: str
    error_type: str
    message: str
    http_status: int | None = None


@dataclass(frozen=True)
class CompanyCandidate:
    """SBIR.gov company match for disambiguation."""

    company_name: str
    city: str
    state: str
    award_count: int
    firm_id: str


@dataclass
class EnrichmentResult:
    """Complete output of the enrichment cascade."""

    uei: str
    fields: list[EnrichedField]
    missing_fields: list[str]
    sources_attempted: list[str]
    sources_succeeded: list[str]
    disambiguation_needed: list[CompanyCandidate] = field(default_factory=list)
    errors: list[SourceError] = field(default_factory=list)

    @classmethod
    def with_missing_fields(
        cls,
        uei: str,
        fields: list[EnrichedField],
        required_fields: list[str],
        sources_attempted: list[str],
        sources_succeeded: list[str],
        disambiguation_needed: list[CompanyCandidate] | None = None,
        errors: list[SourceError] | None = None,
    ) -> EnrichmentResult:
        """Build an EnrichmentResult, computing missing_fields automatically.

        missing_fields = required_fields not covered by any enriched field.
        """
        populated = {f.field_path for f in fields}
        missing = [rf for rf in required_fields if rf not in populated]
        return cls(
            uei=uei,
            fields=fields,
            missing_fields=missing,
            sources_attempted=sources_attempted,
            sources_succeeded=sources_succeeded,
            disambiguation_needed=disambiguation_needed or [],
            errors=errors or [],
        )
