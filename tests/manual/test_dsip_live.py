"""Live integration tests for the DSIP topic CLI.

Invokes scripts/dsip_cli.py as a subprocess — the same way the
sbir-topic-scout agent calls it via Bash.

Run manually:
    pytest tests/manual/test_dsip_live.py -m live -v --tb=short

Excluded from CI via the 'live' marker.
"""

from __future__ import annotations

import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

FIXTURE_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "dsip_live"
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CLI = "scripts/dsip_cli.py"

logger = logging.getLogger(__name__)


def _save_fixture(name: str, data: Any) -> Path:
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    path = FIXTURE_DIR / f"{name}.json"
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    logger.info("Fixture saved: %s (%d bytes)", path, path.stat().st_size)
    return path


def _run_cli(*args: str, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, CLI, *args],
        cwd=str(REPO_ROOT),
        capture_output=True, text=True, timeout=timeout,
    )


def _run_cli_json(*args: str, timeout: int = 120) -> dict[str, Any]:
    result = _run_cli(*args, timeout=timeout)
    assert result.returncode == 0, f"CLI failed (exit {result.returncode}):\n{result.stderr}"
    output: dict[str, Any] = json.loads(result.stdout)
    return output


# ===================================================================
# Test 1: fetch -- metadata only
# ===================================================================


@pytest.mark.live
class TestCliFetch:

    def test_fetch_returns_current_cycle_topics(self) -> None:
        """Fetch should return only active topics, not 32K historical ones."""
        data = _run_cli_json("fetch", "--max-pages", "1", "--limit", "10")

        _save_fixture("cli_fetch_current", data)

        assert data["source"] == "dsip_api"
        assert data["error"] is None
        # With correct searchParam format, total should be <100 (not 32K)
        assert data["total"] < 500, f"Expected current-cycle topics, got {data['total']}"
        assert len(data["topics"]) > 0

        topic = data["topics"][0]
        # Hash ID format (contains underscore)
        assert "_" in topic["topic_id"], f"Expected hash ID, got {topic['topic_id']}"
        # New fields from correct API format
        assert topic.get("cycle_name"), "Missing cycle_name"
        assert topic.get("release_number") is not None, "Missing release_number"
        assert topic.get("status") in ("Open", "Pre-Release"), f"Unexpected status: {topic['status']}"

    def test_fetch_with_status_filter(self) -> None:
        data = _run_cli_json("fetch", "--status", "Pre-Release", "--max-pages", "1")
        assert data["error"] is None
        for t in data["topics"]:
            assert t["status"] == "Pre-Release", f"Expected Pre-Release, got {t['status']}"


# ===================================================================
# Test 2: enrich -- all 4 data types
# ===================================================================


@pytest.mark.live
class TestCliEnrich:

    def test_enrich_returns_all_four_data_types(self, tmp_path: Path) -> None:
        """The core test: enrich must return descriptions, Q&A, solicitation + component instructions."""
        data = _run_cli_json(
            "enrich", "--max-pages", "1", "--limit", "3",
            "--state-dir", str(tmp_path),  # fresh cache
        )

        _save_fixture("cli_enrich_all_four", data)

        assert data["error"] is None
        assert len(data["topics"]) > 0

        # Check completeness messages for all 4 data types
        msg_text = " ".join(data["messages"])
        assert "Descriptions:" in msg_text
        # Q&A may be 0 for some topics (valid), but the message should be present
        assert "Q&A:" in msg_text or "qa" in msg_text.lower()

        topic = data["topics"][0]

        # 1. Description
        assert topic.get("description"), "Missing description"
        assert len(topic["description"]) > 100

        # 2. Q&A (may be empty for some topics, but field must exist)
        assert "qa_entries" in topic
        assert isinstance(topic["qa_entries"], list)

        # 3. Solicitation instructions
        sol = topic.get("solicitation_instructions", "")
        assert sol, "Missing solicitation_instructions"
        assert len(sol) > 1000, f"Solicitation instructions too short: {len(sol)} chars"

        # 4. Component instructions
        comp = topic.get("component_instructions", "")
        assert comp, "Missing component_instructions"
        assert len(comp) > 1000, f"Component instructions too short: {len(comp)} chars"

        # Additional enrichment fields
        assert topic.get("objective"), "Missing objective"
        assert topic.get("keywords"), "Missing keywords"
        assert isinstance(topic.get("technology_areas", []), list)
        assert topic.get("enrichment_status") == "ok"

    def test_enrich_with_capability_filter(self, tmp_path: Path) -> None:
        data = _run_cli_json(
            "enrich", "--max-pages", "1", "--limit", "10",
            "--capabilities", "radar,sensor,AI",
            "--state-dir", str(tmp_path),  # fresh cache
        )
        assert data["error"] is None
        assert data["eliminated_count"] > 0, "Pre-filter should eliminate some topics"


# ===================================================================
# Test 3: detail -- single topic by hash ID
# ===================================================================


@pytest.mark.live
class TestCliDetail:

    def test_detail_enriches_single_topic(self) -> None:
        # First fetch to get a real hash ID
        fetch_data = _run_cli_json("fetch", "--max-pages", "1", "--limit", "3")
        if not fetch_data["topics"]:
            pytest.skip("No topics available")

        topic_id = fetch_data["topics"][0]["topic_id"]
        data = _run_cli_json("detail", "--topic-id", topic_id)

        _save_fixture("cli_detail_hash_id", data)

        assert data["topic_id"] == topic_id
        if data["enriched"]:
            entry = data["enriched"][0]
            assert entry["description"], f"Empty description for {topic_id}"
            assert "qa_entries" in entry


# ===================================================================
# Test 4: score -- full pipeline with scoring
# ===================================================================


@pytest.mark.live
class TestCliScore:

    def test_score_with_profile(self, tmp_path: Path) -> None:
        profile = {
            "company_name": "Test Co",
            "capabilities": ["radar", "sensor", "AI", "metamaterials"],
            "certifications": {"sam_gov": {"active": True}},
            "past_performance": [
                {"agency": "army", "topic_area": "radar sensor", "outcome": "awarded"},
            ],
            "key_personnel": [{"name": "Jane Doe", "expertise": ["radar"]}],
            "employee_count": 25,
        }
        profile_path = tmp_path / "profile.json"
        profile_path.write_text(json.dumps(profile))

        data = _run_cli_json(
            "score", "--max-pages", "1", "--limit", "10",
            "--profile", str(profile_path),
            "--state-dir", str(tmp_path),
            "--no-persist",
        )

        _save_fixture("cli_score_with_profile", data)

        assert data["error"] is None
        assert "scored" in data
        for s in data["scored"]:
            assert s["recommendation"] in ("GO", "EVALUATE", "NO-GO")
            assert 0.0 <= s["composite_score"] <= 1.0


# ===================================================================
# Test 5: Cache behavior
# ===================================================================


@pytest.mark.live
class TestCliCache:

    def test_second_call_uses_cache(self, tmp_path: Path) -> None:
        common = ["enrich", "--max-pages", "1", "--limit", "3", "--state-dir", str(tmp_path)]

        data1 = _run_cli_json(*common)
        assert data1["error"] is None
        assert (tmp_path / "dsip_topics.json").exists()

        data2 = _run_cli_json(*common)
        assert "Using cached enriched data" in data2["messages"]
