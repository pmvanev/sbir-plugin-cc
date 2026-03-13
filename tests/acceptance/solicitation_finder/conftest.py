"""Acceptance test conftest -- fixtures for Solicitation Finder BDD scenarios.

All acceptance tests invoke through driving ports only:
- FinderService (application orchestrator -- fetch, pre-filter, persist)
- TopicFetchPort (topic source abstraction)
- FinderResultsPort (results persistence abstraction)
- ProfilePort (company profile read)
- KeywordPreFilter (pure domain logic -- no I/O)

External dependencies (DSIP API, file system) are replaced with
in-memory fakes. Domain logic uses production code.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pytest


# ---------------------------------------------------------------------------
# Directory Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def sbir_dir(tmp_path: Path) -> Path:
    """Fresh temporary directory simulating .sbir/ for finder results."""
    sbir_dir = tmp_path / ".sbir"
    sbir_dir.mkdir()
    return sbir_dir


@pytest.fixture()
def finder_results_path(sbir_dir: Path) -> Path:
    """Path to finder-results.json within the .sbir directory."""
    return sbir_dir / "finder-results.json"


@pytest.fixture()
def profile_dir(tmp_path: Path) -> Path:
    """Fresh temporary directory simulating ~/.sbir/ for profile storage."""
    profile_dir = tmp_path / ".sbir-profile"
    profile_dir.mkdir()
    return profile_dir


@pytest.fixture()
def profile_path(profile_dir: Path) -> Path:
    """Path to company-profile.json within the profile directory."""
    return profile_dir / "company-profile.json"


# ---------------------------------------------------------------------------
# Sample Company Profile Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def radiant_profile() -> dict[str, Any]:
    """Complete company profile for Radiant Defense Systems."""
    return {
        "company_name": "Radiant Defense Systems, LLC",
        "capabilities": [
            "directed energy",
            "RF power systems",
            "thermal management",
            "laser physics",
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
        "employee_count": 15,
        "key_personnel": [
            {
                "name": "Dr. Elena Vasquez",
                "role": "Chief Scientist",
                "expertise": ["directed energy", "laser physics"],
            },
            {
                "name": "Marcus Chen",
                "role": "Lead Engineer",
                "expertise": ["RF power systems", "thermal management"],
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
def minimal_profile() -> dict[str, Any]:
    """Profile with company name and capabilities only (no optional sections)."""
    return {
        "company_name": "Minimal Corp",
        "capabilities": ["testing"],
    }


@pytest.fixture()
def profile_no_past_performance(radiant_profile: dict[str, Any]) -> dict[str, Any]:
    """Profile with empty past performance."""
    profile = radiant_profile.copy()
    profile["past_performance"] = []
    return profile


@pytest.fixture()
def profile_no_partners(radiant_profile: dict[str, Any]) -> dict[str, Any]:
    """Profile with no research institution partners."""
    profile = radiant_profile.copy()
    profile["research_institution_partners"] = []
    return profile


# ---------------------------------------------------------------------------
# Sample Topic Data Fixtures
# ---------------------------------------------------------------------------


def make_topic(
    topic_id: str = "AF263-042",
    topic_code: str = "AF263-042",
    title: str = "Compact Directed Energy for C-UAS",
    status: str = "Open",
    program: str = "SBIR",
    component: str = "USAF",
    agency: str = "Air Force",
    solicitation_number: str = "26.3",
    cycle_name: str = "DOD_SBIR_2026_P1_C3",
    phase: str = "I",
    deadline: str | None = None,
    cmmc_level: str = "",
    requires_clearance: str = "secret",
) -> dict[str, Any]:
    """Build a topic metadata dict for test scenarios."""
    if deadline is None:
        deadline = (datetime.now() + timedelta(days=61)).strftime("%Y-%m-%d")
    return {
        "topic_id": topic_id,
        "topic_code": topic_code,
        "title": title,
        "status": status,
        "program": program,
        "component": component,
        "agency": agency,
        "solicitation_number": solicitation_number,
        "cycle_name": cycle_name,
        "phase": phase,
        "deadline": deadline,
        "cmmc_level": cmmc_level,
        "requires_clearance": requires_clearance,
    }


@pytest.fixture()
def sample_topics() -> list[dict[str, Any]]:
    """347 simulated topics: 42 match directed-energy keywords, 305 do not."""
    matching = [
        make_topic(
            topic_id=f"AF263-{i:03d}",
            topic_code=f"AF263-{i:03d}",
            title=f"Directed Energy Application #{i}",
        )
        for i in range(1, 43)
    ]
    non_matching = [
        make_topic(
            topic_id=f"BIO-{i:03d}",
            topic_code=f"BIO-{i:03d}",
            title=f"Biodefense Research Topic #{i}",
            component="DTRA",
            agency="DTRA",
        )
        for i in range(1, 306)
    ]
    return matching + non_matching


@pytest.fixture()
def go_topic() -> dict[str, Any]:
    """Topic AF263-042: high-scoring GO recommendation."""
    return make_topic(
        topic_id="AF263-042",
        title="Compact Directed Energy for C-UAS",
    )


@pytest.fixture()
def evaluate_topic() -> dict[str, Any]:
    """Topic N263-044: mid-scoring EVALUATE recommendation."""
    return make_topic(
        topic_id="N263-044",
        topic_code="N263-044",
        title="Shipboard RF Power Management",
        component="USN",
        agency="Navy",
    )


@pytest.fixture()
def ts_clearance_topic() -> dict[str, Any]:
    """Topic AF263-099: requires TS clearance (disqualifier)."""
    return make_topic(
        topic_id="AF263-099",
        topic_code="AF263-099",
        title="Classified Sensor Fusion Platform",
        requires_clearance="top_secret",
    )


@pytest.fixture()
def sttr_topic() -> dict[str, Any]:
    """Topic N263-S05: STTR program (requires research partner)."""
    return make_topic(
        topic_id="N263-S05",
        topic_code="N263-S05",
        title="Academic-Industry RF Collaboration",
        program="STTR",
        component="USN",
        agency="Navy",
    )


@pytest.fixture()
def urgent_topic() -> dict[str, Any]:
    """Topic HR001126-01: deadline within 3 days."""
    return make_topic(
        topic_id="HR001126-01",
        topic_code="HR001126-01",
        title="Rapid Prototyping Challenge",
        component="DARPA",
        agency="DARPA",
        deadline=(datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
    )


@pytest.fixture()
def expired_topic() -> dict[str, Any]:
    """Topic with an expired deadline."""
    return make_topic(
        topic_id="AF263-042",
        title="Compact Directed Energy for C-UAS",
        deadline="2026-03-01",
    )


# ---------------------------------------------------------------------------
# Sample Scored Results Fixture
# ---------------------------------------------------------------------------


def make_scored_result(
    topic_id: str,
    title: str,
    agency: str,
    composite: float,
    recommendation: str,
    deadline: str | None = None,
    dimensions: dict[str, float] | None = None,
    disqualifiers: list[str] | None = None,
    key_personnel: list[str] | None = None,
    phase: str = "I",
) -> dict[str, Any]:
    """Build a scored result entry for test scenarios."""
    if deadline is None:
        deadline = (datetime.now() + timedelta(days=61)).strftime("%Y-%m-%d")
    if dimensions is None:
        dimensions = {
            "subject_matter": 0.80,
            "past_performance": 0.60,
            "certifications": 1.00,
            "eligibility": 1.00,
            "sttr": 1.00,
        }
    return {
        "topic_id": topic_id,
        "topic_code": topic_id,
        "agency": agency,
        "component": agency,
        "title": title,
        "program": "SBIR",
        "phase": phase,
        "deadline": deadline,
        "solicitation_number": "26.3",
        "cmmc_level": "",
        "composite_score": composite,
        "dimensions": dimensions,
        "recommendation": recommendation,
        "rationale": f"Scored {composite} composite for {title}.",
        "disqualifiers": disqualifiers or [],
        "key_personnel_match": key_personnel or [],
        "prefilter_keywords_matched": [],
    }


@pytest.fixture()
def scored_results() -> dict[str, Any]:
    """Complete finder results with GO, EVALUATE, and NO-GO topics."""
    return {
        "schema_version": "1.0.0",
        "finder_run_id": "test-run-001",
        "run_date": "2026-03-13T14:30:00Z",
        "source": {
            "type": "dsip_api",
            "query_params": {"topicStatus": "Open"},
            "fallback_file": None,
        },
        "filters_applied": {
            "agency": None,
            "phase": None,
            "solicitation": None,
        },
        "topics_fetched": 347,
        "topics_after_prefilter": 42,
        "topics_scored": 42,
        "topics_disqualified": 3,
        "company_profile_used": "~/.sbir/company-profile.json",
        "profile_hash": "sha256:test123",
        "results": [
            make_scored_result(
                topic_id="AF263-042",
                title="Compact Directed Energy for C-UAS",
                agency="Air Force",
                composite=0.82,
                recommendation="go",
                deadline="2026-05-15",
                dimensions={
                    "subject_matter": 0.95,
                    "past_performance": 0.80,
                    "certifications": 1.00,
                    "eligibility": 1.00,
                    "sttr": 1.00,
                },
                key_personnel=["Dr. Elena Vasquez", "Marcus Chen"],
            ),
            make_scored_result(
                topic_id="N263-044",
                title="Shipboard RF Power Management",
                agency="Navy",
                composite=0.34,
                recommendation="evaluate",
            ),
            make_scored_result(
                topic_id="AF263-099",
                title="Classified Sensor Fusion Platform",
                agency="Air Force",
                composite=0.0,
                recommendation="no-go",
                disqualifiers=["Requires TS clearance (profile: Secret)"],
            ),
        ],
    }


# ---------------------------------------------------------------------------
# Result Container Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def finder_context() -> dict[str, Any]:
    """Mutable container to hold finder operation results across steps."""
    return {}


@pytest.fixture()
def write_profile(profile_path: Path):
    """Helper to write a profile dict to the profile file."""

    def _write(profile: dict[str, Any]) -> None:
        profile_path.write_text(json.dumps(profile, indent=2))

    return _write


@pytest.fixture()
def write_results(finder_results_path: Path):
    """Helper to write scored results to the finder results file."""

    def _write(results: dict[str, Any]) -> None:
        finder_results_path.write_text(json.dumps(results, indent=2))

    return _write
