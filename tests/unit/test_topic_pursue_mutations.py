"""Targeted mutation-killing tests for TopicPursueService.

Tests exact error messages, edge cases in deadline parsing,
and precise field extraction.
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


def _results_with(*entries: dict[str, Any]) -> dict[str, Any]:
    return {"schema_version": "1.0.0", "results": list(entries)}


def _entry(
    topic_id: str = "AF263-042",
    title: str = "Test Topic",
    agency: str = "Air Force",
    phase: str = "I",
    deadline: str | None = None,
    composite: float = 0.75,
    recommendation: str = "go",
) -> dict[str, Any]:
    if deadline is None:
        deadline = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    return make_scored_result(
        topic_id=topic_id,
        title=title,
        agency=agency,
        composite=composite,
        recommendation=recommendation,
        deadline=deadline,
        phase=phase,
    )


class TestPursueResultFields:
    """Kill mutants on field extraction in pursue()."""

    def test_all_fields_extracted_correctly(self) -> None:
        port = InMemoryFinderResultsAdapter()
        port.write(_results_with(_entry(
            topic_id="N263-044",
            title="RF Power Management",
            agency="Navy",
            phase="II",
            deadline="2026-06-30",
            composite=0.34,
            recommendation="evaluate",
        )))
        svc = TopicPursueService(results_port=port)
        result = svc.pursue("N263-044")
        assert result.topic_id == "N263-044"
        assert result.title == "RF Power Management"
        assert result.agency == "Navy"
        assert result.phase == "II"
        assert result.deadline == "2026-06-30"
        assert result.composite_score == 0.34
        assert result.recommendation == "evaluate"

    def test_pursue_result_is_frozen(self) -> None:
        port = InMemoryFinderResultsAdapter()
        port.write(_results_with(_entry()))
        svc = TopicPursueService(results_port=port)
        result = svc.pursue("AF263-042")
        with pytest.raises(AttributeError):
            result.topic_id = "changed"  # type: ignore[misc]


class TestNotFoundErrors:
    """Kill mutants on TopicNotFoundError messages."""

    def test_no_results_error_message(self) -> None:
        port = InMemoryFinderResultsAdapter()
        svc = TopicPursueService(results_port=port)
        with pytest.raises(TopicNotFoundError, match="No finder results found"):
            svc.pursue("ANY")

    def test_topic_missing_error_message(self) -> None:
        port = InMemoryFinderResultsAdapter()
        port.write(_results_with(_entry(topic_id="EXISTING")))
        svc = TopicPursueService(results_port=port)
        with pytest.raises(TopicNotFoundError, match="MISSING"):
            svc.pursue("MISSING")

    def test_empty_results_list(self) -> None:
        port = InMemoryFinderResultsAdapter()
        port.write({"schema_version": "1.0.0", "results": []})
        svc = TopicPursueService(results_port=port)
        with pytest.raises(TopicNotFoundError):
            svc.pursue("AF263-042")


class TestExpiredErrors:
    """Kill mutants on deadline checking."""

    def test_expired_error_includes_deadline(self) -> None:
        port = InMemoryFinderResultsAdapter()
        port.write(_results_with(_entry(deadline="2025-01-01")))
        svc = TopicPursueService(results_port=port)
        with pytest.raises(TopicExpiredError, match="2025-01-01"):
            svc.pursue("AF263-042")

    def test_future_deadline_succeeds(self) -> None:
        future = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")
        port = InMemoryFinderResultsAdapter()
        port.write(_results_with(_entry(deadline=future)))
        svc = TopicPursueService(results_port=port)
        result = svc.pursue("AF263-042")
        assert result.deadline == future

    def test_today_deadline_succeeds(self) -> None:
        """Today's deadline should NOT be expired (deadline < today, not <=)."""
        today = datetime.now().strftime("%Y-%m-%d")
        port = InMemoryFinderResultsAdapter()
        port.write(_results_with(_entry(deadline=today)))
        svc = TopicPursueService(results_port=port)
        # Should not raise - deadline is today, not expired
        result = svc.pursue("AF263-042")
        assert result.deadline == today

    def test_empty_deadline_succeeds(self) -> None:
        port = InMemoryFinderResultsAdapter()
        entry = _entry()
        entry["deadline"] = ""
        port.write(_results_with(entry))
        svc = TopicPursueService(results_port=port)
        result = svc.pursue("AF263-042")
        assert result.deadline == ""

    def test_unparseable_deadline_succeeds(self) -> None:
        """Unparseable deadline should not block pursuit."""
        port = InMemoryFinderResultsAdapter()
        entry = _entry()
        entry["deadline"] = "not-a-date"
        port.write(_results_with(entry))
        svc = TopicPursueService(results_port=port)
        result = svc.pursue("AF263-042")
        assert result.deadline == "not-a-date"


class TestMultipleTopics:
    """Kill mutants on _find_topic iteration."""

    def test_finds_second_topic_in_list(self) -> None:
        port = InMemoryFinderResultsAdapter()
        port.write(_results_with(
            _entry(topic_id="FIRST", title="First"),
            _entry(topic_id="SECOND", title="Second"),
        ))
        svc = TopicPursueService(results_port=port)
        result = svc.pursue("SECOND")
        assert result.topic_id == "SECOND"
        assert result.title == "Second"

    def test_finds_first_topic_in_list(self) -> None:
        port = InMemoryFinderResultsAdapter()
        port.write(_results_with(
            _entry(topic_id="FIRST", title="First"),
            _entry(topic_id="SECOND", title="Second"),
        ))
        svc = TopicPursueService(results_port=port)
        result = svc.pursue("FIRST")
        assert result.topic_id == "FIRST"
