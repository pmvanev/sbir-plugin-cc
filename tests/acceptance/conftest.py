"""Acceptance test conftest -- fixtures for BDD acceptance scenarios.

All acceptance tests invoke through driving ports only:
- EnforcementEngine (PES rule evaluation)
- ClaudeCodeHookAdapter (hook event translation)
- StateReader (proposal state access)

External dependencies (Claude Code LLM, file system for corpus search)
are replaced with in-memory fakes. PES and state management use real
production code.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Proposal State Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def proposal_dir(tmp_path: Path) -> Path:
    """Fresh temporary directory simulating a user's proposal project."""
    sbir_dir = tmp_path / ".sbir"
    sbir_dir.mkdir()
    (sbir_dir / "audit").mkdir()
    # Wave 1 artifacts
    (tmp_path / "artifacts" / "wave-1-strategy").mkdir(parents=True)
    # Wave 2 artifacts (C2)
    (tmp_path / "artifacts" / "wave-2-research").mkdir(parents=True)
    # Wave 3 artifacts (C2)
    (tmp_path / "artifacts" / "wave-3-outline").mkdir(parents=True)
    # Wave 4 artifacts (C2)
    (tmp_path / "artifacts" / "wave-4-drafting" / "sections").mkdir(parents=True)
    (tmp_path / "artifacts" / "wave-4-drafting" / "reviews").mkdir(parents=True)
    return tmp_path


@pytest.fixture()
def state_file(proposal_dir: Path) -> Path:
    """Path to proposal-state.json within the proposal directory."""
    return proposal_dir / ".sbir" / "proposal-state.json"


@pytest.fixture()
def sample_state() -> dict[str, Any]:
    """Minimal valid proposal state for AF243-001."""
    return {
        "schema_version": "1.0.0",
        "proposal_id": "test-uuid-af243-001",
        "topic": {
            "id": "AF243-001",
            "agency": "Air Force",
            "title": "Compact Directed Energy for Maritime UAS Defense",
            "solicitation_url": None,
            "solicitation_file": "./solicitations/AF243-001.pdf",
            "deadline": "2026-04-15",
            "phase": "I",
        },
        "current_wave": 0,
        "go_no_go": "pending",
        "waves": {
            "0": {"status": "active", "completed_at": None},
            "1": {"status": "not_started", "completed_at": None},
        },
        "corpus": {
            "directories_ingested": [],
            "document_count": 0,
            "file_hashes": {},
        },
        "compliance_matrix": {
            "path": "./artifacts/wave-1-strategy/compliance-matrix.md",
            "item_count": 0,
            "generated_at": None,
        },
        "tpoc": {
            "status": "not_started",
            "questions_path": None,
            "qa_log_path": None,
            "questions_generated_at": None,
            "answers_ingested_at": None,
        },
        "strategy_brief": {
            "path": None,
            "status": "not_started",
            "approved_at": None,
        },
        "fit_scoring": {
            "subject_matter": None,
            "past_performance": None,
            "certifications": None,
            "recommendation": None,
        },
        "created_at": "2026-03-01T10:00:00Z",
        "updated_at": "2026-03-01T10:00:00Z",
    }


@pytest.fixture()
def state_with_go(sample_state: dict[str, Any]) -> dict[str, Any]:
    """Proposal state with Go decision approved, Wave 1 active."""
    state = sample_state.copy()
    state["go_no_go"] = "go"
    state["current_wave"] = 1
    state["waves"] = {
        "0": {"status": "completed", "completed_at": "2026-03-02T10:00:00Z"},
        "1": {"status": "active", "completed_at": None},
    }
    return state


@pytest.fixture()
def write_state(state_file: Path):
    """Helper to write a state dict to the state file."""

    def _write(state: dict[str, Any]) -> None:
        state_file.write_text(json.dumps(state, indent=2))

    return _write


# ---------------------------------------------------------------------------
# PES Configuration Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def pes_config(proposal_dir: Path) -> Path:
    """Default PES configuration file."""
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
                "description": "Wave 2 writing requires strategy brief approval in Wave 1",
                "rule_type": "wave_ordering",
                "condition": {"requires_strategy_approval": True, "target_wave": 2},
                "message": "Wave 2 requires strategy brief approval in Wave 1",
            },
            {
                "rule_id": "wave-3-requires-research",
                "description": "Wave 3 outline requires research review approval in Wave 2",
                "rule_type": "wave_ordering",
                "condition": {"requires_research_approval": True, "target_wave": 3},
                "message": "Wave 3 requires research review approval in Wave 2",
            },
            {
                "rule_id": "wave-4-requires-outline",
                "description": "Wave 4 drafting requires outline approval in Wave 3",
                "rule_type": "wave_ordering",
                "condition": {"requires_outline_approval": True, "target_wave": 4},
                "message": "Wave 4 requires outline approval in Wave 3",
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
        "overrides": {
            "waiver_requires_reason": True,
            "waiver_marker": "<!-- PES-ENFORCEMENT: exempt -->",
        },
    }
    config_path = proposal_dir / ".sbir" / "pes-config.json"
    config_path.write_text(json.dumps(config, indent=2))
    return config_path


# ---------------------------------------------------------------------------
# PES Enforcement Fixtures
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
def rule_loader_from_config(pes_config: Path):
    """RuleLoader that loads from the test PES config file."""
    from pes.adapters.json_rule_adapter import JsonRuleAdapter

    return JsonRuleAdapter(str(pes_config))


@pytest.fixture()
def enforcement_engine(rule_loader_from_config, in_memory_audit_log):
    """EnforcementEngine wired with test adapters."""
    from pes.domain.engine import EnforcementEngine

    return EnforcementEngine(rule_loader_from_config, in_memory_audit_log)


# ---------------------------------------------------------------------------
# Compliance Matrix Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def compliance_matrix_path(proposal_dir: Path) -> Path:
    """Path to compliance matrix artifact."""
    return proposal_dir / "artifacts" / "wave-1-strategy" / "compliance-matrix.md"
