"""Common steps shared across all DSIP Topic Scraper acceptance features.

These steps handle shared preconditions like system availability,
profile setup, and cache state.

Invokes through driving ports only:
- FinderService (application orchestrator)
- TopicEnrichmentPort via InMemoryTopicEnrichmentAdapter (driven port fake)
- TopicCachePort via InMemoryTopicCacheAdapter (driven port fake)
"""

from __future__ import annotations

from typing import Any

from pytest_bdd import given, parsers, then


# --- System availability ---


@given("the solicitation finder system is available")
def finder_system_available():
    """System availability -- satisfied by test fixtures."""
    pass


@given("the enrichment system is available")
def enrichment_system_available():
    """Enrichment system availability -- satisfied by test fixtures."""
    pass


@given("the cache system is available")
def cache_system_available():
    """Cache system availability -- satisfied by test fixtures."""
    pass


# --- Profile setup ---


@given(parsers.parse('Phil has a company profile for "{company}" with capabilities "{cap1}", "{cap2}", "{cap3}"'))
def phil_profile_with_three_capabilities(
    company: str,
    cap1: str,
    cap2: str,
    cap3: str,
    radiant_profile: dict[str, Any],
    write_profile,
    scraper_context: dict[str, Any],
):
    """Write profile with specific capabilities."""
    profile = radiant_profile.copy()
    profile["company_name"] = company
    profile["capabilities"] = [cap1, cap2, cap3]
    write_profile(profile)
    scraper_context["profile"] = profile


@given(parsers.parse('Phil has a company profile with capabilities "{cap1}" and "{cap2}"'))
def phil_profile_with_two_capabilities(
    cap1: str,
    cap2: str,
    radiant_profile: dict[str, Any],
    write_profile,
    scraper_context: dict[str, Any],
):
    """Write profile with two capabilities."""
    profile = radiant_profile.copy()
    profile["capabilities"] = [cap1, cap2]
    write_profile(profile)
    scraper_context["profile"] = profile


@given("Phil has a company profile with capabilities, certifications, and past performance")
def phil_has_full_profile(
    radiant_profile: dict[str, Any],
    write_profile,
    scraper_context: dict[str, Any],
):
    """Write the full Radiant profile with all sections."""
    write_profile(radiant_profile)
    scraper_context["profile"] = radiant_profile


@given("Phil has a company profile")
def phil_has_default_profile(
    radiant_profile: dict[str, Any],
    write_profile,
    scraper_context: dict[str, Any],
):
    """Write the default Radiant Defense profile."""
    write_profile(radiant_profile)
    scraper_context["profile"] = radiant_profile


@given(parsers.parse('Phil has a company profile with capabilities "{cap}"'))
def phil_profile_with_single_capability(
    cap: str,
    radiant_profile: dict[str, Any],
    write_profile,
    scraper_context: dict[str, Any],
):
    """Write profile with a single capability."""
    profile = radiant_profile.copy()
    profile["capabilities"] = [cap]
    write_profile(profile)
    scraper_context["profile"] = profile


@given(parsers.parse('Phil updated his company profile to add capability "{cap}"'))
def phil_updated_profile_capability(
    cap: str,
    radiant_profile: dict[str, Any],
    write_profile,
    scraper_context: dict[str, Any],
):
    """Update profile with an additional capability."""
    profile = radiant_profile.copy()
    profile["capabilities"] = radiant_profile["capabilities"] + [cap]
    write_profile(profile)
    scraper_context["profile"] = profile


# --- Enrichment setup ---


@given("each candidate topic has a downloadable description document")
def each_candidate_has_description(scraper_context: dict[str, Any]):
    """All candidate topics have downloadable description documents."""
    scraper_context.setdefault("enrichment_data", {})


# --- Shared Then steps ---


@then(parsers.parse('the tool displays "{message}"'))
def displays_message(message: str, scraper_context: dict[str, Any]):
    """Verify a specific message is displayed."""
    result = scraper_context.get("result")
    if result is not None:
        messages = result.get("messages", [])
        all_text = " | ".join(str(m) for m in messages)
        assert message.lower() in all_text.lower(), (
            f"Expected message '{message}' not found in: {messages}"
        )


@then(parsers.parse('the tool warns "{message}"'))
def tool_warns_message(message: str, scraper_context: dict[str, Any]):
    """Verify a specific warning message."""
    result = scraper_context.get("result")
    if result is not None:
        messages = result.get("messages", [])
        all_text = " | ".join(str(m) for m in messages)
        assert message.lower() in all_text.lower(), (
            f"Expected warning '{message}' not found in: {messages}"
        )
