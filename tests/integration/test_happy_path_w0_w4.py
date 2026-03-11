"""Happy path: Wave 0 through Wave 4 (intelligence to drafting).

Cross-wave integration test verifying that a proposal transitions
from Wave 0 through Wave 4 without any BLOCK decisions when all
prerequisites are satisfied at each step.

Test Budget: 4 behaviors x 2 = 8 max unit tests
- B1: Full W0-W4 progression returns ALLOW at every transition (acceptance)
- B2: Each individual wave transition returns ALLOW with prerequisites met (parametrized)
- B3: Audit logger records one entry per transition with decision=ALLOW
- B4: State after Wave 4 contains required prerequisite fields
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
# Wave ordering rules (mirrors production pes-config.json)
# ---------------------------------------------------------------------------

WAVE_ORDERING_RULES: list[EnforcementRule] = [
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
]

# Tool names used in each wave (convention: wave_N_<activity>)
WAVE_TOOL_NAMES: dict[int, str] = {
    0: "wave_0_intelligence",
    1: "wave_1_strategy",
    2: "wave_2_research",
    3: "wave_3_outline",
    4: "wave_4_drafting",
}


def _make_engine() -> tuple[EnforcementEngine, InMemoryAuditLogger]:
    """Create engine wired with wave ordering rules and in-memory audit logger."""
    audit_logger = InMemoryAuditLogger()
    rule_loader = InMemoryRuleLoader(rules=WAVE_ORDERING_RULES)
    engine = EnforcementEngine(rule_loader, audit_logger)
    return engine, audit_logger


# ---------------------------------------------------------------------------
# B1: Full W0-W4 progression (acceptance test)
# ---------------------------------------------------------------------------


def test_proposal_transitions_from_wave_0_through_wave_4_without_block() -> None:
    """Proposal transitions W0->W1->W2->W3->W4 with ALLOW at each step.

    Simulates the happy path where all prerequisites are satisfied
    before each wave transition.
    """
    engine, audit_logger = _make_engine()

    # Wave 0: intelligence -- no prerequisites required
    state_w0 = build_state(current_wave=0, go_no_go="go")
    result_w0 = engine.evaluate(state_w0, tool_name=WAVE_TOOL_NAMES[0])
    assert result_w0.decision == Decision.ALLOW
    assert result_w0.messages == []

    # Wave 1: strategy -- requires go_no_go="go" (satisfied)
    state_w1 = build_state(current_wave=1)
    result_w1 = engine.evaluate(state_w1, tool_name=WAVE_TOOL_NAMES[1])
    assert result_w1.decision == Decision.ALLOW
    assert result_w1.messages == []

    # Wave 2: research -- requires strategy approval (satisfied by build_state)
    state_w2 = build_state(current_wave=2)
    result_w2 = engine.evaluate(state_w2, tool_name=WAVE_TOOL_NAMES[2])
    assert result_w2.decision == Decision.ALLOW
    assert result_w2.messages == []

    # Wave 3: outline -- requires research approval (satisfied by build_state)
    state_w3 = build_state(current_wave=3)
    result_w3 = engine.evaluate(state_w3, tool_name=WAVE_TOOL_NAMES[3])
    assert result_w3.decision == Decision.ALLOW
    assert result_w3.messages == []

    # Wave 4: drafting -- requires outline approval (satisfied by build_state)
    state_w4 = build_state(current_wave=4)
    result_w4 = engine.evaluate(state_w4, tool_name=WAVE_TOOL_NAMES[4])
    assert result_w4.decision == Decision.ALLOW
    assert result_w4.messages == []

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
        (0, "wave_0_intelligence"),
        (1, "wave_1_strategy"),
        (2, "wave_2_research"),
        (3, "wave_3_outline"),
        (4, "wave_4_drafting"),
    ],
    ids=["W0-intelligence", "W1-strategy", "W2-research", "W3-outline", "W4-drafting"],
)
def test_individual_wave_transition_returns_allow(wave: int, tool_name: str) -> None:
    """Each wave transition returns ALLOW when prerequisites are met."""
    engine, _audit = _make_engine()
    state = build_state(current_wave=wave)
    result = engine.evaluate(state, tool_name=tool_name)

    assert result.decision == Decision.ALLOW
    assert result.messages == []


# ---------------------------------------------------------------------------
# B3: Audit logger records one entry per transition with decision=ALLOW
# ---------------------------------------------------------------------------


def test_audit_logger_records_allow_entry_per_wave_transition() -> None:
    """Each wave transition produces exactly one audit entry with decision=ALLOW."""
    engine, audit_logger = _make_engine()

    for wave in range(5):
        state = build_state(current_wave=wave)
        engine.evaluate(state, tool_name=WAVE_TOOL_NAMES[wave])

    assert len(audit_logger.entries) == 5
    for i, entry in enumerate(audit_logger.entries):
        assert entry["decision"] == "ALLOW"
        assert entry["event"] == "evaluate"
        assert "timestamp" in entry
        assert entry["proposal_id"] == "test-proposal-001"


# ---------------------------------------------------------------------------
# B4: State after Wave 4 contains correct prerequisite fields
# ---------------------------------------------------------------------------


def test_state_at_wave_4_contains_all_prerequisite_fields() -> None:
    """State built for Wave 4 includes go_no_go, strategy, research, outline approvals."""
    state = build_state(current_wave=4)

    assert state["go_no_go"] == "go"
    assert state["strategy_brief"]["status"] == "approved"
    assert state["strategy_brief"]["approved_at"] is not None
    assert state["research_summary"]["approved_at"] is not None
    assert state["outline"]["status"] == "approved"
    assert state["outline"]["approved_at"] is not None
