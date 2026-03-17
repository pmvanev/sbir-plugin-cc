"""Acceptance test conftest -- fixtures for PES Enforcement Wiring BDD scenarios.

All acceptance tests invoke through the driving port only:
- EnforcementEngine.evaluate() (loaded with real JsonRuleAdapter + real pes-config.json)

No mocks at acceptance level. Real config, real rule loader, real evaluators.
The whole point is proving the wiring end-to-end.
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pytest


# ---------------------------------------------------------------------------
# PES Config Fixture -- Real pes-config.json with 4 new evaluator rules
# ---------------------------------------------------------------------------


@pytest.fixture()
def pes_config_path(tmp_path: Path) -> Path:
    """Write the real pes-config.json (with all 8 rules) to a temp directory.

    This matches what templates/pes-config.json will contain after delivery.
    Uses non_essential_waves [2, 3] per US-PEW-002 user story spec.
    """
    config = {
        "rules": [
            {
                "rule_id": "wave-1-requires-go",
                "description": "Wave 1 strategy work requires Go decision in Wave 0",
                "rule_type": "wave_ordering",
                "condition": {"requires_go_no_go": "go", "target_wave": 1},
                "message": "Wave 1 requires Go decision in Wave 0",
            },
            {
                "rule_id": "wave-2-requires-strategy",
                "description": "Wave 2 writing requires strategy brief approval",
                "rule_type": "wave_ordering",
                "condition": {"requires_strategy_approval": True, "target_wave": 2},
                "message": "Wave 2 requires strategy brief approval in Wave 1",
            },
            {
                "rule_id": "wave-3-requires-research",
                "description": "Wave 3 outline requires research review approval",
                "rule_type": "wave_ordering",
                "condition": {"requires_research_approval": True, "target_wave": 3},
                "message": "Wave 3 requires research review approval in Wave 2",
            },
            {
                "rule_id": "wave-4-requires-outline",
                "description": "Wave 4 drafting requires outline approval",
                "rule_type": "wave_ordering",
                "condition": {"requires_outline_approval": True, "target_wave": 4},
                "message": "Wave 4 requires outline approval in Wave 3",
            },
            {
                "rule_id": "wave-5-requires-pdc-green",
                "description": "Wave 5 requires all PDC items GREEN",
                "rule_type": "pdc_gate",
                "condition": {"requires_pdc_green": True, "target_wave": 5},
                "message": "Wave 5 requires all sections to have Tier 1+2 PDCs GREEN",
            },
            {
                "rule_id": "deadline-critical-blocking",
                "description": "Block non-essential waves near deadline",
                "rule_type": "deadline_blocking",
                "condition": {"critical_days": 3, "non_essential_waves": [2, 3]},
                "message": "Deadline approaching: non-essential waves blocked",
            },
            {
                "rule_id": "submission-immutability",
                "description": "Block all writes to submitted proposal artifacts",
                "rule_type": "submission_immutability",
                "condition": {"requires_immutable": True},
                "message": "Proposal is submitted. Artifacts are read-only.",
            },
            {
                "rule_id": "corpus-outcome-integrity",
                "description": "Win/loss tags are append-only",
                "rule_type": "corpus_integrity",
                "condition": {"append_only_tags": True},
                "message": "Win/loss tags are append-only and cannot be modified",
            },
        ],
        "enforcement": {
            "session_startup_check": True,
            "wave_ordering": "strict",
            "compliance_gate": True,
        },
        "deadlines": {"warning_days": 7, "critical_days": 3},
        "audit_log": {
            "enabled": True,
            "path": "./.sbir/audit/",
            "retention_days": 365,
        },
    }
    config_path = tmp_path / "pes-config.json"
    config_path.write_text(json.dumps(config, indent=2))
    return config_path


# ---------------------------------------------------------------------------
# Engine Fixtures -- Real JsonRuleAdapter + Real EnforcementEngine
# ---------------------------------------------------------------------------


@pytest.fixture()
def in_memory_audit_log():
    """In-memory audit logger that captures entries for assertion."""
    from pes.ports.audit_port import AuditLogger

    class InMemoryAuditLogger(AuditLogger):
        def __init__(self) -> None:
            self.entries: list[dict[str, Any]] = []

        def log(self, entry: dict[str, Any]) -> None:
            self.entries.append(entry)

    return InMemoryAuditLogger()


@pytest.fixture()
def enforcement_engine(pes_config_path, in_memory_audit_log):
    """EnforcementEngine wired with real JsonRuleAdapter and real config."""
    from pes.adapters.json_rule_adapter import JsonRuleAdapter
    from pes.domain.engine import EnforcementEngine

    rule_loader = JsonRuleAdapter(str(pes_config_path))
    return EnforcementEngine(rule_loader, in_memory_audit_log)


# ---------------------------------------------------------------------------
# Proposal State Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def base_proposal_state() -> dict[str, Any]:
    """Minimal valid proposal state for AF243-001."""
    return {
        "schema_version": "1.0.0",
        "proposal_id": "test-uuid-af243-001",
        "topic": {
            "id": "AF243-001",
            "agency": "Air Force",
            "title": "Compact Directed Energy for Maritime UAS Defense",
            "deadline": "2026-04-15",
            "phase": "I",
        },
        "current_wave": 0,
        "go_no_go": "pending",
    }


# ---------------------------------------------------------------------------
# Result Container
# ---------------------------------------------------------------------------


@pytest.fixture()
def enforcement_context() -> dict[str, Any]:
    """Mutable container to hold enforcement result and state across steps."""
    return {}
