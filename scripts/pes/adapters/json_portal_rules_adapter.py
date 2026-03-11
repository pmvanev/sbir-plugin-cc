"""JSON portal rules adapter -- loads portal rules from JSON files.

Implements PortalRulesLoader port using JSON files in a templates directory.
New portal rules added by creating a JSON file -- no code changes required.
"""

from __future__ import annotations

import json
from pathlib import Path

from pes.domain.submission import PortalRules
from pes.ports.portal_rules_port import PortalRulesLoader


class JsonPortalRulesAdapter(PortalRulesLoader):
    """Load portal rules from JSON files in a directory.

    File naming convention: {portal_id_lowercase}.json
    Example: dsip.json, grants-gov.json, nspires.json

    Each JSON file defines agency patterns, naming conventions,
    size limits, required files, and guidance text.
    """

    def __init__(self, templates_dir: str | Path) -> None:
        self._templates_dir = Path(templates_dir)
        self._cache: dict[str, PortalRules] = {}
        self._agency_map: dict[str, str] = {}
        self._loaded = False

    def _ensure_loaded(self) -> None:
        """Load all portal rule files on first access."""
        if self._loaded:
            return
        self._loaded = True

        if not self._templates_dir.exists():
            return

        for filepath in self._templates_dir.glob("*.json"):
            text = filepath.read_text(encoding="utf-8")
            data = json.loads(text)

            rules = PortalRules(
                portal_id=data["portal_id"],
                agency_patterns=data["agency_patterns"],
                naming_convention=data["naming_convention"],
                max_file_size_mb=data["max_file_size_mb"],
                required_files=data["required_files"],
                guidance=data.get("guidance", {}),
            )
            self._cache[rules.portal_id] = rules
            for pattern in rules.agency_patterns:
                self._agency_map[pattern] = rules.portal_id

    def load_rules_for_portal(self, portal_id: str) -> PortalRules | None:
        """Load rules for a specific submission portal.

        Returns PortalRules if found, None if no rules exist.
        """
        self._ensure_loaded()
        return self._cache.get(portal_id)

    def identify_portal(self, agency: str) -> str | None:
        """Identify the submission portal for a given agency.

        Returns portal ID or None if agency not recognized.
        """
        self._ensure_loaded()
        return self._agency_map.get(agency)
