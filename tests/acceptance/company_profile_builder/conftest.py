"""Acceptance test conftest -- fixtures for Company Profile Builder BDD scenarios.

All acceptance tests invoke through driving ports only:
- ProfileValidationService (schema validation)
- ProfilePort (profile read/write/exists/metadata)

External dependencies (file system) are replaced with in-memory fakes
or tmp_path-based adapters. Validation uses real production code.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest


# ---------------------------------------------------------------------------
# Profile Directory Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def profile_dir(tmp_path: Path) -> Path:
    """Fresh temporary directory simulating ~/.sbir/ for profile storage."""
    sbir_dir = tmp_path / ".sbir"
    sbir_dir.mkdir()
    return sbir_dir


@pytest.fixture()
def profile_path(profile_dir: Path) -> Path:
    """Path to company-profile.json within the profile directory."""
    return profile_dir / "company-profile.json"


# ---------------------------------------------------------------------------
# Sample Profile Data Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def valid_profile_data() -> dict[str, Any]:
    """Complete valid company profile for Radiant Defense Systems."""
    return {
        "company_name": "Radiant Defense Systems, LLC",
        "capabilities": [
            "directed energy",
            "RF systems",
            "power electronics",
            "thermal management",
            "embedded firmware",
        ],
        "certifications": {
            "sam_gov": {
                "active": True,
                "cage_code": "7X2K9",
                "uei": "DKJF84NXLE73",
            },
            "socioeconomic": [],
            "security_clearance": "secret",
            "itar_registered": True,
        },
        "employee_count": 23,
        "key_personnel": [
            {
                "name": "Rafael Medina",
                "role": "CEO / Chief Engineer",
                "expertise": ["directed energy", "systems engineering"],
            },
            {
                "name": "Dr. Lena Park",
                "role": "VP Engineering",
                "expertise": ["RF systems", "power electronics"],
            },
        ],
        "past_performance": [
            {
                "agency": "Air Force",
                "topic_area": "Compact Directed Energy",
                "outcome": "awarded",
            },
            {
                "agency": "DARPA",
                "topic_area": "Advanced RF Systems",
                "outcome": "completed",
            },
        ],
        "research_institution_partners": [
            "Georgia Tech Research Institute",
        ],
    }


@pytest.fixture()
def minimal_valid_profile() -> dict[str, Any]:
    """Minimal profile that passes validation (fewest entries)."""
    return {
        "company_name": "Test Corp",
        "capabilities": ["testing"],
        "certifications": {
            "sam_gov": {
                "active": False,
            },
            "socioeconomic": [],
            "security_clearance": "none",
            "itar_registered": False,
        },
        "employee_count": 1,
        "key_personnel": [],
        "past_performance": [],
        "research_institution_partners": [],
    }


# ---------------------------------------------------------------------------
# Profile Builder Helpers
# ---------------------------------------------------------------------------


def build_profile_from_table(
    base: dict[str, Any] | None = None,
    **overrides: Any,
) -> dict[str, Any]:
    """Build a profile dict with specific overrides for test scenarios."""
    profile: dict[str, Any] = base.copy() if base else {
        "company_name": "Test Company",
        "capabilities": ["testing"],
        "certifications": {
            "sam_gov": {"active": True, "cage_code": "ABCD5", "uei": "TEST12345678"},
            "socioeconomic": [],
            "security_clearance": "none",
            "itar_registered": False,
        },
        "employee_count": 10,
        "key_personnel": [],
        "past_performance": [],
        "research_institution_partners": [],
    }

    for key, value in overrides.items():
        if key == "cage_code":
            profile["certifications"]["sam_gov"]["cage_code"] = value
        elif key == "uei":
            profile["certifications"]["sam_gov"]["uei"] = value
        elif key == "sam_gov_active":
            profile["certifications"]["sam_gov"]["active"] = value
        elif key == "clearance":
            profile["certifications"]["security_clearance"] = value
        elif key == "socioeconomic":
            profile["certifications"]["socioeconomic"] = value
        elif key == "itar_registered":
            profile["certifications"]["itar_registered"] = value
        elif key in profile:
            profile[key] = value

    return profile


@pytest.fixture()
def write_profile(profile_path: Path):
    """Helper to write a profile dict to the profile file."""

    def _write(profile: dict[str, Any]) -> None:
        profile_path.write_text(json.dumps(profile, indent=2))

    return _write


# ---------------------------------------------------------------------------
# Result Containers
# ---------------------------------------------------------------------------


@pytest.fixture()
def validation_result() -> dict[str, Any]:
    """Mutable container to hold validation results across when/then steps."""
    return {}


@pytest.fixture()
def profile_context() -> dict[str, Any]:
    """Mutable container to hold profile draft and operation results."""
    return {}
