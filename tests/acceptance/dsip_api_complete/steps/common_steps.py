"""Common steps shared across all dsip-api-complete acceptance features.

These steps handle shared preconditions like system availability,
profile setup, and topic source setup.

Invokes through driving ports only:
- FinderService (application orchestrator)
- TopicFetchPort via DsipApiAdapter (with mocked HTTP transport)
- TopicEnrichmentPort via DsipEnrichmentAdapter (with mocked HTTP transport)
"""

from __future__ import annotations

from typing import Any

from pytest_bdd import given, parsers, then


# --- System availability ---


@given("the DSIP topic source is available")
def dsip_source_available():
    """DSIP topic source availability -- satisfied by test fixtures."""
    pass


@given("the enrichment system is available")
def enrichment_system_available():
    """Enrichment system availability -- satisfied by test fixtures."""
    pass


# --- Profile setup ---


@given(
    parsers.parse(
        'Phil has a company profile for "{company}" with capabilities '
        '"{cap1}", "{cap2}", "{cap3}"'
    )
)
def phil_profile_with_three_caps(
    company: str,
    cap1: str,
    cap2: str,
    cap3: str,
    radiant_profile: dict[str, Any],
    ctx: dict[str, Any],
):
    """Write profile with specific capabilities."""
    profile = radiant_profile.copy()
    profile["company_name"] = company
    profile["capabilities"] = [cap1, cap2, cap3]
    ctx["profile"] = profile


@given(parsers.parse('Phil has a company profile with capabilities "{cap1}" and "{cap2}"'))
def phil_profile_with_two_caps(
    cap1: str,
    cap2: str,
    radiant_profile: dict[str, Any],
    ctx: dict[str, Any],
):
    """Write profile with two capabilities."""
    profile = radiant_profile.copy()
    profile["capabilities"] = [cap1, cap2]
    ctx["profile"] = profile


# --- Topic source setup ---


@given(parsers.parse("the DSIP portal has {count:d} topics in the current solicitation cycle"))
def dsip_portal_has_topics(count: int, ctx: dict[str, Any]):
    """Set up the topic source to return a specific number of topics."""
    ctx["expected_topic_count"] = count


@given(parsers.parse("the current solicitation cycle has {count:d} active topics"))
def cycle_has_active_topics(count: int, ctx: dict[str, Any]):
    """Current cycle has the given number of active topics."""
    ctx["expected_topic_count"] = count


# --- Shared assertions ---


@then(parsers.parse("at most {count:d} topics are returned"))
def at_most_n_topics(count: int, ctx: dict[str, Any]):
    """Verify that the result contains at most N topics."""
    result = ctx.get("result")
    assert result is not None, "No result found in context"
    topics = result.get("topics", [])
    assert len(topics) <= count, (
        f"Expected at most {count} topics, got {len(topics)}"
    )


@then("each topic has a hash identifier containing an underscore")
def each_topic_has_hash_id(ctx: dict[str, Any]):
    """Verify all topic IDs are hash format (contain underscore)."""
    result = ctx.get("result")
    assert result is not None
    topics = result.get("topics", [])
    assert len(topics) > 0, "No topics to verify"
    for topic in topics:
        topic_id = topic.get("topic_id", "")
        assert "_" in topic_id, (
            f"Topic ID '{topic_id}' is not a hash ID (missing underscore)"
        )


@then("each topic includes the solicitation cycle name, release number, and component")
def each_topic_has_cycle_metadata(ctx: dict[str, Any]):
    """Verify all topics have cycle metadata from search response."""
    result = ctx.get("result")
    assert result is not None
    for topic in result.get("topics", []):
        assert topic.get("cycle_name"), f"Missing cycle_name for {topic.get('topic_id')}"
        assert topic.get("release_number") is not None, (
            f"Missing release_number for {topic.get('topic_id')}"
        )
        assert topic.get("component"), f"Missing component for {topic.get('topic_id')}"


@then("each topic includes the count of published Q&A entries")
def each_topic_has_qa_count(ctx: dict[str, Any]):
    """Verify all topics have published_qa_count from search response."""
    result = ctx.get("result")
    assert result is not None
    for topic in result.get("topics", []):
        assert "published_qa_count" in topic, (
            f"Missing published_qa_count for {topic.get('topic_id')}"
        )


@then("no error is reported")
def no_error_reported(ctx: dict[str, Any]):
    """Verify no error in the result."""
    result = ctx.get("result")
    assert result is not None
    assert result.get("error") is None, f"Unexpected error: {result.get('error')}"


@then("zero topics are returned")
def zero_topics_returned(ctx: dict[str, Any]):
    """Verify that the result contains zero topics."""
    result = ctx.get("result")
    assert result is not None
    topics = result.get("topics", [])
    assert len(topics) == 0, f"Expected 0 topics, got {len(topics)}"
