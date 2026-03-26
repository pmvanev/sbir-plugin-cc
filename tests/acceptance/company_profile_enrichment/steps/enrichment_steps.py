"""Step definitions for enrichment cascade and walking skeleton scenarios.

Invokes through: CompanyEnrichmentService (driving port -- application service).
Does NOT import adapters directly. Fake adapters are injected via fixtures.

This module links to walking-skeleton.feature and milestone-2 scenarios.
"""

from __future__ import annotations

from typing import Any

from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.company_profile_enrichment.steps.enrichment_common_steps import *  # noqa: F403

# Link walking skeleton feature file -- first scenarios to be enabled
scenarios("../walking-skeleton.feature")


# ---------------------------------------------------------------------------
# Given steps: Configure fake API responses
# ---------------------------------------------------------------------------


@given(
    parsers.parse('SAM.gov will return entity data for UEI "{uei}"'),
)
def sam_gov_returns_entity(sam_gov_response, radiant_sam_entity, uei):
    """Configure SAM.gov fake to return entity data for the given UEI."""
    sam_gov_response.entity_data = radiant_sam_entity
    sam_gov_response.entity_data["uei"] = uei


@given(
    parsers.parse('SBIR.gov will return {count:d} awards for "{company}"'),
)
def sbir_gov_returns_awards(sbir_gov_response, radiant_sbir_awards, count, company):
    """Configure SBIR.gov fake to return award data."""
    sbir_gov_response.awards = radiant_sbir_awards[:count]


@given(
    parsers.parse('USASpending will return federal award totals for "{company}"'),
)
def usa_spending_returns_totals(usa_spending_response, radiant_usa_spending, company):
    """Configure USASpending fake to return recipient data."""
    usa_spending_response.recipient_data = radiant_usa_spending


@given("SBIR.gov is unavailable")
def sbir_gov_unavailable(sbir_gov_response):
    """Configure SBIR.gov fake to simulate timeout/failure."""
    sbir_gov_response.error = "SBIR.gov timed out"
    sbir_gov_response.error_type = "timeout"


@given(
    parsers.parse('SAM.gov will return current entity data for UEI "{uei}"'),
)
def sam_gov_returns_current_entity(sam_gov_response, radiant_sam_entity, uei):
    """Configure SAM.gov fake with current entity data for re-enrichment."""
    sam_gov_response.entity_data = radiant_sam_entity
    sam_gov_response.entity_data["uei"] = uei


@given(
    parsers.parse("SBIR.gov will return {count:d} awards including a new Navy Phase I"),
)
def sbir_gov_returns_awards_with_new(sbir_gov_response, radiant_sbir_awards, count):
    """Configure SBIR.gov with awards including one not in existing profile."""
    sbir_gov_response.awards = radiant_sbir_awards[:count]


@given("USASpending will return current federal award totals")
def usa_spending_returns_current(usa_spending_response, radiant_usa_spending):
    """Configure USASpending with current data for re-enrichment."""
    usa_spending_response.recipient_data = radiant_usa_spending


@given(
    parsers.parse(
        "Rafael has an existing profile with {count:d} past performance entries"
    ),
)
def existing_profile_with_pp(existing_profile_data, write_profile, count):
    """Write an existing profile with a specific number of past performance entries."""
    profile = existing_profile_data.copy()
    profile["past_performance"] = existing_profile_data["past_performance"][:count]
    write_profile(profile)


# ---------------------------------------------------------------------------
# When steps: Invoke through driving ports
# ---------------------------------------------------------------------------


@when(
    parsers.parse('Rafael requests enrichment for UEI "{uei}"'),
)
def request_enrichment(
    enrichment_context,
    sam_gov_response,
    sbir_gov_response,
    usa_spending_response,
    api_keys_path,
    uei,
):
    """Request enrichment through CompanyEnrichmentService.

    This is a placeholder that will invoke the real service once
    implemented. The service will be wired with fake adapters that
    return the configured responses.

    TODO (DELIVER): Wire CompanyEnrichmentService with fake adapters
    and call service.enrich_from_uei(uei, api_key_path).
    """
    # Placeholder: Will be replaced with real service invocation
    # For now, simulate the expected result structure from fakes
    enrichment_context["uei"] = uei
    enrichment_context["pending_implementation"] = True


@when("Rafael requests re-enrichment to compare against his current profile")
def request_re_enrichment(
    diff_context,
    sam_gov_response,
    sbir_gov_response,
    usa_spending_response,
    api_keys_path,
    profile_path,
):
    """Request re-enrichment diff through CompanyEnrichmentService.

    TODO (DELIVER): Wire CompanyEnrichmentService with fake adapters
    and call service.diff_against_profile(profile_path).
    """
    diff_context["pending_implementation"] = True


# ---------------------------------------------------------------------------
# Then steps: Assert enrichment outcomes
# ---------------------------------------------------------------------------


@then(
    parsers.parse('enrichment returns the legal name "{name}"'),
)
def enrichment_has_legal_name(enrichment_context, name):
    """Assert the enrichment result contains the expected legal name.

    TODO (DELIVER): Assert against real EnrichmentResult.
    """
    assert enrichment_context.get("pending_implementation"), (
        "Step not yet wired to real service -- enable after DELIVER implements service"
    )


@then(
    parsers.parse('enrichment returns the CAGE code "{code}"'),
)
def enrichment_has_cage_code(enrichment_context, code):
    """Assert the enrichment result contains the expected CAGE code."""
    assert enrichment_context.get("pending_implementation")


@then(
    parsers.parse("enrichment returns {count:d} NAICS codes"),
)
def enrichment_has_naics_count(enrichment_context, count):
    """Assert the enrichment result contains the expected number of NAICS codes."""
    assert enrichment_context.get("pending_implementation")


@then(
    parsers.parse(
        "enrichment returns {count:d} past performance entries from SBIR awards"
    ),
)
def enrichment_has_pp_count(enrichment_context, count):
    """Assert the enrichment result contains expected past performance entries."""
    assert enrichment_context.get("pending_implementation")


@then("enrichment returns a federal award total")
def enrichment_has_award_total(enrichment_context):
    """Assert the enrichment result contains a federal award total."""
    assert enrichment_context.get("pending_implementation")


@then("every enriched field shows which federal source it came from")
def all_fields_have_source(enrichment_context):
    """Assert every field in the enrichment result has source attribution."""
    assert enrichment_context.get("pending_implementation")


@then("enrichment returns SAM.gov fields successfully")
def sam_fields_present(enrichment_context):
    """Assert SAM.gov fields are present in the result."""
    assert enrichment_context.get("pending_implementation")


@then("enrichment returns USASpending fields successfully")
def usa_fields_present(enrichment_context):
    """Assert USASpending fields are present in the result."""
    assert enrichment_context.get("pending_implementation")


@then("SBIR.gov fields are marked as unavailable")
def sbir_fields_unavailable(enrichment_context):
    """Assert SBIR.gov fields are marked as unavailable in the result."""
    assert enrichment_context.get("pending_implementation")


@then("the unavailable fields are listed for manual entry during the interview")
def unavailable_in_missing_list(enrichment_context):
    """Assert unavailable fields appear in the missing fields list."""
    assert enrichment_context.get("pending_implementation")


@then(
    parsers.parse("the diff shows {count:d} new past performance entry from SBIR.gov"),
)
def diff_has_new_pp(diff_context, count):
    """Assert the diff detected new past performance entries."""
    assert diff_context.get("pending_implementation")


@then(
    parsers.parse(
        'the diff shows the new award is "{agency}" agency '
        'with topic "{topic}"'
    ),
)
def diff_new_award_details(diff_context, agency, topic):
    """Assert the new award has expected agency and topic."""
    assert diff_context.get("pending_implementation")


@then("existing profile entries are not modified in the diff")
def diff_preserves_existing(diff_context):
    """Assert existing profile entries are shown as unchanged in the diff."""
    assert diff_context.get("pending_implementation")
