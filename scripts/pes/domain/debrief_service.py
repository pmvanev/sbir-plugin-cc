"""Debrief service -- driving port for debrief ingestion and critique mapping.

Orchestrates: debrief parsing via DebriefParser port, critique-to-section mapping,
known weakness flagging, and artifact persistence.
"""

from __future__ import annotations

import json
from pathlib import Path

from pes.domain.debrief import CritiqueMapping, DebriefIngestionResult
from pes.ports.debrief_parser_port import DebriefParser


class DebriefService:
    """Driving port: ingests debriefs and maps critiques to proposal sections."""

    def __init__(self, *, parser: DebriefParser) -> None:
        self._parser = parser

    def ingest_debrief(
        self,
        *,
        debrief_text: str,
        known_weaknesses: list[str],
        artifacts_dir: str,
    ) -> DebriefIngestionResult:
        """Ingest a debrief, map critiques to sections, flag known weaknesses.

        Delegates parsing to the DebriefParser port. Then flags critiques
        matching known weaknesses, and writes the structured result to
        the artifacts directory.
        """
        parse_result = self._parser.parse(debrief_text)

        # Flag critiques matching known weaknesses
        flagged: list[str] = []
        flagged_critiques: list[CritiqueMapping] = []
        if parse_result.is_structured and known_weaknesses:
            for critique in parse_result.critiques:
                comment_lower = critique.comment.lower()
                for weakness in known_weaknesses:
                    if weakness.lower() in comment_lower:
                        flag_msg = (
                            f"Known weakness '{weakness}' found in "
                            f"Section {critique.section}, Page {critique.page}"
                        )
                        flagged.append(flag_msg)
                        flagged_critiques.append(
                            CritiqueMapping(
                                section=critique.section,
                                page=critique.page,
                                comment=critique.comment,
                                flagged_weakness=weakness,
                            )
                        )
                        break

        # Build the critique map with flagged weakness annotations
        critique_map = []
        for critique in parse_result.critiques:
            # Check if this critique was flagged
            flagged_match = next(
                (fc for fc in flagged_critiques if fc.section == critique.section), None
            )
            if flagged_match:
                critique_map.append(flagged_match)
            else:
                critique_map.append(critique)

        # Determine message
        if parse_result.is_structured:
            message = "Debrief parsed successfully"
        else:
            message = "Structured scores could not be extracted from this debrief"

        # Write artifact
        artifact_path = self._write_artifact(
            parse_result=parse_result,
            flagged_weaknesses=flagged,
            critique_map=critique_map,
            artifacts_dir=artifacts_dir,
        )

        return DebriefIngestionResult(
            scores=parse_result.scores,
            critique_map=critique_map,
            flagged_weaknesses=flagged,
            freeform_text=parse_result.freeform_text,
            parsing_confidence=parse_result.parsing_confidence,
            artifact_path=artifact_path,
            message=message,
        )

    def _write_artifact(
        self,
        *,
        parse_result: object,
        flagged_weaknesses: list[str],
        critique_map: list[CritiqueMapping],
        artifacts_dir: str,
    ) -> str:
        """Write structured debrief data to artifacts directory."""
        from pes.domain.debrief import DebriefParseResult

        assert isinstance(parse_result, DebriefParseResult)

        output_dir = Path(artifacts_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        artifact_data: dict[str, object] = {
            "parsing_confidence": parse_result.parsing_confidence,
            "is_structured": parse_result.is_structured,
        }

        if parse_result.is_structured:
            artifact_data["scores"] = [
                {"category": s.category, "score": s.score, "max_score": s.max_score}
                for s in parse_result.scores
            ]
            artifact_data["critique_map"] = [
                {
                    "section": c.section,
                    "page": c.page,
                    "comment": c.comment,
                    "flagged_weakness": c.flagged_weakness,
                }
                for c in critique_map
            ]
            artifact_data["flagged_weaknesses"] = flagged_weaknesses
        else:
            artifact_data["freeform_text"] = parse_result.freeform_text

        output_file = output_dir / "debrief-analysis.json"
        output_file.write_text(json.dumps(artifact_data, indent=2), encoding="utf-8")

        return str(output_file)
