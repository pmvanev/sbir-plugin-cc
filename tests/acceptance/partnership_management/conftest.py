"""Acceptance test conftest -- fixtures for Partnership Management BDD scenarios.

All acceptance tests invoke through driving ports only:
- PartnerProfileValidationService (partner schema validation)
- TopicScoringService (partnership-aware scoring)
- PartnerDesignationService (proposal state partner field)
- PartnerScreeningService (readiness assessment)
- CombinedCapabilityService (overlap/unique analysis)

External dependencies (file system) are replaced with tmp_path-based
adapters. Validation and scoring use real production code.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest


# ---------------------------------------------------------------------------
# Directory Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def sbir_dir(tmp_path: Path) -> Path:
    """Fresh temporary directory simulating ~/.sbir/ for partner profiles."""
    sbir_dir = tmp_path / ".sbir"
    sbir_dir.mkdir()
    return sbir_dir


@pytest.fixture()
def partners_dir(sbir_dir: Path) -> Path:
    """Directory for partner profile storage (~/.sbir/partners/)."""
    partners = sbir_dir / "partners"
    partners.mkdir()
    return partners


@pytest.fixture()
def screenings_dir(tmp_path: Path) -> Path:
    """Directory for screening results (.sbir/partner-screenings/)."""
    project_sbir = tmp_path / "project" / ".sbir" / "partner-screenings"
    project_sbir.mkdir(parents=True)
    return project_sbir


@pytest.fixture()
def proposal_state_path(tmp_path: Path) -> Path:
    """Path to proposal-state.json for partner designation tests."""
    project_sbir = tmp_path / "project" / ".sbir"
    project_sbir.mkdir(parents=True, exist_ok=True)
    return project_sbir / "proposal-state.json"


# ---------------------------------------------------------------------------
# Company Profile Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def company_profile() -> dict[str, Any]:
    """Company profile for Acme Defense (Phil's company)."""
    return {
        "company_name": "Acme Defense Systems, LLC",
        "capabilities": [
            "directed energy",
            "RF engineering",
            "machine learning",
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
                "name": "Phil Santos",
                "role": "CEO / Chief Engineer",
                "expertise": ["directed energy", "systems engineering"],
            },
        ],
        "past_performance": [
            {
                "agency": "Air Force",
                "topic_area": "Compact Directed Energy",
                "outcome": "awarded",
            },
        ],
        "research_institution_partners": [],
    }


# ---------------------------------------------------------------------------
# Partner Profile Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def cu_boulder_profile() -> dict[str, Any]:
    """Complete partner profile for CU Boulder."""
    return {
        "partner_name": "CU Boulder",
        "partner_slug": "cu-boulder",
        "partner_type": "university",
        "capabilities": [
            "autonomous navigation",
            "underwater acoustics",
            "sensor fusion",
        ],
        "key_personnel": [
            {
                "name": "Dr. Sarah Kim",
                "role": "Co-PI",
                "expertise": [
                    "autonomous navigation",
                    "underwater acoustics",
                ],
            },
            {
                "name": "Dr. James Rivera",
                "role": "Researcher",
                "expertise": [
                    "underwater robotics",
                    "acoustic sensing",
                ],
            },
        ],
        "facilities": [
            {
                "name": "underwater acoustics lab",
                "description": "Full anechoic water tank facility",
            },
            {
                "name": "GPU compute cluster",
                "description": "128-node GPU cluster for ML training",
            },
        ],
        "past_collaborations": [
            {
                "agency": "Navy",
                "topic_area": "Underwater Navigation",
                "outcome": "WIN",
                "year": 2024,
            },
        ],
        "sttr_eligibility": {
            "qualifies": True,
            "minimum_effort_capable": True,
            "notes": "",
        },
        "created_at": "2026-03-19T10:00:00Z",
        "updated_at": "2026-03-19T10:00:00Z",
    }


@pytest.fixture()
def swri_profile() -> dict[str, Any]:
    """Complete partner profile for SWRI."""
    return {
        "partner_name": "Southwest Research Institute",
        "partner_slug": "swri",
        "partner_type": "federally_funded_rdc",
        "capabilities": [
            "intelligent systems",
            "autonomy",
            "sensor fusion",
            "applied ML",
        ],
        "key_personnel": [
            {
                "name": "Dr. Rebecca Chen",
                "role": "Co-PI",
                "expertise": [
                    "autonomous navigation",
                    "sensor fusion",
                ],
            },
        ],
        "facilities": [
            {
                "name": "6-DOF motion sim lab",
                "description": "Full motion simulation facility",
            },
            {
                "name": "RF anechoic chamber",
                "description": "Shielded RF testing environment",
            },
        ],
        "past_collaborations": [
            {
                "agency": "Navy",
                "topic_area": "Autonomous UUV",
                "outcome": "WIN",
                "year": 2025,
            },
        ],
        "sttr_eligibility": {
            "qualifies": True,
            "minimum_effort_capable": True,
            "notes": "",
        },
        "created_at": "2026-03-19T10:00:00Z",
        "updated_at": "2026-03-19T10:00:00Z",
    }


@pytest.fixture()
def ndsu_profile() -> dict[str, Any]:
    """Minimal partner profile for NDSU."""
    return {
        "partner_name": "NDSU",
        "partner_slug": "ndsu",
        "partner_type": "university",
        "capabilities": [
            "precision agriculture",
            "sensor networks",
        ],
        "key_personnel": [
            {
                "name": "Dr. Alan Park",
                "role": "Researcher",
                "expertise": ["sensor networks"],
            },
        ],
        "facilities": [],
        "past_collaborations": [],
        "sttr_eligibility": {
            "qualifies": True,
            "minimum_effort_capable": True,
            "notes": "",
        },
        "created_at": "2026-03-19T10:00:00Z",
        "updated_at": "2026-03-19T10:00:00Z",
    }


def make_partner_profile(
    partner_name: str = "Test Partner",
    partner_type: str = "university",
    capabilities: list[str] | None = None,
    **overrides: Any,
) -> dict[str, Any]:
    """Build a partner profile dict with specific overrides for test scenarios."""
    slug = partner_name.lower().replace(" ", "-")
    profile: dict[str, Any] = {
        "partner_name": partner_name,
        "partner_slug": slug,
        "partner_type": partner_type,
        "capabilities": capabilities or ["testing"],
        "key_personnel": [],
        "facilities": [],
        "past_collaborations": [],
        "sttr_eligibility": {
            "qualifies": True,
            "minimum_effort_capable": True,
            "notes": "",
        },
        "created_at": "2026-03-19T10:00:00Z",
        "updated_at": "2026-03-19T10:00:00Z",
    }
    profile.update(overrides)
    return profile


# ---------------------------------------------------------------------------
# Topic Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def sttr_topic_n244() -> dict[str, Any]:
    """STTR topic N244-012: Autonomous UUV Navigation."""
    return {
        "topic_id": "N244-012",
        "topic_code": "N244-012",
        "title": "Autonomous UUV Navigation and Sensing",
        "status": "Open",
        "program": "STTR",
        "component": "USN",
        "agency": "Navy",
        "solicitation_number": "24.4",
        "phase": "I",
        "deadline": "2026-06-15",
        "requires_clearance": "none",
    }


@pytest.fixture()
def sbir_topic_af243() -> dict[str, Any]:
    """SBIR topic AF243-001: Compact Directed Energy."""
    return {
        "topic_id": "AF243-001",
        "topic_code": "AF243-001",
        "title": "Compact Directed Energy for C-UAS",
        "status": "Open",
        "program": "SBIR",
        "component": "USAF",
        "agency": "Air Force",
        "solicitation_number": "24.3",
        "phase": "I",
        "deadline": "2026-05-15",
        "requires_clearance": "secret",
    }


# ---------------------------------------------------------------------------
# Proposal State Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def proposal_state_with_partner() -> dict[str, Any]:
    """Proposal state with CU Boulder designated as partner."""
    return {
        "schema_version": "1.0.0",
        "proposal_id": "test-uuid-n244-012",
        "topic": {
            "id": "N244-012",
            "agency": "Navy",
            "title": "Autonomous UUV Navigation and Sensing",
            "deadline": "2026-06-15",
            "phase": "I",
        },
        "partner": {
            "slug": "cu-boulder",
            "designated_at": "2026-03-19T10:00:00Z",
        },
        "current_wave": 0,
        "go_no_go": "pending",
        "created_at": "2026-03-19T10:00:00Z",
        "updated_at": "2026-03-19T10:00:00Z",
    }


@pytest.fixture()
def proposal_state_no_partner() -> dict[str, Any]:
    """Proposal state for non-partnered SBIR proposal."""
    return {
        "schema_version": "1.0.0",
        "proposal_id": "test-uuid-af243-001",
        "topic": {
            "id": "AF243-001",
            "agency": "Air Force",
            "title": "Compact Directed Energy for C-UAS",
            "deadline": "2026-05-15",
            "phase": "I",
        },
        "partner": None,
        "current_wave": 0,
        "go_no_go": "pending",
        "created_at": "2026-03-19T10:00:00Z",
        "updated_at": "2026-03-19T10:00:00Z",
    }


# ---------------------------------------------------------------------------
# Screening Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def swri_screening_signals() -> dict[str, str]:
    """Screening signals for SWRI with mixed readiness."""
    return {
        "timeline_commitment": "caution",
        "bandwidth": "unknown",
        "sbir_experience": "ok",
        "poc_assignment": "ok",
        "scope_agreement": "caution",
    }


@pytest.fixture()
def all_positive_signals() -> dict[str, str]:
    """All readiness signals positive."""
    return {
        "timeline_commitment": "ok",
        "bandwidth": "ok",
        "sbir_experience": "ok",
        "poc_assignment": "ok",
        "scope_agreement": "ok",
    }


@pytest.fixture()
def all_negative_signals() -> dict[str, str]:
    """All readiness signals negative/unknown."""
    return {
        "timeline_commitment": "unknown",
        "bandwidth": "unknown",
        "sbir_experience": "caution",
        "poc_assignment": "unknown",
        "scope_agreement": "unknown",
    }


# ---------------------------------------------------------------------------
# Helper Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def write_partner_profile(partners_dir: Path):
    """Helper to write a partner profile to the partners directory."""

    def _write(profile: dict[str, Any]) -> None:
        slug = profile.get("partner_slug", "unknown")
        path = partners_dir / f"{slug}.json"
        path.write_text(json.dumps(profile, indent=2))

    return _write


@pytest.fixture()
def write_proposal_state(proposal_state_path: Path):
    """Helper to write proposal state to disk."""

    def _write(state: dict[str, Any]) -> None:
        proposal_state_path.write_text(json.dumps(state, indent=2))

    return _write


@pytest.fixture()
def write_screening(screenings_dir: Path):
    """Helper to write screening results to disk."""

    def _write(slug: str, results: dict[str, Any]) -> None:
        path = screenings_dir / f"{slug}.json"
        path.write_text(json.dumps(results, indent=2))

    return _write


@pytest.fixture()
def partnership_context() -> dict[str, Any]:
    """Mutable container to hold partnership operation results across steps."""
    return {}
