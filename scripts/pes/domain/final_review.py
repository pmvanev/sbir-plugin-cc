"""Final review domain models -- value objects for simulated government evaluator review.

Pure domain objects with no infrastructure imports.
ReviewerScorecard captures criterion scores with rationale.
RedTeamFinding captures objections with severity, section, and page.
DebriefCrossCheckEntry flags known weaknesses from past debriefs.
SignOffRecord records human sign-off with timestamp and unresolved issues.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CriterionScore:
    """Score for a single evaluation criterion with rationale.

    Frozen value object -- immutable after creation.
    """

    criterion: str
    score: int
    rationale: str


@dataclass
class ReviewerScorecard:
    """Aggregates criterion scores from reviewer persona simulation."""

    scores: list[CriterionScore] = field(default_factory=list)
    artifact_written: bool = False

    @property
    def criteria_count(self) -> int:
        """Number of evaluation criteria scored."""
        return len(self.scores)


@dataclass(frozen=True)
class RedTeamFinding:
    """A single red team objection with severity and location reference.

    Severity: HIGH, MEDIUM, LOW.
    """

    objection: str
    severity: str
    section: str
    page: int


@dataclass
class RedTeamResult:
    """Aggregates red team findings."""

    findings: list[RedTeamFinding] = field(default_factory=list)
    artifact_written: bool = False


@dataclass(frozen=True)
class DebriefCrossCheckEntry:
    """A known weakness flagged from past debrief feedback."""

    weakness: str
    addressed: bool
    source_debrief: str = ""


@dataclass
class DebriefCrossCheckResult:
    """Result of debrief cross-check against known weaknesses."""

    entries: list[DebriefCrossCheckEntry] = field(default_factory=list)
    message: str = ""
    improvement_note: str = ""


@dataclass
class SignOffRecord:
    """Records human sign-off with timestamp and any unresolved issues."""

    signed_off: bool = False
    timestamp: str = ""
    unresolved_issues: list[RedTeamFinding] = field(default_factory=list)
    artifact_written: bool = False


@dataclass
class ReReviewResult:
    """Result of a re-review showing resolved issues and iteration count."""

    resolved_issues: list[RedTeamFinding] = field(default_factory=list)
    remaining_issues: list[RedTeamFinding] = field(default_factory=list)
    review_round: int = 0


@dataclass
class ForcedSignOffResult:
    """Result when max iterations reached -- sign-off required."""

    sign_off_required: bool = True
    review_round: int = 0
    unresolved_issues: list[RedTeamFinding] = field(default_factory=list)
    message: str = ""
