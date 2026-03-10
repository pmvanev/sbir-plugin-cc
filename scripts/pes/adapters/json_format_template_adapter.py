"""JSON format template adapter -- loads format templates from JSON files.

Implements FormatTemplateLoader port using JSON files in a templates directory.
New agency templates added by creating a JSON file -- no code changes required.
"""

from __future__ import annotations

import json
from pathlib import Path

from pes.domain.formatting import FormatTemplate
from pes.ports.format_template_port import FormatTemplateLoader


class JsonFormatTemplateAdapter(FormatTemplateLoader):
    """Load format templates from JSON files in a directory.

    File naming convention: {agency}-{solicitation_type}.json
    Example: dod-phase-i.json, nasa-phase-i.json
    """

    def __init__(self, templates_dir: str | Path) -> None:
        self._templates_dir = Path(templates_dir)

    def load_template(
        self, *, agency: str, solicitation_type: str
    ) -> FormatTemplate | None:
        """Load format template from JSON file.

        Returns FormatTemplate if file found and valid, None otherwise.
        """
        filename = f"{agency}-{solicitation_type}.json"
        filepath = self._templates_dir / filename

        if not filepath.exists():
            return None

        text = filepath.read_text(encoding="utf-8")
        data = json.loads(text)

        return FormatTemplate(
            agency=data["agency"],
            solicitation_type=data["solicitation_type"],
            font_family=data["font_family"],
            font_size_pt=data["font_size_pt"],
            margin_top_inches=data["margin_top_inches"],
            margin_bottom_inches=data["margin_bottom_inches"],
            margin_left_inches=data["margin_left_inches"],
            margin_right_inches=data["margin_right_inches"],
            header=data["header"],
            footer=data["footer"],
            page_limit=data["page_limit"],
            line_spacing=data["line_spacing"],
        )
