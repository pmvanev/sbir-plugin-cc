"""JSON config adapter for loading enforcement rules.

Implements RuleLoader port using pes-config.json files.
"""

from __future__ import annotations

import json
from pathlib import Path

from pes.domain.rules import EnforcementRule
from pes.ports.rule_port import RuleLoader


class JsonRuleAdapter(RuleLoader):
    """Load enforcement rules from a JSON config file."""

    def __init__(self, config_path: str) -> None:
        self._config_path = Path(config_path)

    def load_rules(self) -> list[EnforcementRule]:
        """Load rules from pes-config.json.

        Returns default empty rules if config file is missing.
        """
        if not self._config_path.exists():
            return []

        text = self._config_path.read_text(encoding="utf-8")
        config = json.loads(text)

        raw_rules = config.get("rules", [])
        return [
            EnforcementRule(
                rule_id=r["rule_id"],
                description=r["description"],
                rule_type=r["rule_type"],
                condition=r["condition"],
                message=r["message"],
            )
            for r in raw_rules
        ]
