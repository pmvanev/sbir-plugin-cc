"""Step definitions for partnership-aware topic scoring.

Invokes through:
- TopicScoringService (existing driving port -- five-dimension scoring)

The partnership scoring extension will modify TopicScoringService to accept
an optional partner profile alongside the company profile, computing both
solo and partnership scores.

Does NOT import internal scoring logic directly.
"""

from __future__ import annotations

from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from pes.domain.topic_scoring import TopicScoringService

# Link to feature files
scenarios("../milestone-03-partnership-scoring.feature")


# --- Fixtures ---


@pytest.fixture()
def scoring_service() -> TopicScoringService:
    """TopicScoringService instance for partnership scoring tests."""
    return TopicScoringService()


# --- Given steps ---


@given("the topic scoring service is available")
def scoring_service_available(scoring_service: TopicScoringService):
    """Confirm scoring service can be instantiated."""
    assert scoring_service is not None


@given(
    parsers.parse(
        'Phil has a company profile with capabilities "{capabilities}"'
    ),
)
def company_with_capabilities(
    capabilities: str,
    company_profile: dict[str, Any],
    partnership_context: dict[str, Any],
):
    """Set company profile with specific capabilities."""
    profile = company_profile.copy()
    profile["capabilities"] = [c.strip() for c in capabilities.split(",")]
    partnership_context["company_profile"] = profile


@given(
    parsers.parse(
        'Phil has a partner profile for "{name}" with capabilities "{capabilities}"'
    ),
)
def partner_with_capabilities(
    name: str,
    capabilities: str,
    partnership_context: dict[str, Any],
):
    """Set partner profile with specific capabilities."""
    slug = name.lower().replace(" ", "-")
    partnership_context["partner_profile"] = {
        "partner_name": name,
        "partner_slug": slug,
        "partner_type": "university",
        "capabilities": [c.strip() for c in capabilities.split(",")],
        "key_personnel": [],
        "facilities": [],
        "past_collaborations": [],
        "sttr_eligibility": {"qualifies": True, "minimum_effort_capable": True},
    }


@given(
    parsers.parse(
        'CU Boulder is a qualifying research institution of type "{inst_type}"'
    ),
)
def cu_boulder_institution_type(inst_type: str, partnership_context: dict[str, Any]):
    """Confirm partner institution type for STTR eligibility."""
    partner = partnership_context.get("partner_profile", {})
    partner["partner_type"] = inst_type
    partnership_context["partner_profile"] = partner


@given(
    parsers.parse(
        'STTR topic "{topic_id}" requires expertise in "{keywords}"'
    ),
)
def sttr_topic_requirements(
    topic_id: str,
    keywords: str,
    partnership_context: dict[str, Any],
):
    """Set up an STTR topic with specific requirements."""
    partnership_context["topic"] = {
        "topic_id": topic_id,
        "title": keywords,
        "program": "STTR",
        "agency": "Navy",
        "phase": "I",
        "requires_clearance": "none",
    }


# --- When steps ---


@when("the topic is scored for Phil's company alone")
def score_solo(
    partnership_context: dict[str, Any],
    scoring_service: TopicScoringService,
):
    """Score topic using company profile only (solo scoring)."""
    topic = partnership_context["topic"]
    profile = partnership_context["company_profile"]

    # For solo STTR scoring, ensure research_institution_partners is empty
    solo_profile = profile.copy()
    solo_profile["research_institution_partners"] = []

    result = scoring_service.score_topic(topic, solo_profile)
    partnership_context["solo_result"] = result
    partnership_context["solo_composite"] = result.composite_score
    partnership_context["solo_recommendation"] = result.recommendation


@when("the topic is scored with CU Boulder as partner")
def score_with_partner(
    partnership_context: dict[str, Any],
    scoring_service: TopicScoringService,
):
    """Score topic using combined company + partner profile.

    Partnership scoring merges capabilities from both profiles and
    sets research_institution_partners to include the partner.
    This is the current integration approach until TopicScoringService
    is extended with a dedicated partnership scoring method.
    """
    topic = partnership_context["topic"]
    company = partnership_context["company_profile"]
    partner = partnership_context["partner_profile"]

    # Build a combined profile for scoring
    combined_profile = company.copy()
    combined_capabilities = list(set(
        company.get("capabilities", []) + partner.get("capabilities", [])
    ))
    combined_profile["capabilities"] = combined_capabilities

    # Add partner to research institution partners for STTR dimension
    combined_profile["research_institution_partners"] = [
        partner.get("partner_name", "")
    ]

    # Merge key personnel expertise
    combined_personnel = list(company.get("key_personnel", []))
    for person in partner.get("key_personnel", []):
        combined_personnel.append(person)
    combined_profile["key_personnel"] = combined_personnel

    result = scoring_service.score_topic(topic, combined_profile)
    partnership_context["partnership_result"] = result
    partnership_context["partnership_composite"] = result.composite_score
    partnership_context["partnership_recommendation"] = result.recommendation


# --- Then steps ---


@then(parsers.parse("the solo recommendation is {rec}"))
def solo_recommendation(rec: str, partnership_context: dict[str, Any]):
    """Assert solo scoring recommendation."""
    actual = partnership_context["solo_recommendation"]
    assert actual == rec.upper(), (
        f"Expected solo recommendation {rec.upper()}, got {actual} "
        f"(composite={partnership_context['solo_composite']})"
    )


@then(parsers.parse("the partnership recommendation is {rec}"))
def partnership_recommendation(rec: str, partnership_context: dict[str, Any]):
    """Assert partnership scoring recommendation."""
    actual = partnership_context["partnership_recommendation"]
    assert actual == rec.upper(), (
        f"Expected partnership recommendation {rec.upper()}, got {actual} "
        f"(composite={partnership_context['partnership_composite']})"
    )


@then("the partnership score is higher than the solo score")
def partnership_higher_than_solo(partnership_context: dict[str, Any]):
    """Assert partnership composite exceeds solo composite."""
    solo = partnership_context["solo_composite"]
    partner = partnership_context["partnership_composite"]
    assert partner > solo, (
        f"Partnership score {partner} should be higher than solo score {solo}"
    )
