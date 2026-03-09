"""Unit tests for proposal status through StatusService (driving port).

Test Budget: 8 behaviors x 2 = 16 unit tests max.
Tests enter through driving port (StatusService).
StateReader driven port replaced with in-memory fake.
Domain objects (StatusReport, WaveDetail, AsyncEvent) are real collaborators.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

import pytest

from pes.domain.state import StateNotFoundError
from pes.domain.status_service import StatusService
from pes.ports.state_port import StateReader

# ---------------------------------------------------------------------------
# Fake driven port
# ---------------------------------------------------------------------------

class InMemoryStateReader(StateReader):
    """Returns pre-configured state dict."""

    def __init__(self, state: dict[str, Any] | None = None) -> None:
        self._state = state

    def load(self) -> dict[str, Any]:
        if self._state is None:
            raise StateNotFoundError("No active proposal found")
        return self._state

    def exists(self) -> bool:
        return self._state is not None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_state(
    *,
    wave: int = 1,
    topic_id: str = "AF243-001",
    deadline_days: int = 18,
    go_no_go: str = "go",
    tpoc_status: str = "not_started",
    tpoc_generated_days_ago: int | None = None,
    strategy_status: str = "not_started",
) -> dict[str, Any]:
    """Build a minimal valid proposal state."""
    deadline = (date.today() + timedelta(days=deadline_days)).isoformat()

    waves: dict[str, Any] = {}
    for w in range(wave):
        waves[str(w)] = {
            "status": "completed",
            "completed_at": "2026-03-01T10:00:00Z",
        }
    waves[str(wave)] = {"status": "active", "completed_at": None}

    tpoc: dict[str, Any] = {
        "status": tpoc_status,
        "questions_path": None,
        "qa_log_path": None,
        "questions_generated_at": None,
        "answers_ingested_at": None,
    }
    if tpoc_generated_days_ago is not None:
        generated_at = datetime.now() - timedelta(days=tpoc_generated_days_ago)
        tpoc["questions_generated_at"] = generated_at.isoformat()

    return {
        "schema_version": "1.0.0",
        "proposal_id": f"proposal-{topic_id.lower()}",
        "topic": {
            "id": topic_id,
            "agency": "Air Force",
            "title": "Compact Directed Energy for Maritime UAS Defense",
            "deadline": deadline,
            "phase": "I",
        },
        "current_wave": wave,
        "go_no_go": go_no_go,
        "waves": waves,
        "tpoc": tpoc,
        "strategy_brief": {
            "path": None,
            "status": strategy_status,
            "approved_at": None,
        },
        "created_at": "2026-03-01T10:00:00Z",
        "updated_at": "2026-03-01T10:00:00Z",
    }


def _make_service(state: dict[str, Any] | None = None) -> StatusService:
    """Wire StatusService with in-memory fake."""
    reader = InMemoryStateReader(state)
    return StatusService(reader)


# ---------------------------------------------------------------------------
# Behavior 1: Shows wave, progress, and deadline countdown
# ---------------------------------------------------------------------------


class TestWaveProgressAndDeadline:
    def test_shows_current_wave_name_and_deadline_countdown(self):
        state = _make_state(wave=1, deadline_days=18)
        service = _make_service(state)

        report = service.get_status()

        assert report.current_wave == "Wave 1: Requirements & Strategy"
        assert "18 days" in report.deadline_countdown

    def test_shows_progress_summary(self):
        state = _make_state(wave=1)
        service = _make_service(state)

        report = service.get_status()

        assert report.progress is not None
        assert len(report.progress) > 0


# ---------------------------------------------------------------------------
# Behavior 2: Shows pending async events (TPOC)
# ---------------------------------------------------------------------------


class TestPendingAsyncEvents:
    def test_shows_tpoc_pending_with_description(self):
        state = _make_state(
            tpoc_status="questions_generated",
            tpoc_generated_days_ago=5,
        )
        service = _make_service(state)

        report = service.get_status()

        assert len(report.async_events) >= 1
        tpoc_event = report.async_events[0]
        assert "TPOC" in tpoc_event.description
        assert "PENDING" in tpoc_event.description.upper()

    def test_tpoc_pending_suggests_ingest_action(self):
        state = _make_state(
            tpoc_status="questions_generated",
            tpoc_generated_days_ago=5,
        )
        service = _make_service(state)

        report = service.get_status()

        assert "tpoc" in report.next_action.lower()
        assert "ingest" in report.next_action.lower()


# ---------------------------------------------------------------------------
# Behavior 3: Suggests next action based on state
# ---------------------------------------------------------------------------


class TestNextAction:
    def test_suggests_next_action_for_wave_1_not_started(self):
        state = _make_state(wave=1, strategy_status="not_started")
        service = _make_service(state)

        report = service.get_status()

        assert report.next_action is not None
        assert len(report.next_action) > 0


# ---------------------------------------------------------------------------
# Behavior 4: Deadline warning at critical threshold
# ---------------------------------------------------------------------------


class TestDeadlineWarning:
    @pytest.mark.parametrize("days,should_warn", [
        (4, True),
        (5, True),
        (6, False),
        (18, False),
    ])
    def test_deadline_warning_at_threshold(self, days, should_warn):
        state = _make_state(deadline_days=days)
        service = _make_service(state)

        report = service.get_status()

        has_warning = any("critical" in w.lower() for w in report.warnings)
        assert has_warning == should_warn


# ---------------------------------------------------------------------------
# Behavior 5: Handles gracefully when no proposal exists
# ---------------------------------------------------------------------------


class TestNoProposal:
    def test_no_proposal_returns_error_and_suggestion(self):
        service = _make_service(state=None)

        report = service.get_status()

        assert report.error is not None
        assert "No active proposal" in report.error
        assert report.suggestion is not None
        assert "/proposal new" in report.suggestion


# ---------------------------------------------------------------------------
# Behavior 6: All 10 wave names displayed correctly
# ---------------------------------------------------------------------------


class TestAllWaveNames:
    @pytest.mark.parametrize("wave_num,expected_name", [
        (0, "Wave 0: Intelligence & Fit"),
        (1, "Wave 1: Requirements & Strategy"),
        (2, "Wave 2: Research"),
        (3, "Wave 3: Discrimination & Outline"),
        (4, "Wave 4: Drafting"),
        (5, "Wave 5: Visual Assets"),
        (6, "Wave 6: Formatting & Assembly"),
        (7, "Wave 7: Final Review"),
        (8, "Wave 8: Submission"),
        (9, "Wave 9: Debrief & Learning"),
    ])
    def test_wave_name_matches_spec(self, wave_num, expected_name):
        state = _make_state(wave=wave_num)
        service = _make_service(state)

        report = service.get_status()

        assert report.current_wave == expected_name


# ---------------------------------------------------------------------------
# Behavior 7: Unknown wave number produces default label
# ---------------------------------------------------------------------------


class TestUnknownWaveNumber:
    def test_unknown_wave_shows_default_label_without_error(self):
        state = _make_state(wave=0)
        state["current_wave"] = 99
        state["waves"] = {"99": {"status": "active", "completed_at": None}}
        service = _make_service(state)

        report = service.get_status()

        assert "Wave 99" in report.current_wave
        assert report.error is None


# ---------------------------------------------------------------------------
# Behavior 8: Missing wave entries produce zero-completed progress
# ---------------------------------------------------------------------------


class TestMissingWaveEntries:
    def test_empty_waves_shows_zero_completed(self):
        state = _make_state(wave=0)
        state["waves"] = {}
        service = _make_service(state)

        report = service.get_status()

        assert "0/" in report.progress
        assert report.error is None
