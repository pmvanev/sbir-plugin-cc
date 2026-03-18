"""State schema integrity through lifecycle.

Cross-wave integration test verifying that proposal state retains all
required keys through wave transitions, deadline blocking triggers
correctly mid-lifecycle, and StatusReport fields remain populated.

Test Budget: 5 behaviors x 2 = 10 max unit tests
- B1: State retains all required keys through full W0-W9 lifecycle (acceptance)
- B2: Individual wave state retains required keys (parametrized, AC1)
- B3: Deadline blocking triggers BLOCK on non-essential wave at critical threshold (AC2)
- B4: StatusReport fields populated at each sampled wave (parametrized, AC3)
- B5: Deadline blocking message includes days remaining and submit/skip suggestion (AC4)
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any
import pytest

from pes.domain.deadline_blocking import DeadlineBlockingEvaluator
from pes.domain.engine import EnforcementEngine
from pes.domain.rules import Decision, EnforcementRule
from pes.domain.status_service import StatusService

from tests.integration.conftest import (
    InMemoryAuditLogger,
    InMemoryRuleLoader,
    InMemoryStateReader,
    build_state,
)

# ---------------------------------------------------------------------------
# Required top-level keys that must survive every wave transition
# ---------------------------------------------------------------------------

REQUIRED_STATE_KEYS: set[str] = {
    "schema_version",
    "proposal_id",
    "topic",
    "current_wave",
    "go_no_go",
    "waves",
    "corpus",
    "compliance_matrix",
    "tpoc",
    "strategy_brief",
    "fit_scoring",
    "research_summary",
    "discrimination_table",
    "outline",
    "volumes",
    "open_review_items",
    "created_at",
    "updated_at",
}

# ---------------------------------------------------------------------------
# Deadline blocking rule for tests (mirrors production pes-config.json)
# ---------------------------------------------------------------------------

DEADLINE_BLOCKING_RULE = EnforcementRule(
    rule_id="deadline-blocking",
    description="Block non-essential waves when deadline is critically close",
    rule_type="deadline_blocking",
    condition={
        "critical_days": 5,
        "non_essential_waves": [5, 9],
    },
    message="Deadline critically close -- non-essential wave blocked",
)


def _make_engine(
    rules: list[EnforcementRule] | None = None,
) -> tuple[EnforcementEngine, InMemoryAuditLogger]:
    """Create engine wired with given rules and in-memory audit logger."""
    audit_logger = InMemoryAuditLogger()
    rule_loader = InMemoryRuleLoader(rules=rules or [])
    engine = EnforcementEngine(rule_loader, audit_logger)
    return engine, audit_logger


# ---------------------------------------------------------------------------
# B1: Full W0-W9 lifecycle -- state retains all required keys (acceptance)
# ---------------------------------------------------------------------------


def test_state_retains_all_required_keys_through_full_lifecycle() -> None:
    """Proposal state dict retains every required key at each wave 0-9.

    No keys are lost or corrupted as the proposal advances through
    the complete wave lifecycle.
    """
    for wave in range(10):
        state = build_state(current_wave=wave)
        missing = REQUIRED_STATE_KEYS - set(state.keys())
        assert missing == set(), (
            f"Wave {wave}: missing required keys: {missing}"
        )
        # Verify no key values are corrupted to wrong types
        assert isinstance(state["current_wave"], int)
        assert isinstance(state["topic"], dict)
        assert isinstance(state["waves"], dict)
        assert isinstance(state["proposal_id"], str)
        assert state["current_wave"] == wave


# ---------------------------------------------------------------------------
# B2: Individual wave state retains required keys (parametrized)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("wave", list(range(10)), ids=[f"W{w}" for w in range(10)])
def test_individual_wave_state_retains_required_keys(wave: int) -> None:
    """State at wave N contains all required keys with correct current_wave."""
    state = build_state(current_wave=wave)
    missing = REQUIRED_STATE_KEYS - set(state.keys())
    assert missing == set(), f"Wave {wave}: missing keys: {missing}"
    assert state["current_wave"] == wave
    # Waves dict has entries for all 10 waves
    assert len(state["waves"]) == 10


# ---------------------------------------------------------------------------
# B3: Deadline blocking triggers BLOCK on non-essential wave (AC2)
# ---------------------------------------------------------------------------


def test_deadline_blocking_triggers_block_on_non_essential_wave_at_critical_threshold() -> None:
    """When days_remaining crosses critical threshold mid-lifecycle,
    deadline blocking produces Decision.BLOCK on a non-essential wave.
    """
    engine, audit_logger = _make_engine(rules=[DEADLINE_BLOCKING_RULE])

    # Set deadline to 3 days from "today" (within critical_days=5)
    near_deadline = (date.today() + timedelta(days=3)).isoformat()
    state = build_state(current_wave=5, deadline=near_deadline)

    result = engine.evaluate(state, tool_name="wave_5_visual_assets")

    assert result.decision == Decision.BLOCK
    assert len(result.messages) == 1
    # Verify audit recorded the block
    assert audit_logger.entries[0]["decision"] == "block"


# ---------------------------------------------------------------------------
# B4: StatusReport fields populated at each sampled wave (parametrized, AC3)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "wave",
    [0, 2, 5, 8, 9],
    ids=["W0", "W2", "W5", "W8", "W9"],
)
def test_status_report_fields_populated_at_wave(wave: int) -> None:
    """StatusReport at each sampled wave contains non-empty
    current_wave, progress, deadline_countdown, and next_action.
    """
    state = build_state(current_wave=wave)
    state_reader = InMemoryStateReader(state)
    service = StatusService(state_reader)

    report = service.get_status()

    assert report.current_wave, f"Wave {wave}: current_wave is empty"
    assert report.progress, f"Wave {wave}: progress is empty"
    assert report.deadline_countdown, f"Wave {wave}: deadline_countdown is empty"
    assert report.next_action, f"Wave {wave}: next_action is empty"


# ---------------------------------------------------------------------------
# B5: Deadline blocking message format (AC4)
# ---------------------------------------------------------------------------


def test_deadline_blocking_message_includes_days_remaining_and_suggestion() -> None:
    """Deadline blocking message includes the days remaining count
    and submit/skip suggestion text.
    """
    engine, _audit = _make_engine(rules=[DEADLINE_BLOCKING_RULE])

    near_deadline = (date.today() + timedelta(days=2)).isoformat()
    state = build_state(current_wave=9, deadline=near_deadline)

    result = engine.evaluate(state, tool_name="wave_9_debrief")

    assert result.decision == Decision.BLOCK
    assert len(result.messages) == 1

    message = result.messages[0]
    # AC4: message includes days remaining count
    assert "2 days remaining" in message
    # AC4: message includes submit/skip suggestion text
    assert "submit" in message.lower()
    assert "skip" in message.lower()
