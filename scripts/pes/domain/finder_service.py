"""Finder service -- driving port for solicitation topic discovery.

Application service that orchestrates topic fetching, pre-filtering,
and scoring through driven ports. Tests invoke through this service.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

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


class FinderService:
    """Application service for solicitation topic discovery.

    Driving port: search(), search_with_document()
    Driven ports: TopicFetchPort (topic source)
    """

    def __init__(
        self,
        topic_fetch: TopicFetchPort,
        profile: dict[str, Any] | None = None,
    ) -> None:
        self._topic_fetch = topic_fetch
        self._profile = profile

    def search(
        self,
        filters: dict[str, str] | None = None,
    ) -> SearchResult:
        """Search for solicitation topics through the topic source.

        Args:
            filters: Optional filters (agency, phase, etc.).

        Returns:
            SearchResult with topics and metadata.
        """
        if self._profile is None:
            return SearchResult(
                messages=[
                    "No company profile found",
                    "The company profile enables matching, eligibility, and personnel alignment",
                    "Create a company profile first",
                ],
            )

        company_name = self._profile.get("company_name", "")

        progress_reported = False

        def on_progress(info: Any) -> None:
            nonlocal progress_reported
            progress_reported = True

        fetch_result: FetchResult = self._topic_fetch.fetch(
            filters=filters,
            on_progress=on_progress,
        )

        messages: list[str] = []

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
