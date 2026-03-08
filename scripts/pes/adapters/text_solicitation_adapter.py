"""Text-based solicitation parser adapter.

Extracts structured metadata from solicitation text using pattern matching.
Does NOT call external APIs -- operates on user-provided text content.
"""

from __future__ import annotations

import re

from pes.domain.solicitation import SolicitationParseResult, TopicInfo
from pes.ports.solicitation_port import SolicitationParser

# Patterns for extracting solicitation fields
_PATTERNS: dict[str, re.Pattern[str]] = {
    "topic_id": re.compile(r"Topic\s*ID\s*:\s*(.+?)(?:\n|$)", re.IGNORECASE),
    "agency": re.compile(r"Agency\s*:\s*(.+?)(?:\n|$)", re.IGNORECASE),
    "phase": re.compile(r"Phase\s*:\s*(.+?)(?:\n|$)", re.IGNORECASE),
    "deadline": re.compile(r"Deadline\s*:\s*(.+?)(?:\n|$)", re.IGNORECASE),
    "title": re.compile(r"Title\s*:\s*(.+?)(?:\n|$)", re.IGNORECASE),
}

_REQUIRED_FIELDS = {"topic_id", "agency", "title"}
_OPTIONAL_FIELDS_WITH_WARNINGS = {"deadline": "Deadline could not be extracted from solicitation"}


class TextSolicitationAdapter(SolicitationParser):
    """Parses solicitation text for structured metadata using regex patterns."""

    def parse(self, text: str) -> SolicitationParseResult:
        """Extract metadata fields from solicitation text."""
        extracted: dict[str, str] = {}

        for field_name, pattern in _PATTERNS.items():
            match = pattern.search(text)
            if match:
                extracted[field_name] = match.group(1).strip()

        # Check if we found enough fields to consider this parseable
        found_required = _REQUIRED_FIELDS.intersection(extracted.keys())
        if len(found_required) < 2:
            return SolicitationParseResult(
                error="Could not parse solicitation: insufficient metadata found"
            )

        # Collect warnings for missing optional fields
        warnings: list[str] = []
        for field, warning_msg in _OPTIONAL_FIELDS_WITH_WARNINGS.items():
            if field not in extracted or not extracted[field]:
                warnings.append(warning_msg)

        # Default phase if missing
        phase = extracted.get("phase", "I")

        topic = TopicInfo(
            topic_id=extracted.get("topic_id", ""),
            agency=extracted.get("agency", ""),
            phase=phase,
            deadline=extracted.get("deadline", ""),
            title=extracted.get("title", ""),
        )

        return SolicitationParseResult(
            topic=topic,
            warnings=warnings if warnings else None,
        )
