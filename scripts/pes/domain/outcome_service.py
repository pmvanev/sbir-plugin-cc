"""Outcome service -- driving port for outcome recording and debrief request letter generation.

Orchestrates: agency-specific debrief letter generation from templates,
debrief skip recording, outcome archiving, and letter artifact persistence.
"""

from __future__ import annotations

import os

from pes.domain.outcome import (
    DebriefLetterResult,
    DebriefSkipRecord,
    LessonsLearnedResult,
    OutcomeRecord,
    PatternAnalysisResult,
)
from pes.ports.artifact_writer_port import ArtifactWriter
from pes.ports.template_loader_port import TemplateLoader

# Agency-to-template mapping
_AGENCY_TEMPLATES: dict[str, str] = {
    "Air Force": "dod-far-15-505.md",
    "Army": "dod-far-15-505.md",
    "Navy": "dod-far-15-505.md",
    "NASA": "nasa-debrief.md",
}


class OutcomeService:
    """Driving port: generates debrief request letters and records outcomes."""

    def __init__(
        self,
        *,
        template_loader: TemplateLoader,
        artifact_writer: ArtifactWriter,
    ) -> None:
        self._template_loader = template_loader
        self._artifact_writer = artifact_writer

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

        template_content = self._template_loader.load_template(template_name)

        # Substitute placeholders
        content = template_content.replace("{topic_id}", topic_id)
        content = content.replace("{confirmation_number}", confirmation_number)

        # Write letter to artifacts directory
        output_file = os.path.join(artifacts_dir, f"debrief-request-{topic_id}.md")
        self._artifact_writer.write_artifact(output_file, content)

        return DebriefLetterResult(
            topic_id=topic_id,
            agency=agency,
            confirmation_number=confirmation_number,
            content=content,
            file_path=output_file,
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
        if outcome == "awarded":
            # Archive the winning proposal with outcome tag
            archive_data = {
                "topic_id": topic_id,
                "outcome": "awarded",
                "discriminators": [],
            }
            archive_file = os.path.join(artifacts_dir, f"outcome-{topic_id}.json")
            self._artifact_writer.write_json(archive_file, archive_data)

            return OutcomeRecord(
                topic_id=topic_id,
                outcome_tag="awarded",
                archived=True,
                discriminators=[],
                debrief_artifacts_created=False,
                archive_path=archive_file,
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
        recurring_weaknesses = self._tally_patterns(corpus_outcomes, "weaknesses")
        recurring_strengths = self._tally_patterns(corpus_outcomes, "strengths")

        # Confidence scales with corpus size
        corpus_size = len(corpus_outcomes)
        if corpus_size >= 20:
            confidence_level = "high"
        elif corpus_size >= 10:
            confidence_level = "medium"
        else:
            confidence_level = "low"

        # Write pattern analysis artifact
        analysis_data = {
            "corpus_size": corpus_size,
            "confidence_level": confidence_level,
            "recurring_weaknesses": recurring_weaknesses,
            "recurring_strengths": recurring_strengths,
        }
        artifact_file = os.path.join(artifacts_dir, "pattern-analysis.json")
        self._artifact_writer.write_json(artifact_file, analysis_data)

        return PatternAnalysisResult(
            recurring_weaknesses=recurring_weaknesses,
            recurring_strengths=recurring_strengths,
            confidence_level=confidence_level,
            corpus_size=corpus_size,
            artifact_path=artifact_file,
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

    @staticmethod
    def _tally_patterns(
        corpus_outcomes: list[dict[str, object]], key: str
    ) -> list[dict[str, object]]:
        """Tally recurring patterns from corpus outcomes by key (weaknesses/strengths)."""
        counts: dict[str, int] = {}
        for entry in corpus_outcomes:
            items = entry.get(key, [])
            if not isinstance(items, list):
                continue
            for item in items:
                if isinstance(item, str):
                    counts[item] = counts.get(item, 0) + 1
        return [
            {"pattern": pattern, "count": count}
            for pattern, count in sorted(counts.items(), key=lambda x: x[1], reverse=True)
        ]
