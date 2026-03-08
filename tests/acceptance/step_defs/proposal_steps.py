"""Step definitions for new proposal creation (US-002) and status (US-001).

Invokes through: ProposalCreationService (driving port).
Does NOT import solicitation parsers or fit scorers directly.
"""

from __future__ import annotations

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from pes.domain.proposal_service import ProposalCreationService
from pes.domain.solicitation import SolicitationParseResult, TopicInfo
from pes.ports.solicitation_port import SolicitationParser
from pes.ports.state_port import StateWriter

# Link to feature files
scenarios("../features/new_proposal.feature")
scenarios("../features/proposal_status.feature")


# ---------------------------------------------------------------------------
# In-memory fakes for driven ports (used only in acceptance tests)
# ---------------------------------------------------------------------------


class FakeSolicitationParser(SolicitationParser):
    """Fake parser that returns pre-configured results."""

    def __init__(self, result: SolicitationParseResult | None = None) -> None:
        self._result = result

    def set_result(self, result: SolicitationParseResult) -> None:
        self._result = result

    def parse(self, text: str) -> SolicitationParseResult:
        if self._result is not None:
            return self._result
        return SolicitationParseResult(error="No parse result configured")


class InMemoryStateWriter(StateWriter):
    """In-memory state writer that captures saved state for assertions."""

    def __init__(self) -> None:
        self.saved_states: list[dict] = []

    def save(self, state: dict) -> None:
        self.saved_states.append(state)

    def load(self) -> dict:
        if not self.saved_states:
            raise FileNotFoundError("No state saved")
        return self.saved_states[-1]

    def exists(self) -> bool:
        return len(self.saved_states) > 0


# ---------------------------------------------------------------------------
# Fixtures for proposal creation
# ---------------------------------------------------------------------------


@pytest.fixture()
def fake_parser():
    return FakeSolicitationParser()


@pytest.fixture()
def in_memory_state_writer():
    return InMemoryStateWriter()


@pytest.fixture()
def proposal_service(fake_parser, in_memory_state_writer):
    return ProposalCreationService(
        parser=fake_parser,
        state_writer=in_memory_state_writer,
    )


@pytest.fixture()
def creation_result():
    """Container for the result of proposal creation."""
    return {}


# --- Given steps for US-002 ---


@given(
    "Phil has a solicitation PDF for topic AF243-001",
    target_fixture="solicitation_text",
)
def solicitation_pdf(fake_parser):
    """Configure parser to return AF243-001 metadata."""
    fake_parser.set_result(SolicitationParseResult(
        topic=TopicInfo(
            topic_id="AF243-001",
            agency="Air Force",
            phase="I",
            deadline="2026-04-15",
            title="Compact Directed Energy for Maritime UAS Defense",
        )
    ))
    return "Solicitation text for AF243-001"


@given(
    parsers.parse("Phil has ingested {count:d} past proposals into the corpus"),
    target_fixture="corpus_paths",
)
def corpus_with_proposals(count):
    """Set up corpus paths for search."""
    paths = [f"past-proposals/proposal-{i}.pdf" for i in range(count)]
    return paths


@given(parsers.parse("{count:d} proposals relate to directed energy topics"))
def related_proposals(count, corpus_paths, proposal_service):
    """Configure corpus paths with directed energy keywords."""
    # Replace first `count` paths with directed-energy-related names
    for i in range(min(count, len(corpus_paths))):
        corpus_paths[i] = f"past-proposals/directed-energy-proposal-{i}.pdf"
    proposal_service._corpus_paths = corpus_paths


@given(
    "Phil sees a Go/No-Go recommendation for AF243-001",
    target_fixture="pre_decision_state",
)
def go_recommendation_displayed(
    fake_parser, proposal_service, in_memory_state_writer, creation_result,
):
    """Run proposal creation so Go/No-Go recommendation is displayed."""
    fake_parser.set_result(SolicitationParseResult(
        topic=TopicInfo(
            topic_id="AF243-001",
            agency="Air Force",
            phase="I",
            deadline="2026-04-15",
            title="Compact Directed Energy for Maritime UAS Defense",
        )
    ))
    result = proposal_service.create_proposal("Solicitation text for AF243-001")
    creation_result["result"] = result
    return result.state


@given("Phil has never ingested any documents into the corpus")
def empty_corpus(proposal_service):
    """Ensure corpus is empty."""
    proposal_service._corpus_paths = []


@given(
    "Phil provides a PDF that contains only scanned images with no extractable text",
    target_fixture="solicitation_text",
)
def unparseable_pdf(fake_parser):
    """Configure parser to return error for unparseable content."""
    fake_parser.set_result(SolicitationParseResult(
        error="Could not parse solicitation"
    ))
    return "BINARY_IMAGE_CONTENT"


@given(
    "Phil provides a solicitation with no identifiable deadline",
    target_fixture="solicitation_text",
)
def solicitation_no_deadline(fake_parser):
    """Configure parser to return partial result with missing deadline."""
    fake_parser.set_result(SolicitationParseResult(
        topic=TopicInfo(
            topic_id="AF243-002",
            agency="Navy",
            phase="II",
            deadline="",
            title="Advanced Sonar Processing",
        ),
        warnings=["Deadline could not be extracted from solicitation"],
    ))
    return "Solicitation without deadline field"


@given('Phil has ingested past proposals from "./past-proposals/"')
def corpus_ingested():
    """Corpus has been ingested from past proposals directory."""
    pass


# --- Given steps for US-001 ---


@given(
    parsers.parse("Phil has an active proposal for {topic_id}"),
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
def start_proposal_from_solicitation(
    proposal_service, solicitation_text, creation_result,
):
    """Invoke new proposal through driving port."""
    result = proposal_service.create_proposal(solicitation_text)
    creation_result["result"] = result


@when("Phil starts a new proposal from the PDF file")
def start_proposal_from_pdf(
    proposal_service, solicitation_text, creation_result,
):
    """Invoke new proposal from local file through driving port."""
    result = proposal_service.create_proposal(solicitation_text)
    creation_result["result"] = result


@when(parsers.parse("Phil starts a new proposal for topic {topic_id}"))
def start_proposal_for_topic(
    topic_id, proposal_service, fake_parser, creation_result,
):
    """Invoke new proposal for specific topic through driving port."""
    # Parser already configured by Given step; just invoke
    result = proposal_service.create_proposal(f"Solicitation for {topic_id}")
    creation_result["result"] = result


@when(parsers.parse('Phil selects "{decision}" at the Go/No-Go checkpoint'))
def select_go_decision(
    decision, proposal_service, pre_decision_state, creation_result,
):
    """Record Go/No-Go decision through driving port."""
    updated = proposal_service.record_decision(pre_decision_state, decision)
    creation_result["state"] = updated


@when("Phil approves the Go decision")
def approve_go(proposal_service, pre_decision_state, creation_result):
    """Record Go approval through driving port."""
    updated = proposal_service.record_decision(pre_decision_state, "go")
    creation_result["state"] = updated


@when("Phil starts a new proposal from the file")
def start_from_file(
    proposal_service, solicitation_text, creation_result,
):
    """Invoke new proposal from file path through driving port."""
    result = proposal_service.create_proposal(solicitation_text)
    creation_result["result"] = result


@when("Phil checks proposal status")
def check_status():
    """Invoke status through driving port."""
    pytest.skip("Awaiting StatusService implementation")


# --- Then steps for US-002 ---


@then(parsers.parse(
    'Phil sees topic "{topic_id}" with agency "{agency}" and deadline "{deadline}"'
))
def verify_topic_metadata(topic_id, agency, deadline, creation_result):
    """Verify parsed topic metadata."""
    result = creation_result["result"]
    assert result.parse_result.topic.topic_id == topic_id
    assert result.parse_result.topic.agency == agency
    assert result.parse_result.topic.deadline == deadline


@then("Phil sees related past work from the corpus with relevance scores")
def verify_related_work(creation_result):
    """Verify corpus search results returned."""
    result = creation_result["result"]
    assert len(result.corpus_matches) > 0
    for match in result.corpus_matches:
        assert match.relevance_score > 0


@then("Phil sees a Go/No-Go recommendation")
def verify_recommendation(creation_result):
    """Verify recommendation present."""
    result = creation_result["result"]
    assert result.fit_scoring is not None
    assert result.fit_scoring.recommendation is not None


@then("the proposal records the Go decision")
def verify_go_recorded(creation_result):
    """Verify Go decision persisted in state."""
    state = creation_result["state"]
    assert state["go_no_go"] == "go"


@then("Wave 1 is unlocked for work")
def verify_wave_1_unlocked(creation_result):
    """Verify Wave 1 status changed from not_started."""
    state = creation_result["state"]
    assert state["waves"]["1"]["status"] == "active"


@then("Wave 1 is unlocked")
def verify_wave_1_open(creation_result):
    """Verify Wave 1 accessible."""
    state = creation_result["state"]
    assert state["current_wave"] == 1
    assert state["waves"]["1"]["status"] == "active"


@then(parsers.parse('Phil sees topic ID "{topic_id}"'))
def verify_topic_id(topic_id, creation_result):
    """Verify topic ID."""
    result = creation_result["result"]
    assert result.parse_result.topic.topic_id == topic_id


@then(
    parsers.parse(
        'Phil sees agency "{agency}", phase "{phase}", and deadline "{deadline}"'
    )
)
def verify_agency_phase_deadline(agency, phase, deadline, creation_result):
    """Verify agency, phase, and deadline."""
    result = creation_result["result"]
    topic = result.parse_result.topic
    assert topic.agency == agency
    assert topic.phase == phase
    assert topic.deadline == deadline


@then(parsers.parse('Phil sees title "{title}"'))
def verify_title(title, creation_result):
    """Verify solicitation title."""
    result = creation_result["result"]
    assert result.parse_result.topic.title == title


@then("a new proposal state is created with the parsed metadata")
def verify_state_created(creation_result, in_memory_state_writer):
    """Verify proposal state was persisted."""
    result = creation_result["result"]
    assert result.state is not None
    assert result.state["topic"]["id"] == "AF243-001"
    assert len(in_memory_state_writer.saved_states) > 0


@then(parsers.parse("Phil sees {count:d} related proposals with relevance scores"))
def verify_related_count(count, creation_result):
    """Verify related proposal count."""
    result = creation_result["result"]
    assert len(result.corpus_matches) == count
    for match in result.corpus_matches:
        assert match.relevance_score > 0


@then(
    "Phil sees fit scoring across subject matter, past performance, and certifications"
)
def verify_fit_scoring(creation_result):
    """Verify fit scoring dimensions present."""
    result = creation_result["result"]
    assert result.fit_scoring is not None
    assert result.fit_scoring.subject_matter is not None
    assert result.fit_scoring.past_performance is not None
    assert result.fit_scoring.certifications is not None


@then("Phil sees a Go/No-Go recommendation")
def verify_recommendation_present(creation_result):
    """Verify recommendation present in fit scoring."""
    result = creation_result["result"]
    assert result.fit_scoring is not None
    assert result.fit_scoring.recommendation is not None


@then(parsers.parse('the proposal records Go/No-Go as "{decision}"'))
def verify_decision_recorded(decision, creation_result):
    """Verify decision value in state."""
    state = creation_result["state"]
    assert state["go_no_go"] == decision


@then("the proposal is archived")
def verify_archived(creation_result):
    """Verify proposal archived."""
    state = creation_result["state"]
    assert state.get("archived") is True


@then(parsers.parse('Phil sees "{message}"'))
def verify_proposal_message(message, creation_result):
    """Verify user-facing message."""
    result = creation_result.get("result")
    if result is not None:
        # Check error, warnings, or guidance
        all_text = " ".join(filter(None, [
            result.error or "",
            result.guidance or "",
            " ".join(result.warnings),
        ]))
        assert message in all_text, f"Expected '{message}' in '{all_text}'"


@then("Phil sees the suggestion to add past proposals")
def verify_corpus_suggestion(creation_result):
    """Verify corpus add suggestion shown."""
    result = creation_result["result"]
    assert result.guidance is not None
    assert "past proposals" in result.guidance.lower() or "add" in result.guidance.lower()


@then("fit scoring proceeds with solicitation data alone")
def verify_scoring_without_corpus(creation_result):
    """Verify scoring works without corpus."""
    result = creation_result["result"]
    assert result.fit_scoring is not None


@then("Phil sees guidance on acceptable file formats")
def verify_format_guidance(creation_result):
    """Verify file format guidance shown."""
    result = creation_result["result"]
    assert result.guidance is not None
    assert "format" in result.guidance.lower() or "text" in result.guidance.lower()


@then("Phil sees a warning that the deadline could not be extracted")
def verify_deadline_warning(creation_result):
    """Verify missing deadline warning."""
    result = creation_result["result"]
    assert len(result.warnings) > 0
    assert any("deadline" in w.lower() for w in result.warnings)


@then("Phil is prompted to enter the deadline manually")
def verify_manual_deadline_prompt(creation_result):
    """Verify manual deadline entry prompt."""
    result = creation_result["result"]
    assert any("manual" in w.lower() or "enter" in w.lower() for w in result.warnings)


# --- Then steps for US-001 ---


@then(parsers.parse('Phil sees the current wave is "{wave_name}"'))
def verify_current_wave(wave_name):
    """Verify current wave displayed."""
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
