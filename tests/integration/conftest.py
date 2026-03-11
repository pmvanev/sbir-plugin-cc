"""Integration test fixtures -- state builder, in-memory port stubs.

Provides reusable infrastructure for cross-wave integration tests:
- build_state(): produces valid proposal state for any wave 0-9
- InMemoryRuleLoader: stub returning configurable enforcement rules
- InMemoryAuditLogger: stub capturing audit entries for assertion
- InMemoryStateReader/Writer: stub for state persistence

All stubs implement port interfaces at hexagonal boundaries.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest

from pes.domain.rules import EnforcementRule
from pes.domain.state import SCHEMA_VERSION
from pes.domain.status_service import WAVE_NAMES
from pes.ports.audit_port import AuditLogger
from pes.ports.rule_port import RuleLoader
from pes.ports.state_port import StateReader, StateWriter


# ---------------------------------------------------------------------------
# State builder
# ---------------------------------------------------------------------------

def build_state(
    *,
    current_wave: int = 0,
    proposal_id: str = "test-proposal-001",
    go_no_go: str | None = None,
    deadline: str = "2026-06-15",
    overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a valid proposal state dict for the given wave.

    Produces a state that passes schema validation with all required fields.
    Waves before current_wave are marked completed; current_wave is active;
    waves after are not_started.

    Args:
        current_wave: Wave number 0-9 to set as active.
        proposal_id: Proposal identifier.
        go_no_go: Go/No-Go decision. Defaults to "go" if wave >= 1, else "pending".
        deadline: Submission deadline date string.
        overrides: Additional fields to merge into state (deep merge on top-level keys).
    """
    if go_no_go is None:
        go_no_go = "go" if current_wave >= 1 else "pending"

    now = datetime.now(UTC).isoformat()

    waves: dict[str, dict[str, Any]] = {}
    for w in range(10):
        if w < current_wave:
            waves[str(w)] = {
                "status": "completed",
                "completed_at": now,
            }
        elif w == current_wave:
            waves[str(w)] = {
                "status": "active",
                "completed_at": None,
            }
        else:
            waves[str(w)] = {
                "status": "not_started",
                "completed_at": None,
            }

    state: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "proposal_id": proposal_id,
        "topic": {
            "id": "AF243-001",
            "agency": "Air Force",
            "title": "Compact Directed Energy for Maritime UAS Defense",
            "solicitation_url": None,
            "solicitation_file": None,
            "deadline": deadline,
            "phase": "I",
        },
        "current_wave": current_wave,
        "go_no_go": go_no_go,
        "waves": waves,
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
        "research_summary": {"findings": []},
        "discrimination_table": {"items": []},
        "outline": {
            "path": None,
            "status": "not_started",
            "approved_at": None,
        },
        "volumes": {
            "technical": {
                "status": "not_started",
                "current_draft": None,
                "review_comments": [],
                "iterations": 0,
            },
            "management": {
                "status": "not_started",
                "current_draft": None,
                "review_comments": [],
                "iterations": 0,
            },
            "cost": {
                "status": "not_started",
                "current_draft": None,
                "review_comments": [],
                "iterations": 0,
            },
        },
        "open_review_items": [],
        "created_at": now,
        "updated_at": now,
    }

    # Apply overrides for prerequisite gates (e.g., approvals for later waves)
    if current_wave >= 1:
        state["strategy_brief"]["status"] = "approved"
        state["strategy_brief"]["approved_at"] = now
    if current_wave >= 2:
        state["research_summary"]["approved_at"] = now
    if current_wave >= 3:
        state["outline"]["status"] = "approved"
        state["outline"]["approved_at"] = now
    if current_wave >= 8:
        state["final_review"] = {"signed_off": True, "signed_off_at": now}

    if overrides:
        for key, value in overrides.items():
            if isinstance(value, dict) and isinstance(state.get(key), dict):
                state[key].update(value)
            else:
                state[key] = value

    return state


# ---------------------------------------------------------------------------
# In-memory port stubs
# ---------------------------------------------------------------------------


class InMemoryRuleLoader(RuleLoader):
    """In-memory rule loader returning configurable enforcement rules.

    Supports all subsequent integration test steps: wave transitions,
    prerequisite gates, error paths.
    """

    def __init__(self, rules: list[EnforcementRule] | None = None) -> None:
        self._rules = rules or []

    def load_rules(self) -> list[EnforcementRule]:
        return list(self._rules)

    def set_rules(self, rules: list[EnforcementRule]) -> None:
        """Replace loaded rules (useful for multi-step scenarios)."""
        self._rules = rules


class InMemoryAuditLogger(AuditLogger):
    """In-memory audit logger capturing entries for assertion.

    Each entry contains timestamp, event, decision, and proposal_id fields
    as written by the EnforcementEngine.
    """

    def __init__(self) -> None:
        self.entries: list[dict[str, Any]] = []

    def log(self, entry: dict[str, Any]) -> None:
        self.entries.append(entry)

    def clear(self) -> None:
        """Reset captured entries between test scenarios."""
        self.entries.clear()

    def find_by_event(self, event: str) -> list[dict[str, Any]]:
        """Filter entries by event type (convenience for multi-step assertions)."""
        return [e for e in self.entries if e.get("event") == event]


class InMemoryStateReader(StateReader):
    """In-memory state reader for integration tests."""

    def __init__(self, state: dict[str, Any] | None = None) -> None:
        self._state = state

    def load(self) -> dict[str, Any]:
        if self._state is None:
            from pes.domain.state import StateNotFoundError
            raise StateNotFoundError("No proposal state")
        return dict(self._state)

    def exists(self) -> bool:
        return self._state is not None

    def set_state(self, state: dict[str, Any]) -> None:
        """Update state for multi-step scenarios."""
        self._state = state


class InMemoryStateWriter(StateWriter):
    """In-memory state writer capturing saved states."""

    def __init__(self) -> None:
        self.saved_states: list[dict[str, Any]] = []

    def save(self, state: dict[str, Any]) -> None:
        self.saved_states.append(state)

    @property
    def last_saved(self) -> dict[str, Any] | None:
        return self.saved_states[-1] if self.saved_states else None


# ---------------------------------------------------------------------------
# Pytest fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def audit_logger() -> InMemoryAuditLogger:
    """Fresh in-memory audit logger."""
    return InMemoryAuditLogger()


@pytest.fixture()
def rule_loader() -> InMemoryRuleLoader:
    """Fresh in-memory rule loader with no rules."""
    return InMemoryRuleLoader()


@pytest.fixture()
def state_reader() -> InMemoryStateReader:
    """Fresh in-memory state reader with no state."""
    return InMemoryStateReader()


@pytest.fixture()
def state_writer() -> InMemoryStateWriter:
    """Fresh in-memory state writer."""
    return InMemoryStateWriter()
