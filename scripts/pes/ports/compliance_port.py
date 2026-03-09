"""Port interface for compliance extraction.

Driven port: ComplianceExtractor
Adapters implement this to extract requirements from solicitation text.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from pes.domain.compliance import ComplianceItem


class ComplianceExtractor(ABC):
    """Extract compliance items from solicitation text -- driven port."""

    @abstractmethod
    def extract(self, text: str) -> list[ComplianceItem]:
        """Extract requirements from solicitation text.

        Returns list of ComplianceItem with requirement type, text,
        and proposed section mapping.
        """
