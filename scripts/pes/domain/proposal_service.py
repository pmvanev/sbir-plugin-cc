"""Proposal creation service -- driving port for /proposal new flow.

Orchestrates: solicitation parsing, corpus search, Go/No-Go checkpoint,
and initial proposal state creation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from pes.domain.solicitation import SolicitationParseResult, TopicInfo
from pes.domain.state import SCHEMA_VERSION
from pes.ports.solicitation_port import SolicitationParser
from pes.ports.state_port import StateWriter


@dataclass
class CorpusMatch:
    """A past work document matching the solicitation topic."""

    path: str
    relevance_score: float


@dataclass
class FitScoring:
    """Fit assessment across three dimensions."""

    subject_matter: float | None = None
    past_performance: float | None = None
    certifications: float | None = None
    recommendation: str | None = None


@dataclass
class ProposalCreationResult:
    """Outcome of the /proposal new flow."""

    parse_result: SolicitationParseResult | None = None
    corpus_matches: list[CorpusMatch] = field(default_factory=list)
    fit_scoring: FitScoring | None = None
    state: dict[str, Any] | None = None
    error: str | None = None
    warnings: list[str] = field(default_factory=list)
    guidance: str | None = None

    @property
    def success(self) -> bool:
        return self.error is None and self.parse_result is not None and self.parse_result.success


class ProposalCreationService:
    """Driving port: creates a new proposal from solicitation text.

    Collaborators injected via constructor:
    - parser: SolicitationParser (driven port) for metadata extraction
    - state_writer: StateWriter (driven port) for persisting proposal state
    - corpus_paths: list of corpus entry paths for keyword search
    """

    def __init__(
        self,
        parser: SolicitationParser,
        state_writer: StateWriter,
        corpus_paths: list[str] | None = None,
    ) -> None:
        self._parser = parser
        self._state_writer = state_writer
        self._corpus_paths = corpus_paths or []

    def create_proposal(self, solicitation_text: str) -> ProposalCreationResult:
        """Parse solicitation and create initial proposal state.

        Returns ProposalCreationResult with parsed metadata, corpus matches,
        and initial state dict.
        """
        parse_result = self._parser.parse(solicitation_text)

        if not parse_result.success:
            return ProposalCreationResult(
                parse_result=parse_result,
                error=parse_result.error,
                guidance=(
                    "Ensure the solicitation contains extractable text. "
                    "Supported formats: plain text or text-based PDF. "
                    "Scanned image PDFs require OCR processing first."
                ),
            )

        corpus_matches = self._search_corpus(parse_result.topic)
        fit_scoring = self._compute_fit_scoring(corpus_matches)

        guidance = None
        if not self._corpus_paths:
            guidance = (
                "No corpus documents found. Consider adding past proposals "
                "to improve fit scoring accuracy."
            )

        warnings = list(parse_result.warnings) if parse_result.warnings else []

        state = self._build_initial_state(parse_result.topic)
        self._state_writer.save(state)

        return ProposalCreationResult(
            parse_result=parse_result,
            corpus_matches=corpus_matches,
            fit_scoring=fit_scoring,
            state=state,
            warnings=warnings,
            guidance=guidance,
        )

    def record_decision(
        self, state: dict[str, Any], decision: str
    ) -> dict[str, Any]:
        """Record Go/No-Go decision and update proposal state.

        Args:
            state: current proposal state dict
            decision: one of 'go', 'no-go', 'defer'

        Returns updated state dict.
        """
        updated = dict(state)
        updated["go_no_go"] = decision
        updated["updated_at"] = datetime.now(UTC).isoformat()

        if decision == "go":
            updated["current_wave"] = 1
            updated["waves"] = dict(updated.get("waves", {}))
            updated["waves"]["0"] = {
                "status": "completed",
                "completed_at": datetime.now(UTC).isoformat(),
            }
            updated["waves"]["1"] = {"status": "active", "completed_at": None}

        elif decision == "no-go":
            updated["archived"] = True
            topic_id = updated.get("topic", {}).get("id", "unknown")
            updated["archive_message"] = f"{topic_id} archived as no-go"

        self._state_writer.save(updated)
        return updated

    def _search_corpus(self, topic: TopicInfo) -> list[CorpusMatch]:
        """Search corpus paths for keyword matches against topic metadata."""
        if not self._corpus_paths:
            return []

        keywords = self._extract_keywords(topic)
        matches: list[CorpusMatch] = []

        for path in self._corpus_paths:
            path_lower = path.lower()
            score = sum(1 for kw in keywords if kw in path_lower)
            if score > 0:
                relevance = min(score / len(keywords), 1.0)
                matches.append(CorpusMatch(path=path, relevance_score=round(relevance, 2)))

        matches.sort(key=lambda m: m.relevance_score, reverse=True)
        return matches

    def _extract_keywords(self, topic: TopicInfo) -> list[str]:
        """Extract search keywords from topic metadata."""
        stop_words = {"for", "the", "a", "an", "of", "in", "to", "and", "or"}
        words = topic.title.lower().split()
        return [w for w in words if len(w) > 2 and w not in stop_words]

    def _compute_fit_scoring(self, corpus_matches: list[CorpusMatch]) -> FitScoring:
        """Compute fit scoring based on corpus matches."""
        if not corpus_matches:
            return FitScoring(
                subject_matter=0.0,
                past_performance=0.0,
                certifications=0.0,
                recommendation="insufficient_data",
            )

        avg_relevance = sum(m.relevance_score for m in corpus_matches) / len(corpus_matches)
        return FitScoring(
            subject_matter=round(avg_relevance, 2),
            past_performance=round(avg_relevance * 0.8, 2),
            certifications=round(avg_relevance * 0.5, 2),
            recommendation="go" if avg_relevance > 0.3 else "evaluate",
        )

    def _build_initial_state(self, topic: TopicInfo) -> dict[str, Any]:
        """Build initial proposal state dict from parsed topic."""
        now = datetime.now(UTC).isoformat()
        return {
            "schema_version": SCHEMA_VERSION,
            "proposal_id": f"proposal-{topic.topic_id.lower()}",
            "topic": {
                "id": topic.topic_id,
                "agency": topic.agency,
                "title": topic.title,
                "solicitation_url": None,
                "solicitation_file": None,
                "deadline": topic.deadline,
                "phase": topic.phase,
            },
            "current_wave": 0,
            "go_no_go": "pending",
            "output_format": "docx",
            "waves": {
                "0": {"status": "active", "completed_at": None},
                **{
                    str(i): {"status": "not_started", "completed_at": None}
                    for i in range(1, 10)
                },
            },
            "corpus": {
                "directories_ingested": [],
                "document_count": 0,
                "file_hashes": {},
            },
            "compliance_matrix": {
                "path": None,
                "item_count": 0,
                "generated_at": None,
            },
            "tpoc": {
                "status": "not_started",
                "questions_path": None,
                "qa_log_path": None,
                "questions_generated_at": None,
                "answers_ingested_at": None,
            },
            "strategy_brief": {
                "path": None,
                "status": "not_started",
                "approved_at": None,
            },
            "fit_scoring": {
                "subject_matter": None,
                "past_performance": None,
                "certifications": None,
                "recommendation": None,
            },
            "research_summary": {"findings": []},
            "discrimination_table": {"items": []},
            "volumes": {
                "technical": {
                    "status": "not_started",
                    "current_draft": None,
                    "review_comments": [],
                    "iterations": 0,
                },
                "management": {
                    "status": "not_started",
                    "current_draft": None,
                    "review_comments": [],
                    "iterations": 0,
                },
                "cost": {
                    "status": "not_started",
                    "current_draft": None,
                    "review_comments": [],
                    "iterations": 0,
                },
            },
            "open_review_items": [],
            "created_at": now,
            "updated_at": now,
        }
