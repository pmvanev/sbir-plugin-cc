"""Text-based debrief parser adapter.

Extracts structured data from debrief text using pattern matching.
Does NOT call external APIs -- operates on user-provided text content.
"""

from __future__ import annotations

import re

from pes.domain.debrief import CritiqueMapping, DebriefParseResult, ReviewerScore
from pes.ports.debrief_parser_port import DebriefParser

# Score patterns: "Category: X/Y" or "Category: X.X/Y.Y"
_SCORE_PATTERN = re.compile(
    r"^\s*([A-Za-z][A-Za-z &/-]+?):\s*(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)",
    re.MULTILINE,
)

# Critique patterns: "N. Section X.Y (Title), Page Z: comment"
_CRITIQUE_PATTERN = re.compile(
    r"^\s*\d+\.\s*Section\s+(\S+)\s*\([^)]*\),?\s*Page\s+(\d+)\s*:\s*(.+?)(?:\n|$)",
    re.MULTILINE,
)


class TextDebriefParserAdapter(DebriefParser):
    """Parses debrief text for scores, critiques, and structure using regex patterns."""

    def parse(self, text: str) -> DebriefParseResult:
        """Extract structured data from debrief text."""
        scores = self._extract_scores(text)
        critiques = self._extract_critiques(text)

        is_structured = len(scores) > 0 or len(critiques) > 0

        if is_structured:
            confidence = self._calculate_confidence(scores, critiques)
            return DebriefParseResult(
                scores=scores,
                critiques=critiques,
                parsing_confidence=confidence,
                is_structured=True,
            )

        # Freeform fallback -- preserve the full text
        return DebriefParseResult(
            scores=[],
            critiques=[],
            freeform_text=text.strip(),
            parsing_confidence=0.2,
            is_structured=False,
        )

    def _extract_scores(self, text: str) -> list[ReviewerScore]:
        """Extract reviewer scores from text."""
        scores: list[ReviewerScore] = []
        for match in _SCORE_PATTERN.finditer(text):
            category = match.group(1).strip()
            score = float(match.group(2))
            max_score = float(match.group(3))
            scores.append(ReviewerScore(category=category, score=score, max_score=max_score))
        return scores

    def _extract_critiques(self, text: str) -> list[CritiqueMapping]:
        """Extract critique mappings from text."""
        critiques: list[CritiqueMapping] = []
        for match in _CRITIQUE_PATTERN.finditer(text):
            section = match.group(1).strip()
            page = int(match.group(2))
            comment = match.group(3).strip()
            critiques.append(CritiqueMapping(section=section, page=page, comment=comment))
        return critiques

    def _calculate_confidence(
        self, scores: list[ReviewerScore], critiques: list[CritiqueMapping]
    ) -> float:
        """Calculate parsing confidence based on extraction completeness."""
        # Base confidence from having scores and critiques
        confidence = 0.0
        if scores:
            confidence += 0.45
        if critiques:
            confidence += 0.40
        # Bonus for having both
        if scores and critiques:
            confidence = max(confidence, 0.85)
        return min(confidence, 1.0)
