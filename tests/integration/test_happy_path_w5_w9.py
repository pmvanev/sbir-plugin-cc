"""Happy path: Wave 5 through Wave 9 (visual assets to debrief).

Cross-wave integration test verifying that a proposal transitions
from Wave 5 through Wave 9 without any BLOCK decisions when all
prerequisites are satisfied at each step.

Test Budget: 4 behaviors x 2 = 8 max unit tests
- B1: Full W5-W9 progression returns ALLOW at every transition (acceptance)
- B2: Each individual wave transition returns ALLOW with prerequisites met (parametrized)
- B3: Audit logger records one entry per transition with decision=ALLOW
- B4: Final state after Wave 9 contains submission and learning fields
"""

from __future__ import annotations

from typing import Any

import pytest

from pes.domain.engine import EnforcementEngine
from pes.domain.rules import Decision, EnforcementRule

from tests.integration.conftest import (
    InMemoryAuditLogger,
    InMemoryRuleLoader,
    build_state,
)

# ---------------------------------------------------------------------------
# Wave ordering + gate rules for W5-W9 (mirrors production pes-config.json)
# ---------------------------------------------------------------------------

WAVE_59_RULES: list[EnforcementRule] = [
    # W0-W4 prerequisites (carried forward from W0-W4 test)
    EnforcementRule(
        rule_id="wave-1-requires-go",
        description="Wave 1 strategy work requires Go decision in Wave 0",
        rule_type="wave_ordering",
        condition={"requires_go_no_go": "go", "target_wave": 1},
        message="Wave 1 requires Go decision in Wave 0",
    ),
    EnforcementRule(
        rule_id="wave-2-requires-strategy",
        description="Wave 2 writing requires strategy brief approval in Wave 1",
        rule_type="wave_ordering",
        condition={"requires_strategy_approval": True, "target_wave": 2},
        message="Wave 2 requires strategy brief approval in Wave 1",
    ),
    EnforcementRule(
        rule_id="wave-3-requires-research",
        description="Wave 3 outline requires research review approval in Wave 2",
        rule_type="wave_ordering",
        condition={"requires_research_approval": True, "target_wave": 3},
        message="Wave 3 requires research review approval in Wave 2",
    ),
    EnforcementRule(
        rule_id="wave-4-requires-outline",
        description="Wave 4 drafting requires outline approval in Wave 3",
        rule_type="wave_ordering",
        condition={"requires_outline_approval": True, "target_wave": 4},
        message="Wave 4 requires outline approval in Wave 3",
    ),
    # W5: PDC gate -- all sections must be GREEN
    EnforcementRule(
        rule_id="wave-5-requires-pdc-green",
        description="Wave 5 visual assets requires all PDC sections GREEN",
        rule_type="pdc_gate",
        condition={"requires_pdc_green": True, "target_wave": 5},
        message="Wave 5 requires all PDC sections GREEN",
    ),
    # W8: final review sign-off
    EnforcementRule(
        rule_id="wave-8-requires-signoff",
        description="Wave 8 submission requires final review sign-off",
        rule_type="wave_ordering",
        condition={"requires_final_review_signoff": True, "target_wave": 8},
        message="Wave 8 requires final review sign-off",
    ),
]

WAVE_TOOL_NAMES: dict[int, str] = {
    5: "wave_5_visuals",
    6: "wave_6_format",
    7: "wave_7_review",
    8: "wave_8_submission",
    9: "wave_9_debrief",
}

# PDC status with all sections GREEN (prerequisite for Wave 5)
ALL_GREEN_PDC: dict[str, Any] = {
    "3.1": {"tier_1": "GREEN", "tier_2": "GREEN", "red_items": []},
    "3.2": {"tier_1": "GREEN", "tier_2": "GREEN", "red_items": []},
}

# Submission record present after Wave 8
SUBMISSION_RECORD: dict[str, Any] = {
    "status": "submitted",
    "confirmation_number": "SBIR-2026-AF243-001",
    "submitted_at": "2026-06-14T10:00:00Z",
    "archive_path": "artifacts/wave-8-submission/archive.zip",
    "immutable": True,
}

# Learning record present after Wave 9
LEARNING_RECORD: dict[str, Any] = {
    "outcome": "awarded",
    "debrief_recorded": True,
    "recorded_at": "2026-09-01T12:00:00Z",
}


def _make_engine() -> tuple[EnforcementEngine, InMemoryAuditLogger]:
    """Create engine wired with W5-W9 rules and in-memory audit logger."""
    audit_logger = InMemoryAuditLogger()
    rule_loader = InMemoryRuleLoader(rules=WAVE_59_RULES)
    engine = EnforcementEngine(rule_loader, audit_logger)
    return engine, audit_logger


def _state_for_wave(wave: int) -> dict[str, Any]:
    """Build state with all prerequisites satisfied for the given wave."""
    overrides: dict[str, Any] = {"pdc_status": ALL_GREEN_PDC}

    if wave >= 8:
        overrides["final_review"] = {"signed_off": True, "signed_off_at": "2026-06-13T10:00:00Z"}
    if wave >= 9:
        overrides["submission"] = SUBMISSION_RECORD
        overrides["learning"] = LEARNING_RECORD

    return build_state(current_wave=wave, overrides=overrides)


# ---------------------------------------------------------------------------
# B1: Full W5-W9 progression (acceptance test)
# ---------------------------------------------------------------------------


def test_proposal_transitions_from_wave_5_through_wave_9_without_block() -> None:
    """Proposal transitions W5->W6->W7->W8->W9 with ALLOW at each step.

    Simulates the happy path where all prerequisites are satisfied
    before each wave transition.
    """
    engine, audit_logger = _make_engine()

    for wave in range(5, 10):
        state = _state_for_wave(wave)
        result = engine.evaluate(state, tool_name=WAVE_TOOL_NAMES[wave])
        assert result.decision == Decision.ALLOW, (
            f"Wave {wave} blocked unexpectedly: {result.messages}"
        )
        assert result.messages == []

    # Verify audit trail: 5 transitions, all ALLOW
    assert len(audit_logger.entries) == 5
    for entry in audit_logger.entries:
        assert entry["decision"] == "ALLOW"


# ---------------------------------------------------------------------------
# B2: Each individual transition returns ALLOW (parametrized)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "wave,tool_name",
    [
        (5, "wave_5_visuals"),
        (6, "wave_6_format"),
        (7, "wave_7_review"),
        (8, "wave_8_submission"),
        (9, "wave_9_debrief"),
    ],
    ids=["W5-visuals", "W6-format", "W7-review", "W8-submission", "W9-debrief"],
)
def test_individual_wave_transition_returns_allow(wave: int, tool_name: str) -> None:
    """Each wave transition returns ALLOW when prerequisites are met."""
    engine, _audit = _make_engine()
    state = _state_for_wave(wave)
    result = engine.evaluate(state, tool_name=tool_name)

    assert result.decision == Decision.ALLOW
    assert result.messages == []


# ---------------------------------------------------------------------------
# B3: Audit logger records one ALLOW entry per wave transition
# ---------------------------------------------------------------------------


def test_audit_logger_records_allow_entry_per_wave_transition() -> None:
    """Each wave transition produces exactly one audit entry with decision=ALLOW."""
    engine, audit_logger = _make_engine()

    for wave in range(5, 10):
        state = _state_for_wave(wave)
        engine.evaluate(state, tool_name=WAVE_TOOL_NAMES[wave])

    assert len(audit_logger.entries) == 5
    for i, entry in enumerate(audit_logger.entries):
        assert entry["decision"] == "ALLOW"
        assert entry["event"] == "evaluate"
        assert "timestamp" in entry
        assert entry["proposal_id"] == "test-proposal-001"


# ---------------------------------------------------------------------------
# B4: Wave 8 requires sign-off + final state has submission and learning
# ---------------------------------------------------------------------------


def test_wave_8_returns_allow_only_when_final_review_signed_off() -> None:
    """Wave 8 transition returns ALLOW only when final_review.signed_off is truthy."""
    engine, _audit = _make_engine()

    # Without sign-off: BLOCK
    state_no_signoff = build_state(
        current_wave=8,
        overrides={
            "pdc_status": ALL_GREEN_PDC,
            "final_review": {"signed_off": False},
        },
    )
    result_blocked = engine.evaluate(state_no_signoff, tool_name="wave_8_submission")
    assert result_blocked.decision == Decision.BLOCK

    # With sign-off: ALLOW
    state_signed = _state_for_wave(8)
    result_allowed = engine.evaluate(state_signed, tool_name="wave_8_submission")
    assert result_allowed.decision == Decision.ALLOW


def test_final_state_after_wave_9_contains_submission_and_learning() -> None:
    """State after Wave 9 has submission.confirmation_number and learning.outcome."""
    state = _state_for_wave(9)

    # AC3: submission with confirmation_number
    assert state["submission"]["confirmation_number"] == "SBIR-2026-AF243-001"
    assert state["submission"]["status"] == "submitted"

    # AC3: learning with outcome recorded
    assert state["learning"]["outcome"] == "awarded"
    assert state["learning"]["debrief_recorded"] is True
