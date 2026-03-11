"""Port interface for debrief parsing.

Driven port: DebriefParser
Adapters implement this to extract structured data from debrief text.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from pes.domain.debrief import DebriefParseResult


class DebriefParser(ABC):
    """Parse debrief text to extract scores, critiques, and structure -- driven port."""

    @abstractmethod
    def parse(self, text: str) -> DebriefParseResult:
        """Parse debrief text and return structured parse result.

        Returns DebriefParseResult with scores, critiques, confidence,
        and freeform text fallback.
        """
