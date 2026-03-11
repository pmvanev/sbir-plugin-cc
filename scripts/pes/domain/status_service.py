"""Status service -- driving port for /proposal status.

Reads proposal state and generates a StatusReport with wave progress,
deadline countdown, pending async events, and suggested next actions.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pes.domain.state import StateNotFoundError
from pes.domain.status import AsyncEvent, StatusReport, SubmissionDetail, WaveDetail
from pes.ports.state_port import StateReader

WAVE_NAMES: dict[int, str] = {
    0: "Wave 0: Intelligence & Fit",
    1: "Wave 1: Requirements & Strategy",
    2: "Wave 2: Research",
    3: "Wave 3: Discrimination & Outline",
    4: "Wave 4: Drafting",
    5: "Wave 5: Visual Assets",
    6: "Wave 6: Formatting & Assembly",
    7: "Wave 7: Final Review",
    8: "Wave 8: Submission",
    9: "Wave 9: Debrief & Learning",
}

CRITICAL_THRESHOLD_DAYS = 5


class StatusService:
    """Driving port: generates proposal status report from current state."""

    def __init__(self, state_reader: StateReader) -> None:
        self._state_reader = state_reader

    def get_status(self) -> StatusReport:
        """Generate status report from current proposal state.

        Returns StatusReport with all status fields populated.
        When no proposal exists, returns a report with error and suggestion.
        """
        try:
            state = self._state_reader.load()
        except StateNotFoundError:
            return StatusReport(
                current_wave="",
                progress="",
                deadline_countdown="",
                next_action="",
                error="No active proposal found",
                suggestion="Start with /proposal new",
            )

        current_wave_num = state.get("current_wave", 0)
        current_wave = WAVE_NAMES.get(current_wave_num, f"Wave {current_wave_num}")
        deadline_countdown = self._compute_deadline_countdown(state)
        waves = self._build_wave_details(state)
        progress = self._compute_progress(state, waves)
        async_events = self._build_async_events(state)
        warnings = self._build_warnings(state)
        next_action = self._suggest_next_action(state, async_events)
        submission = self._build_submission_detail(state)

        return StatusReport(
            current_wave=current_wave,
            progress=progress,
            deadline_countdown=deadline_countdown,
            next_action=next_action,
            waves=waves,
            async_events=async_events,
            warnings=warnings,
            submission=submission,
        )

    def _compute_deadline_countdown(self, state: dict[str, Any]) -> str:
        days_remaining = self._days_to_deadline(state)
        if days_remaining is None:
            deadline_str = state.get("topic", {}).get("deadline", "")
            if not deadline_str:
                return "No deadline set"
            return "Invalid deadline"
        return f"{days_remaining} days to deadline"

    def _build_wave_details(self, state: dict[str, Any]) -> list[WaveDetail]:
        waves_data = state.get("waves", {})
        details: list[WaveDetail] = []
        for wave_num_str, wave_info in sorted(waves_data.items()):
            wave_num = int(wave_num_str)
            name = WAVE_NAMES.get(wave_num, f"Wave {wave_num}")
            status = wave_info.get("status", "not_started")
            detail = self._wave_detail_text(state, wave_num, status)
            completion_pct = self._compute_wave_completion_pct(wave_info, status)
            details.append(
                WaveDetail(
                    wave_number=wave_num,
                    name=name,
                    status=status,
                    detail=detail,
                    completion_pct=completion_pct,
                )
            )
        return details

    def _compute_wave_completion_pct(self, wave_info: dict[str, Any], status: str) -> float:
        """Compute completion percentage for a wave."""
        if status == "completed":
            return 100.0
        tasks_total = wave_info.get("tasks_total", 0)
        tasks_completed = wave_info.get("tasks_completed", 0)
        if tasks_total > 0:
            return round(tasks_completed / tasks_total * 100, 1)
        return 0.0

    def _wave_detail_text(self, state: dict[str, Any], wave_num: int, status: str) -> str | None:
        if wave_num == 0 and status == "completed":
            go_no_go = state.get("go_no_go", "pending")
            display = "approved" if go_no_go == "go" else go_no_go
            return f"Go: {display}"
        return None

    def _compute_progress(self, state: dict[str, Any], waves: list[WaveDetail]) -> str:
        completed = sum(1 for w in waves if w.status == "completed")
        total = len(waves)
        current = state.get("current_wave", 0)
        wave_name = WAVE_NAMES.get(current, f"Wave {current}")
        return f"{completed}/{total} waves completed, active: {wave_name}"

    def _build_async_events(self, state: dict[str, Any]) -> list[AsyncEvent]:
        events: list[AsyncEvent] = []
        tpoc = state.get("tpoc", {})
        tpoc_status = tpoc.get("status", "not_started")
        if tpoc_status == "questions_generated":
            days_since = None
            generated_at_str = tpoc.get("questions_generated_at")
            if generated_at_str:
                try:
                    generated_at = datetime.fromisoformat(generated_at_str)
                    days_since = (datetime.now() - generated_at).days
                except ValueError:
                    pass
            events.append(
                AsyncEvent(
                    name="TPOC",
                    status="pending",
                    description="TPOC questions generated -- PENDING CALL",
                    days_since=days_since,
                )
            )
        return events

    def _build_warnings(self, state: dict[str, Any]) -> list[str]:
        warnings: list[str] = []
        days_remaining = self._days_to_deadline(state)
        if days_remaining is not None and days_remaining <= CRITICAL_THRESHOLD_DAYS:
            warnings.append(f"{days_remaining} days remaining -- critical threshold")
        return warnings

    def _suggest_next_action(self, state: dict[str, Any], async_events: list[AsyncEvent]) -> str:
        days_remaining = self._days_to_deadline(state)
        if days_remaining is not None and days_remaining <= CRITICAL_THRESHOLD_DAYS:
            return "Prioritize highest-impact incomplete work before deadline"

        for event in async_events:
            if event.name == "TPOC" and event.status == "pending":
                return "Have TPOC call, then /proposal tpoc ingest"

        current_wave = state.get("current_wave", 0)
        go_no_go = state.get("go_no_go", "pending")

        if current_wave == 0 and go_no_go == "pending":
            return "Complete Go/No-Go decision with /proposal new"

        strategy = state.get("strategy_brief", {})
        if current_wave == 1 and strategy.get("status") == "not_started":
            return "Start strategy brief with /proposal strategy"

        return f"Continue work on {WAVE_NAMES.get(current_wave, f'Wave {current_wave}')}"

    def _build_submission_detail(self, state: dict[str, Any]) -> SubmissionDetail | None:
        """Build submission details if proposal has been submitted."""
        submission = state.get("submission", {})
        if submission.get("status") != "submitted":
            return None
        return SubmissionDetail(
            confirmation_number=submission.get("confirmation_number", ""),
            archive_path=submission.get("archive_path", ""),
            read_only=submission.get("immutable", False),
        )

    def _days_to_deadline(self, state: dict[str, Any]) -> int | None:
        deadline_str = state.get("topic", {}).get("deadline", "")
        if not deadline_str:
            return None
        try:
            deadline = date.fromisoformat(deadline_str)
            return (deadline - date.today()).days
        except ValueError:
            return None
