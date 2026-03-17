"""Step definitions for Downstream Agent Quality Artifact Consumption feature.

Tests validate that downstream agents can load, filter, and gracefully
degrade when quality artifacts are missing or malformed.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.proposal_quality_discovery.conftest import (
    build_feedback_entry,
    build_quality_preferences,
    build_winning_patterns,
    build_writing_quality_profile,
    load_artifact,
    now_iso,
    write_artifact,
)

scenarios("../features/downstream_consumption.feature")


# ---------------------------------------------------------------------------
# Helpers: Agency filtering and alert matching
# ---------------------------------------------------------------------------


def filter_patterns_by_agency(
    winning_patterns: dict[str, Any], agency: str
) -> list[dict[str, Any]]:
    """Filter winning patterns for a target agency (including universal)."""
    result = []
    for pattern in winning_patterns.get("patterns", []):
        if agency in pattern.get("agencies", []) or pattern.get("universal", False):
            result.append(pattern)
    return result


def check_quality_alerts(
    profile: dict[str, Any], agency: str, section: str
) -> list[dict[str, Any]]:
    """Check for writing quality alerts matching agency and section."""
    alerts = []
    for entry in profile.get("entries", []):
        if (
            entry.get("agency") == agency
            and entry.get("sentiment") == "negative"
            and (
                entry.get("section") == section
                or entry.get("section") == "general"
            )
        ):
            alerts.append(entry)
    return alerts


def check_practices_to_avoid(
    preferences: dict[str, Any], text: str
) -> list[str]:
    """Check if draft text matches any practices to avoid."""
    matches = []
    for practice in preferences.get("practices_to_avoid", []):
        # Simple keyword extraction: check if key phrases from practice appear in text
        # Extract first few significant words for matching
        key_words = [
            w.lower()
            for w in practice.split()
            if len(w) > 3 and w.lower() not in {"with", "without", "from", "that"}
        ]
        text_lower = text.lower()
        matched_count = sum(1 for w in key_words if w in text_lower)
        if matched_count >= len(key_words) * 0.5:
            matches.append(practice)
    return matches


# ---------------------------------------------------------------------------
# Given steps
# ---------------------------------------------------------------------------


@given("no quality preferences file exists")
def no_prefs(quality_dir, artifact_context):
    artifact_context["quality_dir"] = quality_dir
    # Ensure file does not exist
    path = quality_dir / "quality-preferences.json"
    if path.exists():
        path.unlink()


@given("no winning patterns file exists")
def no_patterns(quality_dir, artifact_context):
    artifact_context["quality_dir"] = quality_dir
    path = quality_dir / "winning-patterns.json"
    if path.exists():
        path.unlink()


@given("no writing quality profile file exists")
def no_wqp(quality_dir, artifact_context):
    artifact_context["quality_dir"] = quality_dir
    path = quality_dir / "writing-quality-profile.json"
    if path.exists():
        path.unlink()


@given(
    parsers.parse(
        'winning patterns with {agency} pattern "{pattern}"'
    ),
)
def winning_pattern_for_agency(artifact_context, quality_dir, agency, pattern):
    artifact_context.setdefault("quality_dir", quality_dir)
    artifact_context.setdefault("patterns_list", [])
    artifact_context["patterns_list"].append(
        {
            "pattern": pattern,
            "frequency": 1,
            "agencies": [agency],
            "source_proposals": ["PROP-001"],
            "universal": False,
            "first_seen": now_iso(),
            "last_seen": now_iso(),
        }
    )
    # Write/overwrite the artifact
    wp = build_winning_patterns(
        win_count=len(artifact_context["patterns_list"]),
        patterns=artifact_context["patterns_list"],
    )
    write_artifact(quality_dir / "winning-patterns.json", wp)


@given("winning patterns with Air Force patterns only")
def af_patterns_only(artifact_context, quality_dir):
    artifact_context["quality_dir"] = quality_dir
    wp = build_winning_patterns(
        win_count=2,
        patterns=[
            {
                "pattern": "Lead with quantitative results",
                "frequency": 2,
                "agencies": ["Air Force"],
                "source_proposals": ["AF243-001", "AF244-015"],
                "universal": False,
                "first_seen": now_iso(),
                "last_seen": now_iso(),
            }
        ],
    )
    write_artifact(quality_dir / "winning-patterns.json", wp)


@given(
    parsers.parse(
        'a winning pattern "{pattern}" marked as universal'
    ),
)
def universal_pattern(artifact_context, quality_dir, pattern):
    artifact_context.setdefault("quality_dir", quality_dir)
    artifact_context.setdefault("patterns_list", [])
    artifact_context["patterns_list"].append(
        {
            "pattern": pattern,
            "frequency": 5,
            "agencies": ["Air Force", "Navy"],
            "source_proposals": ["AF243-001"],
            "universal": True,
            "first_seen": now_iso(),
            "last_seen": now_iso(),
        }
    )
    wp = build_winning_patterns(
        win_count=5,
        patterns=artifact_context["patterns_list"],
    )
    write_artifact(quality_dir / "winning-patterns.json", wp)


@given("the current proposal is for DARPA")
def current_agency_darpa(artifact_context):
    artifact_context["current_agency"] = "DARPA"


@given(
    parsers.parse(
        'writing quality profile has negative "{category}" for {agency} {section}'
    ),
)
def wqp_negative_entry(artifact_context, quality_dir, category, agency, section):
    artifact_context["quality_dir"] = quality_dir
    entry = build_feedback_entry(
        comment="Technical approach was difficult to follow",
        agency=agency,
        outcome="LOSS",
        category=category,
        sentiment="negative",
        section=section.replace(" ", "_"),
    )
    wqp = build_writing_quality_profile(entries=[entry])
    write_artifact(quality_dir / "writing-quality-profile.json", wqp)


@given(
    parsers.parse(
        'quality preferences with practice to avoid "{practice}"'
    ),
)
def prefs_with_avoid(artifact_context, quality_dir, practice):
    artifact_context["quality_dir"] = quality_dir
    prefs = build_quality_preferences(
        practices_to_avoid=[practice],
    )
    write_artifact(quality_dir / "quality-preferences.json", prefs)


@given("a quality preferences file with invalid content")
def malformed_prefs(artifact_context, quality_dir):
    artifact_context["quality_dir"] = quality_dir
    path = quality_dir / "quality-preferences.json"
    path.write_text("{ this is not valid json !!!}")


# ---------------------------------------------------------------------------
# When steps
# ---------------------------------------------------------------------------


@when(
    "a downstream agent attempts to load quality preferences",
    target_fixture="load_result",
)
def load_prefs(artifact_context):
    qdir = artifact_context["quality_dir"]
    path = qdir / "quality-preferences.json"
    if not path.exists():
        return {"available": False, "data": None, "error": None}
    try:
        data = json.loads(path.read_text())
        return {"available": True, "data": data, "error": None}
    except (json.JSONDecodeError, ValueError) as e:
        return {"available": False, "data": None, "error": str(e)}


@when(
    "a downstream agent attempts to load winning patterns",
    target_fixture="load_result",
)
def load_patterns(artifact_context):
    qdir = artifact_context["quality_dir"]
    result = load_artifact(qdir / "winning-patterns.json")
    return {"available": result is not None, "data": result, "error": None}


@when(
    "a downstream agent attempts to load the writing quality profile",
    target_fixture="load_result",
)
def load_wqp(artifact_context):
    qdir = artifact_context["quality_dir"]
    result = load_artifact(qdir / "writing-quality-profile.json")
    return {"available": result is not None, "data": result, "error": None}


@when(
    parsers.parse("patterns are filtered for an {agency} proposal"),
    target_fixture="filter_result",
)
def filter_for_agency(artifact_context, agency):
    qdir = artifact_context["quality_dir"]
    wp = load_artifact(qdir / "winning-patterns.json")
    assert wp is not None
    filtered = filter_patterns_by_agency(wp, agency)
    return {"patterns": filtered, "agency": agency}


@when(
    parsers.parse("patterns are filtered for a {agency} proposal"),
    target_fixture="filter_result",
)
def filter_for_agency_a(artifact_context, agency):
    qdir = artifact_context["quality_dir"]
    wp = load_artifact(qdir / "winning-patterns.json")
    assert wp is not None
    filtered = filter_patterns_by_agency(wp, agency)
    return {"patterns": filtered, "agency": agency}


@when(
    parsers.parse(
        "quality alerts are checked for {agency} {section} section"
    ),
    target_fixture="alert_result",
)
def check_alerts(artifact_context, agency, section):
    qdir = artifact_context["quality_dir"]
    wqp = load_artifact(qdir / "writing-quality-profile.json")
    if wqp is None:
        return {"alerts": []}
    alerts = check_quality_alerts(wqp, agency, section.replace(" ", "_"))
    return {"alerts": alerts}


@when(
    parsers.parse(
        'a draft section contains "{text}"'
    ),
    target_fixture="avoid_result",
)
def check_draft_text(artifact_context, text):
    qdir = artifact_context["quality_dir"]
    prefs = load_artifact(qdir / "quality-preferences.json")
    if prefs is None:
        return {"matches": []}
    matches = check_practices_to_avoid(prefs, text)
    return {"matches": matches}


# ---------------------------------------------------------------------------
# Then steps
# ---------------------------------------------------------------------------


@then("the agent receives an indication that no preferences are available")
def no_prefs_available(load_result):
    assert not load_result["available"]


@then("the agent receives an indication that no patterns are available")
def no_patterns_available(load_result):
    assert not load_result["available"]


@then("the agent receives an indication that no profile is available")
def no_profile_available(load_result):
    assert not load_result["available"]


@then("no error occurs")
def no_error(load_result=None, filter_result=None):
    # Accept either fixture; the important thing is no exception was raised.
    pass


@then(parsers.parse('the result includes "{pattern}"'))
def result_includes(filter_result, pattern):
    pattern_names = [p["pattern"] for p in filter_result["patterns"]]
    assert pattern in pattern_names


@then(parsers.parse('the result does not include "{pattern}"'))
def result_excludes(filter_result, pattern):
    pattern_names = [p["pattern"] for p in filter_result["patterns"]]
    assert pattern not in pattern_names


@then("the result is empty")
def result_empty(filter_result):
    assert len(filter_result["patterns"]) == 0


@then("an alert is returned referencing the past evaluator feedback")
def alert_returned(alert_result):
    assert len(alert_result["alerts"]) > 0


@then("no alert is returned")
def no_alert(alert_result):
    assert len(alert_result["alerts"]) == 0


@then("the practice-to-avoid match is flagged")
def avoid_flagged(avoid_result):
    assert len(avoid_result["matches"]) > 0


@then("the agent receives a warning about the malformed file")
def malformed_warning(load_result):
    assert load_result["error"] is not None or not load_result["available"]


@then("the agent can proceed with defaults")
def can_proceed(load_result):
    # Agent proceeds when data is None and no crash occurred
    assert load_result["data"] is None
