"""Acceptance test conftest -- fixtures for Company Profile Enrichment BDD scenarios.

All acceptance tests invoke through driving ports only:
- CompanyEnrichmentService (enrichment orchestration)
- ApiKeyPort (API key management)

External dependencies (SAM.gov, SBIR.gov, USASpending.gov HTTP calls)
are replaced with fake adapters implementing EnrichmentSourcePort.
Domain logic, service orchestration, and diff computation use real
production code.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest


# ---------------------------------------------------------------------------
# Directory and Path Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def enrichment_dir(tmp_path: Path) -> Path:
    """Fresh temporary directory simulating ~/.sbir/ for enrichment storage."""
    sbir_dir = tmp_path / ".sbir"
    sbir_dir.mkdir()
    return sbir_dir


@pytest.fixture()
def api_keys_path(enrichment_dir: Path) -> Path:
    """Path to api-keys.json within the enrichment directory."""
    return enrichment_dir / "api-keys.json"


@pytest.fixture()
def profile_path(enrichment_dir: Path) -> Path:
    """Path to company-profile.json within the enrichment directory."""
    return enrichment_dir / "company-profile.json"


# ---------------------------------------------------------------------------
# Fake API Adapters (replace external HTTP calls)
# ---------------------------------------------------------------------------


@dataclass
class FakeSamGovResponse:
    """Canned SAM.gov API response for testing."""

    entity_data: dict[str, Any] | None = None
    error: str | None = None
    error_type: str | None = None


@dataclass
class FakeSbirGovResponse:
    """Canned SBIR.gov API response for testing."""

    awards: list[dict[str, Any]] = field(default_factory=list)
    candidates: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None
    error_type: str | None = None


@dataclass
class FakeUsaSpendingResponse:
    """Canned USASpending API response for testing."""

    recipient_data: dict[str, Any] | None = None
    error: str | None = None
    error_type: str | None = None


@pytest.fixture()
def sam_gov_response() -> FakeSamGovResponse:
    """Mutable container for SAM.gov fake response configuration."""
    return FakeSamGovResponse()


@pytest.fixture()
def sbir_gov_response() -> FakeSbirGovResponse:
    """Mutable container for SBIR.gov fake response configuration."""
    return FakeSbirGovResponse()


@pytest.fixture()
def usa_spending_response() -> FakeUsaSpendingResponse:
    """Mutable container for USASpending fake response configuration."""
    return FakeUsaSpendingResponse()


# ---------------------------------------------------------------------------
# Sample Data Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def radiant_sam_entity() -> dict[str, Any]:
    """SAM.gov entity data for Radiant Defense Systems, LLC."""
    return {
        "legal_name": "Radiant Defense Systems, LLC",
        "cage_code": "7X2K9",
        "uei": "DKJF84NXLE73",
        "naics_codes": [
            {"code": "334511", "primary": True},
            {"code": "541715", "primary": False},
            {"code": "334220", "primary": False},
        ],
        "registration_status": "Active",
        "registration_expiration": "2027-01-15",
        "socioeconomic_certifications": [],
        "business_types": [],
    }


@pytest.fixture()
def radiant_sbir_awards() -> list[dict[str, Any]]:
    """SBIR.gov award data for Radiant Defense Systems, LLC."""
    return [
        {
            "agency": "Air Force",
            "topic_area": "Compact DE for Maritime UAS",
            "phase": "Phase I",
            "outcome": "awarded",
        },
        {
            "agency": "DARPA",
            "topic_area": "High-Power RF Source",
            "phase": "Phase II",
            "outcome": "Completed",
        },
        {
            "agency": "Navy",
            "topic_area": "Shipboard Power Conditioning",
            "phase": "Phase I",
            "outcome": "awarded",
        },
    ]


@pytest.fixture()
def radiant_usa_spending() -> dict[str, Any]:
    """USASpending recipient data for Radiant Defense Systems, LLC."""
    return {
        "total_federal_awards": 2400000,
        "total_federal_awards_display": "$2.4M",
        "transaction_count": 5,
        "business_types": ["Small Business", "For-Profit"],
    }


@pytest.fixture()
def existing_profile_data() -> dict[str, Any]:
    """Existing company profile for re-enrichment diff scenarios."""
    return {
        "company_name": "Radiant Defense Systems, LLC",
        "capabilities": ["directed energy", "RF systems", "power electronics"],
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
        "naics_codes": [
            {"code": "334511", "primary": True},
            {"code": "541715", "primary": False},
        ],
        "employee_count": 23,
        "key_personnel": [
            {
                "name": "Rafael Medina",
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
            {
                "agency": "DARPA",
                "topic_area": "Advanced RF Systems",
                "outcome": "completed",
            },
        ],
        "research_institution_partners": ["Georgia Tech Research Institute"],
    }


# ---------------------------------------------------------------------------
# Result Containers
# ---------------------------------------------------------------------------


@pytest.fixture()
def enrichment_context() -> dict[str, Any]:
    """Mutable container for enrichment results across when/then steps."""
    return {}


@pytest.fixture()
def diff_context() -> dict[str, Any]:
    """Mutable container for diff results across when/then steps."""
    return {}


# ---------------------------------------------------------------------------
# Helper: Write profile to disk
# ---------------------------------------------------------------------------


@pytest.fixture()
def write_profile(profile_path: Path):
    """Helper to write a profile dict to the profile file."""

    def _write(profile: dict[str, Any]) -> None:
        profile_path.write_text(json.dumps(profile, indent=2))

    return _write


# ---------------------------------------------------------------------------
# Helper: Write API key to disk
# ---------------------------------------------------------------------------


@pytest.fixture()
def write_api_key(api_keys_path: Path):
    """Helper to write an API key to the keys file."""

    def _write(key: str) -> None:
        api_keys_path.write_text(json.dumps({"sam_gov_api_key": key}, indent=2))

    return _write
