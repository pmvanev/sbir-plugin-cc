"""Step definitions for finder results display and persistence scenarios.

Invokes through:
- FinderResultsPort (driven port -- results persistence)
- FinderService (orchestrator for results display)

Does NOT import JSON file adapter or file system internals directly.
"""

from __future__ import annotations

from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.solicitation_finder.steps.finder_common_steps import *  # noqa: F403

# Link to feature files
scenarios("../milestone-01-results.feature")


# --- Given steps: results setup ---


@given(parsers.parse("scoring has completed for {count:d} candidate topics"))
def scoring_completed(
    count: int,
    scored_results: dict[str, Any],
    finder_context: dict[str, Any],
):
    """Scoring has produced results for N topics."""
    finder_context["scored_results"] = scored_results


@given(
    parsers.parse(
        "{go:d} topics scored GO, {eval:d} scored EVALUATE, and "
        "{dq:d} were disqualified"
    ),
)
def result_breakdown(
    go: int, eval: int, dq: int, finder_context: dict[str, Any]
):
    """Set up result breakdown counts."""
    finder_context["expected_go"] = go
    finder_context["expected_evaluate"] = eval
    finder_context["expected_disqualified"] = dq


@given(
    parsers.parse(
        'finder results include topic "{topic_id}" with composite {score:g}'
    ),
)
def results_include_topic(
    topic_id: str,
    score: float,
    scored_results: dict[str, Any],
    write_results,
    finder_context: dict[str, Any],
):
    """Write results including a specific topic."""
    write_results(scored_results)
    finder_context["scored_results"] = scored_results


@given(
    parsers.parse(
        '"{topic_id}" scored subject matter {sme:g}, past performance {pp:g}, '
        "certifications {cert:g}, eligibility {elig:g}, partnership {sttr:g}"
    ),
)
def topic_dimension_scores(
    topic_id: str,
    sme: float,
    pp: float,
    cert: float,
    elig: float,
    sttr: float,
    finder_context: dict[str, Any],
):
    """Set expected dimension scores for topic detail."""
    finder_context["expected_dimensions"] = {
        "subject_matter": sme,
        "past_performance": pp,
        "certifications": cert,
        "eligibility": elig,
        "sttr": sttr,
    }


@given(
    parsers.parse(
        'finder results include topic "{topic_id}" disqualified for TS clearance'
    ),
)
def results_include_dq_topic(
    topic_id: str,
    scored_results: dict[str, Any],
    write_results,
    finder_context: dict[str, Any],
):
    """Write results including a disqualified topic."""
    write_results(scored_results)
    finder_context["scored_results"] = scored_results
    finder_context["dq_topic_id"] = topic_id


@given(parsers.parse('topic "{topic_id}" has a deadline within {days:d} days'))
def topic_deadline_soon(
    topic_id: str, days: int, finder_context: dict[str, Any]
):
    """Topic with an imminent deadline."""
    finder_context.setdefault("deadline_topics", {})[topic_id] = days


@given(parsers.parse('topic "{topic_id}" has a deadline in {days:d} days'))
def topic_deadline_future(
    topic_id: str, days: int, finder_context: dict[str, Any]
):
    """Topic with a normal deadline."""
    finder_context.setdefault("deadline_topics", {})[topic_id] = days


@given("scoring has completed for all candidate topics")
def scoring_completed_all(
    scored_results: dict[str, Any],
    finder_context: dict[str, Any],
):
    """Scoring is done for all topics."""
    finder_context["scored_results"] = scored_results


@given("no finder results exist")
def no_results_exist(finder_results_path, finder_context: dict[str, Any]):
    """Ensure no finder results file exists."""
    if finder_results_path.exists():
        finder_results_path.unlink()
    finder_context["results_exist"] = False


@given("any set of scored finder results")
def any_scored_results(finder_context: dict[str, Any]):
    """Property test setup: any valid scored results."""
    finder_context["property_test"] = "results_roundtrip"


# --- Given steps: walking skeleton results ---


@given(
    parsers.parse(
        "{count:d} candidate topics have been scored with five-dimension fit analysis"
    ),
)
def n_candidates_scored(count: int, finder_context: dict[str, Any]):
    """N candidates have been scored."""
    finder_context["scored_count"] = count


@given(
    parsers.parse(
        'topic "{topic_id}" scored {score:g} composite with recommendation {rec}'
    ),
)
def topic_scored_with_rec(
    topic_id: str,
    score: float,
    rec: str,
    finder_context: dict[str, Any],
):
    """Topic has a specific score and recommendation."""
    finder_context.setdefault("expected_topics", {})[topic_id] = {
        "composite": score,
        "recommendation": rec,
    }


@given(
    parsers.parse(
        'topic "{topic_id}" was disqualified for requiring TS clearance'
    ),
)
def topic_disqualified(topic_id: str, finder_context: dict[str, Any]):
    """Topic was disqualified."""
    finder_context.setdefault("disqualified_topics", {})[topic_id] = (
        "Requires TS clearance"
    )


@given(
    parsers.parse(
        'Phil has finder results with topic "{topic_id}" scored {rec} at {score:g}'
    ),
)
def phil_has_results(
    topic_id: str,
    rec: str,
    score: float,
    scored_results: dict[str, Any],
    write_results,
    finder_context: dict[str, Any],
):
    """Phil has persisted finder results with a specific topic."""
    write_results(scored_results)
    finder_context["scored_results"] = scored_results


@given(
    parsers.parse(
        'topic "{topic_id}" is "{title}" by "{agency}" Phase "{phase}" '
        'with deadline "{deadline}"'
    ),
)
def topic_metadata(
    topic_id: str,
    title: str,
    agency: str,
    phase: str,
    deadline: str,
    finder_context: dict[str, Any],
):
    """Set topic metadata for handoff verification."""
    finder_context["topic_metadata"] = {
        "topic_id": topic_id,
        "title": title,
        "agency": agency,
        "phase": phase,
        "deadline": deadline,
    }


# --- When steps ---


@when("Phil views the finder results")
def view_results(finder_context: dict[str, Any]):
    """Phil views the ranked results table.

    TODO: Wire to FinderService results display.
    """
    finder_context["action"] = "view_results"


@when("the results are displayed")
def results_displayed(finder_context: dict[str, Any]):
    """Results table is rendered.

    TODO: Wire to display logic.
    """
    finder_context["action"] = "display"


@when("the results table is displayed")
def results_table_displayed(finder_context: dict[str, Any]):
    """Results table rendered (alternate phrasing)."""
    finder_context["action"] = "display_table"


@when(parsers.parse('Phil views details for topic "{topic_id}"'))
def view_topic_details(topic_id: str, finder_context: dict[str, Any]):
    """Phil drills into a topic's detail view.

    TODO: Wire to FinderResultsPort.read() for detail.
    """
    finder_context["action"] = "view_details"
    finder_context["detail_topic_id"] = topic_id


@when("the results are persisted")
def persist_results(
    finder_context: dict[str, Any],
    finder_results_port,
):
    """Persist scored results via FinderResultsPort.write()."""
    results = finder_context["scored_results"]
    finder_results_port.write(results)
    finder_context["action"] = "persist"


@when("Phil attempts to view topic details")
def attempt_view_details(
    finder_context: dict[str, Any],
    finder_results_port,
):
    """Phil tries to view details without results -- read returns None."""
    finder_context["read_result"] = finder_results_port.read()
    finder_context["action"] = "view_details_missing"


@when("the results are saved and then loaded")
def save_and_load_results(
    finder_context: dict[str, Any],
    finder_results_port,
    scored_results: dict[str, Any],
):
    """Save then load results via FinderResultsPort write/read cycle."""
    finder_results_port.write(scored_results)
    finder_context["loaded_results"] = finder_results_port.read()
    finder_context["original_results"] = scored_results
    finder_context["action"] = "roundtrip"


@when(parsers.parse('Phil chooses to pursue topic "{topic_id}"'))
def pursue_topic(topic_id: str, finder_context: dict[str, Any]):
    """Phil selects a topic for pursuit.

    TODO: Wire to pursue flow.
    """
    finder_context["action"] = "pursue"
    finder_context["pursue_topic_id"] = topic_id


@when("Phil confirms the selection")
def confirm_selection(finder_context: dict[str, Any]):
    """Phil confirms the pursue action."""
    finder_context["confirmed"] = True


# --- Then steps ---


@then(
    parsers.parse(
        "the ranked table shows {count:d} scored topics in descending score order"
    ),
)
def ranked_table_shows(count: int, finder_context: dict[str, Any]):
    """Verify ranked table content."""
    # TODO: Assert table content
    pass


@then(
    parsers.parse("the ranked table shows scored topics in descending score order"),
)
def ranked_table_descending(finder_context: dict[str, Any]):
    """Verify descending order."""
    # TODO: Assert sort order
    pass


@then("disqualified topics appear in a separate section below")
def dq_section_separate(finder_context: dict[str, Any]):
    """Verify disqualified topics in separate section."""
    # TODO: Assert section separation
    pass


@then(
    "each entry shows topic ID, agency, title, score, recommendation, and deadline",
)
def entry_shows_fields(finder_context: dict[str, Any]):
    """Verify each entry contains all required fields."""
    # TODO: Assert field presence
    pass


@then("all five dimension scores are displayed with rationale")
def dimensions_with_rationale(finder_context: dict[str, Any]):
    """Verify five-dimension breakdown."""
    # TODO: Assert dimension display
    pass


@then("matching key personnel from the company profile are shown")
def key_personnel_shown(finder_context: dict[str, Any]):
    """Verify key personnel display."""
    # TODO: Assert personnel list
    pass


@then(parsers.parse('the deadline shows "{remaining}"'))
def deadline_remaining(remaining: str, finder_context: dict[str, Any]):
    """Verify deadline remaining display."""
    # TODO: Assert deadline calculation
    pass


@then('the tool offers "pursue" and "back" actions')
def offers_pursue_back(finder_context: dict[str, Any]):
    """Verify available actions."""
    # TODO: Assert action options
    pass


@then("the disqualification reason is displayed prominently")
def dq_reason_prominent(finder_context: dict[str, Any]):
    """Verify disqualification reason display."""
    # TODO: Assert prominence
    pass


@then("the tool shows which profile field triggered the disqualification")
def shows_triggering_field(finder_context: dict[str, Any]):
    """Verify triggering profile field is shown."""
    # TODO: Assert field display
    pass


@then('the tool does not offer "pursue" as an action')
def no_pursue_action(finder_context: dict[str, Any]):
    """Verify pursue is not offered for disqualified topics."""
    # TODO: Assert action absence
    pass


@then(parsers.parse('"{topic_id}" shows an URGENT flag'))
def shows_urgent_flag(topic_id: str, finder_context: dict[str, Any]):
    """Verify URGENT flag for imminent deadlines."""
    # TODO: Assert flag presence
    pass


@then(parsers.parse('"{topic_id}" shows the deadline without a flag'))
def shows_deadline_no_flag(topic_id: str, finder_context: dict[str, Any]):
    """Verify normal deadline display."""
    # TODO: Assert no flag
    pass


@then(parsers.parse('topic "{topic_id}" appears first with recommendation {rec}'))
def topic_appears_first(
    topic_id: str, rec: str, finder_context: dict[str, Any]
):
    """Verify topic rank position."""
    # TODO: Assert rank
    pass


@then(
    parsers.parse(
        'disqualified topic "{topic_id}" appears in a separate section '
        'with reason "{reason}"'
    ),
)
def dq_topic_with_reason(
    topic_id: str, reason: str, finder_context: dict[str, Any]
):
    """Verify disqualified topic section."""
    # TODO: Assert section and reason
    pass


@then("results are saved to the finder results file")
def results_saved(finder_context: dict[str, Any], finder_results_port):
    """Verify results persistence -- file exists after write."""
    assert finder_results_port.exists(), "Finder results file should exist after persist"


@then("the file includes all scored topics with dimension breakdowns")
def file_includes_scores(finder_context: dict[str, Any], finder_results_port):
    """Verify file content completeness -- all topics with dimensions present."""
    loaded = finder_results_port.read()
    assert loaded is not None, "Results should be readable after persist"
    results = loaded["results"]
    original = finder_context["scored_results"]["results"]
    assert len(results) == len(original), (
        f"Expected {len(original)} topics, got {len(results)}"
    )
    for entry in results:
        assert "dimensions" in entry, f"Topic {entry['topic_id']} missing dimensions"
        assert len(entry["dimensions"]) == 5, (
            f"Topic {entry['topic_id']} should have 5 dimensions"
        )


@then(
    "the file includes run metadata with date, source, and company name",
)
def file_includes_metadata(finder_context: dict[str, Any], finder_results_port):
    """Verify metadata in persisted file -- run_date, source, company_profile_used."""
    loaded = finder_results_port.read()
    assert loaded is not None, "Results should be readable after persist"
    assert "run_date" in loaded, "Missing run_date in persisted results"
    assert "source" in loaded, "Missing source in persisted results"
    assert "company_profile_used" in loaded, "Missing company_profile_used"
    assert "schema_version" in loaded, "Missing schema_version field"


@then("the tool suggests running the solicitation finder first")
def suggests_running_finder(finder_context: dict[str, Any]):
    """Verify read returned None when no results exist."""
    assert finder_context.get("read_result") is None, (
        "Reading missing results should return None"
    )


@then("the loaded results match the original scores exactly")
def results_match_original(finder_context: dict[str, Any]):
    """Roundtrip preserves data -- loaded results equal original."""
    loaded = finder_context["loaded_results"]
    original = finder_context["original_results"]
    assert loaded == original, (
        "Roundtrip mismatch: loaded results differ from original"
    )


@then(parsers.parse('the proposal workflow begins with topic "{topic_id}" pre-loaded'))
def proposal_begins(topic_id: str, finder_context: dict[str, Any]):
    """Verify proposal workflow started with topic."""
    # TODO: Assert TopicInfo handoff
    pass


@then(
    parsers.parse(
        'the proposal has agency "{agency}", phase "{phase}", and deadline "{deadline}"'
    ),
)
def proposal_has_metadata(
    agency: str, phase: str, deadline: str, finder_context: dict[str, Any]
):
    """Verify proposal metadata from topic."""
    # TODO: Assert TopicInfo fields
    pass


@then("Phil does not need to re-enter any topic metadata")
def no_reenter_metadata(finder_context: dict[str, Any]):
    """Verify all metadata pre-loaded."""
    # TODO: Assert no manual entry needed
    pass


@then(parsers.parse('Phil sees "{message}"'))
def phil_sees_message(message: str, finder_context: dict[str, Any]):
    """Verify Phil sees a specific message."""
    # TODO: Assert against output
    pass
