"""Port interface for fetching solicitation topics.

Driven port: TopicFetchPort
Defines the business contract for topic retrieval from external sources.
Adapters implement this for specific infrastructure (DSIP API, files, etc.).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class FetchResult:
    """Result of a topic fetch operation.

    Attributes:
        topics: List of normalized topic dicts.
        total: Total number of topics available at the source.
        source: Description of the data source (e.g., "dsip_api", "document").
        partial: True if only a subset was retrieved (rate limit, error).
        error: Error description if the fetch was incomplete or failed, else None.
    """

    topics: list[dict[str, Any]] = field(default_factory=list)
    total: int = 0
    source: str = ""
    partial: bool = False
    error: str | None = None


class TopicFetchPort(ABC):
    """Abstract interface for fetching solicitation topics."""

    @abstractmethod
    def fetch(
        self,
        filters: dict[str, str] | None = None,
        on_progress: Any | None = None,
    ) -> FetchResult:
        """Fetch topics from the source with optional filters.

        Args:
            filters: Optional key-value filters (e.g., agency, phase, topicStatus).
            on_progress: Optional callback invoked with progress updates.

        Returns:
            FetchResult with topics and metadata.
        """
