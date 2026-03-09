"""Review domain models -- value objects for proposal review.

Pure domain objects with no infrastructure imports.
ReviewFinding captures a single finding with location, severity, and suggestion.
ReviewScorecard aggregates findings with strengths and weaknesses.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ReviewFinding:
    """A single review finding with location, severity, and suggestion.

    Frozen value object -- immutable after creation.
    Severity: critical, major, minor.
    Location: section_id or line reference.
    """

    location: str
    severity: str
    suggestion: str


@dataclass
class ReviewScorecard:
    """Aggregates review findings with strengths and weaknesses."""

    findings: list[ReviewFinding] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)

    def count_by_severity(self, severity: str) -> int:
        """Count findings matching the given severity."""
        return sum(1 for f in self.findings if f.severity == severity)

    @property
    def has_critical_findings(self) -> bool:
        """True when at least one critical finding exists."""
        return self.count_by_severity("critical") > 0

    @property
    def has_major_findings(self) -> bool:
        """True when at least one major finding exists."""
        return self.count_by_severity("major") > 0
