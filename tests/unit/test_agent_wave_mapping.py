"""Targeted unit tests for agent_wave_mapping domain module.

Tests domain functions directly for mutation coverage.
These complement the EnforcementEngine driving-port tests by catching
fine-grained mutations in boolean logic and mapping lookups.
"""

from __future__ import annotations

import pytest

from pes.domain.agent_wave_mapping import (
    AGENT_WAVE_MAPPING,
    ALL_KNOWN_AGENTS,
    is_agent_authorized_for_wave,
    is_agent_recognized,
)


# --- is_agent_recognized: every known agent returns True ---


@pytest.mark.parametrize("agent_name", sorted(ALL_KNOWN_AGENTS))
def test_known_agent_is_recognized(agent_name: str) -> None:
    assert is_agent_recognized(agent_name) is True


@pytest.mark.parametrize("agent_name", [
    "unknown-agent",
    "nonexistent",
    "",
    "Writer",  # case-sensitive: capital W
    "RESEARCHER",
])
def test_unknown_agent_is_not_recognized(agent_name: str) -> None:
    assert is_agent_recognized(agent_name) is False


# --- is_agent_authorized_for_wave: correct wave mappings ---


@pytest.mark.parametrize("agent_name,wave", [
    (agent, wave)
    for wave, agents in AGENT_WAVE_MAPPING.items()
    for agent in agents
])
def test_agent_authorized_for_mapped_wave(agent_name: str, wave: int) -> None:
    assert is_agent_authorized_for_wave(agent_name, wave) is True


@pytest.mark.parametrize("agent_name,wave", [
    ("corpus-librarian", 1),   # corpus-librarian is wave 0 and 9, not 1
    ("corpus-librarian", 3),
    ("writer", 0),             # writer is wave 3/4/5, not 0
    ("writer", 1),
    ("writer", 2),
    ("submission-agent", 0),   # submission-agent is wave 8 only
    ("submission-agent", 7),
    ("strategist", 3),         # strategist is wave 1/2, not 3
    ("reviewer", 0),           # reviewer is wave 3/4/7, not 0
    ("reviewer", 2),
])
def test_agent_not_authorized_for_unmapped_wave(agent_name: str, wave: int) -> None:
    assert is_agent_authorized_for_wave(agent_name, wave) is False


def test_unknown_agent_not_authorized_for_any_wave() -> None:
    for wave in range(10):
        assert is_agent_authorized_for_wave("unknown-agent", wave) is False


def test_invalid_wave_number_returns_false() -> None:
    assert is_agent_authorized_for_wave("writer", -1) is False
    assert is_agent_authorized_for_wave("writer", 99) is False


# --- ALL_KNOWN_AGENTS consistency ---


def test_all_known_agents_matches_mapping_values() -> None:
    expected = set()
    for agents in AGENT_WAVE_MAPPING.values():
        expected.update(agents)
    assert ALL_KNOWN_AGENTS == frozenset(expected)
