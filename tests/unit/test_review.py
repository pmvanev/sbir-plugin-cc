"""Unit tests for review domain value objects.

Test Budget: 3 behaviors x 2 = 6 unit tests max.

These are pure domain value objects tested directly per step 04-01.
No driving port exists yet -- domain models are built first.

Behaviors:
1. ReviewFinding captures location, severity, and suggestion (frozen VO)
2. ReviewScorecard aggregates findings with strengths and weaknesses
3. ReviewScorecard provides severity counts and critical/major checks
"""

from __future__ import annotations

import pytest

from pes.domain.review import ReviewFinding, ReviewScorecard


# ---------------------------------------------------------------------------
# Behavior 1: ReviewFinding captures location, severity, suggestion
# ---------------------------------------------------------------------------


class TestReviewFindingConstruction:
    def test_finding_captures_location_severity_and_suggestion(self):
        finding = ReviewFinding(
            location="tech-approach",
            severity="critical",
            suggestion="Add quantitative performance metrics to support claims.",
        )

        assert finding.location == "tech-approach"
        assert finding.severity == "critical"
        assert finding.suggestion == "Add quantitative performance metrics to support claims."

    def test_finding_is_frozen_value_object(self):
        finding = ReviewFinding(
            location="intro",
            severity="minor",
            suggestion="Consider rephrasing for clarity.",
        )

        with pytest.raises(AttributeError):
            finding.severity = "major"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Behavior 2: ReviewScorecard aggregates findings with strengths/weaknesses
# ---------------------------------------------------------------------------


class TestReviewScorecardAggregation:
    def test_scorecard_holds_findings_strengths_and_weaknesses(self):
        findings = [
            ReviewFinding(
                location="tech-approach",
                severity="major",
                suggestion="Strengthen evidence for TRL claim.",
            ),
            ReviewFinding(
                location="management",
                severity="minor",
                suggestion="Add milestone dates.",
            ),
        ]
        scorecard = ReviewScorecard(
            findings=findings,
            strengths=["Strong technical narrative", "Clear commercialization plan"],
            weaknesses=["Weak cost justification"],
        )

        assert len(scorecard.findings) == 2
        assert len(scorecard.strengths) == 2
        assert len(scorecard.weaknesses) == 1

    def test_empty_scorecard_has_no_findings(self):
        scorecard = ReviewScorecard()

        assert len(scorecard.findings) == 0
        assert len(scorecard.strengths) == 0
        assert len(scorecard.weaknesses) == 0


# ---------------------------------------------------------------------------
# Behavior 3: Severity counts and critical/major checks
# ---------------------------------------------------------------------------


class TestReviewScorecardSeverityCounts:
    def test_counts_findings_by_severity(self):
        findings = [
            ReviewFinding(location="s1", severity="critical", suggestion="Fix A."),
            ReviewFinding(location="s2", severity="critical", suggestion="Fix B."),
            ReviewFinding(location="s3", severity="major", suggestion="Fix C."),
            ReviewFinding(location="s4", severity="minor", suggestion="Fix D."),
        ]
        scorecard = ReviewScorecard(findings=findings)

        assert scorecard.count_by_severity("critical") == 2
        assert scorecard.count_by_severity("major") == 1
        assert scorecard.count_by_severity("minor") == 1
        assert scorecard.count_by_severity("info") == 0

    def test_has_critical_and_has_major_findings(self):
        findings = [
            ReviewFinding(location="s1", severity="critical", suggestion="Fix."),
            ReviewFinding(location="s2", severity="minor", suggestion="Tweak."),
        ]
        scorecard = ReviewScorecard(findings=findings)

        assert scorecard.has_critical_findings is True
        assert scorecard.has_major_findings is False
