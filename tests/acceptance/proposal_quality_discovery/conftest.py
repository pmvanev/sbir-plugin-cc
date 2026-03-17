"""Acceptance test conftest -- fixtures for Quality Discovery BDD scenarios.

Quality discovery is a markdown-first feature with no new Python domain code.
Acceptance tests validate the testable Python aspects:
- Artifact schema validation (JSON structure against jsonschema)
- Artifact file persistence (read/write/merge to ~/.sbir/)
- Confidence level calculation (pure domain logic)
- Downstream consumption patterns (load, filter, graceful degradation)

Tests operate on JSON artifacts directly -- there are no Python driving ports
for this feature. The "driving port" is the file system interface for
quality artifact read/write.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest


# ---------------------------------------------------------------------------
# Quality Artifact Directory Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def quality_dir(tmp_path: Path) -> Path:
    """Fresh temporary directory simulating ~/.sbir/ for quality artifacts."""
    sbir_dir = tmp_path / ".sbir"
    sbir_dir.mkdir()
    return sbir_dir


# ---------------------------------------------------------------------------
# Schema Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def quality_preferences_schema() -> dict[str, Any]:
    """Load the quality-preferences JSON schema."""
    schema_path = (
        Path(__file__).resolve().parents[3]
        / "templates"
        / "quality-preferences-schema.json"
    )
    return json.loads(schema_path.read_text())


@pytest.fixture(scope="session")
def winning_patterns_schema() -> dict[str, Any]:
    """Load the winning-patterns JSON schema."""
    schema_path = (
        Path(__file__).resolve().parents[3]
        / "templates"
        / "winning-patterns-schema.json"
    )
    return json.loads(schema_path.read_text())


@pytest.fixture(scope="session")
def writing_quality_profile_schema() -> dict[str, Any]:
    """Load the writing-quality-profile JSON schema."""
    schema_path = (
        Path(__file__).resolve().parents[3]
        / "templates"
        / "writing-quality-profile-schema.json"
    )
    return json.loads(schema_path.read_text())


# ---------------------------------------------------------------------------
# Artifact Builder Helpers
# ---------------------------------------------------------------------------


def now_iso() -> str:
    """Current timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


def build_quality_preferences(
    tone: str = "direct_data_driven",
    tone_custom_description: str | None = None,
    detail_level: str = "deep_technical",
    evidence_style: str = "inline_quantitative",
    organization: str = "short_paragraphs",
    practices_to_replicate: list[str] | None = None,
    practices_to_avoid: list[str] | None = None,
) -> dict[str, Any]:
    """Build a quality-preferences artifact dict."""
    result: dict[str, Any] = {
        "schema_version": "1.0.0",
        "updated_at": now_iso(),
        "tone": tone,
        "detail_level": detail_level,
        "evidence_style": evidence_style,
        "organization": organization,
        "practices_to_replicate": practices_to_replicate or [],
        "practices_to_avoid": practices_to_avoid or [],
    }
    if tone_custom_description is not None:
        result["tone_custom_description"] = tone_custom_description
    return result


def build_winning_patterns(
    win_count: int = 0,
    proposal_ratings: list[dict[str, Any]] | None = None,
    patterns: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a winning-patterns artifact dict."""
    if win_count < 10:
        confidence = "low"
    elif win_count < 20:
        confidence = "medium"
    else:
        confidence = "high"

    return {
        "schema_version": "1.0.0",
        "updated_at": now_iso(),
        "confidence_level": confidence,
        "win_count": win_count,
        "proposal_ratings": proposal_ratings or [],
        "patterns": patterns or [],
    }


def build_proposal_rating(
    topic_id: str = "AF243-001",
    agency: str = "Air Force",
    topic_area: str = "Directed Energy",
    outcome: str = "WIN",
    quality_rating: str = "strong",
    winning_practices: list[str] | None = None,
    evaluator_praise: list[str] | None = None,
) -> dict[str, Any]:
    """Build a single proposal rating entry."""
    return {
        "topic_id": topic_id,
        "agency": agency,
        "topic_area": topic_area,
        "outcome": outcome,
        "quality_rating": quality_rating,
        "winning_practices": winning_practices or [],
        "evaluator_praise": evaluator_praise or [],
        "rated_at": now_iso(),
    }


def build_writing_quality_profile(
    entries: list[dict[str, Any]] | None = None,
    agency_patterns: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a writing-quality-profile artifact dict."""
    result: dict[str, Any] = {
        "schema_version": "1.0.0",
        "updated_at": now_iso(),
        "entries": entries or [],
    }
    if agency_patterns is not None:
        result["agency_patterns"] = agency_patterns
    return result


def build_feedback_entry(
    comment: str = "Technical approach was difficult to follow",
    topic_id: str = "AF243-002",
    agency: str = "Air Force",
    outcome: str = "LOSS",
    category: str = "organization_clarity",
    sentiment: str = "negative",
    section: str = "technical_approach",
    auto_categorized: bool = True,
    user_confirmed: bool = True,
) -> dict[str, Any]:
    """Build a single feedback entry for writing quality profile."""
    return {
        "comment": comment,
        "topic_id": topic_id,
        "agency": agency,
        "outcome": outcome,
        "category": category,
        "sentiment": sentiment,
        "section": section,
        "auto_categorized": auto_categorized,
        "user_confirmed": user_confirmed,
        "added_at": now_iso(),
    }


# ---------------------------------------------------------------------------
# Confidence Calculation Helper
# ---------------------------------------------------------------------------


def calculate_confidence(win_count: int) -> str:
    """Calculate confidence level from win count.

    Thresholds: low (<10), medium (10-19), high (>=20).
    """
    if win_count < 10:
        return "low"
    if win_count < 20:
        return "medium"
    return "high"


# ---------------------------------------------------------------------------
# File I/O Helpers
# ---------------------------------------------------------------------------


def write_artifact(path: Path, data: dict[str, Any]) -> None:
    """Write a quality artifact to disk (simulates agent atomic write)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def load_artifact(path: Path) -> dict[str, Any] | None:
    """Load a quality artifact from disk. Returns None if not found."""
    if not path.exists():
        return None
    return json.loads(path.read_text())


# ---------------------------------------------------------------------------
# Result Containers
# ---------------------------------------------------------------------------


@pytest.fixture()
def artifact_context() -> dict[str, Any]:
    """Mutable container to hold artifact data across Given/When/Then steps."""
    return {}


@pytest.fixture()
def validation_result() -> dict[str, Any]:
    """Mutable container to hold validation results across steps."""
    return {}
