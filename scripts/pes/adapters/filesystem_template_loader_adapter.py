"""Filesystem template loader adapter.

Implements TemplateLoader port by reading templates from a local directory.
"""

from __future__ import annotations

from pathlib import Path

from pes.ports.template_loader_port import TemplateLoader


class FilesystemTemplateLoader(TemplateLoader):
    """Loads templates from a directory on the local filesystem."""

    def __init__(self, templates_dir: str) -> None:
        self._templates_dir = Path(templates_dir)

    def load_template(self, name: str) -> str:
        """Load template content by filename from the configured directory."""
        template_path = self._templates_dir / name
        if not template_path.exists():
            msg = f"Template not found: {template_path}"
            raise FileNotFoundError(msg)
        return template_path.read_text(encoding="utf-8")
