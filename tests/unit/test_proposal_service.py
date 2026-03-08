"""Unit tests for proposal creation through ProposalCreationService (driving port).

Test Budget: 6 behaviors x 2 = 12 unit tests max.
Tests enter through driving port (ProposalCreationService).
SolicitationParser driven port replaced with fake.
StateWriter driven port replaced with in-memory fake.
Domain objects (TopicInfo, SolicitationParseResult) used as real collaborators.
"""

from __future__ import annotations

from typing import Any

from pes.domain.proposal_service import ProposalCreationService
from pes.domain.solicitation import SolicitationParseResult, TopicInfo
from pes.ports.solicitation_port import SolicitationParser
from pes.ports.state_port import StateWriter

# ---------------------------------------------------------------------------
# Fake driven ports
# ---------------------------------------------------------------------------


class FakeSolicitationParser(SolicitationParser):
    """Returns pre-configured parse result."""

    def __init__(self, result: SolicitationParseResult) -> None:
        self._result = result

    def parse(self, text: str) -> SolicitationParseResult:
        return self._result


class InMemoryStateWriter(StateWriter):
    """Captures saved state for assertions."""

    def __init__(self) -> None:
        self.saved_states: list[dict[str, Any]] = []

    def save(self, state: dict[str, Any]) -> None:
        self.saved_states.append(state)

    def load(self) -> dict[str, Any]:
        if not self.saved_states:
            raise FileNotFoundError
        return self.saved_states[-1]

    def exists(self) -> bool:
        return len(self.saved_states) > 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

AF243_TOPIC = TopicInfo(
    topic_id="AF243-001",
    agency="Air Force",
    phase="I",
    deadline="2026-04-15",
    title="Compact Directed Energy for Maritime UAS Defense",
)


def _make_service(
    parse_result: SolicitationParseResult | None = None,
    corpus_paths: list[str] | None = None,
) -> tuple[ProposalCreationService, InMemoryStateWriter]:
    """Wire ProposalCreationService with fakes."""
    parser = FakeSolicitationParser(
        parse_result or SolicitationParseResult(topic=AF243_TOPIC)
    )
    writer = InMemoryStateWriter()
    service = ProposalCreationService(parser, writer, corpus_paths)
    return service, writer


# ---------------------------------------------------------------------------
# Behavior 1: Parses solicitation and creates proposal state
# ---------------------------------------------------------------------------


class TestParseSolicitationAndCreateState:
    def test_creates_state_with_parsed_topic_metadata(self):
        service, _writer = _make_service()

        result = service.create_proposal("solicitation text")

        assert result.success
        topic = result.parse_result.topic
        assert topic.topic_id == "AF243-001"
        assert topic.agency == "Air Force"
        assert topic.phase == "I"
        assert topic.deadline == "2026-04-15"
        assert topic.title == "Compact Directed Energy for Maritime UAS Defense"

    def test_persists_state_with_topic_fields(self):
        service, writer = _make_service()

        service.create_proposal("solicitation text")

        assert len(writer.saved_states) == 1
        state = writer.saved_states[0]
        assert state["topic"]["id"] == "AF243-001"
        assert state["topic"]["agency"] == "Air Force"
        assert state["topic"]["phase"] == "I"
        assert state["topic"]["deadline"] == "2026-04-15"
        assert state["go_no_go"] == "pending"
        assert state["current_wave"] == 0


# ---------------------------------------------------------------------------
# Behavior 2: Corpus search finds related past work
# ---------------------------------------------------------------------------


class TestCorpusSearch:
    def test_finds_related_documents_by_keyword_matching(self):
        corpus_paths = [
            "past-proposals/directed-energy-defense.pdf",
            "past-proposals/sonar-processing.pdf",
            "past-proposals/energy-beam-system.pdf",
        ]
        service, _ = _make_service(corpus_paths=corpus_paths)

        result = service.create_proposal("solicitation text")

        # "directed" and "energy" appear in topic title, should match 2 paths
        assert len(result.corpus_matches) >= 1
        matched_paths = [m.path for m in result.corpus_matches]
        assert "past-proposals/directed-energy-defense.pdf" in matched_paths

    def test_empty_corpus_returns_no_matches_with_guidance(self):
        service, _ = _make_service(corpus_paths=[])

        result = service.create_proposal("solicitation text")

        assert len(result.corpus_matches) == 0
        assert result.guidance is not None
        assert "corpus" in result.guidance.lower() or "past" in result.guidance.lower()


# ---------------------------------------------------------------------------
# Behavior 3: Go decision records and unlocks Wave 1
# ---------------------------------------------------------------------------


class TestGoDecision:
    def test_go_decision_sets_go_and_unlocks_wave_1(self):
        service, _writer = _make_service()
        result = service.create_proposal("solicitation text")
        state = result.state

        updated = service.record_decision(state, "go")

        assert updated["go_no_go"] == "go"
        assert updated["current_wave"] == 1
        assert updated["waves"]["1"]["status"] == "active"
        assert updated["waves"]["0"]["status"] == "completed"


# ---------------------------------------------------------------------------
# Behavior 4: No-go decision archives proposal
# ---------------------------------------------------------------------------


class TestNoGoDecision:
    def test_no_go_decision_archives_proposal(self):
        service, _writer = _make_service()
        result = service.create_proposal("solicitation text")
        state = result.state

        updated = service.record_decision(state, "no-go")

        assert updated["go_no_go"] == "no-go"
        assert updated["archived"] is True

    def test_no_go_produces_archive_message(self):
        service, _writer = _make_service()
        result = service.create_proposal("solicitation text")
        state = result.state

        updated = service.record_decision(state, "no-go")

        assert updated.get("archive_message") is not None
        assert "AF243-001" in updated["archive_message"]


# ---------------------------------------------------------------------------
# Behavior 5: Unparseable solicitation produces actionable error
# ---------------------------------------------------------------------------


class TestUnparseableSolicitation:
    def test_parse_error_returns_error_with_guidance(self):
        parse_result = SolicitationParseResult(
            error="Could not parse solicitation"
        )
        service, writer = _make_service(parse_result=parse_result)

        result = service.create_proposal("BINARY_CONTENT")

        assert not result.success
        assert result.error == "Could not parse solicitation"
        assert result.guidance is not None
        assert len(writer.saved_states) == 0


# ---------------------------------------------------------------------------
# Behavior 6: Missing metadata produces warnings
# ---------------------------------------------------------------------------


class TestMissingMetadata:
    def test_missing_deadline_produces_warning(self):
        topic = TopicInfo(
            topic_id="AF243-002",
            agency="Navy",
            phase="II",
            deadline="",
            title="Advanced Sonar Processing",
        )
        parse_result = SolicitationParseResult(
            topic=topic,
            warnings=["Deadline could not be extracted from solicitation"],
        )
        service, _writer = _make_service(parse_result=parse_result)

        result = service.create_proposal("solicitation text")

        assert result.success
        assert len(result.warnings) > 0
        assert any("deadline" in w.lower() for w in result.warnings)
