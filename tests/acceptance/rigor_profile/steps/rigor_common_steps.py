"""Common step definitions shared across rigor profile feature files.

These steps handle the Given preconditions that appear in multiple features.
Organized by domain concept (rigor profile setup), not by feature file.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pytest_bdd import given, parsers, then


# ---------------------------------------------------------------------------
# Given: Proposal with rigor profile
# ---------------------------------------------------------------------------


@given(
    parsers.parse('Elena has an active proposal "{topic_id}" at "{profile}" rigor'),
    target_fixture="proposal_dir",
)
def elena_proposal_with_rigor(
    create_proposal_with_rigor, topic_id: str, profile: str
) -> Path:
    """Create Elena's proposal with specified rigor profile."""
    return create_proposal_with_rigor(topic_id, rigor_profile=profile)


@given(
    parsers.parse('Marcus has an active proposal "{topic_id}" at "{profile}" rigor'),
    target_fixture="proposal_dir",
)
def marcus_proposal_with_rigor(
    create_proposal_with_rigor, topic_id: str, profile: str
) -> Path:
    """Create Marcus's proposal with specified rigor profile."""
    return create_proposal_with_rigor(topic_id, rigor_profile=profile)


@given(
    parsers.parse(
        'Elena has an active proposal "{topic_id}" at "{profile}" rigor on wave {wave:d}'
    ),
    target_fixture="proposal_dir",
)
def elena_proposal_with_rigor_and_wave(
    create_proposal_with_rigor, topic_id: str, profile: str, wave: int
) -> Path:
    """Create Elena's proposal with specified rigor and wave number."""
    return create_proposal_with_rigor(
        topic_id, rigor_profile=profile, current_wave=wave
    )


@given(
    parsers.parse('Phil has a proposal "{topic_id}" with no rigor configuration'),
    target_fixture="proposal_dir",
)
def phil_proposal_without_rigor(create_proposal_with_rigor, topic_id: str) -> Path:
    """Create Phil's proposal without rigor-profile.json (pre-rigor proposal)."""
    return create_proposal_with_rigor(topic_id, include_rigor=False)


@given("no proposal is currently active", target_fixture="proposal_dir")
def no_active_proposal(workspace_root: Path) -> Path:
    """Ensure no active proposal pointer exists. Return workspace root."""
    sbir_dir = workspace_root / ".sbir"
    sbir_dir.mkdir(exist_ok=True)
    active_file = sbir_dir / "active-proposal"
    if active_file.exists():
        active_file.unlink()
    return workspace_root


@given(
    "the plugin provides four rigor profiles: lean, standard, thorough, exhaustive"
)
def plugin_provides_profiles():
    """Declarative context: profiles are defined in plugin config.

    The actual profile definitions are loaded from config/rigor-profiles.json
    by the rigor service. This step documents the precondition.
    """
    pass


# ---------------------------------------------------------------------------
# Then: Shared assertions used across multiple feature files
# ---------------------------------------------------------------------------


@then(parsers.parse('the active rigor profile is "{profile}"'))
def rigor_profile_is(proposal_dir: Path, profile: str):
    """Verify the persisted rigor profile matches expected value."""
    rigor_path = proposal_dir / "rigor-profile.json"
    assert rigor_path.exists(), f"rigor-profile.json not found at {rigor_path}"
    data = json.loads(rigor_path.read_text())
    assert data["profile"] == profile, (
        f"Expected profile '{profile}', got '{data['profile']}'"
    )
