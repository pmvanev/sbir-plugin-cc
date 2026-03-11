"""Port interface for loading portal-specific submission rules.

Driven port: PortalRulesLoader
Adapters implement this to load portal rules from specific sources (JSON files, etc.).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from pes.domain.submission import PortalRules


class PortalRulesLoader(ABC):
    """Load portal-specific submission rules -- driven port."""

    @abstractmethod
    def load_rules_for_portal(self, portal_id: str) -> PortalRules | None:
        """Load rules for a specific submission portal.

        Returns PortalRules if found, None if no rules exist for the portal.
        """

    @abstractmethod
    def identify_portal(self, agency: str) -> str | None:
        """Identify the submission portal for a given agency.

        Returns portal ID string (e.g., 'DSIP', 'NSPIRES', 'Grants.gov')
        or None if agency is not recognized.
        """
