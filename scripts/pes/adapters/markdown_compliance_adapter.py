"""Markdown compliance matrix adapter.

Renders a ComplianceMatrix to human-editable markdown
and reads it back from markdown format.
"""

from __future__ import annotations

import re
from pathlib import Path

from pes.domain.compliance import (
    ComplianceItem,
    ComplianceMatrix,
    CoverageStatus,
    RequirementType,
)


class MarkdownComplianceAdapter:
    """Renders and reads compliance matrix as markdown."""

    def render(self, matrix: ComplianceMatrix) -> str:
        """Render compliance matrix to markdown table."""
        lines = [
            "# Compliance Matrix",
            "",
            f"**Total items:** {matrix.item_count}",
            f"**Coverage:** {matrix.coverage_summary()}",
            "",
        ]

        if matrix.warnings:
            lines.append("## Warnings")
            lines.append("")
            for warning in matrix.warnings:
                lines.append(f"- {warning}")
            lines.append("")

        lines.extend([
            "## Requirements",
            "",
            "| ID | Type | Requirement | Section | Status | Ambiguity |",
            "|---:|------|-------------|---------|--------|-----------|",
        ])

        for item in matrix.items:
            ambiguity = item.ambiguity or ""
            section = item.proposal_section or ""
            lines.append(
                f"| {item.item_id} "
                f"| {item.requirement_type.value} "
                f"| {item.text} "
                f"| {section} "
                f"| {item.status.value} "
                f"| {ambiguity} |"
            )

        lines.append("")
        return "\n".join(lines)

    def write(self, matrix: ComplianceMatrix, path: Path) -> None:
        """Write compliance matrix to markdown file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.render(matrix), encoding="utf-8")

    def read(self, path: Path) -> ComplianceMatrix:
        """Read compliance matrix from markdown file."""
        content = path.read_text(encoding="utf-8")
        return self._parse_markdown(content)

    def _parse_markdown(self, content: str) -> ComplianceMatrix:
        """Parse markdown table back into ComplianceMatrix."""
        items: list[ComplianceItem] = []
        warnings: list[str] = []

        # Extract warnings
        in_warnings = False
        for line in content.split("\n"):
            if line.strip() == "## Warnings":
                in_warnings = True
                continue
            if line.startswith("## ") and in_warnings:
                in_warnings = False
                continue
            if in_warnings and line.startswith("- "):
                warnings.append(line[2:].strip())

        # Extract table rows
        table_pattern = re.compile(
            r"\|\s*(\d+)\s*"
            r"\|\s*(\w+)\s*"
            r"\|\s*(.*?)\s*"
            r"\|\s*(.*?)\s*"
            r"\|\s*(.*?)\s*"
            r"\|\s*(.*?)\s*\|"
        )

        for line in content.split("\n"):
            match = table_pattern.match(line)
            if match:
                item_id = int(match.group(1))
                req_type = RequirementType(match.group(2).strip())
                text = match.group(3).strip()
                section = match.group(4).strip() or None
                status = CoverageStatus(match.group(5).strip())
                ambiguity = match.group(6).strip() or None

                items.append(ComplianceItem(
                    item_id=item_id,
                    text=text,
                    requirement_type=req_type,
                    proposal_section=section,
                    ambiguity=ambiguity,
                    status=status,
                ))

        return ComplianceMatrix(items=items, warnings=warnings)
