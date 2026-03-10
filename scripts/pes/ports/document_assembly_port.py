"""Port interface for document assembly.

Driven port: DocumentAssembler
Adapters implement this to assemble proposal volumes from formatted sections.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class AssembledVolume:
    """A single assembled proposal volume."""

    volume_number: int
    title: str
    content: str
    page_count: int


class DocumentAssembler(ABC):
    """Assemble proposal volumes from formatted content -- driven port."""

    @abstractmethod
    def assemble_volumes(
        self, *, sections: list[str], format_template_agency: str
    ) -> list[AssembledVolume]:
        """Assemble formatted sections into proposal volumes.

        Returns list of AssembledVolume objects.
        """
