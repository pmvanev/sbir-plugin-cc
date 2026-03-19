"""Acceptance test conftest -- fixtures for DSIP Topic Scraper BDD scenarios.

All acceptance tests invoke through driving ports only:
- FinderService (application orchestrator -- fetch, pre-filter, persist)
- TopicEnrichmentPort (enrichment abstraction -- not yet implemented)
- TopicCachePort (cache abstraction -- not yet implemented)
- TopicFetchPort (topic source abstraction)
- FinderResultsPort (results persistence abstraction)

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
    """Fresh temporary directory simulating .sbir/ for topic cache and results."""
    sbir_dir = tmp_path / ".sbir"
    sbir_dir.mkdir()
    return sbir_dir


@pytest.fixture()
def cache_path(sbir_dir: Path) -> Path:
    """Path to dsip_topics.json cache within the .sbir directory."""
    return sbir_dir / "dsip_topics.json"


@pytest.fixture()
def finder_results_path(sbir_dir: Path) -> Path:
    """Path to finder-results.json within the .sbir directory."""
    return sbir_dir / "finder-results.json"


@pytest.fixture()
def debug_response_path(sbir_dir: Path) -> Path:
    """Path to dsip_debug_response.json for diagnostic data."""
    return sbir_dir / "dsip_debug_response.json"


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


# ---------------------------------------------------------------------------
# Topic Data Factory
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


def make_enriched_topic(
    topic_id: str = "AF263-042",
    title: str = "Compact Directed Energy for C-UAS",
    agency: str = "Air Force",
    description: str | None = None,
    instructions: str | None = None,
    component_instructions: str | None = None,
    qa_entries: list[dict[str, str]] | None = None,
    enrichment_status: str = "ok",
    **kwargs: Any,
) -> dict[str, Any]:
    """Build an enriched topic dict combining metadata + enrichment data."""
    base = make_topic(topic_id=topic_id, title=title, agency=agency, **kwargs)
    if description is None:
        description = (
            f"Background: This topic seeks innovative approaches to {title.lower()}. "
            f"Phase I will demonstrate feasibility of the proposed concept through "
            f"modeling, simulation, and limited prototyping. Phase II will develop "
            f"a working prototype suitable for field evaluation. The expected TRL "
            f"entry is 3 with TRL 5 exit. References include prior SBIR work in "
            f"related areas. Proposers should demonstrate relevant domain expertise "
            f"and access to necessary test facilities. "
            * 3  # Ensure > 500 characters
        )
    base["description"] = description
    base["instructions"] = instructions or "Standard DoD SBIR submission instructions apply."
    base["component_instructions"] = component_instructions
    base["qa_entries"] = qa_entries or []
    base["qa_count"] = len(base["qa_entries"])
    base["enrichment_status"] = enrichment_status
    return base


# ---------------------------------------------------------------------------
# Sample Topic Collections
# ---------------------------------------------------------------------------


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
def enriched_candidates() -> list[dict[str, Any]]:
    """42 enriched candidate topics for scoring tests."""
    return [
        make_enriched_topic(
            topic_id=f"AF263-{i:03d}",
            title=f"Directed Energy Application #{i}",
            qa_entries=[
                {"question": f"Q{q}: What is the TRL expectation?", "answer": f"TRL 3 entry, TRL 5 exit."}
                for q in range(1, 4)
            ]
            if i % 3 == 0
            else [],
        )
        for i in range(1, 43)
    ]


# ---------------------------------------------------------------------------
# Cache Data Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def fresh_cache_data(enriched_candidates: list[dict[str, Any]]) -> dict[str, Any]:
    """Cache data that is less than 24 hours old."""
    return {
        "scrape_date": (datetime.now() - timedelta(hours=12)).isoformat(),
        "source": "dsip_api",
        "ttl_hours": 24,
        "total_topics": 247,
        "filters_applied": {},
        "enrichment_completeness": {
            "descriptions": 42,
            "instructions": 38,
            "qa": 29,
            "total": 42,
        },
        "topics": enriched_candidates,
    }


@pytest.fixture()
def stale_cache_data(enriched_candidates: list[dict[str, Any]]) -> dict[str, Any]:
    """Cache data that is older than 24 hours."""
    return {
        "scrape_date": (datetime.now() - timedelta(hours=36)).isoformat(),
        "source": "dsip_api",
        "ttl_hours": 24,
        "total_topics": 247,
        "filters_applied": {},
        "enrichment_completeness": {
            "descriptions": 42,
            "instructions": 38,
            "qa": 29,
            "total": 42,
        },
        "topics": enriched_candidates,
    }


# ---------------------------------------------------------------------------
# Scored Results Fixtures
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
        "key_personnel_match": [],
        "prefilter_keywords_matched": [],
    }


@pytest.fixture()
def scored_results() -> dict[str, Any]:
    """Complete finder results with DSIP-sourced scored topics."""
    return {
        "schema_version": "1.0.0",
        "finder_run_id": "test-run-dsip-001",
        "run_date": "2026-03-19T14:30:00Z",
        "source": {
            "type": "dsip_api",
            "query_params": {"topicStatus": "Open"},
            "fallback_file": None,
        },
        "filters_applied": {
            "agency": "Air Force",
            "phase": None,
            "solicitation": None,
        },
        "topics_fetched": 247,
        "topics_after_prefilter": 42,
        "topics_scored": 42,
        "topics_disqualified": 0,
        "company_profile_used": "~/.sbir/company-profile.json",
        "profile_hash": "sha256:test123",
        "results": [
            make_scored_result(
                topic_id="AF263-042",
                title="Compact Directed Energy for C-UAS",
                agency="Air Force",
                composite=0.84,
                recommendation="go",
                deadline="2026-05-15",
                dimensions={
                    "subject_matter": 0.95,
                    "past_performance": 0.80,
                    "certifications": 1.00,
                    "eligibility": 1.00,
                    "sttr": 1.00,
                },
            ),
            make_scored_result(
                topic_id="N263-044",
                title="Shipboard RF Power Management",
                agency="Navy",
                composite=0.62,
                recommendation="go",
            ),
            make_scored_result(
                topic_id="AF263-115",
                title="Thermal Management for Compact DE",
                agency="Air Force",
                composite=0.41,
                recommendation="evaluate",
            ),
        ],
    }


# ---------------------------------------------------------------------------
# Helper Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def scraper_context() -> dict[str, Any]:
    """Mutable container to hold scraper operation results across steps."""
    return {}


@pytest.fixture()
def write_profile(profile_path: Path):
    """Helper to write a profile dict to the profile file."""

    def _write(profile: dict[str, Any]) -> None:
        profile_path.write_text(json.dumps(profile, indent=2))

    return _write


@pytest.fixture()
def write_cache(cache_path: Path):
    """Helper to write cache data to the cache file."""

    def _write(data: dict[str, Any]) -> None:
        cache_path.write_text(json.dumps(data, indent=2))

    return _write


@pytest.fixture()
def write_results(finder_results_path: Path):
    """Helper to write scored results to the finder results file."""

    def _write(results: dict[str, Any]) -> None:
        finder_results_path.write_text(json.dumps(results, indent=2))

    return _write
