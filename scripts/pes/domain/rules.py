"""Rule domain model -- enforcement rules as objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Decision(Enum):
    """Enforcement decision outcome."""

    ALLOW = "ALLOW"
    BLOCK = "BLOCK"


@dataclass(frozen=True)
class EnforcementResult:
    """Result of evaluating enforcement rules."""

    decision: Decision
    messages: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class EnforcementRule:
    """A single enforcement rule loaded from configuration.

    Attributes:
        rule_id: Unique identifier for the rule.
        description: Human-readable description.
        rule_type: Category of rule (wave_ordering, compliance_gate, etc.).
        condition: Dict describing when the rule triggers.
        message: Message to display when rule blocks an action.
    """

    rule_id: str
    description: str
    rule_type: str
    condition: dict[str, Any]
    message: str
