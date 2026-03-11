"""StatusService cross-wave integration tests.

Validates that StatusService produces correct StatusReport fields as
a proposal progresses through the wave lifecycle (Waves 0-9).

Test Budget: 5 behaviors x 2 = 10 max unit tests
- B1: current_wave matches WAVE_NAMES for active wave (AC1, parametrized: 0, 4, 9)
- B2: progress contains completed/total and active wave name at Wave 4 (AC2)
- B3: warnings includes critical threshold when days_remaining <= 5 (AC3)
- B4: next_action changes as proposal progresses (AC4, parametrized)
- B5: submission populated after Wave 8 submission (AC5)
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from pes.domain.status_service import StatusService, WAVE_NAMES

from tests.integration.conftest import InMemoryStateReader, build_state


# ---------------------------------------------------------------------------
# B1: current_wave matches WAVE_NAMES at sampled waves (AC1)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "wave_num",
    [0, 4, 9],
    ids=["wave-0-intelligence", "wave-4-drafting", "wave-9-debrief"],
)
def test_current_wave_matches_wave_names(wave_num: int) -> None:
    """StatusReport.current_wave matches WAVE_NAMES for the active wave."""
    state = build_state(current_wave=wave_num)
    reader = InMemoryStateReader(state)
    service = StatusService(reader)

    report = service.get_status()

    assert report.current_wave == WAVE_NAMES[wave_num]


# ---------------------------------------------------------------------------
# B2: progress at mid-lifecycle Wave 4 (AC2)
# ---------------------------------------------------------------------------


def test_progress_at_wave_4_shows_completed_total_and_active_name() -> None:
    """StatusReport.progress contains completed/total count and active wave name."""
    state = build_state(current_wave=4)
    reader = InMemoryStateReader(state)
    service = StatusService(reader)

    report = service.get_status()

    # Waves 0-3 completed = 4, total = 10 waves, active = Wave 4
    assert "4/10" in report.progress
    assert WAVE_NAMES[4] in report.progress


# ---------------------------------------------------------------------------
# B3: warnings with critical threshold (AC3)
# ---------------------------------------------------------------------------


def test_warnings_include_critical_threshold_when_deadline_within_5_days() -> None:
    """StatusReport.warnings includes critical threshold message when
    days_remaining <= 5 during active lifecycle."""
    near_deadline = (date.today() + timedelta(days=3)).isoformat()
    state = build_state(current_wave=4, deadline=near_deadline)
    reader = InMemoryStateReader(state)
    service = StatusService(reader)

    report = service.get_status()

    assert len(report.warnings) >= 1
    assert any("critical threshold" in w for w in report.warnings)
    assert any("3 days" in w for w in report.warnings)


# ---------------------------------------------------------------------------
# B4: next_action changes as proposal progresses (AC4)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "wave_num,go_no_go_val,overrides,expected_fragment",
    [
        (0, "pending", None, "Go/No-Go"),
        (1, "go", {"strategy_brief": {"status": "not_started", "approved_at": None, "path": None}}, "strategy"),
        (4, "go", None, "Continue"),
    ],
    ids=["wave-0-go-decision", "wave-1-strategy", "wave-4-continue"],
)
def test_next_action_reflects_proposal_stage(
    wave_num: int,
    go_no_go_val: str,
    overrides: dict | None,
    expected_fragment: str,
) -> None:
    """StatusReport.next_action changes appropriately as proposal progresses."""
    # Use a far deadline to avoid critical-threshold override
    state = build_state(
        current_wave=wave_num,
        go_no_go=go_no_go_val,
        deadline="2026-12-31",
        overrides=overrides,
    )
    reader = InMemoryStateReader(state)
    service = StatusService(reader)

    report = service.get_status()

    assert expected_fragment.lower() in report.next_action.lower()


# ---------------------------------------------------------------------------
# B5: submission detail after Wave 8 (AC5)
# ---------------------------------------------------------------------------


def test_submission_populated_after_wave_8_with_confirmation_and_read_only() -> None:
    """StatusReport.submission is populated with confirmation_number and
    read_only=true after Wave 8 submission."""
    state = build_state(
        current_wave=9,
        overrides={
            "submission": {
                "status": "submitted",
                "immutable": True,
                "confirmation_number": "SBIR-2026-AF243-001",
                "submitted_at": "2026-06-14T10:00:00Z",
                "archive_path": "artifacts/wave-8-submission/archive.zip",
            },
        },
    )
    reader = InMemoryStateReader(state)
    service = StatusService(reader)

    report = service.get_status()

    assert report.submission is not None
    assert report.submission.confirmation_number == "SBIR-2026-AF243-001"
    assert report.submission.read_only is True
