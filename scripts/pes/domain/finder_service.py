"""Finder service -- driving port for solicitation topic discovery.

Application service that orchestrates topic fetching, pre-filtering,
and scoring through driven ports. Tests invoke through this service.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pes.domain.keyword_prefilter import KeywordPreFilter
from pes.ports.finder_results_port import FinderResultsPort
from pes.ports.topic_fetch_port import FetchResult, TopicFetchPort


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

    Driving port: search(), search_with_document()
    Driven ports: TopicFetchPort (topic source)
    """

    def __init__(
        self,
        topic_fetch: TopicFetchPort,
        profile: dict[str, Any] | None = None,
        results_port: FinderResultsPort | None = None,
    ) -> None:
        self._topic_fetch = topic_fetch
        self._profile = profile
        self._results_port = results_port
        self._prefilter = KeywordPreFilter()

    # Profile sections that trigger per-section warnings when missing.
    _OPTIONAL_SECTIONS: list[tuple[str, str]] = [
        ("certifications", "certifications"),
        ("past_performance", "past performance"),
        ("key_personnel", "key personnel"),
    ]

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

        company_name = (
            self._profile.get("company_name", "") if self._profile else None
        )

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
            # Complete failure
            messages.append("topic source unavailable")
            messages.append("You can provide a solicitation document as a file instead")
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
        company_name = (
            self._profile.get("company_name", "") if self._profile else None
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

        # Filter phase
        capabilities = (
            self._profile.get("capabilities", []) if self._profile else []
        )

        if on_progress is not None:
            on_progress({"phase": "filter", "status": "started"})

        filter_result = self._prefilter.filter(fetch_result.topics, capabilities)

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
