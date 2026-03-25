"""Unit tests for FeedbackSnapshotService.

Test budget: 5 distinct behaviors x 2 = 10 max unit tests.
Behaviors:
  1. completed_waves and skipped_waves derived from waves dict status field
  2. Privacy boundary: capability text, past_performance descriptions, draft content, key_personnel excluded
  3. top_scored_topics limited to 5 entries with only topic_id, composite_score, recommendation
  4. plugin_version via subprocess git rev-parse, falls back to 'unknown' on non-zero exit
  5. Handles missing/None inputs gracefully (all-None inputs produce valid snapshot)
"""

from __future__ import annotations

import json
import time
from unittest.mock import patch

import pytest

from pes.domain.feedback_service import FeedbackSnapshotService


# ---------- Helpers ----------

def _make_state(waves: dict | None = None, proposal_id: str = "prop-001",
                name: str = "Radar Project", topic_id: str = "N00-001") -> dict:
    return {
        "id": proposal_id,
        "name": name,
        "topic_id": topic_id,
        "waves": waves or {},
    }


def _make_rigor(profile: str = "standard") -> dict:
    return {"profile": profile}


def _make_profile(company_name: str = "Acme Defense",
                  capabilities: str = "radar sensor fusion",
                  past_performance: list | None = None,
                  key_personnel: list | None = None) -> dict:
    d: dict = {
        "company_name": company_name,
        "capabilities": capabilities,
        "past_performance": past_performance or [{"title": "DoD Contract", "description": "Classified work."}],
        "key_personnel": key_personnel or [{"name": "Jane Doe", "role": "PI", "bio": "20 years exp."}],
    }
    return d


def _make_finder(topics: list | None = None) -> dict:
    return {"topics": topics or []}


def _make_mtimes(state: float | None = None, profile: float | None = None,
                 finder: float | None = None) -> dict:
    return {"state": state, "profile": profile, "finder": finder}


# ---------- Behavior 1: completed_waves and skipped_waves from waves status ----------

def test_completed_and_skipped_waves_derived_from_status():
    waves = {
        "0": {"status": "completed"},
        "1": {"status": "completed"},
        "2": {"status": "skipped"},
        "3": {"status": "active"},
    }
    svc = FeedbackSnapshotService()
    snapshot = svc.build_snapshot(
        state=_make_state(waves=waves),
        rigor=_make_rigor(),
        profile=_make_profile(),
        finder=_make_finder(),
        mtimes=_make_mtimes(),
        cwd="/some/project",
    )
    assert sorted(snapshot.completed_waves) == [0, 1]
    assert sorted(snapshot.skipped_waves) == [2]


def test_current_wave_is_the_active_wave_number():
    waves = {
        "0": {"status": "completed"},
        "5": {"status": "active"},
    }
    svc = FeedbackSnapshotService()
    snapshot = svc.build_snapshot(
        state=_make_state(waves=waves),
        rigor=_make_rigor(),
        profile=_make_profile(),
        finder=_make_finder(),
        mtimes=_make_mtimes(),
        cwd="/some/project",
    )
    assert snapshot.current_wave == 5


# ---------- Behavior 2: Privacy boundary ----------

def test_privacy_boundary_excludes_sensitive_profile_fields():
    profile = _make_profile(
        capabilities="radar, sensor fusion",
        past_performance=[{"title": "Proj A", "description": "Sensitive work."}],
        key_personnel=[{"name": "Bob", "role": "PI", "bio": "Expert in X."}],
    )
    svc = FeedbackSnapshotService()
    snapshot = svc.build_snapshot(
        state=_make_state(),
        rigor=_make_rigor(),
        profile=profile,
        finder=_make_finder(),
        mtimes=_make_mtimes(),
        cwd="/some/project",
    )
    snapshot_dict = snapshot.to_dict()
    # company_name is allowed
    assert snapshot.company_name == "Acme Defense"
    # sensitive profile content is NOT embedded in snapshot at all
    serialized = json.dumps(snapshot_dict)
    assert "radar, sensor fusion" not in serialized
    assert "Sensitive work." not in serialized
    assert "Expert in X." not in serialized


def test_privacy_boundary_does_not_include_draft_content():
    state = _make_state()
    state["draft"] = "This is a draft with secret approach details."
    svc = FeedbackSnapshotService()
    snapshot = svc.build_snapshot(
        state=state,
        rigor=_make_rigor(),
        profile=_make_profile(),
        finder=_make_finder(),
        mtimes=_make_mtimes(),
        cwd="/some/project",
    )
    serialized = json.dumps(snapshot.to_dict())
    assert "secret approach details" not in serialized


# ---------- Behavior 3: top_scored_topics limited to 5, only allowed fields ----------

def test_top_scored_topics_limited_to_five():
    topics = [
        {"topic_id": f"T{i:02d}", "composite_score": 90 - i, "recommendation": "apply", "extra": "data"}
        for i in range(8)
    ]
    svc = FeedbackSnapshotService()
    snapshot = svc.build_snapshot(
        state=_make_state(),
        rigor=_make_rigor(),
        profile=_make_profile(),
        finder=_make_finder(topics=topics),
        mtimes=_make_mtimes(),
        cwd="/some/project",
    )
    assert len(snapshot.top_scored_topics) == 5


def test_top_scored_topics_contain_only_allowed_fields():
    topics = [
        {"topic_id": "T01", "composite_score": 85, "recommendation": "apply",
         "title": "Secret Title", "agency": "Navy", "extra": "hidden"}
    ]
    svc = FeedbackSnapshotService()
    snapshot = svc.build_snapshot(
        state=_make_state(),
        rigor=_make_rigor(),
        profile=_make_profile(),
        finder=_make_finder(topics=topics),
        mtimes=_make_mtimes(),
        cwd="/some/project",
    )
    assert len(snapshot.top_scored_topics) == 1
    entry = snapshot.top_scored_topics[0]
    assert set(entry.keys()) == {"topic_id", "composite_score", "recommendation"}
    assert entry["topic_id"] == "T01"
    assert entry["composite_score"] == 85
    assert entry["recommendation"] == "apply"


# ---------- Behavior 4: plugin_version via subprocess git rev-parse ----------

def test_plugin_version_obtained_from_git_rev_parse():
    svc = FeedbackSnapshotService()
    with patch("pes.domain.feedback_service.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "abc1234\n"
        snapshot = svc.build_snapshot(
            state=_make_state(),
            rigor=_make_rigor(),
            profile=_make_profile(),
            finder=_make_finder(),
            mtimes=_make_mtimes(),
            cwd="/some/project",
        )
    assert snapshot.plugin_version == "abc1234"
    mock_run.assert_called_once()


def test_plugin_version_falls_back_to_unknown_on_git_error():
    svc = FeedbackSnapshotService()
    with patch("pes.domain.feedback_service.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""
        snapshot = svc.build_snapshot(
            state=_make_state(),
            rigor=_make_rigor(),
            profile=_make_profile(),
            finder=_make_finder(),
            mtimes=_make_mtimes(),
            cwd="/some/project",
        )
    assert snapshot.plugin_version == "unknown"


# ---------- Behavior 5: Handles all-None inputs gracefully ----------

def test_all_none_inputs_produce_valid_snapshot():
    svc = FeedbackSnapshotService()
    with patch("pes.domain.feedback_service.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""
        snapshot = svc.build_snapshot(
            state=None,
            rigor=None,
            profile=None,
            finder=None,
            mtimes=_make_mtimes(),
            cwd="/some/project",
        )
    assert snapshot.proposal_id is None
    assert snapshot.current_wave is None
    assert snapshot.topic_id is None
    assert snapshot.topic_title is None
    assert snapshot.topic_agency is None
    assert snapshot.topic_deadline is None
    assert snapshot.topic_phase is None
    assert snapshot.completed_waves == []
    assert snapshot.skipped_waves == []
    assert snapshot.generated_artifacts == []
    assert snapshot.rigor_profile is None
    assert snapshot.company_name is None
    assert snapshot.company_profile_age_days is None
    assert snapshot.finder_results_age_days is None
    assert snapshot.top_scored_topics == []
    assert snapshot.plugin_version == "unknown"


def test_mtime_age_days_computed_from_mtime():
    """age_days is computed as int((now - mtime) / 86400), floored."""
    now = time.time()
    # Profile mtime = 3 days ago
    three_days_ago = now - (3 * 86400 + 100)
    svc = FeedbackSnapshotService()
    with patch("pes.domain.feedback_service.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "deadbeef\n"
        snapshot = svc.build_snapshot(
            state=None,
            rigor=None,
            profile=_make_profile(),
            finder=None,
            mtimes=_make_mtimes(profile=three_days_ago),
            cwd="/some/project",
        )
    assert snapshot.company_profile_age_days == 3


# ---------- Additional mutation-coverage tests ----------

def test_state_topic_fields_extracted_into_snapshot():
    """Verify all topic fields are read from the correct state keys."""
    state = {
        "id": "prop-001",
        "topic_id": "N00-001",
        "topic_title": "Advanced Radar",
        "topic_agency": "Navy",
        "topic_deadline": "2026-06-01",
        "topic_phase": "I",
        "generated_artifacts": ["draft.md", "exec-summary.md"],
        "waves": {},
    }
    svc = FeedbackSnapshotService()
    with patch("pes.domain.feedback_service.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "abc1234\n"
        snapshot = svc.build_snapshot(
            state=state,
            rigor=None,
            profile=None,
            finder=None,
            mtimes=_make_mtimes(),
            cwd="/some/project",
        )
    assert snapshot.topic_id == "N00-001"
    assert snapshot.topic_title == "Advanced Radar"
    assert snapshot.topic_agency == "Navy"
    assert snapshot.topic_deadline == "2026-06-01"
    assert snapshot.topic_phase == "I"
    assert snapshot.generated_artifacts == ["draft.md", "exec-summary.md"]


def test_non_integer_wave_keys_are_skipped_not_aborting_loop():
    """Non-integer wave keys trigger continue, not break."""
    waves = {
        "0": {"status": "completed"},
        "not-a-wave": {"status": "completed"},  # should be skipped, not abort
        "2": {"status": "completed"},
    }
    svc = FeedbackSnapshotService()
    with patch("pes.domain.feedback_service.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""
        snapshot = svc.build_snapshot(
            state=_make_state(waves=waves),
            rigor=None,
            profile=None,
            finder=None,
            mtimes=_make_mtimes(),
            cwd="/some/project",
        )
    assert sorted(snapshot.completed_waves) == [0, 2]


def test_plugin_version_subprocess_called_with_correct_args():
    """Git subprocess invoked with exact expected command and kwargs."""
    svc = FeedbackSnapshotService()
    with patch("pes.domain.feedback_service.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "abc1234\n"
        svc.build_snapshot(
            state=None,
            rigor=None,
            profile=None,
            finder=None,
            mtimes=_make_mtimes(),
            cwd="/my/project",
        )
    mock_run.assert_called_once_with(
        ["git", "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
        cwd="/my/project",
    )


def test_age_days_exactly_one_day_boundary():
    """_age_days uses 86400 seconds per day (not 86401 or other)."""
    from pes.domain.feedback_service import _age_days
    now = time.time()
    assert _age_days(now - 86400, now) == 1   # exactly 1 day → 1
    assert _age_days(now - 86399, now) == 0   # 1 second short → still 0
