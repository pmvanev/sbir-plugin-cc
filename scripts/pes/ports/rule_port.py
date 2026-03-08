"""Port interface for loading enforcement rules.

Driven port: RuleLoader
Adapters implement this to load rules from specific sources (JSON config, etc.).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pes.domain.rules import EnforcementRule


class RuleLoader(ABC):
    """Load enforcement rules -- driven port."""

    @abstractmethod
    def load_rules(self) -> list[EnforcementRule]:
        """Load all enforcement rules from configuration.

        Returns list of EnforcementRule objects.
        If config is missing, returns default rules.
        """
