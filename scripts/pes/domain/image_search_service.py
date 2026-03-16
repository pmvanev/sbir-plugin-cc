"""Image search and browse service -- driving port for corpus image discovery.

Provides list with filters and relevance-ranked search over the image registry.

Relevance score = caption_match * 0.4 + agency_match * 0.25
                + outcome_boost * 0.2 + recency * 0.15
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class ScoredResult:
    """A single search result with its relevance score."""

    entry: object  # ImageRegistryEntry from fakes or domain
    score: float


@dataclass(frozen=True)
class ListResult:
    """Result of a list_images operation."""

    entries: list
    message: str | None = None


@dataclass(frozen=True)
class SearchResult:
    """Result of a search operation."""

    scored_results: list[ScoredResult] = field(default_factory=list)
    message: str | None = None


class ImageSearchService:
    """Driving port: search and browse corpus images.

    Delegates to ImageRegistryPort (driven port) for data access.
    """

    def __init__(self, registry: object) -> None:
        self._registry = registry

    def list_images(
        self,
        *,
        figure_type: str | None = None,
        outcome: str | None = None,
        agency: str | None = None,
        source: str | None = None,
    ) -> ListResult:
        """List images with optional filters.

        Returns ListResult with entries and optional guidance message.
        """
        all_entries = self._registry.get_all()

        if not all_entries and not any([figure_type, outcome, agency, source]):
            return ListResult(
                entries=[],
                message="No images in catalog",
            )

        filtered = all_entries
        if figure_type is not None:
            filtered = [e for e in filtered if e.figure_type == figure_type]
        if outcome is not None:
            filtered = [e for e in filtered if e.outcome == outcome]
        if agency is not None:
            filtered = [e for e in filtered if e.agency == agency]
        if source is not None:
            filtered = [
                e for e in filtered if e.source_proposal == source
            ]

        return ListResult(entries=filtered)

    def search(
        self,
        *,
        query: str,
        current_agency: str = "",
    ) -> SearchResult:
        """Search images by query with relevance ranking.

        Scoring formula:
          caption_match * 0.4 + agency_match * 0.25
          + outcome_boost * 0.2 + recency * 0.15

        Only results with score above recency baseline (0.15) are included.
        """
        all_entries = self._registry.get_all()
        query_lower = query.lower()

        scored: list[ScoredResult] = []
        for entry in all_entries:
            caption_text = getattr(entry, "caption", "") or ""
            caption_match = (
                1.0 if query_lower in caption_text.lower() else 0.0
            )

            entry_agency = getattr(entry, "agency", "") or ""
            agency_match = (
                1.0 if entry_agency == current_agency and current_agency else 0.0
            )

            entry_outcome = getattr(entry, "outcome", "") or ""
            if entry_outcome == "WIN":
                outcome_boost = 1.0
            elif entry_outcome == "LOSS":
                outcome_boost = 0.0
            else:
                outcome_boost = 0.5

            recency = self._compute_recency(entry)

            score = (
                caption_match * 0.4
                + agency_match * 0.25
                + outcome_boost * 0.2
                + recency * 0.15
            )

            # Include only if caption matches the query
            if caption_match > 0.0:
                scored.append(ScoredResult(entry=entry, score=score))

        scored.sort(key=lambda sr: sr.score, reverse=True)

        if not scored:
            return SearchResult(
                scored_results=[],
                message="No matching images found",
            )

        return SearchResult(scored_results=scored)

    @staticmethod
    def _compute_recency(entry: object) -> float:
        """Compute recency score: linear decay from 1.0 (today) to 0.0 (36 months).

        Uses extraction_date attribute if available.
        """
        extraction_date_str = getattr(entry, "extraction_date", None)
        if not extraction_date_str:
            return 0.5  # default for unknown dates

        try:
            extraction_date = datetime.strptime(
                extraction_date_str, "%Y-%m-%d"
            )
        except (ValueError, TypeError):
            return 0.5

        days_ago = (datetime.now() - extraction_date).days
        months_ago = days_ago / 30.0
        max_months = 36.0

        if months_ago <= 0:
            return 1.0
        if months_ago >= max_months:
            return 0.0

        return 1.0 - (months_ago / max_months)
