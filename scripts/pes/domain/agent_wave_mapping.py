"""Agent-to-wave authorization rules.

Maps which SBIR agents are valid for which proposal waves.
Source: skills/orchestrator/wave-agent-mapping.md
"""

from __future__ import annotations

# Canonical agent-wave mapping: wave number -> list of authorized agent names
AGENT_WAVE_MAPPING: dict[int, list[str]] = {
    0: ["corpus-librarian", "solution-shaper"],
    1: ["compliance-sheriff", "tpoc-analyst", "strategist"],
    2: ["researcher", "strategist"],
    3: ["writer", "reviewer"],
    4: ["writer", "reviewer"],
    5: ["formatter", "writer"],
    6: ["formatter", "compliance-sheriff"],
    7: ["reviewer", "compliance-sheriff"],
    8: ["submission-agent"],
    9: ["debrief-analyst", "corpus-librarian"],
}

# All recognized agent names (union of all wave values)
ALL_KNOWN_AGENTS: frozenset[str] = frozenset(
    agent for agents in AGENT_WAVE_MAPPING.values() for agent in agents
)


def is_agent_recognized(agent_name: str) -> bool:
    """Check if the agent name is in the known agent registry."""
    return agent_name in ALL_KNOWN_AGENTS


def is_agent_authorized_for_wave(agent_name: str, wave: int) -> bool:
    """Check if the agent is authorized to work in the given wave."""
    authorized = AGENT_WAVE_MAPPING.get(wave, [])
    return agent_name in authorized
