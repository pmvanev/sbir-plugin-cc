"""Formatting service -- driving port for document formatting operations.

Orchestrates: format template loading, document formatting, and assembly.
Delegates to FormatTemplateLoader driven port for template data.
"""

from __future__ import annotations

from pes.domain.formatting import FormatTemplateResult
from pes.ports.format_template_port import FormatTemplateLoader


class FormattingService:
    """Driving port: loads format templates and orchestrates formatting.

    Delegates to FormatTemplateLoader driven port for template data access.
    """

    def __init__(self, format_template_loader: FormatTemplateLoader) -> None:
        self._loader = format_template_loader

    def load_format_template(
        self, *, agency: str, solicitation_type: str
    ) -> FormatTemplateResult:
        """Load format template for the given agency and solicitation type.

        Returns FormatTemplateResult with template or error details.
        """
        template = self._loader.load_template(
            agency=agency, solicitation_type=solicitation_type
        )

        if template is None:
            return FormatTemplateResult(
                error=f"No format template found for agency '{agency}' "
                f"with solicitation type '{solicitation_type}'"
            )

        return FormatTemplateResult(template=template)
