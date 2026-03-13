"""In-memory fake adapters for solicitation finder acceptance tests.

These fakes implement driven port interfaces with in-memory state,
enabling fast isolated testing without real infrastructure.
"""

from __future__ import annotations

from typing import Any

from pes.ports.finder_results_port import FinderResultsPort
from pes.ports.topic_fetch_port import FetchResult, TopicFetchPort


class InMemoryFinderResultsAdapter(FinderResultsPort):
    """In-memory fake for FinderResultsPort.

    Stores results in memory for fast isolated testing.
    """

    def __init__(self) -> None:
        self._data: dict[str, Any] | None = None

    def read(self) -> dict[str, Any] | None:
        """Read stored results."""
        return self._data

    def write(self, results: dict[str, Any]) -> None:
        """Write results to memory."""
        self._data = results

    def exists(self) -> bool:
        """Check if results exist."""
        return self._data is not None


class InMemoryTopicFetchAdapter(TopicFetchPort):
    """In-memory fake for TopicFetchPort.

    Simulates topic source behavior including rate limiting and unavailability.
    """

    def __init__(
        self,
        topics: list[dict[str, Any]] | None = None,
        available: bool = True,
        rate_limit_after: int | None = None,
    ) -> None:
        self._topics = topics or []
        self._available = available
        self._rate_limit_after = rate_limit_after

    def fetch(
        self,
        filters: dict[str, str] | None = None,
        on_progress: Any | None = None,
    ) -> FetchResult:
        """Fetch topics from in-memory store."""
        if not self._available:
            return FetchResult(
                topics=[],
                total=0,
                source="dsip_api",
                partial=False,
                error="topic source unavailable",
            )

        topics = self._topics

        # Apply filters if provided
        if filters:
            if "agency" in filters:
                topics = [t for t in topics if t.get("agency") == filters["agency"]]
            if "phase" in filters:
                topics = [t for t in topics if t.get("phase") == filters["phase"]]

        # Report progress
        if on_progress is not None:
            on_progress({"fetched": len(topics), "total": len(topics)})

        # Simulate rate limiting: when set, return at most N topics as partial
        if self._rate_limit_after is not None:
            limited = topics[: self._rate_limit_after]
            return FetchResult(
                topics=limited,
                total=len(topics),
                source="dsip_api",
                partial=True,
                error=f"rate limited after {len(limited)} topics",
            )

        return FetchResult(
            topics=topics,
            total=len(topics),
            source="dsip_api",
            partial=False,
            error=None,
        )
