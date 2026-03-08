"""Port interface for solicitation parsing.

Driven port: SolicitationParser
Adapters implement this to extract metadata from solicitation text.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from pes.domain.solicitation import SolicitationParseResult


class SolicitationParser(ABC):
    """Parse solicitation text to extract structured metadata -- driven port."""

    @abstractmethod
    def parse(self, text: str) -> SolicitationParseResult:
        """Parse solicitation text and return structured metadata.

        Returns SolicitationParseResult with topic info or error details.
        """
