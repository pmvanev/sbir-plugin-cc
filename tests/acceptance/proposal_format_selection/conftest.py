"""Acceptance test conftest -- fixtures for Proposal Format Selection BDD scenarios.

All acceptance tests invoke through driving ports only:
- FormatConfigService (format validation, rework risk, state update)
- ProposalCreationService (initial state creation with output_format)
- StateReader / StateWriter (state persistence)

External dependencies (file system) use tmp_path-based adapters.
Domain logic uses real production code.
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
    return tmp_path


@pytest.fixture()
def state_file(proposal_dir: Path) -> Path:
    """Path to proposal-state.json within the proposal directory."""
    return proposal_dir / ".sbir" / "proposal-state.json"


@pytest.fixture()
def base_proposal_state() -> dict[str, Any]:
    """Minimal valid proposal state for AF243-001 with output_format."""
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
        "output_format": "docx",
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
            "path": None,
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
def write_state(state_file: Path):
    """Helper to write a state dict to the state file."""

    def _write(state: dict[str, Any]) -> None:
        state_file.write_text(json.dumps(state, indent=2))

    return _write


@pytest.fixture()
def read_state(state_file: Path):
    """Helper to read state from the state file."""

    def _read() -> dict[str, Any]:
        return json.loads(state_file.read_text())

    return _read


# ---------------------------------------------------------------------------
# Result Containers
# ---------------------------------------------------------------------------


@pytest.fixture()
def format_result() -> dict[str, Any]:
    """Mutable container to hold format operation results across steps."""
    return {}


@pytest.fixture()
def proposal_context() -> dict[str, Any]:
    """Mutable container to hold proposal state and service context."""
    return {}
