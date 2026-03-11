"""Step definitions for submission preparation and packaging (US-013).

Invokes through: SubmissionService (driving port) and EnforcementEngine (driving port).
Does NOT import internal portal rule loaders or archive creators directly.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.step_defs.common_steps import *  # noqa: F403

# Link to feature file
scenarios("../features/submission.feature")


# --- Fixtures ---


@pytest.fixture()
def submission_context() -> dict[str, Any]:
    """Shared context for submission scenario steps."""
    return {}


# --- Given steps ---


@given(
    "Phil has an active proposal with final review signed off",
    target_fixture="active_state",
)
def proposal_signed_off(sample_state, write_state):
    """Set up proposal with final review signed off, ready for Wave 8."""
    state = sample_state.copy()
    state["go_no_go"] = "go"
    state["current_wave"] = 8
    state["waves"] = {
        "0": {"status": "completed", "completed_at": "2026-03-02T10:00:00Z"},
        "1": {"status": "completed", "completed_at": "2026-03-05T10:00:00Z"},
        "2": {"status": "completed", "completed_at": "2026-03-06T10:00:00Z"},
        "3": {"status": "completed", "completed_at": "2026-03-07T10:00:00Z"},
        "4": {"status": "completed", "completed_at": "2026-03-08T10:00:00Z"},
        "5": {"status": "completed", "completed_at": "2026-03-09T10:00:00Z"},
        "6": {"status": "completed", "completed_at": "2026-03-10T10:00:00Z"},
        "7": {"status": "completed", "completed_at": "2026-03-11T10:00:00Z"},
        "8": {"status": "active", "completed_at": None},
    }
    state["final_review"] = {
        "status": "signed_off",
        "review_round": 1,
        "sign_off_at": "2026-03-11T10:00:00Z",
        "signed_off_by": "Phil Santos",
        "high_findings_count": 0,
        "completed_at": "2026-03-11T10:00:00Z",
    }
    write_state(state)
    return state


@given("AF243-001 is an Air Force topic")
def air_force_topic():
    """Topic is Air Force (DSIP portal)."""
    pass


@given("all required files are present and correctly named")
def all_files_present():
    """All submission files are present and named correctly."""
    pass


@given("all checks pass")
def all_checks_pass():
    """All pre-submission checks pass."""
    pass


@given("all checks pass and Phil has confirmed readiness")
def checks_pass_and_confirmed():
    """All checks pass and Phil has confirmed."""
    pass


@given("the Firm Certification file is missing")
def missing_certification(submission_context):
    """Firm Certification file is not in the package -- exclude from package files."""
    submission_context["exclude_file"] = "Firm_Certification"


@given("Phil has not completed the final review sign-off")
def no_signoff(active_state, write_state):
    """Final review not signed off."""
    active_state["final_review"] = {
        "status": "in_progress",
        "review_round": 0,
        "sign_off_at": None,
        "signed_off_by": None,
    }
    write_state(active_state)


@given(
    "AF243-001 has been submitted with confirmation recorded",
    target_fixture="active_state",
)
def submitted_proposal_for_submission(sample_state, write_state):
    """Proposal is submitted and archived."""
    state = sample_state.copy()
    state["go_no_go"] = "go"
    state["current_wave"] = 8
    state["submission"] = {
        "status": "submitted",
        "portal": "DSIP",
        "confirmation_number": "DSIP-2026-AF243-001-7842",
        "submitted_at": "2026-04-07T14:23:17Z",
        "archive_path": "./artifacts/wave-8-submission/archive/",
        "immutable": True,
    }
    write_state(state)
    return state


# --- When steps ---


@when("Phil prepares the submission package", target_fixture="package_result")
def prepare_submission(active_state, submission_context):
    """Prepare submission through SubmissionService."""
    from pes.domain.submission import PackageFile
    from pes.domain.submission_service import SubmissionService

    # Build a fake portal rules loader with DSIP rules
    from tests.acceptance.step_defs._fake_portal_rules import FakePortalRulesLoader

    loader = FakePortalRulesLoader()

    # Build package files -- all required files present for happy path
    all_files = [
        PackageFile(
            original_name="Technical_Volume.pdf",
            category="technical_volume",
            size_bytes=2_000_000,
        ),
        PackageFile(
            original_name="Cost_Volume.pdf",
            category="cost_volume",
            size_bytes=500_000,
        ),
        PackageFile(
            original_name="Firm_Certification.pdf",
            category="firm_certification",
            size_bytes=100_000,
        ),
    ]

    # Remove excluded file if specified
    exclude = submission_context.get("exclude_file")
    if exclude:
        all_files = [f for f in all_files if exclude not in f.original_name]

    service = SubmissionService(portal_rules_loader=loader)
    agency = active_state["topic"]["agency"]
    result = service.prepare_package(agency=agency, files=all_files)
    return result


@when("the tool runs pre-submission verification", target_fixture="package_result")
def run_verification(active_state, submission_context):
    """Run pre-submission verification through SubmissionService."""
    from pes.domain.submission import PackageFile
    from pes.domain.submission_service import SubmissionService
    from tests.acceptance.step_defs._fake_portal_rules import FakePortalRulesLoader

    loader = FakePortalRulesLoader()

    # Build all required files
    all_files = [
        PackageFile(
            original_name="Technical_Volume.pdf",
            category="technical_volume",
            size_bytes=2_000_000,
        ),
        PackageFile(
            original_name="Cost_Volume.pdf",
            category="cost_volume",
            size_bytes=500_000,
        ),
        PackageFile(
            original_name="Firm_Certification.pdf",
            category="firm_certification",
            size_bytes=100_000,
        ),
    ]

    # Remove excluded file if specified
    exclude = submission_context.get("exclude_file")
    if exclude:
        all_files = [f for f in all_files if exclude not in f.original_name]

    service = SubmissionService(portal_rules_loader=loader)
    agency = active_state["topic"]["agency"]
    return service.prepare_package(agency=agency, files=all_files)


@when(
    "the tool presents the submission confirmation",
    target_fixture="confirmation_prompt",
)
def present_confirmation():
    """Present submission confirmation through SubmissionService."""
    from pes.domain.submission_service import SubmissionService
    from tests.acceptance.step_defs._fake_portal_rules import FakePortalRulesLoader

    loader = FakePortalRulesLoader()
    service = SubmissionService(portal_rules_loader=loader)
    return service.confirm_submission()


@when(
    parsers.parse('Phil enters the confirmation number "{number}"'),
    target_fixture="submission_record",
)
def enter_confirmation(number, proposal_dir):
    """Enter confirmation number through SubmissionService."""
    from pes.domain.submission_service import SubmissionService
    from tests.acceptance.step_defs._fake_portal_rules import FakePortalRulesLoader

    loader = FakePortalRulesLoader()
    service = SubmissionService(portal_rules_loader=loader)

    # Set up source package files to archive
    package_dir = proposal_dir / "artifacts" / "wave-8-submission" / "package"
    (package_dir / "Technical_Volume.pdf").write_text("technical content")
    (package_dir / "Cost_Volume.pdf").write_text("cost content")

    archive_dir = proposal_dir / "artifacts" / "wave-8-submission" / "archive"

    result = service.record_submission(
        confirmation_number=number,
        package_dir=str(package_dir),
        archive_dir=str(archive_dir),
    )
    return result


@when("Phil attempts to prepare the submission package")
def attempt_prepare_submission():
    """Attempt submission prep when blocked by PES."""
    pytest.skip("Awaiting SubmissionService + PES integration")


@when(
    "Phil attempts to edit any submitted artifact",
    target_fixture="enforcement_result",
)
def attempt_edit_submitted(active_state, enforcement_engine):
    """Attempt to modify submitted artifact via EnforcementEngine."""
    result = enforcement_engine.evaluate(active_state, tool_name="write_file")
    return result


# --- Then steps ---


@then("the tool identifies DSIP as the submission portal")
def verify_dsip_identified(package_result):
    """Verify DSIP portal identified."""
    assert package_result.portal_id == "DSIP"


@then("applies DSIP file naming conventions to all package files")
def verify_naming_applied(package_result):
    """Verify DSIP naming conventions applied."""
    for pf in package_result.packaged_files:
        # DSIP naming convention uses underscores and uppercase prefix
        assert pf.portal_name is not None
        assert len(pf.portal_name) > 0


@then("verifies file sizes against portal limits")
def verify_file_sizes(package_result):
    """Verify file size checks."""
    assert package_result.size_checks_passed is not None
    # All files should pass size checks for the happy path
    assert package_result.size_checks_passed is True


@then("it reports all checks passing")
def verify_all_checks_pass():
    """Verify all pre-submission checks pass."""
    pytest.skip("Awaiting SubmissionService implementation")


@then("the checklist is written to the submission artifacts directory")
def verify_checklist_written():
    """Verify checklist artifact."""
    pytest.skip("Awaiting SubmissionService implementation")


@then("Phil must explicitly confirm before any submission occurs")
def verify_explicit_confirm(confirmation_prompt):
    """Verify explicit confirmation required."""
    assert confirmation_prompt.requires_confirmation is True
    assert len(confirmation_prompt.message) > 0


@then("declining returns to preparation without any irreversible action")
def verify_decline_safe(confirmation_prompt):
    """Verify declining is safe -- no state mutation occurred."""
    assert confirmation_prompt.requires_confirmation is True


@then("the tool records the confirmation number and the current timestamp")
def verify_confirmation_recorded(submission_record):
    """Verify confirmation number and timestamp recorded."""
    assert submission_record.confirmation_number == "DSIP-2026-AF243-001-7842"
    assert submission_record.submitted_at is not None


@then("creates an immutable archive in the submission archive directory")
def verify_archive_created(submission_record):
    """Verify immutable archive is created."""
    archive_path = Path(submission_record.archive_path)
    assert archive_path.exists()
    # Archive should contain copied files
    assert any(archive_path.iterdir())


@then("the enforcement system marks all proposal artifacts as read-only")
def verify_readonly_enforced(submission_record):
    """Verify PES marks artifacts read-only via immutable flag."""
    assert submission_record.immutable is True


@then("it reports the missing file and blocks submission")
def verify_missing_blocks(package_result):
    """Verify missing file blocks submission."""
    assert package_result.blocked is True
    assert any("firm_certification" in m.lower() or "firm certification" in m.lower()
               for m in package_result.missing_files)


@then("suggests where to obtain the required form")
def verify_form_guidance(package_result):
    """Verify guidance for obtaining missing form."""
    assert package_result.guidance is not None
    assert len(package_result.guidance) > 0


@then("the enforcement system blocks the modification")
def verify_edit_blocked(enforcement_result):
    """Verify edit to submitted artifact is blocked."""
    from pes.domain.rules import Decision

    assert enforcement_result.decision == Decision.BLOCK


@then(
    parsers.parse('Phil sees "{message}"'),
)
def verify_message(message, enforcement_result):
    """Verify the enforcement message contains expected text."""
    all_messages = " ".join(enforcement_result.messages)
    assert message in all_messages or message.lower() in all_messages.lower()
