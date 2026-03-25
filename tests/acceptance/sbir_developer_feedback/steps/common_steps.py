"""Common step definitions for sbir-developer-feedback acceptance tests.

All steps drive through production code:
- FeedbackSnapshotService (domain)
- FilesystemFeedbackAdapter (adapter)
- sbir_feedback_cli.py via subprocess (CLI integration)

Filesystem is controlled via pytest tmp_path -- no real .sbir/ is read or written.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

import pytest
from pytest_bdd import given, when, then, parsers


# ---------------------------------------------------------------------------
# Fixtures (shared context)
# ---------------------------------------------------------------------------


@pytest.fixture
def ctx() -> dict[str, Any]:
    """Shared test context passed between steps."""
    return {}


@pytest.fixture
def feedback_dir(tmp_path: Path) -> Path:
    d = tmp_path / ".sbir" / "feedback"
    return d


@pytest.fixture
def state_dir(tmp_path: Path) -> Path:
    return tmp_path / ".sbir"


# ---------------------------------------------------------------------------
# GIVEN — workspace setup
# ---------------------------------------------------------------------------


@given(
    parsers.parse(
        'Maya has an active proposal for topic "{topic_id}" in wave {wave:d} '
        'with rigor profile "{rigor}"'
    )
)
def active_proposal_with_rigor(
    topic_id: str,
    wave: int,
    rigor: str,
    tmp_path: Path,
    ctx: dict[str, Any],
) -> None:
    """Write proposal-state.json and rigor-profile.json to tmp workspace."""
    proposals_dir = tmp_path / ".sbir" / "proposals" / f"proposal-{topic_id.lower()}"
    proposals_dir.mkdir(parents=True, exist_ok=True)

    state = {
        "id": f"proposal-{topic_id.lower()}",
        "topic_id": topic_id,
        "topic_title": f"Test Topic {topic_id}",
        "topic_agency": "ARMY",
        "topic_deadline": "2025-11-15",
        "topic_phase": "I",
        "waves": {
            "0": {"status": "completed", "completed_at": "2026-01-01T00:00:00Z"},
            "1": {"status": "completed", "completed_at": "2026-01-02T00:00:00Z"},
            "2": {"status": "completed", "completed_at": "2026-01-03T00:00:00Z"},
            str(wave): {"status": "active", "completed_at": None},
        },
        "generated_artifacts": [],
    }
    (proposals_dir / "proposal-state.json").write_text(
        json.dumps(state), encoding="utf-8"
    )

    rigor_data = {"profile": rigor, "model_tier": "standard"}
    (proposals_dir / "rigor-profile.json").write_text(
        json.dumps(rigor_data), encoding="utf-8"
    )

    # Write active-proposal pointer
    active_pointer = tmp_path / ".sbir" / "active-proposal.json"
    active_pointer.parent.mkdir(parents=True, exist_ok=True)
    active_pointer.write_text(
        json.dumps({"active_proposal": f"proposal-{topic_id.lower()}"}),
        encoding="utf-8",
    )

    ctx["workspace_root"] = tmp_path
    ctx["proposal_dir"] = proposals_dir
    ctx["proposal_id"] = f"proposal-{topic_id.lower()}"


@given(
    parsers.parse(
        'the company profile is {age:d} days old for "{company}"'
    )
)
def company_profile_with_age(
    age: int,
    company: str,
    tmp_path: Path,
    ctx: dict[str, Any],
) -> None:
    """Write company profile to a test location and record path in ctx."""
    profile_dir = tmp_path / "home_sbir"
    profile_dir.mkdir(parents=True, exist_ok=True)
    profile_path = profile_dir / "company-profile.json"

    profile = {
        "company_name": company,
        "capabilities": ["radar", "sensor fusion"],
        "past_performance": [{"agency": "army", "description": "classified work"}],
        "key_personnel": [{"name": "Jane Doe", "expertise": ["radar"]}],
    }
    profile_path.write_text(json.dumps(profile), encoding="utf-8")

    # Backdate the mtime to simulate age
    mtime = datetime.now(timezone.utc) - timedelta(days=age)
    os.utime(profile_path, (mtime.timestamp(), mtime.timestamp()))

    ctx["profile_path"] = profile_path
    ctx["company_name"] = company
    ctx["company_profile_age_days"] = age


@given(
    parsers.parse(
        "finder results are {age:d} days old with {count:d} scored topics"
    )
)
def finder_results_with_age(
    age: int,
    count: int,
    tmp_path: Path,
    ctx: dict[str, Any],
) -> None:
    """Write finder-results.json with specified age and topic count."""
    sbir_dir = tmp_path / ".sbir"
    sbir_dir.mkdir(parents=True, exist_ok=True)
    results_path = sbir_dir / "finder-results.json"

    topics = [
        {
            "topic_id": f"TOPIC-{i:03d}",
            "composite_score": round(0.9 - i * 0.1, 2),
            "recommendation": "GO" if i == 0 else "EVALUATE",
            "description": "This should NOT appear in snapshot",
        }
        for i in range(count)
    ]
    results = {"source": "dsip_api", "topics": topics}
    results_path.write_text(json.dumps(results), encoding="utf-8")

    mtime = datetime.now(timezone.utc) - timedelta(days=age)
    os.utime(results_path, (mtime.timestamp(), mtime.timestamp()))

    ctx["finder_results_age_days"] = age


@given("no active proposal exists")
def no_active_proposal(tmp_path: Path, ctx: dict[str, Any]) -> None:
    """Ensure no .sbir/proposals/ directory exists."""
    ctx["workspace_root"] = tmp_path
    ctx["profile_path"] = tmp_path / "home_sbir" / "company-profile.json"
    profile_dir = tmp_path / "home_sbir"
    profile_dir.mkdir(parents=True, exist_ok=True)
    (tmp_path / "home_sbir" / "company-profile.json").write_text(
        json.dumps({"company_name": "Test Company"}), encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# WHEN — submit feedback via CLI
# ---------------------------------------------------------------------------


def _run_feedback_cli(
    ctx: dict[str, Any],
    feedback_type: str,
    ratings: dict | None = None,
    free_text: str | None = None,
) -> subprocess.CompletedProcess:
    """Invoke sbir_feedback_cli.py save via subprocess."""
    workspace_root = ctx.get("workspace_root", Path("."))
    profile_path = ctx.get("profile_path", Path.home() / ".sbir" / "company-profile.json")
    state_dir = workspace_root / ".sbir"
    feedback_dir = state_dir / "feedback"

    cmd = [
        sys.executable,
        "scripts/sbir_feedback_cli.py",
        "save",
        "--type", feedback_type,
        "--state-dir", str(state_dir),
        "--profile-path", str(profile_path),
        "--feedback-dir", str(feedback_dir),
    ]
    if ratings:
        cmd += ["--ratings", json.dumps(ratings)]
    if free_text:
        cmd += ["--free-text", free_text]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(Path(__file__).resolve().parent.parent.parent.parent.parent),
    )
    ctx["cli_result"] = result
    if result.returncode == 0:
        ctx["cli_output"] = json.loads(result.stdout)
    return result


@when(
    parsers.parse(
        "Maya submits a quality issue rating past_performance {pp:d} "
        'with text "{text}"'
    )
)
def submit_quality_issue(
    pp: int,
    text: str,
    ctx: dict[str, Any],
) -> None:
    _run_feedback_cli(
        ctx,
        feedback_type="quality",
        ratings={"past_performance": pp},
        free_text=text,
    )


@when(parsers.parse('Maya submits a bug with text "{text}"'))
def submit_bug(text: str, ctx: dict[str, Any]) -> None:
    _run_feedback_cli(ctx, feedback_type="bug", free_text=text)


# ---------------------------------------------------------------------------
# THEN — assertions
# ---------------------------------------------------------------------------


def _load_feedback_file(ctx: dict[str, Any]) -> dict[str, Any]:
    """Load the written feedback file from the path in CLI output."""
    assert "cli_output" in ctx, f"CLI did not produce output. stderr: {ctx.get('cli_result', {}).stderr if 'cli_result' in ctx else 'no result'}"
    file_path = Path(ctx["cli_output"]["file_path"])
    assert file_path.exists(), f"Feedback file not found: {file_path}"
    return json.loads(file_path.read_text(encoding="utf-8"))


@then("a feedback entry is written to the feedback directory")
def feedback_entry_written(ctx: dict[str, Any]) -> None:
    result = ctx.get("cli_result")
    assert result is not None, "CLI was not invoked"
    assert result.returncode == 0, f"CLI failed (exit {result.returncode}):\n{result.stderr}"
    entry = _load_feedback_file(ctx)
    ctx["feedback_entry"] = entry


@then(parsers.parse('the feedback entry has type "{expected_type}"'))
def feedback_entry_type(expected_type: str, ctx: dict[str, Any]) -> None:
    entry = ctx.get("feedback_entry") or _load_feedback_file(ctx)
    assert entry["type"] == expected_type, f"Expected type {expected_type!r}, got {entry['type']!r}"


@then(parsers.parse("the feedback entry has past_performance_rating {rating:d}"))
def feedback_entry_pp_rating(rating: int, ctx: dict[str, Any]) -> None:
    entry = ctx.get("feedback_entry") or _load_feedback_file(ctx)
    assert entry["ratings"]["past_performance"] == rating


@then(parsers.parse('the feedback entry has free_text "{text}"'))
def feedback_entry_free_text(text: str, ctx: dict[str, Any]) -> None:
    entry = ctx.get("feedback_entry") or _load_feedback_file(ctx)
    assert entry["free_text"] == text


@then(parsers.parse('the context snapshot captures proposal_id "{expected}"'))
def snapshot_proposal_id(expected: str, ctx: dict[str, Any]) -> None:
    entry = ctx.get("feedback_entry") or _load_feedback_file(ctx)
    assert entry["context_snapshot"]["proposal_id"] == expected


@then("the context snapshot captures proposal_id null")
def snapshot_proposal_id_null(ctx: dict[str, Any]) -> None:
    entry = ctx.get("feedback_entry") or _load_feedback_file(ctx)
    assert entry["context_snapshot"]["proposal_id"] is None


@then(parsers.parse("the context snapshot captures current_wave {wave:d}"))
def snapshot_current_wave(wave: int, ctx: dict[str, Any]) -> None:
    entry = ctx.get("feedback_entry") or _load_feedback_file(ctx)
    assert entry["context_snapshot"]["current_wave"] == wave


@then("the context snapshot captures current_wave null")
def snapshot_current_wave_null(ctx: dict[str, Any]) -> None:
    entry = ctx.get("feedback_entry") or _load_feedback_file(ctx)
    assert entry["context_snapshot"]["current_wave"] is None


@then(parsers.parse("the context snapshot captures completed_waves {waves_str}"))
def snapshot_completed_waves(waves_str: str, ctx: dict[str, Any]) -> None:
    entry = ctx.get("feedback_entry") or _load_feedback_file(ctx)
    expected = json.loads(waves_str)
    assert entry["context_snapshot"]["completed_waves"] == expected


@then(parsers.parse('the context snapshot captures rigor_profile "{profile}"'))
def snapshot_rigor_profile(profile: str, ctx: dict[str, Any]) -> None:
    entry = ctx.get("feedback_entry") or _load_feedback_file(ctx)
    assert entry["context_snapshot"]["rigor_profile"] == profile


@then(parsers.parse('the context snapshot captures company_name "{name}"'))
def snapshot_company_name(name: str, ctx: dict[str, Any]) -> None:
    entry = ctx.get("feedback_entry") or _load_feedback_file(ctx)
    assert entry["context_snapshot"]["company_name"] == name


@then(parsers.parse("the context snapshot captures company_profile_age_days {age:d}"))
def snapshot_company_age(age: int, ctx: dict[str, Any]) -> None:
    entry = ctx.get("feedback_entry") or _load_feedback_file(ctx)
    # Allow ±1 day tolerance for mtime precision
    actual = entry["context_snapshot"]["company_profile_age_days"]
    assert abs(actual - age) <= 1, f"Expected age ~{age}, got {actual}"


@then(parsers.parse("the context snapshot captures finder_results_age_days {age:d}"))
def snapshot_finder_age(age: int, ctx: dict[str, Any]) -> None:
    entry = ctx.get("feedback_entry") or _load_feedback_file(ctx)
    actual = entry["context_snapshot"]["finder_results_age_days"]
    assert abs(actual - age) <= 1, f"Expected age ~{age}, got {actual}"
