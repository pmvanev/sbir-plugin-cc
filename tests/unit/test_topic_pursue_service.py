"""Unit tests for TopicPursueService -- driving port for topic pursuit.

Test Budget: 3 behaviors x 2 = 6 max unit tests.
Tests invoke through TopicPursueService (driving port) with
InMemoryFinderResultsAdapter (fake driven port). No mocks inside the hexagon.

Behaviors tested:
1. Pursue valid topic -> returns TopicInfo dict with metadata
2. Pursue expired topic -> raises TopicExpiredError
3. Pursue non-existent topic -> raises TopicNotFoundError
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import pytest

from pes.domain.topic_pursue_service import (
    PursueResult,
    TopicExpiredError,
    TopicNotFoundError,
    TopicPursueService,
)
from tests.acceptance.solicitation_finder.conftest import make_scored_result
from tests.acceptance.solicitation_finder.fakes import InMemoryFinderResultsAdapter


def _make_results_with_topic(
    topic_id: str = "AF263-042",
    title: str = "Compact Directed Energy for C-UAS",
    agency: str = "Air Force",
    phase: str = "I",
    deadline: str | None = None,
    composite: float = 0.82,
    recommendation: str = "go",
) -> dict[str, Any]:
    """Build a minimal finder results dict containing one topic."""
    if deadline is None:
        deadline = (datetime.now() + timedelta(days=61)).strftime("%Y-%m-%d")
    return {
        "schema_version": "1.0.0",
        "finder_run_id": "test-run-001",
        "run_date": "2026-03-13T14:30:00Z",
        "source": {"type": "dsip_api"},
        "results": [
            make_scored_result(
                topic_id=topic_id,
                title=title,
                agency=agency,
                composite=composite,
                recommendation=recommendation,
                deadline=deadline,
                phase=phase,
            ),
        ],
    }


class TestPursueValidTopic:
    """Behavior 1: Pursue a valid, non-expired topic returns TopicInfo."""

    def test_returns_topic_info_with_all_metadata(self) -> None:
        results_port = InMemoryFinderResultsAdapter()
        results_port.write(
            _make_results_with_topic(
                topic_id="AF263-042",
                title="Compact Directed Energy for C-UAS",
                agency="Air Force",
                phase="I",
                deadline="2026-05-15",
                composite=0.82,
                recommendation="go",
            )
        )
        service = TopicPursueService(results_port=results_port)

        result = service.pursue("AF263-042")

        assert isinstance(result, PursueResult)
        assert result.topic_id == "AF263-042"
        assert result.title == "Compact Directed Energy for C-UAS"
        assert result.agency == "Air Force"
        assert result.phase == "I"
        assert result.deadline == "2026-05-15"
        assert result.composite_score == 0.82
        assert result.recommendation == "go"

    def test_returns_topic_info_for_evaluate_recommendation(self) -> None:
        results_port = InMemoryFinderResultsAdapter()
        results_port.write(
            _make_results_with_topic(
                topic_id="N263-044",
                title="Shipboard RF Power Management",
                agency="Navy",
                phase="II",
                deadline="2026-06-30",
                composite=0.34,
                recommendation="evaluate",
            )
        )
        service = TopicPursueService(results_port=results_port)

        result = service.pursue("N263-044")

        assert result.topic_id == "N263-044"
        assert result.agency == "Navy"
        assert result.phase == "II"


class TestPursueExpiredTopic:
    """Behavior 2: Pursue expired topic raises TopicExpiredError."""

    def test_expired_topic_raises_error_with_deadline(self) -> None:
        results_port = InMemoryFinderResultsAdapter()
        results_port.write(
            _make_results_with_topic(
                topic_id="AF263-042",
                deadline="2026-03-01",
            )
        )
        service = TopicPursueService(results_port=results_port)

        with pytest.raises(TopicExpiredError) as exc_info:
            service.pursue("AF263-042")

        assert "2026-03-01" in str(exc_info.value)


class TestPursueNonExistentTopic:
    """Behavior 3: Pursue non-existent topic raises TopicNotFoundError."""

    def test_missing_topic_raises_error(self) -> None:
        results_port = InMemoryFinderResultsAdapter()
        results_port.write(
            _make_results_with_topic(topic_id="AF263-042")
        )
        service = TopicPursueService(results_port=results_port)

        with pytest.raises(TopicNotFoundError):
            service.pursue("DOES-NOT-EXIST")

    def test_no_results_file_raises_error(self) -> None:
        results_port = InMemoryFinderResultsAdapter()
        # No results written
        service = TopicPursueService(results_port=results_port)

        with pytest.raises(TopicNotFoundError):
            service.pursue("AF263-042")
