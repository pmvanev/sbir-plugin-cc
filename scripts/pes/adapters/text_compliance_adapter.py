"""Regex-based compliance extraction adapter.

Extracts shall-statements, format requirements, and implicit requirements
from solicitation text using pattern matching.
"""

from __future__ import annotations

import re

from pes.domain.compliance import ComplianceItem, RequirementType
from pes.ports.compliance_port import ComplianceExtractor

_SHALL_PATTERN = re.compile(
    r"([^.]*\bshall\b[^.]*\.)", re.IGNORECASE
)

_FORMAT_KEYWORDS = r"must use|shall not exceed|font|page limit|format"
_FORMAT_PATTERNS = [
    re.compile(rf"([^.]*\b(?:{_FORMAT_KEYWORDS})\b[^.]*\.)", re.IGNORECASE),
    re.compile(
        r"([^.]*\b(?:margin|spacing|submission format)\b[^.]*\.)",
        re.IGNORECASE,
    ),
]

_EVAL_KEYWORDS = r"evaluation criteria|will be evaluated|assessed based on"
_IMPLICIT_PATTERNS = [
    re.compile(rf"([^.]*\b(?:{_EVAL_KEYWORDS})\b[^.]*\.)", re.IGNORECASE),
    re.compile(
        r"([^.]*\b(?:offerors are expected|expected to demonstrate)\b[^.]*\.)",
        re.IGNORECASE,
    ),
]

_SECTION_MAP: dict[str, str] = {
    "technical": "Technical Volume",
    "cost": "Cost Volume",
    "management": "Management Volume",
    "risk": "Technical Volume",
    "prototype": "Technical Volume",
    "schedule": "Management Volume",
    "budget": "Cost Volume",
    "personnel": "Management Volume",
}


class TextComplianceAdapter(ComplianceExtractor):
    """Extracts compliance items from solicitation text using regex patterns."""

    def extract(self, text: str) -> list[ComplianceItem]:
        """Extract requirements from solicitation text."""
        items: list[ComplianceItem] = []
        seen_texts: set[str] = set()
        item_id = 1

        # Extract shall-statements
        for match in _SHALL_PATTERN.finditer(text):
            normalized = match.group(1).strip()
            if normalized not in seen_texts:
                seen_texts.add(normalized)
                section = self._infer_section(normalized)
                # Check if it's also a format requirement
                req_type = RequirementType.SHALL
                if any(p.search(normalized) for p in _FORMAT_PATTERNS):
                    req_type = RequirementType.FORMAT
                items.append(ComplianceItem(
                    item_id=item_id,
                    text=normalized,
                    requirement_type=req_type,
                    proposal_section=section,
                ))
                item_id += 1

        # Extract format requirements not already captured
        for pattern in _FORMAT_PATTERNS:
            for match in pattern.finditer(text):
                normalized = match.group(1).strip()
                if normalized not in seen_texts:
                    seen_texts.add(normalized)
                    items.append(ComplianceItem(
                        item_id=item_id,
                        text=normalized,
                        requirement_type=RequirementType.FORMAT,
                        proposal_section="All Sections",
                    ))
                    item_id += 1

        # Extract implicit requirements
        for pattern in _IMPLICIT_PATTERNS:
            for match in pattern.finditer(text):
                normalized = match.group(1).strip()
                if normalized not in seen_texts:
                    seen_texts.add(normalized)
                    section = self._infer_section(normalized)
                    items.append(ComplianceItem(
                        item_id=item_id,
                        text=normalized,
                        requirement_type=RequirementType.IMPLICIT,
                        proposal_section=section,
                        ambiguity=(
                            "Implicit from evaluation criteria"
                            " -- verify weighting and scope"
                        ),
                    ))
                    item_id += 1

        return items

    def _infer_section(self, text: str) -> str | None:
        """Map requirement text to a proposal section based on keywords."""
        text_lower = text.lower()

        # Check for explicit section references
        section_match = re.search(r"[Ss]ection\s+(\d+)", text)
        if section_match:
            return f"Section {section_match.group(1)}"

        # Keyword-based mapping
        for keyword, section in _SECTION_MAP.items():
            if keyword in text_lower:
                return section

        return None
