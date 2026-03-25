"""Step definitions for dsip-api-complete walking skeleton scenarios.

Invokes through driving ports:
- DsipApiAdapter (TopicFetchPort) with mocked HTTP transport
- FinderService (application orchestrator)

External HTTP calls are replaced with recorded fixture data.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.dsip_api_complete.conftest import make_search_topic

scenarios("../walking-skeleton.feature")


# --- Given steps ---


@given("each topic has structured details, Q&A entries, and instruction documents available")
def each_topic_has_all_data(ctx: dict[str, Any]):
    """Mark that all 4 data types are available for enrichment."""
    ctx["all_data_available"] = True


# --- When steps ---


@when("Phil searches for open solicitation topics")
def phil_searches_open_topics(
    raw_search_response: dict[str, Any],
    ctx: dict[str, Any],
):
    """Search for open topics using DsipApiAdapter with mocked HTTP.

    Uses the recorded search fixture to simulate the corrected API response.
    Invokes through TopicFetchPort.fetch() -- the driving port.
    """
    from unittest.mock import patch

    from pes.adapters.dsip_api_adapter import DsipApiAdapter

    mock_response = MagicMock()
    mock_response.json.return_value = raw_search_response
    mock_response.raise_for_status = MagicMock()

    with patch("pes.adapters.dsip_api_adapter.httpx.get", return_value=mock_response):
        adapter = DsipApiAdapter(page_size=100, max_pages=1)
        result = adapter.fetch(filters={"topicStatus": "Open"})

    ctx["result"] = {
        "topics": result.topics,
        "total": result.total,
        "source": result.source,
        "error": result.error,
    }


@when("Phil searches for matching topics with enrichment")
def phil_searches_with_enrichment(ctx: dict[str, Any]):
    """Search and enrich through FinderService -- placeholder for walking skeleton 2."""
    # This scenario is @skip -- implementation deferred to step 02-01
    pass
