"""Acceptance test conftest -- fixtures for dsip-api-complete BDD scenarios.

All acceptance tests invoke through driving ports only:
- FinderService (application orchestrator -- fetch, filter, enrich, cache)
- TopicFetchPort (topic source abstraction)
- TopicEnrichmentPort (enrichment abstraction)

External dependencies (DSIP API HTTP calls) are replaced with
recorded fixture data via mock HTTP transport. Domain logic uses
production code.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

FIXTURE_DIR = Path(__file__).resolve().parent.parent.parent / "fixtures" / "dsip_live"


# ---------------------------------------------------------------------------
# Recorded API Response Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def raw_search_response() -> dict[str, Any]:
    """Recorded search response using correct searchParam format (3 topics)."""
    path = FIXTURE_DIR / "raw_api_search_correct_format.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture()
def raw_details_response() -> dict[str, Any]:
    """Recorded details response for topic A254-049."""
    path = FIXTURE_DIR / "raw_api_details_response.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture()
def raw_qa_response() -> list[dict[str, Any]]:
    """Recorded Q&A response for topic A254-049 (7 entries)."""
    path = FIXTURE_DIR / "raw_api_qa_response.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture()
def raw_component_instructions_pdf() -> bytes:
    """Recorded ARMY component instructions PDF (990KB)."""
    path = FIXTURE_DIR / "raw_component_instructions_army.pdf"
    return path.read_bytes()


@pytest.fixture()
def raw_solicitation_instructions_pdf() -> bytes:
    """Recorded BAA preface PDF (658KB)."""
    path = FIXTURE_DIR / "raw_solicitation_instructions.pdf"
    return path.read_bytes()


# ---------------------------------------------------------------------------
# Topic Data Factory
# ---------------------------------------------------------------------------


def make_search_topic(
    topic_id: str = "7051b2da4a1e4c52bd0e7daf80d514f7_86352",
    topic_code: str = "A254-049",
    title: str = "Affordable Ka-Band Metamaterial-Based Electronically Scanned Array Radar",
    status: str = "Pre-Release",
    program: str = "SBIR",
    component: str = "ARMY",
    cycle_name: str = "DOD_SBIR_2025_P1_C4",
    release_number: int = 12,
    published_qa_count: int = 7,
    solicitation_number: str = "25.4",
    cmmc_level: str = "",
) -> dict[str, Any]:
    """Build a topic dict as returned from the corrected search endpoint."""
    return {
        "topic_id": topic_id,
        "topic_code": topic_code,
        "title": title,
        "status": status,
        "program": program,
        "component": component,
        "cycle_name": cycle_name,
        "release_number": release_number,
        "published_qa_count": published_qa_count,
        "solicitation_number": solicitation_number,
        "cmmc_level": cmmc_level,
        "phase": "I",
        "start_date": "2026-04-20T00:00:00+00:00",
        "deadline": "2026-05-28T00:00:00+00:00",
    }


# ---------------------------------------------------------------------------
# Mutable Context Fixture
# ---------------------------------------------------------------------------


@pytest.fixture()
def ctx() -> dict[str, Any]:
    """Mutable container to hold operation results across steps."""
    return {}


# ---------------------------------------------------------------------------
# Profile Fixtures
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
        ],
        "certifications": {
            "sam_gov": {"active": True, "cage_code": "7X2K9"},
            "itar_registered": True,
        },
        "past_performance": [
            {"agency": "Air Force", "topic_area": "Compact Directed Energy"},
        ],
        "key_personnel": [
            {"name": "Dr. Elena Vasquez", "role": "Chief Scientist"},
        ],
    }
