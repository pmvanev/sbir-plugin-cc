"""Topic pursue service -- driving port for topic pursuit and handoff.

Application service that reads finder results, validates topic eligibility
(deadline not expired), and returns TopicInfo for proposal creation handoff.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from pes.ports.finder_results_port import FinderResultsPort


class TopicNotFoundError(Exception):
    """Raised when the requested topic ID is not in finder results."""


class TopicExpiredError(Exception):
    """Raised when the requested topic's deadline has passed."""


@dataclass(frozen=True)
class PursueResult:
    """Result of a successful topic pursuit -- TopicInfo for proposal handoff."""

    topic_id: str
    title: str
    agency: str
    phase: str
    deadline: str
    composite_score: float
    recommendation: str


class TopicPursueService:
    """Application service for pursuing a scored topic.

    Driving port: pursue(topic_id)
    Driven ports: FinderResultsPort (results persistence)
    """

    def __init__(self, results_port: FinderResultsPort) -> None:
        self._results_port = results_port

    def pursue(self, topic_id: str) -> PursueResult:
        """Pursue a topic by ID from persisted finder results.

        Args:
            topic_id: The topic identifier to pursue.

        Returns:
            PursueResult with topic metadata for proposal handoff.

        Raises:
            TopicNotFoundError: If topic ID not found or no results exist.
            TopicExpiredError: If topic deadline has passed.
        """
        results = self._results_port.read()
        if results is None:
            raise TopicNotFoundError(
                f"No finder results found -- run solicitation finder first"
            )

        topic_entry = self._find_topic(results, topic_id)
        if topic_entry is None:
            raise TopicNotFoundError(
                f"Topic '{topic_id}' not found in finder results"
            )

        self._check_deadline(topic_entry)

        return PursueResult(
            topic_id=topic_entry["topic_id"],
            title=topic_entry["title"],
            agency=topic_entry["agency"],
            phase=topic_entry["phase"],
            deadline=topic_entry["deadline"],
            composite_score=topic_entry["composite_score"],
            recommendation=topic_entry["recommendation"],
        )

    def _find_topic(
        self, results: dict[str, Any], topic_id: str
    ) -> dict[str, Any] | None:
        """Find a topic entry by ID in the results list."""
        for entry in results.get("results", []):
            if entry.get("topic_id") == topic_id:
                return entry
        return None

    def _check_deadline(self, topic_entry: dict[str, Any]) -> None:
        """Raise TopicExpiredError if the topic deadline has passed."""
        deadline_str = topic_entry.get("deadline", "")
        if not deadline_str:
            return
        try:
            deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            if deadline < today:
                raise TopicExpiredError(
                    f"Topic deadline has expired ({deadline_str})"
                )
        except ValueError:
            # If deadline can't be parsed, don't block pursuit
            pass
