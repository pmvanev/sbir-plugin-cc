"""Port interface for per-topic detail enrichment.

Driven port: TopicEnrichmentPort
Defines the business contract for enriching topics with descriptions,
submission instructions, component instructions, and Q&A data.
Adapters implement this for specific infrastructure (DSIP PDF download, etc.).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class EnrichmentResult:
    """Result of enriching a batch of topics.

    Attributes:
        enriched: List of successfully enriched topic data dicts.
            Each dict contains: topic_id, description, instructions,
            component_instructions, qa_entries.
        errors: List of error records for failed topics.
            Each dict contains: topic_id, error (description string).
        completeness: Dict with counts: descriptions, instructions, qa, total.
    """

    enriched: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)
    completeness: dict[str, int] = field(default_factory=dict)


class TopicEnrichmentPort(ABC):
    """Abstract interface for per-topic detail enrichment."""

    @abstractmethod
    def enrich(
        self,
        topics: list[dict[str, Any]],
        on_progress: Any | None = None,
    ) -> EnrichmentResult:
        """Enrich topics by fetching and extracting detail data.

        Downloads per-topic detail documents, extracts description,
        submission instructions, component instructions, and Q&A entries.

        Per-topic failures are isolated: logged in errors, do not stop batch.
        Progress callback invoked per topic with status updates.

        Args:
            topics: List of topic dicts containing at minimum topic_id,
                plus cycle_name, release_number, component,
                published_qa_count, baa_instructions.
            on_progress: Optional callback invoked per topic with a dict
                containing: index, total, topic_id, status.

        Returns:
            EnrichmentResult with enriched data, errors, and completeness metrics.
        """
