"""Outcome service -- driving port for outcome recording and debrief request letter generation.

Orchestrates: agency-specific debrief letter generation from templates,
debrief skip recording, outcome archiving, and letter artifact persistence.
"""

from __future__ import annotations

import json
from pathlib import Path

from pes.domain.outcome import DebriefLetterResult, DebriefSkipRecord, OutcomeRecord

# Agency-to-template mapping
_AGENCY_TEMPLATES: dict[str, str] = {
    "Air Force": "dod-far-15-505.md",
    "Army": "dod-far-15-505.md",
    "Navy": "dod-far-15-505.md",
    "NASA": "nasa-debrief.md",
}

# Resolve templates directory relative to project root
_TEMPLATES_DIR = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "templates"
    / "debrief-request"
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
            archive_file.write_text(
                json.dumps(archive_data, indent=2), encoding="utf-8"
            )

            return OutcomeRecord(
                topic_id=topic_id,
                outcome_tag="awarded",
                archived=True,
                discriminators=[],
                debrief_artifacts_created=False,
                archive_path=str(archive_file),
                message=f"Awarded proposal {topic_id} archived. "
                "Consider Phase II pre-planning.",
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
