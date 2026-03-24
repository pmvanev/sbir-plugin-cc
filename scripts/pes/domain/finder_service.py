"""Finder service -- driving port for solicitation topic discovery.

Application service that orchestrates topic fetching, pre-filtering,
and scoring through driven ports. Tests invoke through this service.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from pes.domain.keyword_prefilter import KeywordPreFilter
from pes.domain.topic_enrichment import combine_topics_with_enrichment, completeness_report
from pes.ports.finder_results_port import FinderResultsPort
from pes.ports.topic_enrichment_port import TopicEnrichmentPort
from pes.ports.topic_fetch_port import FetchResult, TopicFetchPort

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Result of a solicitation topic search."""

    topics: list[dict[str, Any]] = field(default_factory=list)
    total: int = 0
    source: str = ""
    partial: bool = False
    error: str | None = None
    company_name: str | None = None
    filters_applied: dict[str, str] = field(default_factory=dict)
    progress_reported: bool = False
    messages: list[str] = field(default_factory=list)
    total_fetched: int = 0
    candidates_count: int = 0
    eliminated_count: int = 0


class FinderService:
    """Application service for solicitation topic discovery.

    Driving port: search(), search_and_filter(), search_and_enrich()
    Driven ports: TopicFetchPort, TopicEnrichmentPort, TopicCachePort
    """

    def __init__(
        self,
        topic_fetch: TopicFetchPort,
        profile: dict[str, Any] | None = None,
        results_port: FinderResultsPort | None = None,
        diagnostic_dir: Path | None = None,
        enrichment_port: TopicEnrichmentPort | None = None,
        cache_port: Any | None = None,
    ) -> None:
        self._topic_fetch = topic_fetch
        self._profile = profile
        self._results_port = results_port
        self._diagnostic_dir = diagnostic_dir
        self._prefilter = KeywordPreFilter()
        self._enrichment_port = enrichment_port
        self._cache_port = cache_port

    # Profile sections that trigger per-section warnings when missing.
    _OPTIONAL_SECTIONS: list[tuple[str, str]] = [
        ("certifications", "certifications"),
        ("past_performance", "past performance"),
        ("key_personnel", "key personnel"),
    ]

    @property
    def _company_name(self) -> str | None:
        """Extract company name from profile, or None if no profile."""
        return self._profile.get("company_name", "") if self._profile else None

    @property
    def _capabilities(self) -> list[str]:
        """Extract capabilities from profile, or empty list if no profile."""
        return self._profile.get("capabilities", []) if self._profile else []

    def search(
        self,
        filters: dict[str, str] | None = None,
        *,
        degraded_mode: bool = False,
    ) -> SearchResult:
        """Search for solicitation topics through the topic source.

        Args:
            filters: Optional filters (agency, phase, etc.).
            degraded_mode: If True, allow search without profile (document fallback).

        Returns:
            SearchResult with topics and metadata.
        """
        if self._profile is None and not degraded_mode:
            return SearchResult(
                messages=[
                    "No company profile found",
                    "The company profile enables matching, eligibility, and personnel alignment",
                    "Create a company profile first",
                ],
            )

        messages: list[str] = []

        if self._profile is None and degraded_mode:
            messages.append(
                "No company profile: scoring accuracy severely degraded"
            )

        company_name = self._company_name

        # Check for incomplete profile sections
        if self._profile is not None:
            self._check_profile_completeness(messages)

        progress_reported = False

        def on_progress(info: Any) -> None:
            nonlocal progress_reported
            progress_reported = True

        fetch_result: FetchResult = self._topic_fetch.fetch(
            filters=filters,
            on_progress=on_progress,
        )

        if fetch_result.error and not fetch_result.topics:
            # Check for structural change (API schema change)
            if self._is_structural_change(fetch_result.error):
                self._handle_structural_change(fetch_result.error, messages)
            else:
                # Generic failure
                messages.append("topic source unavailable")
                messages.append(
                    "You can provide a solicitation document as a file instead"
                )
                messages.append(
                    "Download solicitation documents from "
                    "https://www.dodsbirsttr.mil/topics-app/"
                )
            return SearchResult(
                source=fetch_result.source,
                error=fetch_result.error,
                company_name=company_name,
                filters_applied=filters or {},
                messages=messages,
            )

        if fetch_result.partial:
            messages.append(
                f"source rate limit reached after {len(fetch_result.topics)} topics"
            )
            messages.append("You can score partial results or retry later")

        # Add source summary for document-based fetches
        if fetch_result.source == "baa_pdf":
            messages.append(
                f"Source: solicitation document "
                f"({len(fetch_result.topics)} topics extracted)"
            )

        return SearchResult(
            topics=fetch_result.topics,
            total=fetch_result.total,
            source=fetch_result.source,
            partial=fetch_result.partial,
            error=fetch_result.error,
            company_name=company_name,
            filters_applied=filters or {},
            progress_reported=progress_reported,
            messages=messages,
        )

    def search_and_filter(
        self,
        filters: dict[str, str] | None = None,
        *,
        on_progress: Any | None = None,
    ) -> SearchResult:
        """Fetch topics and apply keyword pre-filter using profile capabilities.

        Orchestrates: fetch via TopicFetchPort -> pre-filter via KeywordPreFilter
        -> return SearchResult with candidates and statistics.

        Args:
            filters: Optional filters (agency, phase, etc.).
            on_progress: Optional callback receiving dicts with 'phase' key.

        Returns:
            SearchResult with candidates, statistics, and messages.
        """
        # Fetch phase
        if on_progress is not None:
            on_progress({"phase": "fetch", "status": "started"})

        fetch_result: FetchResult = self._topic_fetch.fetch(
            filters=filters,
            on_progress=on_progress,
        )

        if on_progress is not None:
            on_progress({
                "phase": "fetch",
                "status": "complete",
                "count": len(fetch_result.topics),
            })

        messages: list[str] = []
        company_name = self._company_name

        if fetch_result.error and not fetch_result.topics:
            return SearchResult(
                source=fetch_result.source,
                error=fetch_result.error,
                company_name=company_name,
                filters_applied=filters or {},
                messages=["topic source unavailable"],
                total_fetched=0,
                candidates_count=0,
                eliminated_count=0,
            )

        # Filter phase

        if on_progress is not None:
            on_progress({"phase": "filter", "status": "started"})

        filter_result = self._prefilter.filter(fetch_result.topics, self._capabilities)

        if on_progress is not None:
            on_progress({
                "phase": "filter",
                "status": "complete",
                "candidates": len(filter_result.candidates),
                "eliminated": filter_result.eliminated_count,
            })

        messages.extend(filter_result.warnings)

        return SearchResult(
            topics=filter_result.candidates,
            total=len(fetch_result.topics),
            source=fetch_result.source,
            partial=fetch_result.partial,
            error=fetch_result.error,
            company_name=company_name,
            filters_applied=filters or {},
            progress_reported=on_progress is not None,
            messages=messages,
            total_fetched=len(fetch_result.topics),
            candidates_count=len(filter_result.candidates),
            eliminated_count=filter_result.eliminated_count,
        )

    def search_and_enrich(
        self,
        filters: dict[str, str] | None = None,
        *,
        ttl_hours: int = 24,
        on_progress: Any | None = None,
    ) -> SearchResult:
        """Fetch, pre-filter, enrich, and cache topics.

        Orchestrates: cache check -> if fresh return cached -> else fetch ->
        pre-filter -> enrich -> combine -> cache write -> return.

        Args:
            filters: Optional filters (agency, phase, etc.).
            ttl_hours: Cache freshness window in hours.
            on_progress: Optional callback for progress updates.

        Returns:
            SearchResult with enriched candidates and completeness messages.
        """
        messages: list[str] = []
        company_name = self._company_name

        # Step 1: Check cache freshness
        if self._cache_port is not None and self._cache_port.is_fresh(ttl_hours):
            cached = self._cache_port.read()
            if cached is not None:
                cached_topics = cached.topics
                return SearchResult(
                    topics=cached_topics,
                    total=len(cached_topics),
                    source=cached.source,
                    company_name=company_name,
                    messages=["Using cached enriched data"],
                    total_fetched=cached.total_topics or len(cached_topics),
                    candidates_count=len(cached_topics),
                )

        # Step 2: Fetch
        fetch_result: FetchResult = self._topic_fetch.fetch(
            filters=filters,
            on_progress=on_progress,
        )

        if fetch_result.error and not fetch_result.topics:
            return SearchResult(
                source=fetch_result.source,
                error=fetch_result.error,
                company_name=company_name,
                filters_applied=filters or {},
                messages=["topic source unavailable"],
                total_fetched=0,
                candidates_count=0,
                eliminated_count=0,
            )

        # Step 3: Pre-filter
        filter_result = self._prefilter.filter(fetch_result.topics, self._capabilities)
        messages.extend(filter_result.warnings)

        candidates = filter_result.candidates

        # Step 4: Enrich
        if self._enrichment_port is not None and candidates:
            enrichment_result = self._enrichment_port.enrich(
                topics=candidates,
                on_progress=on_progress,
            )

            # Step 4a: Combine candidates with enrichment data
            combined = combine_topics_with_enrichment(
                candidates, enrichment_result.enriched
            )

            # Step 4b: Completeness report
            messages.extend(
                completeness_report(
                    enrichment_result.completeness,
                    enrichment_result.errors,
                )
            )

            # Step 5: Write to cache
            if self._cache_port is not None:
                metadata = {
                    "scrape_date": datetime.now().isoformat(),
                    "source": fetch_result.source,
                    "ttl_hours": ttl_hours,
                    "total_topics": len(fetch_result.topics),
                    "enrichment_completeness": enrichment_result.completeness,
                    "filters_applied": filters or {},
                }
                self._cache_port.write(combined, metadata)

            return SearchResult(
                topics=combined,
                total=len(fetch_result.topics),
                source=fetch_result.source,
                partial=fetch_result.partial,
                company_name=company_name,
                filters_applied=filters or {},
                messages=messages,
                total_fetched=len(fetch_result.topics),
                candidates_count=len(combined),
                eliminated_count=filter_result.eliminated_count,
            )

        # No enrichment port: return pre-filtered candidates as-is
        return SearchResult(
            topics=candidates,
            total=len(fetch_result.topics),
            source=fetch_result.source,
            partial=fetch_result.partial,
            company_name=company_name,
            filters_applied=filters or {},
            messages=messages,
            total_fetched=len(fetch_result.topics),
            candidates_count=len(candidates),
            eliminated_count=filter_result.eliminated_count,
        )

    def persist_results(self, scored_data: dict[str, Any]) -> None:
        """Persist scored finder results via FinderResultsPort.

        Args:
            scored_data: Dict of scored results to persist.

        Raises:
            ValueError: If no results port was configured.
        """
        if self._results_port is None:
            raise ValueError(
                "No results port configured -- "
                "pass results_port to FinderService constructor"
            )
        self._results_port.write(scored_data)

    def _check_profile_completeness(self, messages: list[str]) -> None:
        """Add warnings for each missing optional profile section."""
        assert self._profile is not None
        for key, label in self._OPTIONAL_SECTIONS:
            value = self._profile.get(key)
            if not value:
                messages.append(
                    f"Missing profile section: {label} -- "
                    f"scoring capped at EVALUATE for {label} dimension"
                )

    @staticmethod
    def _is_structural_change(error: str) -> bool:
        """Check if error indicates a structural API change."""
        return error.startswith("structural_change:")

    def _handle_structural_change(
        self, error: str, messages: list[str]
    ) -> None:
        """Produce what/why/do messages and save diagnostics for structural change."""
        detail = error.removeprefix("structural_change:").strip()
        messages.append(
            f"What: DSIP API response structure changed -- {detail}"
        )
        messages.append(
            "Why: The DSIP API may have been updated with a new schema"
        )
        messages.append(
            "Do: Report the issue and use --file with a downloaded BAA PDF as fallback"
        )
        self._save_structural_diagnostic(error)

    def _save_structural_diagnostic(self, error: str) -> None:
        """Save raw error data to .sbir/dsip_debug_response.json."""
        if self._diagnostic_dir is None:
            return
        debug_path = self._diagnostic_dir / "dsip_debug_response.json"
        try:
            debug_path.write_text(
                json.dumps({"raw_error": error}, indent=2)
            )
            logger.info("Diagnostic data saved to %s", debug_path)
        except OSError as exc:
            logger.warning("Failed to save diagnostic data: %s", exc)
