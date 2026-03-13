"""DSIP API adapter for fetching solicitation topics.

Implements TopicFetchPort using the DoD SBIR/STTR Information Portal
(DSIP) public topics search API.

Features:
- Pagination with configurable page size
- Rate limiting (1-2 second delay between page requests)
- Timeout (30s per request) with 3 retries and exponential backoff
- Partial results on failure with error context
"""

from __future__ import annotations

import time
from datetime import UTC, datetime
from typing import Any

import httpx

from pes.ports.topic_fetch_port import FetchResult, TopicFetchPort

DSIP_API_URL = "https://www.dodsbirsttr.mil/topics/api/public/topics/search"
DEFAULT_PAGE_SIZE = 100
DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_MAX_RETRIES = 3
DEFAULT_RATE_LIMIT_MIN = 1.0
DEFAULT_RATE_LIMIT_MAX = 2.0


def _unix_ms_to_iso(unix_ms: int | None) -> str:
    """Convert Unix millisecond timestamp to ISO 8601 string."""
    if unix_ms is None:
        return ""
    dt = datetime.fromtimestamp(unix_ms / 1000, tz=UTC)
    return dt.isoformat()


def _normalize_topic(raw: dict[str, Any]) -> dict[str, Any]:
    """Map DSIP API topic fields to normalized dict."""
    return {
        "topic_id": raw.get("topicId", ""),
        "topic_code": raw.get("topicCode", ""),
        "title": raw.get("topicTitle", ""),
        "status": raw.get("topicStatus", ""),
        "program": raw.get("program", ""),
        "component": raw.get("component", ""),
        "solicitation_number": raw.get("solicitationNumber", ""),
        "cycle_name": raw.get("cycleName", ""),
        "start_date": _unix_ms_to_iso(raw.get("topicStartDate")),
        "deadline": _unix_ms_to_iso(raw.get("topicEndDate")),
        "cmmc_level": raw.get("cmmcLevel", ""),
        "phase": raw.get("phaseHierarchy", ""),
    }


class DsipApiAdapter(TopicFetchPort):
    """DSIP API adapter with pagination, retry, rate limiting, and timeout.

    Args:
        base_url: API endpoint URL.
        page_size: Number of topics per page request.
        timeout: Request timeout in seconds.
        max_retries: Maximum retry attempts per request.
        rate_limit_min: Minimum delay in seconds between page requests.
        rate_limit_max: Maximum delay in seconds between page requests.
    """

    def __init__(
        self,
        base_url: str = DSIP_API_URL,
        page_size: int = DEFAULT_PAGE_SIZE,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        max_retries: int = DEFAULT_MAX_RETRIES,
        rate_limit_min: float = DEFAULT_RATE_LIMIT_MIN,
        rate_limit_max: float = DEFAULT_RATE_LIMIT_MAX,
    ) -> None:
        self._base_url = base_url
        self._page_size = page_size
        self._timeout = timeout
        self._max_retries = max_retries
        self._rate_limit_min = rate_limit_min
        self._rate_limit_max = rate_limit_max

    def fetch(
        self,
        filters: dict[str, str] | None = None,
        on_progress: Any | None = None,
    ) -> FetchResult:
        """Fetch topics from DSIP API with pagination.

        Args:
            filters: Optional filters (topicStatus, component, program, etc.).
            on_progress: Optional callback(dict) for progress updates.

        Returns:
            FetchResult with normalized topics and metadata.
        """
        all_topics: list[dict[str, Any]] = []
        page = 0
        total = 0
        error: str | None = None

        params: dict[str, Any] = {
            "numPerPage": self._page_size,
        }
        if filters:
            params.update(filters)

        while True:
            params["page"] = page

            try:
                data = self._fetch_page(params)
            except Exception as exc:
                error = str(exc)
                if all_topics:
                    # Partial results available
                    return FetchResult(
                        topics=all_topics,
                        total=total or len(all_topics),
                        source="dsip_api",
                        partial=True,
                        error=error,
                    )
                return FetchResult(
                    topics=[],
                    total=0,
                    source="dsip_api",
                    partial=False,
                    error=error,
                )

            raw_topics = data.get("data", [])
            total = data.get("total", 0)

            normalized = [_normalize_topic(t) for t in raw_topics]
            all_topics.extend(normalized)

            if on_progress is not None:
                on_progress({"fetched": len(all_topics), "total": total})

            # Check if we have all topics
            if len(all_topics) >= total or len(raw_topics) < self._page_size:
                break

            # Rate limiting between pages
            delay = (self._rate_limit_min + self._rate_limit_max) / 2
            time.sleep(delay)

            page += 1

        return FetchResult(
            topics=all_topics,
            total=total,
            source="dsip_api",
            partial=False,
            error=None,
        )

    def _fetch_page(self, params: dict[str, Any]) -> dict[str, Any]:
        """Fetch a single page with timeout and retry logic.

        Retries with exponential backoff on timeout or server errors.

        Returns:
            Parsed JSON response dict.

        Raises:
            RuntimeError: After max retries exhausted.
        """
        last_error: Exception | None = None

        for attempt in range(self._max_retries):
            try:
                response = httpx.get(
                    self._base_url,
                    params=params,
                    timeout=self._timeout,
                )
                response.raise_for_status()
                result: dict[str, Any] = response.json()
                return result
            except (httpx.TimeoutException, httpx.HTTPStatusError) as exc:
                last_error = exc
                if attempt < self._max_retries - 1:
                    backoff = 2**attempt
                    time.sleep(backoff)
            except httpx.HTTPError as exc:
                last_error = exc
                break

        msg = f"DSIP API request failed after {self._max_retries} attempts"
        if last_error:
            msg = f"{msg}: {last_error}"
        raise RuntimeError(msg)
