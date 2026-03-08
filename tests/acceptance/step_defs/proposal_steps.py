"""Step definitions for new proposal creation (US-002) and status (US-001).

Invokes through: Proposal creation service, status service (driving ports).
Does NOT import solicitation parsers or fit scorers directly.
"""

from __future__ import annotations

import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# Link to feature files
scenarios("../features/new_proposal.feature")
scenarios("../features/proposal_status.feature")


# --- Given steps for US-002 ---


@given("Phil has a solicitation PDF for topic AF243-001")
def solicitation_pdf(tmp_path):
    """Create a mock solicitation PDF file."""
    pdf_path = tmp_path / "solicitations" / "AF243-001.pdf"
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    pdf_path.write_text("Mock solicitation content for AF243-001")
    return pdf_path


@given(parsers.parse("Phil has ingested {count:d} past proposals into the corpus"))
def corpus_with_proposals(count):
    """Set up corpus with ingested proposals."""
    # TODO: Set up corpus state with ingested documents
    pass


@given(parsers.parse("{count:d} proposals relate to directed energy topics"))
def related_proposals(count):
    """Mark proposals as related to current topic."""
    pass


@given("Phil sees a Go/No-Go recommendation for AF243-001")
def go_recommendation_displayed():
    """Go/No-Go recommendation has been displayed."""
    pass


@given("Phil has never ingested any documents into the corpus")
def empty_corpus():
    """Ensure corpus is empty."""
    pass


@given("Phil provides a PDF that contains only scanned images with no extractable text")
def unparseable_pdf(tmp_path):
    """Create a mock unparseable PDF."""
    pdf_path = tmp_path / "bad-solicitation.pdf"
    pdf_path.write_text("BINARY_IMAGE_CONTENT")
    return pdf_path


@given("Phil provides a solicitation with no identifiable deadline")
def solicitation_no_deadline(tmp_path):
    """Create solicitation missing deadline metadata."""
    pdf_path = tmp_path / "no-deadline.pdf"
    pdf_path.write_text("Solicitation without deadline field")
    return pdf_path


@given("Phil has ingested past proposals from \"./past-proposals/\"")
def corpus_ingested():
    """Corpus has been ingested from past proposals directory."""
    pass


# --- Given steps for US-001 ---


@given(
    parsers.parse(
        "Phil has an active proposal for {topic_id}"
    ),
)
def active_proposal_for_topic(sample_state, write_state, topic_id):
    """Set up active proposal for given topic."""
    state = sample_state.copy()
    state["topic"]["id"] = topic_id
    write_state(state)


@given(parsers.parse("the compliance matrix has {count:d} items"))
def matrix_item_count(active_state, write_state, count):
    """Set compliance matrix item count."""
    active_state["compliance_matrix"]["item_count"] = count
    write_state(active_state)


@given(
    parsers.parse(
        'TPOC questions were generated {days:d} days ago with status "pending"'
    ),
)
def tpoc_pending(active_state, write_state, days):
    """Set TPOC status to pending with generation date."""
    from datetime import datetime, timedelta

    generated_at = datetime.now() - timedelta(days=days)
    active_state["tpoc"]["status"] = "questions_generated"
    active_state["tpoc"]["questions_generated_at"] = generated_at.isoformat()
    write_state(active_state)


@given("Phil has an active proposal with Wave 0 completed with Go approved")
def wave_0_completed(state_with_go, write_state):
    """Set up proposal with Wave 0 completed."""
    write_state(state_with_go)


@given("Wave 1 is active with strategy brief not yet started")
def wave_1_active(state_with_go):
    """Ensure Wave 1 is active, strategy not started."""
    state_with_go["strategy_brief"]["status"] = "not_started"


# --- When steps ---


@when("Phil starts a new proposal from the solicitation")
def start_proposal_from_solicitation():
    """Invoke new proposal through driving port."""
    # TODO: Invoke through ProposalCreationService
    pytest.skip("Awaiting ProposalCreationService implementation")


@when("Phil starts a new proposal from the PDF file")
def start_proposal_from_pdf():
    """Invoke new proposal from local file."""
    # TODO: Invoke through ProposalCreationService
    pytest.skip("Awaiting ProposalCreationService implementation")


@when(parsers.parse("Phil starts a new proposal for topic {topic_id}"))
def start_proposal_for_topic(topic_id):
    """Invoke new proposal for specific topic."""
    # TODO: Invoke through ProposalCreationService
    pytest.skip("Awaiting ProposalCreationService implementation")


@when(parsers.parse('Phil selects "{decision}" at the Go/No-Go checkpoint'))
def select_go_decision(decision):
    """Record Go/No-Go decision through driving port."""
    # TODO: Invoke through CheckpointService
    pytest.skip("Awaiting CheckpointService implementation")


@when("Phil approves the Go decision")
def approve_go():
    """Record Go approval."""
    # TODO: Invoke through CheckpointService
    pytest.skip("Awaiting CheckpointService implementation")


@when("Phil starts a new proposal from the file")
def start_from_file():
    """Invoke new proposal from file path."""
    # TODO: Invoke through ProposalCreationService
    pytest.skip("Awaiting ProposalCreationService implementation")


@when("Phil checks proposal status")
def check_status():
    """Invoke status through driving port."""
    # TODO: Invoke through StatusService
    pytest.skip("Awaiting StatusService implementation")


# --- Then steps for US-002 ---


@then(parsers.parse('Phil sees topic "{topic_id}" with agency "{agency}" and deadline "{deadline}"'))
def verify_topic_metadata(topic_id, agency, deadline):
    """Verify parsed topic metadata displayed."""
    pass


@then("Phil sees related past work from the corpus with relevance scores")
def verify_related_work():
    """Verify corpus search results shown."""
    pass


@then("Phil sees a Go/No-Go recommendation")
def verify_recommendation():
    """Verify recommendation displayed."""
    pass


@then("the proposal records the Go decision")
def verify_go_recorded():
    """Verify Go decision persisted in state."""
    pass


@then("Wave 1 is unlocked for work")
def verify_wave_1_unlocked():
    """Verify Wave 1 status changed from not_started."""
    pass


@then("Wave 1 is unlocked")
def verify_wave_1_open():
    """Verify Wave 1 accessible."""
    pass


@then(parsers.parse('Phil sees topic ID "{topic_id}"'))
def verify_topic_id(topic_id):
    """Verify topic ID displayed."""
    pass


@then(
    parsers.parse(
        'Phil sees agency "{agency}", phase "{phase}", and deadline "{deadline}"'
    )
)
def verify_agency_phase_deadline(agency, phase, deadline):
    """Verify agency, phase, and deadline displayed."""
    pass


@then(parsers.parse('Phil sees title "{title}"'))
def verify_title(title):
    """Verify solicitation title displayed."""
    pass


@then("a new proposal state is created with the parsed metadata")
def verify_state_created():
    """Verify proposal-state.json created."""
    pass


@then(parsers.parse("Phil sees {count:d} related proposals with relevance scores"))
def verify_related_count(count):
    """Verify related proposal count."""
    pass


@then(
    "Phil sees fit scoring across subject matter, past performance, and certifications"
)
def verify_fit_scoring():
    """Verify fit scoring dimensions displayed."""
    pass


@then(parsers.parse('the proposal records Go/No-Go as "{decision}"'))
def verify_decision_recorded(decision):
    """Verify decision value in state."""
    pass


@then("the proposal is archived")
def verify_archived():
    """Verify proposal archived."""
    pass


@then(parsers.parse('Phil sees "{message}"'))
def verify_proposal_message(message):
    """Verify user-facing message."""
    pass


@then("Phil sees the suggestion to add past proposals")
def verify_corpus_suggestion():
    """Verify corpus add suggestion shown."""
    pass


@then("fit scoring proceeds with solicitation data alone")
def verify_scoring_without_corpus():
    """Verify scoring works without corpus."""
    pass


@then("Phil sees guidance on acceptable file formats")
def verify_format_guidance():
    """Verify file format guidance shown."""
    pass


@then("Phil sees a warning that the deadline could not be extracted")
def verify_deadline_warning():
    """Verify missing deadline warning."""
    pass


@then("Phil is prompted to enter the deadline manually")
def verify_manual_deadline_prompt():
    """Verify manual deadline entry prompt."""
    pass


# --- Then steps for US-001 ---


@then(parsers.parse('Phil sees the current wave is "{wave_name}"'))
def verify_current_wave(wave_name):
    """Verify current wave displayed."""
    pass


@then(parsers.parse('Phil sees "{info}"'))
def verify_info(info):
    """Generic info verification."""
    pass


@then(parsers.parse('Phil sees the suggested next action "{action}"'))
def verify_next_action(action):
    """Verify suggested action displayed."""
    pass


@then(parsers.parse('Wave 0 shows as completed with "{detail}"'))
def verify_wave_0_completed(detail):
    """Verify Wave 0 completion detail."""
    pass


@then("Wave 1 shows as active with detail for each sub-task")
def verify_wave_1_detail():
    """Verify Wave 1 active detail."""
    pass


@then('subsequent waves show as "not started"')
def verify_subsequent_waves():
    """Verify later waves show not started."""
    pass


@then(parsers.parse('Phil sees a deadline warning "{warning}"'))
def verify_deadline_warning_message(warning):
    """Verify specific deadline warning text."""
    pass


@then("Phil sees suggestions to prioritize the highest-impact incomplete work")
def verify_priority_suggestions():
    """Verify prioritization suggestions shown."""
    pass
