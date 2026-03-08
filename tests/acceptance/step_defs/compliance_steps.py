"""Step definitions for compliance matrix (US-004) and compliance check (US-008).

Invokes through: ComplianceService, ComplianceCheckService (driving ports).
Does NOT import matrix parsers or requirement extractors directly.
"""

from __future__ import annotations

import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# Link to feature files
scenarios("../features/compliance_matrix.feature")
scenarios("../features/compliance_check.feature")


# --- Given steps ---


@given(parsers.parse('Phil has an active proposal for AF243-001 with Go/No-Go "{decision}"'))
def proposal_with_go(state_with_go, write_state, decision):
    """Set up proposal with specified Go/No-Go."""
    state_with_go["go_no_go"] = decision
    write_state(state_with_go)


@given(parsers.parse("a compliance matrix exists with {count:d} items"))
def matrix_exists(count, compliance_matrix_path, state_with_go, write_state):
    """Create a compliance matrix with N items."""
    state_with_go["compliance_matrix"]["item_count"] = count
    state_with_go["compliance_matrix"]["generated_at"] = "2026-03-05T10:00:00Z"
    write_state(state_with_go)
    lines = ["# Compliance Matrix\n", "| # | Requirement | Section | Status |\n"]
    for i in range(count):
        lines.append(f"| {i + 1} | Requirement {i + 1} | Section {(i % 5) + 1} | -- |\n")
    compliance_matrix_path.write_text("".join(lines))


@given("a solicitation with minimal structured requirements")
def minimal_solicitation():
    """Solicitation with few extractable requirements."""
    pass


@given(
    parsers.parse(
        '{covered:d} items have status "covered" and {not_started:d} have status "not started"'
    ),
)
def matrix_with_coverage(covered, not_started):
    """Set coverage status on matrix items."""
    pass


@given(
    parsers.parse(
        "{covered:d} items are covered, {partial:d} partial, "
        "{missing:d} missing, and {waived:d} waived"
    ),
)
def matrix_full_coverage(covered, partial, missing, waived):
    """Set full coverage breakdown on matrix."""
    pass


@given(parsers.parse('Phil has a proposal with Go/No-Go "{decision}"'))
def proposal_with_pending(sample_state, write_state, decision):
    """Set up proposal with specific decision state."""
    state = sample_state.copy()
    state["go_no_go"] = decision
    write_state(state)


@given("no compliance matrix exists")
def no_matrix(compliance_matrix_path):
    """Ensure compliance matrix file does not exist."""
    if compliance_matrix_path.exists():
        compliance_matrix_path.unlink()


@given("a compliance matrix was just generated with 47 items")
def fresh_matrix(compliance_matrix_path, state_with_go, write_state):
    """Create fresh matrix with all items at not-started status."""
    state_with_go["compliance_matrix"]["item_count"] = 47
    write_state(state_with_go)
    lines = ["# Compliance Matrix\n", "| # | Requirement | Section | Status |\n"]
    for i in range(47):
        lines.append(f"| {i + 1} | Requirement {i + 1} | Section {(i % 5) + 1} | -- |\n")
    compliance_matrix_path.write_text("".join(lines))


@given("the compliance matrix file exists but has invalid formatting")
def malformed_matrix(compliance_matrix_path):
    """Write malformed content to compliance matrix."""
    compliance_matrix_path.write_text("This is not a valid compliance matrix format.")


# --- When steps ---


@when("Phil runs the strategy wave command")
def run_strategy_wave():
    """Invoke strategy wave through driving port."""
    # TODO: Invoke through StrategyWaveService
    pytest.skip("Awaiting StrategyWaveService implementation")


@when(parsers.parse('Phil adds a compliance item "{item}"'))
def add_compliance_item(item):
    """Add manual compliance item through driving port."""
    # TODO: Invoke through ComplianceService
    pytest.skip("Awaiting ComplianceService implementation")


@when("the compliance matrix is generated")
def generate_matrix():
    """Invoke matrix generation through driving port."""
    # TODO: Invoke through ComplianceService
    pytest.skip("Awaiting ComplianceService implementation")


@when("Phil checks compliance matrix status")
def check_matrix_status():
    """Invoke compliance status check."""
    # TODO: Invoke through ComplianceCheckService
    pytest.skip("Awaiting ComplianceCheckService implementation")


@when("Phil attempts to run the strategy wave command")
def attempt_strategy_wave():
    """Attempt strategy wave (expect PES block)."""
    # TODO: Invoke through EnforcementEngine
    pytest.skip("Awaiting EnforcementEngine implementation")


@when("Phil attempts to add a compliance item")
def attempt_add_item():
    """Attempt to add item without matrix."""
    # TODO: Invoke through ComplianceService
    pytest.skip("Awaiting ComplianceService implementation")


@when("Phil runs the compliance check")
def run_compliance_check():
    """Invoke compliance check through driving port."""
    # TODO: Invoke through ComplianceCheckService
    pytest.skip("Awaiting ComplianceCheckService implementation")


# --- Then steps ---


@then("the compliance matrix is generated with items mapped to proposal sections")
def verify_matrix_generated():
    """Verify matrix created with section mappings."""
    pass


@then('explicit "shall" statements are extracted')
def verify_shall_statements():
    """Verify shall statement extraction."""
    pass


@then("format requirements are extracted")
def verify_format_requirements():
    """Verify format requirement extraction."""
    pass


@then("implicit requirements from evaluation criteria are extracted")
def verify_implicit_requirements():
    """Verify implicit requirement extraction."""
    pass


@then("ambiguous requirements are flagged with explanations")
def verify_ambiguities_flagged():
    """Verify ambiguity flagging."""
    pass


@then("the matrix is written to the Wave 1 strategy artifacts")
def verify_matrix_written():
    """Verify matrix file location."""
    pass


@then(parsers.parse("the matrix updates to {count:d} items"))
def verify_matrix_count(count):
    """Verify updated item count."""
    pass


@then('the new item is marked as "manually added"')
def verify_manually_added():
    """Verify manual addition marking."""
    pass


@then("the item is mapped to Section 3")
def verify_section_mapping():
    """Verify section mapping for added item."""
    pass


@then("Phil sees a warning about the low extraction count")
def verify_low_count_warning():
    """Verify low extraction count warning."""
    pass


@then("Phil sees guidance to review manually for implicit requirements")
def verify_manual_review_guidance():
    """Verify guidance for manual review."""
    pass


@then(parsers.parse('Phil sees "{coverage}"'))
def verify_coverage_display(coverage):
    """Verify coverage breakdown display."""
    pass


@then("the enforcement system blocks the action")
def verify_blocked():
    """Verify PES blocks action."""
    pass


@then("Phil sees guidance to generate one first")
def verify_generate_guidance():
    """Verify guidance to generate matrix."""
    pass


@then("Phil sees guidance to generate one with the strategy wave command")
def verify_strategy_guidance():
    """Verify strategy wave suggestion."""
    pass


@then("Phil sees guidance to verify the file format")
def verify_format_check_guidance():
    """Verify file format guidance."""
    pass
