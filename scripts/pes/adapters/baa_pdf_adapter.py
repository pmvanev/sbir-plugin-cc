"""BAA PDF adapter -- TopicFetchPort for user-provided BAA documents.

Driven port adapter: receives pre-extracted text content from a BAA PDF
(the agent reads the PDF via Claude's PDF reading, then passes the text here).
Parses structured text to extract topic metadata.
"""

from __future__ import annotations

import re
from typing import Any

from pes.ports.topic_fetch_port import FetchResult, TopicFetchPort


class BaaPdfAdapter(TopicFetchPort):
    """Extract topic metadata from pre-extracted BAA document text.

    The adapter receives plain text (not raw PDF bytes). It parses
    the text looking for topic blocks with structured fields.

    Constructor Args:
        text_content: Pre-extracted text content from a BAA PDF.
    """

    def __init__(self, text_content: str) -> None:
        self._text = text_content

    def fetch(
        self,
        filters: dict[str, str] | None = None,
        on_progress: Any | None = None,
    ) -> FetchResult:
        """Parse BAA text to extract topic metadata.

        Args:
            filters: Optional filters (not typically used for document parsing).
            on_progress: Optional progress callback.

        Returns:
            FetchResult with extracted topics and source="baa_pdf".
        """
        topics = self._parse_topics()

        if on_progress is not None:
            on_progress({"extracted": len(topics), "total": len(topics)})

        return FetchResult(
            topics=topics,
            total=len(topics),
            source="baa_pdf",
            partial=False,
            error=None,
        )

    def _parse_topics(self) -> list[dict[str, Any]]:
        """Parse topic blocks from BAA text content.

        Expected format per topic block:
            Topic Number: <id>
            Title: <title>
            Agency: <agency>
            Phase: <phase>
            Deadline: <deadline>

        Returns:
            List of topic metadata dicts.
        """
        topics: list[dict[str, Any]] = []
        current: dict[str, Any] = {}

        for line in self._text.splitlines():
            line = line.strip()
            if not line:
                if current.get("topic_id"):
                    topics.append(self._finalize_topic(current))
                    current = {}
                continue

            match = re.match(r"^(Topic Number|Title|Agency|Phase|Deadline):\s*(.+)$", line)
            if match:
                key, value = match.group(1), match.group(2).strip()
                if key == "Topic Number":
                    current["topic_id"] = value
                    current["topic_code"] = value
                elif key == "Title":
                    current["title"] = value
                elif key == "Agency":
                    current["agency"] = value
                elif key == "Phase":
                    current["phase"] = value
                elif key == "Deadline":
                    current["deadline"] = value

        # Flush last topic if text doesn't end with blank line
        if current.get("topic_id"):
            topics.append(self._finalize_topic(current))

        return topics

    @staticmethod
    def _finalize_topic(raw: dict[str, Any]) -> dict[str, Any]:
        """Fill in defaults for missing fields."""
        return {
            "topic_id": raw.get("topic_id", "UNKNOWN"),
            "topic_code": raw.get("topic_code", "UNKNOWN"),
            "title": raw.get("title", "Untitled"),
            "status": "Open",
            "program": "SBIR",
            "component": raw.get("agency", "DoD"),
            "agency": raw.get("agency", "DoD"),
            "solicitation_number": "",
            "cycle_name": "",
            "phase": raw.get("phase", "I"),
            "deadline": raw.get("deadline", "TBD"),
            "cmmc_level": "",
            "requires_clearance": "",
        }
