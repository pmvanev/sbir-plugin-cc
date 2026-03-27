"""Integration tests: end-to-end wiring from pes-config.json through EnforcementEngine.

Loads the REAL templates/pes-config.json through JsonRuleAdapter, feeds it to
EnforcementEngine, and verifies each new evaluator triggers BLOCK on correct
conditions and ALLOW otherwise.

Test Budget: 8 behaviors x 2 = 16 max unit tests.
  1. Config loads all 12 rules through JsonRuleAdapter
  2. PDC gate evaluator: BLOCK on RED Tier 1/2, ALLOW otherwise
  3. Deadline blocking evaluator: BLOCK near deadline on non-essential wave, ALLOW otherwise
  4. Submission immutability evaluator: BLOCK on submitted+immutable, ALLOW otherwise
  5. Corpus integrity evaluator: BLOCK on outcome change, ALLOW otherwise
  6. Figure pipeline rule has correct structure (rule_id, condition)
  7. Style profile rule has correct structure (rule_id, condition)
  8. Writing style gate rule has correct structure (rule_id, condition)
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pytest

from pes.adapters.json_rule_adapter import JsonRuleAdapter
from pes.domain.engine import EnforcementEngine
from pes.ports.audit_port import AuditLogger

# ---------------------------------------------------------------------------
# Path to real pes-config.json
# ---------------------------------------------------------------------------

REAL_CONFIG_PATH = str(
    Path(__file__).resolve().parents[2] / "templates" / "pes-config.json"
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


class InMemoryAuditLogger(AuditLogger):
    """Captures audit entries for assertion."""

    def __init__(self) -> None:
        self.entries: list[dict[str, Any]] = []

    def log(self, entry: dict[str, Any]) -> None:
        self.entries.append(entry)


@pytest.fixture()
def engine() -> EnforcementEngine:
    """EnforcementEngine wired with real pes-config.json via JsonRuleAdapter."""
    rule_loader = JsonRuleAdapter(REAL_CONFIG_PATH)
    audit_logger = InMemoryAuditLogger()
    return EnforcementEngine(rule_loader, audit_logger)


# ---------------------------------------------------------------------------
# 1. Config loading: all 8 rules loaded and dispatched
# ---------------------------------------------------------------------------


def test_real_config_loads_all_twelve_rules():
    """JsonRuleAdapter loads all 12 rules from real pes-config.json."""
    adapter = JsonRuleAdapter(REAL_CONFIG_PATH)
    rules = adapter.load_rules()
    assert len(rules) == 12
    rule_types = [r.rule_type for r in rules]
    assert rule_types.count("wave_ordering") == 4
    assert "pdc_gate" in rule_types
    assert "deadline_blocking" in rule_types
    assert "submission_immutability" in rule_types
    assert "corpus_integrity" in rule_types
    assert "figure_pipeline_gate" in rule_types
    assert "style_profile_gate" in rule_types
    assert "writing_style_gate" in rule_types
    assert "outline_gate" in rule_types


def test_real_config_figure_pipeline_rule_has_correct_structure():
    """figure-pipeline-requires-specs rule has correct rule_id and condition."""
    adapter = JsonRuleAdapter(REAL_CONFIG_PATH)
    rules = adapter.load_rules()
    fig_rules = [r for r in rules if r.rule_type == "figure_pipeline_gate"]
    assert len(fig_rules) == 1
    rule = fig_rules[0]
    assert rule.rule_id == "figure-pipeline-requires-specs"
    assert rule.condition["target_directory"] == "wave-5-visuals"
    assert rule.condition["required_artifact"] == "figure-specs.md"


def test_real_config_style_profile_rule_has_correct_structure():
    """figure-generation-requires-style rule has correct rule_id and condition."""
    adapter = JsonRuleAdapter(REAL_CONFIG_PATH)
    rules = adapter.load_rules()
    style_rules = [r for r in rules if r.rule_type == "style_profile_gate"]
    assert len(style_rules) == 1
    rule = style_rules[0]
    assert rule.rule_id == "figure-generation-requires-style"
    assert rule.condition["target_directory"] == "wave-5-visuals"
    assert rule.condition["required_artifact"] == "style-profile.yaml"


# ---------------------------------------------------------------------------
# 2. PDC gate: BLOCK on RED Tier 1/2, ALLOW when all GREEN
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "pdc_status, expected_decision",
    [
        pytest.param(
            {"section_a": {"tier_1": "RED", "tier_2": "GREEN"}},
            "BLOCK",
            id="red-tier1-blocks",
        ),
        pytest.param(
            {"section_a": {"tier_1": "GREEN", "tier_2": "RED"}},
            "BLOCK",
            id="red-tier2-blocks",
        ),
        pytest.param(
            {"section_a": {"tier_1": "GREEN", "tier_2": "GREEN"}},
            "ALLOW",
            id="all-green-allows",
        ),
        pytest.param(
            {},
            "ALLOW",
            id="no-pdc-status-allows",
        ),
    ],
)
def test_pdc_gate_evaluator_wiring(
    engine: EnforcementEngine,
    pdc_status: dict[str, Any],
    expected_decision: str,
) -> None:
    """Engine dispatches pdc_gate rule and evaluates PDC status correctly."""
    state = {
        "proposal_id": "test-001",
        "current_wave": 5,
        "pdc_status": pdc_status,
    }
    result = engine.evaluate(state, "wave_5_start")
    assert result.decision.value == expected_decision


# ---------------------------------------------------------------------------
# 3. Deadline blocking: BLOCK near deadline on non-essential wave, ALLOW otherwise
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "current_wave, days_until_deadline, expected_decision",
    [
        pytest.param(2, 2, "BLOCK", id="wave2-within-critical-blocks"),
        pytest.param(3, 1, "BLOCK", id="wave3-within-critical-blocks"),
        pytest.param(2, 10, "ALLOW", id="wave2-outside-critical-allows"),
        pytest.param(4, 2, "ALLOW", id="wave4-not-nonessential-allows"),
    ],
)
def test_deadline_blocking_evaluator_wiring(
    engine: EnforcementEngine,
    current_wave: int,
    days_until_deadline: int,
    expected_decision: str,
) -> None:
    """Engine dispatches deadline_blocking rule and evaluates proximity correctly."""
    deadline = (date.today() + timedelta(days=days_until_deadline)).isoformat()
    state = {
        "proposal_id": "test-001",
        "current_wave": current_wave,
        "topic": {"deadline": deadline},
        "go_no_go": "go",
        "strategy_brief": {"approved_at": "2026-01-01"},
        "research_summary": {"approved_at": "2026-01-01"},
        "outline": {"approved_at": "2026-01-01"},
    }
    result = engine.evaluate(state, f"wave_{current_wave}_start")
    assert result.decision.value == expected_decision


# ---------------------------------------------------------------------------
# 4. Submission immutability: BLOCK on submitted+immutable, ALLOW otherwise
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "submission, expected_decision",
    [
        pytest.param(
            {"status": "submitted", "immutable": True},
            "BLOCK",
            id="submitted-immutable-blocks",
        ),
        pytest.param(
            {"status": "submitted", "immutable": False},
            "ALLOW",
            id="submitted-not-immutable-allows",
        ),
        pytest.param(
            {"status": "draft"},
            "ALLOW",
            id="draft-allows",
        ),
        pytest.param(
            {},
            "ALLOW",
            id="no-submission-allows",
        ),
    ],
)
def test_submission_immutability_evaluator_wiring(
    engine: EnforcementEngine,
    submission: dict[str, Any],
    expected_decision: str,
) -> None:
    """Engine dispatches submission_immutability rule and evaluates state correctly."""
    state = {
        "proposal_id": "test-001",
        "current_wave": 0,
        "submission": submission,
    }
    result = engine.evaluate(state, "any_tool")
    assert result.decision.value == expected_decision


# ---------------------------------------------------------------------------
# 5. Corpus integrity: BLOCK on outcome change, ALLOW otherwise
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "learning, requested_change, expected_decision",
    [
        pytest.param(
            {"outcome": "win"},
            "loss",
            "BLOCK",
            id="change-existing-outcome-blocks",
        ),
        pytest.param(
            {"outcome": "win"},
            "win",
            "ALLOW",
            id="same-outcome-allows",
        ),
        pytest.param(
            {"outcome": None},
            "win",
            "ALLOW",
            id="no-existing-outcome-allows",
        ),
        pytest.param(
            {},
            "loss",
            "ALLOW",
            id="no-outcome-field-allows",
        ),
    ],
)
def test_corpus_integrity_evaluator_wiring(
    engine: EnforcementEngine,
    learning: dict[str, Any],
    requested_change: str | None,
    expected_decision: str,
) -> None:
    """Engine dispatches corpus_integrity rule and evaluates outcome tags correctly."""
    state: dict[str, Any] = {
        "proposal_id": "test-001",
        "current_wave": 0,
        "learning": learning,
    }
    if requested_change is not None:
        state["requested_outcome_change"] = requested_change
    result = engine.evaluate(state, "record_outcome")
    assert result.decision.value == expected_decision


# ---------------------------------------------------------------------------
# 8. Writing style gate rule structure
# ---------------------------------------------------------------------------


def test_real_config_writing_style_gate_rule_has_correct_structure():
    """drafting-requires-style-selection rule has correct rule_id and condition."""
    adapter = JsonRuleAdapter(REAL_CONFIG_PATH)
    rules = adapter.load_rules()
    wsg_rules = [r for r in rules if r.rule_type == "writing_style_gate"]
    assert len(wsg_rules) == 1
    rule = wsg_rules[0]
    assert rule.rule_id == "drafting-requires-style-selection"
    assert rule.condition["target_directory"] == "wave-4-drafting"
    assert rule.condition["required_global_artifact"] == "quality-preferences.json"
