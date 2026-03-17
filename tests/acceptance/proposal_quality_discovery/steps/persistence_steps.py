"""Step definitions for Quality Artifact Persistence feature.

Tests validate file read/write/merge behavior for quality artifacts.
All scenarios except the first walking skeleton are marked skip.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import jsonschema
import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.proposal_quality_discovery.conftest import (
    build_feedback_entry,
    build_proposal_rating,
    build_quality_preferences,
    build_winning_patterns,
    build_writing_quality_profile,
    load_artifact,
    now_iso,
    write_artifact,
)

scenarios("../features/artifact_persistence.feature")


# ---------------------------------------------------------------------------
# Given steps
# ---------------------------------------------------------------------------


@given("quality preferences have been captured", target_fixture="artifact_context")
def prefs_captured():
    return {
        "quality_preferences": build_quality_preferences(
            practices_to_replicate=["Lead with results"],
            practices_to_avoid=["Vague claims"],
        ),
        "has_prefs": True,
    }


@given(
    parsers.parse("winning patterns have been captured from {n:d} rated proposals"),
)
def patterns_captured(artifact_context, n):
    ratings = [
        build_proposal_rating(
            topic_id=f"PROP-{i:03d}",
            outcome="WIN",
            quality_rating="strong",
        )
        for i in range(n)
    ]
    artifact_context["winning_patterns"] = build_winning_patterns(
        win_count=n,
        proposal_ratings=ratings,
    )
    artifact_context["has_patterns"] = True


@given("writing quality feedback has been captured")
def feedback_captured(artifact_context):
    artifact_context["writing_quality_profile"] = build_writing_quality_profile(
        entries=[build_feedback_entry()],
    )
    artifact_context["has_feedback"] = True


@given("no winning patterns were captured")
def no_patterns(artifact_context):
    artifact_context["has_patterns"] = False


@given("no writing quality feedback was captured")
def no_feedback(artifact_context):
    artifact_context["has_feedback"] = False


@given("no quality preferences were captured")
def no_prefs(artifact_context):
    artifact_context["has_prefs"] = False


@given(
    parsers.parse(
        "quality preferences file already exists with {n:d} practices to replicate"
    ),
)
def existing_prefs(artifact_context, quality_dir, n):
    prefs = build_quality_preferences(
        practices_to_replicate=[f"Original practice {i+1}" for i in range(n)],
    )
    original_time = prefs["updated_at"]
    write_artifact(quality_dir / "quality-preferences.json", prefs)
    artifact_context["original_prefs"] = prefs
    artifact_context["original_timestamp"] = original_time
    artifact_context["quality_dir"] = quality_dir


@given(
    parsers.parse(
        "winning patterns file already exists with {n:d} proposal ratings"
    ),
)
def existing_patterns(artifact_context, quality_dir, n):
    ratings = [
        build_proposal_rating(topic_id=f"ORIG-{i:03d}") for i in range(n)
    ]
    patterns = build_winning_patterns(win_count=n, proposal_ratings=ratings)
    write_artifact(quality_dir / "winning-patterns.json", patterns)
    artifact_context["original_patterns"] = patterns
    artifact_context["original_timestamp"] = patterns["updated_at"]
    artifact_context["quality_dir"] = quality_dir


@given(
    parsers.parse(
        "writing quality profile already exists with {n:d} feedback entries"
    ),
)
def existing_wqp(artifact_context, quality_dir, n):
    entries = [
        build_feedback_entry(comment=f"Original comment {i+1}") for i in range(n)
    ]
    wqp = build_writing_quality_profile(entries=entries)
    write_artifact(quality_dir / "writing-quality-profile.json", wqp)
    artifact_context["original_wqp"] = wqp
    artifact_context["original_timestamp"] = wqp["updated_at"]
    artifact_context["quality_dir"] = quality_dir


@given("the quality artifact directory does not exist")
def no_quality_dir(tmp_path, artifact_context):
    nonexistent = tmp_path / "missing_sbir"
    artifact_context["quality_dir"] = nonexistent


@given("no quality preferences file exists")
def no_prefs_file(quality_dir, artifact_context):
    artifact_context["quality_dir"] = quality_dir


@given("no winning patterns file exists")
def no_patterns_file(quality_dir, artifact_context):
    artifact_context["quality_dir"] = quality_dir


@given("no writing quality profile file exists")
def no_wqp_file(quality_dir, artifact_context):
    artifact_context["quality_dir"] = quality_dir


@given("any valid quality preferences artifact", target_fixture="artifact_context")
def any_valid_prefs():
    return {
        "roundtrip_artifact": build_quality_preferences(
            practices_to_replicate=["Test practice"],
        ),
        "artifact_type": "quality_preferences",
    }


@given("any valid winning patterns artifact", target_fixture="artifact_context")
def any_valid_patterns():
    return {
        "roundtrip_artifact": build_winning_patterns(
            win_count=5,
            proposal_ratings=[build_proposal_rating()],
        ),
        "artifact_type": "winning_patterns",
    }


@given(
    "any valid writing quality profile artifact",
    target_fixture="artifact_context",
)
def any_valid_wqp():
    return {
        "roundtrip_artifact": build_writing_quality_profile(
            entries=[build_feedback_entry()],
        ),
        "artifact_type": "writing_quality_profile",
    }


# ---------------------------------------------------------------------------
# When steps
# ---------------------------------------------------------------------------


@when("all quality artifacts are saved")
def save_all_artifacts(artifact_context, quality_dir):
    artifact_context["quality_dir"] = quality_dir
    if artifact_context.get("has_prefs"):
        write_artifact(
            quality_dir / "quality-preferences.json",
            artifact_context["quality_preferences"],
        )
    if artifact_context.get("has_patterns"):
        write_artifact(
            quality_dir / "winning-patterns.json",
            artifact_context["winning_patterns"],
        )
    if artifact_context.get("has_feedback"):
        write_artifact(
            quality_dir / "writing-quality-profile.json",
            artifact_context["writing_quality_profile"],
        )


@when("quality artifacts are saved")
def save_available_artifacts(artifact_context, quality_dir):
    artifact_context["quality_dir"] = quality_dir
    if artifact_context.get("has_prefs"):
        write_artifact(
            quality_dir / "quality-preferences.json",
            artifact_context.get(
                "quality_preferences", build_quality_preferences()
            ),
        )
    if artifact_context.get("has_patterns"):
        write_artifact(
            quality_dir / "winning-patterns.json",
            artifact_context.get("winning_patterns", build_winning_patterns()),
        )
    if artifact_context.get("has_feedback"):
        write_artifact(
            quality_dir / "writing-quality-profile.json",
            artifact_context.get(
                "writing_quality_profile", build_writing_quality_profile()
            ),
        )


@when(parsers.parse("{n:d} new practices to replicate are added"))
def add_practices(artifact_context, n):
    # Simulate a brief delay so updated_at differs
    time.sleep(0.01)
    qdir = artifact_context["quality_dir"]
    existing = load_artifact(qdir / "quality-preferences.json")
    assert existing is not None
    for i in range(n):
        existing["practices_to_replicate"].append(f"New practice {i+1}")
    existing["updated_at"] = now_iso()
    artifact_context["updated_prefs"] = existing


@when("the updated quality preferences are saved")
def save_updated_prefs(artifact_context):
    qdir = artifact_context["quality_dir"]
    write_artifact(qdir / "quality-preferences.json", artifact_context["updated_prefs"])


@when(parsers.parse("{n:d} new proposal rating is added"))
def add_rating(artifact_context, n):
    time.sleep(0.01)
    qdir = artifact_context["quality_dir"]
    existing = load_artifact(qdir / "winning-patterns.json")
    assert existing is not None
    for i in range(n):
        existing["proposal_ratings"].append(
            build_proposal_rating(topic_id=f"NEW-{i:03d}")
        )
    existing["win_count"] = len(existing["proposal_ratings"])
    existing["updated_at"] = now_iso()
    artifact_context["updated_patterns"] = existing


@when("the updated winning patterns are saved")
def save_updated_patterns(artifact_context):
    qdir = artifact_context["quality_dir"]
    write_artifact(
        qdir / "winning-patterns.json", artifact_context["updated_patterns"]
    )


@when(parsers.parse("{n:d} new feedback entry is added"))
def add_feedback(artifact_context, n):
    time.sleep(0.01)
    qdir = artifact_context["quality_dir"]
    existing = load_artifact(qdir / "writing-quality-profile.json")
    assert existing is not None
    for i in range(n):
        existing["entries"].append(
            build_feedback_entry(comment=f"New feedback {i+1}")
        )
    existing["updated_at"] = now_iso()
    artifact_context["updated_wqp"] = existing


@when("the updated writing quality profile is saved")
def save_updated_wqp(artifact_context):
    qdir = artifact_context["quality_dir"]
    write_artifact(
        qdir / "writing-quality-profile.json", artifact_context["updated_wqp"]
    )


@when("quality preferences are saved")
def save_prefs_to_missing_dir(artifact_context):
    qdir = artifact_context["quality_dir"]
    write_artifact(qdir / "quality-preferences.json", build_quality_preferences())


@when("the system checks for existing quality preferences")
def check_prefs(artifact_context):
    qdir = artifact_context["quality_dir"]
    artifact_context["load_result"] = load_artifact(
        qdir / "quality-preferences.json"
    )


@when("the system checks for existing winning patterns")
def check_patterns(artifact_context):
    qdir = artifact_context["quality_dir"]
    artifact_context["load_result"] = load_artifact(
        qdir / "winning-patterns.json"
    )


@when("the system checks for existing writing quality profile")
def check_wqp(artifact_context):
    qdir = artifact_context["quality_dir"]
    artifact_context["load_result"] = load_artifact(
        qdir / "writing-quality-profile.json"
    )


@when("the artifact is saved and then loaded", target_fixture="roundtrip_result")
def roundtrip(artifact_context, quality_dir):
    artifact = artifact_context["roundtrip_artifact"]
    atype = artifact_context["artifact_type"]
    filenames = {
        "quality_preferences": "quality-preferences.json",
        "winning_patterns": "winning-patterns.json",
        "writing_quality_profile": "writing-quality-profile.json",
    }
    path = quality_dir / filenames[atype]
    write_artifact(path, artifact)
    return load_artifact(path)


# ---------------------------------------------------------------------------
# Then steps
# ---------------------------------------------------------------------------


@then("quality preferences file exists at the company profile location")
def prefs_exists(artifact_context):
    qdir = artifact_context["quality_dir"]
    assert (qdir / "quality-preferences.json").exists()


@then("winning patterns file exists at the company profile location")
def patterns_exists(artifact_context):
    qdir = artifact_context["quality_dir"]
    assert (qdir / "winning-patterns.json").exists()


@then("writing quality profile file exists at the company profile location")
def wqp_exists(artifact_context):
    qdir = artifact_context["quality_dir"]
    assert (qdir / "writing-quality-profile.json").exists()


@then("each file contains valid data matching its schema")
def files_valid(
    artifact_context,
    quality_preferences_schema,
    winning_patterns_schema,
    writing_quality_profile_schema,
):
    qdir = artifact_context["quality_dir"]
    prefs_path = qdir / "quality-preferences.json"
    if prefs_path.exists():
        data = json.loads(prefs_path.read_text())
        jsonschema.validate(data, quality_preferences_schema)
    patterns_path = qdir / "winning-patterns.json"
    if patterns_path.exists():
        data = json.loads(patterns_path.read_text())
        jsonschema.validate(data, winning_patterns_schema)
    wqp_path = qdir / "writing-quality-profile.json"
    if wqp_path.exists():
        data = json.loads(wqp_path.read_text())
        jsonschema.validate(data, writing_quality_profile_schema)


@then("winning patterns file does not exist")
def patterns_not_exists(artifact_context):
    qdir = artifact_context["quality_dir"]
    assert not (qdir / "winning-patterns.json").exists()


@then("writing quality profile file does not exist")
def wqp_not_exists(artifact_context):
    qdir = artifact_context["quality_dir"]
    assert not (qdir / "writing-quality-profile.json").exists()


@then("quality preferences file does not exist")
def prefs_not_exists(artifact_context):
    qdir = artifact_context["quality_dir"]
    assert not (qdir / "quality-preferences.json").exists()


@then("writing quality profile file exists at the company profile location")
def wqp_exists_alt(artifact_context):
    qdir = artifact_context["quality_dir"]
    assert (qdir / "writing-quality-profile.json").exists()


@then(parsers.parse("quality preferences file contains {n:d} practices to replicate"))
def prefs_practice_count(artifact_context, n):
    qdir = artifact_context["quality_dir"]
    data = load_artifact(qdir / "quality-preferences.json")
    assert data is not None
    assert len(data["practices_to_replicate"]) == n


@then("the updated timestamp is more recent than the original")
def timestamp_newer(artifact_context):
    # The updated_at is a string comparison that works for ISO-8601
    original = artifact_context["original_timestamp"]
    qdir = artifact_context["quality_dir"]
    # Check whichever file was updated
    for fname in [
        "quality-preferences.json",
        "winning-patterns.json",
        "writing-quality-profile.json",
    ]:
        data = load_artifact(qdir / fname)
        if data is not None and data["updated_at"] != original:
            assert data["updated_at"] > original
            return
    # If we reach here, we should verify from the updated context
    for key in ["updated_prefs", "updated_patterns", "updated_wqp"]:
        if key in artifact_context:
            assert artifact_context[key]["updated_at"] > original
            return


@then(parsers.parse("winning patterns file contains {n:d} proposal ratings"))
def patterns_rating_count(artifact_context, n):
    qdir = artifact_context["quality_dir"]
    data = load_artifact(qdir / "winning-patterns.json")
    assert data is not None
    assert len(data["proposal_ratings"]) == n


@then(parsers.parse("writing quality profile contains {n:d} feedback entries"))
def wqp_entry_count(artifact_context, n):
    qdir = artifact_context["quality_dir"]
    data = load_artifact(qdir / "writing-quality-profile.json")
    assert data is not None
    assert len(data["entries"]) == n


@then("the directory is created")
def dir_created(artifact_context):
    qdir = artifact_context["quality_dir"]
    assert qdir.exists()


@then("the quality preferences file is written successfully")
def prefs_written(artifact_context):
    qdir = artifact_context["quality_dir"]
    assert (qdir / "quality-preferences.json").exists()


@then("the system reports no quality preferences found")
def no_prefs_found(artifact_context):
    assert artifact_context["load_result"] is None


@then("the system reports no winning patterns found")
def no_patterns_found(artifact_context):
    assert artifact_context["load_result"] is None


@then("the system reports no writing quality profile found")
def no_wqp_found(artifact_context):
    assert artifact_context["load_result"] is None


@then("the loaded artifact matches the original exactly")
def roundtrip_matches(artifact_context, roundtrip_result):
    original = artifact_context["roundtrip_artifact"]
    assert roundtrip_result == original
