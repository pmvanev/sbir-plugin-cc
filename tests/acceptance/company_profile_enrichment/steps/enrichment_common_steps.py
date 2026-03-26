"""Common steps shared across all Company Profile Enrichment acceptance features.

These steps handle shared preconditions like system availability, API key
setup, and fake API response configuration.

Driving ports used:
- CompanyEnrichmentService (enrichment orchestration)
- ApiKeyPort (API key management)

All external API calls are replaced with fake adapters at the port boundary.
"""

from __future__ import annotations

from pytest_bdd import given


@given("the enrichment system is available")
def enrichment_system_available():
    """System availability -- satisfied by test fixtures.

    In acceptance tests, the system is 'available' when the enrichment
    service and fake adapters are instantiated with test fixtures.
    """
    pass


@given("Rafael has a valid SAM.gov API key stored")
def valid_api_key_stored(write_api_key):
    """Store a valid test API key in the key file."""
    write_api_key("test-valid-api-key-for-sam-gov")


@given("enrichment has returned results from federal sources")
def enrichment_results_available():
    """Precondition: enrichment has already run.

    Individual scenarios configure specific result fields in their
    own Given steps.
    """
    pass
