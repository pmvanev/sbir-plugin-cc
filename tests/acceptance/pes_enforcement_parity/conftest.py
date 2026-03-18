"""Acceptance test conftest -- fixtures for PES Enforcement Parity BDD scenarios.

All acceptance tests invoke through driving ports only:
- EnforcementEngine (session start, evaluate, post-action, agent lifecycle)
- process_hook_event (hook adapter translation)

No mocks at acceptance level. Real config, real rule loader, real evaluators.
AuditLogger uses a file-based adapter for active audit logging scenarios
and an in-memory adapter for assertion inspection.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest


# ---------------------------------------------------------------------------
# PES Config Fixture -- Real pes-config.json with parity extensions
# ---------------------------------------------------------------------------


@pytest.fixture()
def pes_config_path(tmp_path: Path) -> Path:
    """Write the real pes-config.json with parity features to temp directory.

    Includes audit_log configuration with retention_days and size_limit,
    agent_wave_mapping for dispatch verification, and post_action_validation.
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
                "rule_id": "wave-5-requires-pdc-green",
                "description": "Wave 5 requires all PDC items GREEN",
                "rule_type": "pdc_gate",
                "condition": {"requires_pdc_green": True, "target_wave": 5},
                "message": "Wave 5 requires all sections to have Tier 1+2 PDCs GREEN",
            },
            {
                "rule_id": "submission-immutability",
                "description": "Block all writes to submitted proposal artifacts",
                "rule_type": "submission_immutability",
                "condition": {"requires_immutable": True},
                "message": "Proposal is submitted. Artifacts are read-only.",
            },
        ],
        "enforcement": {
            "session_startup_check": True,
            "wave_ordering": "strict",
            "post_action_validation": True,
            "agent_lifecycle_tracking": True,
        },
        "deadlines": {"warning_days": 7, "critical_days": 3},
        "audit_log": {
            "enabled": True,
            "path": "./.sbir/audit/",
            "retention_days": 365,
            "max_file_size_bytes": 10485760,
        },
        "agent_wave_mapping": {
            "0": ["corpus-librarian", "solution-shaper"],
            "1": ["compliance-sheriff", "tpoc-analyst", "strategist"],
            "2": ["researcher", "strategist"],
            "3": ["writer", "reviewer"],
            "4": ["writer", "reviewer"],
            "5": ["formatter", "writer"],
            "6": ["formatter", "compliance-sheriff"],
            "7": ["reviewer", "compliance-sheriff"],
            "8": ["submission-agent"],
            "9": ["debrief-analyst", "corpus-librarian"],
        },
    }
    config_path = tmp_path / "pes-config.json"
    config_path.write_text(json.dumps(config, indent=2))
    return config_path


# ---------------------------------------------------------------------------
# Proposal Directory Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def proposal_dir(tmp_path: Path) -> Path:
    """Fresh temporary directory simulating a user's proposal project."""
    sbir_dir = tmp_path / ".sbir"
    sbir_dir.mkdir()
    (sbir_dir / "audit").mkdir()
    # Wave artifact directories
    for wave_num, wave_name in [
        (1, "strategy"), (2, "research"), (3, "outline"),
        (4, "drafting"), (5, "visuals"), (6, "format"),
        (7, "review"), (8, "submission"), (9, "learning"),
    ]:
        (tmp_path / "artifacts" / f"wave-{wave_num}-{wave_name}").mkdir(parents=True)
    # Drafting subdirs
    (tmp_path / "artifacts" / "wave-4-drafting" / "sections").mkdir(exist_ok=True)
    return tmp_path


# ---------------------------------------------------------------------------
# Engine Fixtures
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
def enforcement_engine(pes_config_path, in_memory_audit_log, proposal_dir):
    """EnforcementEngine wired with real JsonRuleAdapter, in-memory + file audit.

    Uses a tee logger that writes to both in-memory (for assertions) and
    file-based adapter (for disk persistence scenarios).
    """
    from pes.adapters.file_audit_adapter import FileAuditAdapter
    from pes.adapters.json_rule_adapter import JsonRuleAdapter
    from pes.domain.engine import EnforcementEngine
    from pes.ports.audit_port import AuditLogger

    audit_dir = str(proposal_dir / ".sbir" / "audit")
    file_logger = FileAuditAdapter(audit_dir)

    class _TeeAuditLogger(AuditLogger):
        """Writes to both in-memory and file loggers."""

        def __init__(self, mem: AuditLogger, file: AuditLogger) -> None:
            self._mem = mem
            self._file = file

        def log(self, entry: dict[str, Any]) -> None:
            self._mem.log(entry)
            self._file.log(entry)

    tee_logger = _TeeAuditLogger(in_memory_audit_log, file_logger)
    rule_loader = JsonRuleAdapter(str(pes_config_path))
    return EnforcementEngine(rule_loader, tee_logger)


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


# ---------------------------------------------------------------------------
# Crash Signal Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def crash_signal_file(proposal_dir: Path) -> Path:
    """Create a crash signal file simulating an abnormal session end."""
    signal = proposal_dir / ".sbir" / "session-crash.signal"
    signal.write_text(json.dumps({
        "session_id": "prev-session-001",
        "timestamp": "2026-03-17T14:30:00Z",
        "reason": "unexpected_termination",
    }))
    return signal


# ---------------------------------------------------------------------------
# Audit Log Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def aged_audit_entries(proposal_dir: Path) -> Path:
    """Create an audit log file with entries older than retention window."""
    audit_dir = proposal_dir / ".sbir" / "audit"
    audit_file = audit_dir / "enforcement.log"
    old_timestamp = (datetime.now(UTC) - timedelta(days=400)).isoformat()
    recent_timestamp = datetime.now(UTC).isoformat()
    entries = [
        json.dumps({"timestamp": old_timestamp, "event": "evaluate", "decision": "allow"}),
        json.dumps({"timestamp": recent_timestamp, "event": "evaluate", "decision": "block"}),
    ]
    audit_file.write_text("\n".join(entries) + "\n")
    return audit_file
