"""Port interface for template loading.

Driven port: TemplateLoader
Adapters implement this to load template content by name.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class TemplateLoader(ABC):
    """Load template content by name -- driven port."""

    @abstractmethod
    def load_template(self, name: str) -> str:
        """Load and return the content of the named template.

        Raises:
            FileNotFoundError: if the template does not exist.
        """
