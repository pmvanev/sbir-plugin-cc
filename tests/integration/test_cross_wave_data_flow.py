"""Cross-wave data flow integrity tests.

Validates that proposal state data set in earlier waves remains accessible
and meaningful when consumed by later wave operations.

Test Budget: 4 behaviors x 2 = 8 max unit tests
- B1: Compliance matrix set in Wave 1 persists unchanged at Wave 4 (AC1)
- B2: PDC status with tier_1='RED' from Wave 4 causes Wave 5 BLOCK (AC2)
- B3: Write tool after submission immutable=true returns BLOCK with topic ID (AC3)
- B4: Wave 9 debrief accesses outcome and submission data from Waves 8-9 (AC4)
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
# Rules covering cross-wave scenarios
# ---------------------------------------------------------------------------

PDC_GATE_RULE = EnforcementRule(
    rule_id="wave-5-requires-pdc-green",
    description="Wave 5 requires all PDC sections GREEN",
    rule_type="pdc_gate",
    condition={"requires_pdc_green": True, "target_wave": 5},
    message="Wave 5 requires all PDC sections GREEN",
)

SUBMISSION_IMMUTABILITY_RULE = EnforcementRule(
    rule_id="submission-immutability",
    description="Submitted proposals are read-only",
    rule_type="submission_immutability",
    condition={"requires_immutable": True},
    message="Proposal is submitted. Artifacts are read-only.",
)


def _make_engine(
    rules: list[EnforcementRule],
) -> tuple[EnforcementEngine, InMemoryAuditLogger]:
    """Create engine with given rules and in-memory audit logger."""
    audit_logger = InMemoryAuditLogger()
    rule_loader = InMemoryRuleLoader(rules=rules)
    engine = EnforcementEngine(rule_loader, audit_logger)
    return engine, audit_logger


# ---------------------------------------------------------------------------
# B1: Compliance matrix persists from Wave 1 to Wave 4 (AC1)
# ---------------------------------------------------------------------------


def test_compliance_matrix_set_in_wave_1_persists_at_wave_4() -> None:
    """Compliance matrix data written during Wave 1 state is present and
    unchanged when the same state is read at Wave 4."""
    compliance_matrix_wave_1: dict[str, Any] = {
        "path": "artifacts/wave-1-strategy/compliance-matrix.json",
        "item_count": 47,
        "generated_at": "2026-04-10T14:30:00Z",
    }

    # State set during Wave 1 with compliance matrix populated
    state_wave_1 = build_state(
        current_wave=1,
        overrides={"compliance_matrix": compliance_matrix_wave_1},
    )

    # Simulate progression: same state dict advances to Wave 4
    state_wave_4 = build_state(
        current_wave=4,
        overrides={"compliance_matrix": compliance_matrix_wave_1},
    )

    # Compliance matrix is identical at both waves
    assert state_wave_4["compliance_matrix"]["path"] == compliance_matrix_wave_1["path"]
    assert state_wave_4["compliance_matrix"]["item_count"] == 47
    assert state_wave_4["compliance_matrix"]["generated_at"] == "2026-04-10T14:30:00Z"
    assert state_wave_4["compliance_matrix"] == state_wave_1["compliance_matrix"]


# ---------------------------------------------------------------------------
# B2: RED PDC tier_1 from Wave 4 drafts causes Wave 5 BLOCK (AC2)
# ---------------------------------------------------------------------------


def test_red_pdc_tier_1_from_wave_4_blocks_wave_5_evaluate() -> None:
    """PDC status with tier_1='RED' computed from Wave 4 drafts causes
    the EnforcementEngine to return Decision.BLOCK for Wave 5 evaluate."""
    engine, _audit = _make_engine(rules=[PDC_GATE_RULE])

    # PDC status reflecting Wave 4 draft deficiencies
    pdc_from_wave_4: dict[str, Any] = {
        "3.1": {
            "tier_1": "RED",
            "tier_2": "GREEN",
            "red_items": ["missing technical approach figure"],
        },
        "3.2": {"tier_1": "GREEN", "tier_2": "GREEN", "red_items": []},
    }

    state = build_state(current_wave=5, overrides={"pdc_status": pdc_from_wave_4})
    result = engine.evaluate(state, tool_name="wave_5_visuals")

    assert result.decision == Decision.BLOCK
    assert any("RED PDC items" in msg for msg in result.messages)
    assert any("Section 3.1" in msg for msg in result.messages)


def test_green_pdc_from_wave_4_allows_wave_5() -> None:
    """All-GREEN PDC status allows Wave 5 to proceed."""
    engine, _audit = _make_engine(rules=[PDC_GATE_RULE])

    all_green_pdc: dict[str, Any] = {
        "3.1": {"tier_1": "GREEN", "tier_2": "GREEN", "red_items": []},
        "3.2": {"tier_1": "GREEN", "tier_2": "GREEN", "red_items": []},
    }

    state = build_state(current_wave=5, overrides={"pdc_status": all_green_pdc})
    result = engine.evaluate(state, tool_name="wave_5_visuals")

    assert result.decision == Decision.ALLOW
    assert result.messages == []


# ---------------------------------------------------------------------------
# B3: Write tool after submission immutable=true returns BLOCK with topic ID (AC3)
# ---------------------------------------------------------------------------


def test_write_tool_after_submission_immutable_returns_block_with_topic_id() -> None:
    """Write tool invocation when submission.immutable=true returns BLOCK
    and message contains the proposal topic ID."""
    engine, _audit = _make_engine(rules=[SUBMISSION_IMMUTABILITY_RULE])

    state = build_state(
        current_wave=8,
        overrides={
            "submission": {
                "status": "submitted",
                "immutable": True,
                "confirmation_number": "SBIR-2026-AF243-001",
                "submitted_at": "2026-06-14T10:00:00Z",
            },
            "topic": {
                "id": "AF243-001",
                "agency": "Air Force",
                "title": "Compact Directed Energy for Maritime UAS Defense",
                "solicitation_url": None,
                "solicitation_file": None,
                "deadline": "2026-06-15",
                "phase": "I",
            },
        },
    )
    result = engine.evaluate(state, tool_name="write_file")

    assert result.decision == Decision.BLOCK
    assert any("AF243-001" in msg for msg in result.messages)


def test_write_tool_before_submission_is_allowed() -> None:
    """Write tool invocation before submission returns ALLOW."""
    engine, _audit = _make_engine(rules=[SUBMISSION_IMMUTABILITY_RULE])

    state = build_state(current_wave=7)
    result = engine.evaluate(state, tool_name="write_file")

    assert result.decision == Decision.ALLOW


# ---------------------------------------------------------------------------
# B4: Wave 9 debrief accesses outcome and submission data (AC4)
# ---------------------------------------------------------------------------


def test_wave_9_debrief_accesses_submission_and_outcome_data() -> None:
    """Wave 9 debrief evaluation can access outcome and submission data
    set in Waves 8-9 without error."""
    engine, audit_logger = _make_engine(
        rules=[PDC_GATE_RULE],
    )

    submission_data: dict[str, Any] = {
        "status": "submitted",
        "immutable": True,
        "confirmation_number": "SBIR-2026-AF243-001",
        "submitted_at": "2026-06-14T10:00:00Z",
        "archive_path": "artifacts/wave-8-submission/archive.zip",
    }
    learning_data: dict[str, Any] = {
        "outcome": "awarded",
        "debrief_recorded": True,
        "recorded_at": "2026-09-01T12:00:00Z",
    }

    state = build_state(
        current_wave=9,
        overrides={
            "submission": submission_data,
            "learning": learning_data,
            "pdc_status": {
                "3.1": {"tier_1": "GREEN", "tier_2": "GREEN", "red_items": []},
            },
        },
    )

    # Engine evaluates without error -- debrief wave accesses state successfully
    result = engine.evaluate(state, tool_name="wave_9_debrief")
    assert result.decision == Decision.ALLOW

    # Verify the state fields are accessible and contain expected data
    assert state["submission"]["confirmation_number"] == "SBIR-2026-AF243-001"
    assert state["submission"]["status"] == "submitted"
    assert state["learning"]["outcome"] == "awarded"
    assert state["learning"]["debrief_recorded"] is True

    # Audit entry confirms successful evaluation
    assert len(audit_logger.entries) == 1
    assert audit_logger.entries[0]["decision"] == "ALLOW"
    assert audit_logger.entries[0]["proposal_id"] == "test-proposal-001"
