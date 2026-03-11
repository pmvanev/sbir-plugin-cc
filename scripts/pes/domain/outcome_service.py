"""Outcome service -- driving port for outcome recording and debrief request letter generation.

Orchestrates: agency-specific debrief letter generation from templates,
debrief skip recording, outcome archiving, and letter artifact persistence.
"""

from __future__ import annotations

import json
from pathlib import Path

from pes.domain.outcome import (
    DebriefLetterResult,
    DebriefSkipRecord,
    LessonsLearnedResult,
    OutcomeRecord,
    PatternAnalysisResult,
)

# Agency-to-template mapping
_AGENCY_TEMPLATES: dict[str, str] = {
    "Air Force": "dod-far-15-505.md",
    "Army": "dod-far-15-505.md",
    "Navy": "dod-far-15-505.md",
    "NASA": "nasa-debrief.md",
}

# Resolve templates directory relative to project root
_TEMPLATES_DIR = (
    Path(__file__).resolve().parent.parent.parent.parent / "templates" / "debrief-request"
)


class OutcomeService:
    """Driving port: generates debrief request letters and records outcomes."""

    def generate_debrief_letter(
        self,
        *,
        topic_id: str,
        agency: str,
        confirmation_number: str,
        artifacts_dir: str,
    ) -> DebriefLetterResult:
        """Generate an agency-specific debrief request letter.

        Selects the appropriate template based on agency, substitutes
        topic and confirmation values, and writes the letter to the
        artifacts directory.
        """
        template_name = _AGENCY_TEMPLATES.get(agency)
        if template_name is None:
            # Default to DoD template for unknown agencies
            template_name = "dod-far-15-505.md"

        template_path = _TEMPLATES_DIR / template_name
        template_content = template_path.read_text(encoding="utf-8")

        # Substitute placeholders
        content = template_content.replace("{topic_id}", topic_id)
        content = content.replace("{confirmation_number}", confirmation_number)

        # Write letter to artifacts directory
        output_dir = Path(artifacts_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"debrief-request-{topic_id}.md"
        output_file.write_text(content, encoding="utf-8")

        return DebriefLetterResult(
            topic_id=topic_id,
            agency=agency,
            confirmation_number=confirmation_number,
            content=content,
            file_path=str(output_file),
        )

    def skip_debrief_request(
        self,
        *,
        topic_id: str,
    ) -> DebriefSkipRecord:
        """Record that the user chose not to request a debrief.

        Returns a DebriefSkipRecord with status "debrief not requested"
        and letter_created=False.
        """
        return DebriefSkipRecord(
            topic_id=topic_id,
            status="debrief not requested",
            letter_created=False,
        )

    def record_outcome(
        self,
        *,
        topic_id: str,
        outcome: str,
        artifacts_dir: str,
    ) -> OutcomeRecord:
        """Record a proposal outcome and archive if awarded.

        For awarded proposals: archives with outcome tag, extracts discriminators
        placeholder, and suggests Phase II pre-planning.

        For not_selected proposals: records outcome as valid terminal state,
        noting that debrief can be ingested later.
        """
        output_dir = Path(artifacts_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if outcome == "awarded":
            # Archive the winning proposal with outcome tag
            archive_data = {
                "topic_id": topic_id,
                "outcome": "awarded",
                "discriminators": [],
            }
            archive_file = output_dir / f"outcome-{topic_id}.json"
            archive_file.write_text(json.dumps(archive_data, indent=2), encoding="utf-8")

            return OutcomeRecord(
                topic_id=topic_id,
                outcome_tag="awarded",
                archived=True,
                discriminators=[],
                debrief_artifacts_created=False,
                archive_path=str(archive_file),
                message=f"Awarded proposal {topic_id} archived. Consider Phase II pre-planning.",
            )

        # Not selected -- valid terminal state without debrief
        return OutcomeRecord(
            topic_id=topic_id,
            outcome_tag=outcome,
            archived=False,
            discriminators=[],
            debrief_artifacts_created=False,
            archive_path="",
            message=f"Outcome '{outcome}' recorded for {topic_id}. "
            "Debrief can be ingested later if received.",
        )

    def update_pattern_analysis(
        self,
        *,
        corpus_outcomes: list[dict[str, object]],
        artifacts_dir: str,
    ) -> PatternAnalysisResult:
        """Update cumulative win/loss pattern analysis across the corpus.

        Analyzes recurring strengths from awarded proposals and recurring
        weaknesses from not-selected proposals. Notes confidence level
        based on corpus size.
        """
        # Tally patterns across outcomes
        weakness_counts: dict[str, int] = {}
        strength_counts: dict[str, int] = {}

        for entry in corpus_outcomes:
            for w in entry.get("weaknesses", []):
                if isinstance(w, str):
                    weakness_counts[w] = weakness_counts.get(w, 0) + 1
            for s in entry.get("strengths", []):
                if isinstance(s, str):
                    strength_counts[s] = strength_counts.get(s, 0) + 1

        recurring_weaknesses = [
            {"pattern": pattern, "count": count}
            for pattern, count in sorted(weakness_counts.items(), key=lambda x: x[1], reverse=True)
        ]
        recurring_strengths = [
            {"pattern": pattern, "count": count}
            for pattern, count in sorted(strength_counts.items(), key=lambda x: x[1], reverse=True)
        ]

        # Confidence scales with corpus size
        corpus_size = len(corpus_outcomes)
        if corpus_size >= 20:
            confidence_level = "high"
        elif corpus_size >= 10:
            confidence_level = "medium"
        else:
            confidence_level = "low"

        # Write pattern analysis artifact
        output_dir = Path(artifacts_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        analysis_data = {
            "corpus_size": corpus_size,
            "confidence_level": confidence_level,
            "recurring_weaknesses": recurring_weaknesses,
            "recurring_strengths": recurring_strengths,
        }
        artifact_file = output_dir / "pattern-analysis.json"
        artifact_file.write_text(json.dumps(analysis_data, indent=2), encoding="utf-8")

        return PatternAnalysisResult(
            recurring_weaknesses=recurring_weaknesses,
            recurring_strengths=recurring_strengths,
            confidence_level=confidence_level,
            corpus_size=corpus_size,
            artifact_path=str(artifact_file),
        )

    def present_lessons_learned(
        self,
        *,
        artifacts_dir: str,
    ) -> LessonsLearnedResult:
        """Present lessons learned for human review checkpoint.

        Returns a result with requires_human_acknowledgment=True and
        status='pending_review'. The corpus update does not complete
        until the human acknowledges the lessons.
        """
        return LessonsLearnedResult(
            requires_human_acknowledgment=True,
            status="pending_review",
            lessons=[],
            artifact_path=artifacts_dir,
        )
