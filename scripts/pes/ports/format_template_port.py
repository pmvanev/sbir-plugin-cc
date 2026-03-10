"""Port interface for loading format templates.

Driven port: FormatTemplateLoader
Adapters implement this to load format templates from specific sources (JSON files, etc.).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from pes.domain.formatting import FormatTemplate


class FormatTemplateLoader(ABC):
    """Load format templates by agency and solicitation type -- driven port."""

    @abstractmethod
    def load_template(
        self, *, agency: str, solicitation_type: str
    ) -> FormatTemplate | None:
        """Load a format template for the given agency and solicitation type.

        Returns FormatTemplate if found, None if no template exists.
        """
