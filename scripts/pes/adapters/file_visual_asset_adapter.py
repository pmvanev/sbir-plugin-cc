"""File-based visual asset adapter.

Implements VisualAssetPort for JSON file persistence of
figure inventories and cross-reference logs.
Also implements FigurePersistence protocol for figure generation artifacts.
"""

from __future__ import annotations

import json
from pathlib import Path

from pes.domain.visual_asset import (
    CrossReferenceEntry,
    CrossReferenceLog,
    ExternalBrief,
    FigureInventory,
    FigurePlaceholder,
    GeneratedFigure,
)
from pes.ports.visual_asset_port import VisualAssetPort


class FileVisualAssetAdapter(VisualAssetPort):
    """Reads and writes visual asset artifacts as JSON files.

    Also satisfies FigurePersistence protocol for VisualAssetService.
    """

    def __init__(self, artifacts_dir: Path) -> None:
        self._dir = artifacts_dir

    def write_inventory(self, inventory: FigureInventory) -> None:
        """Write figure inventory to figure-inventory.json."""
        self._dir.mkdir(parents=True, exist_ok=True)
        path = self._dir / "figure-inventory.json"
        data = {
            "placeholders": [
                {
                    "figure_number": p.figure_number,
                    "section_id": p.section_id,
                    "description": p.description,
                    "figure_type": p.figure_type,
                    "generation_method": p.generation_method,
                }
                for p in inventory.placeholders
            ],
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def read_inventory(self) -> FigureInventory:
        """Read figure inventory from figure-inventory.json."""
        path = self._dir / "figure-inventory.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        placeholders = [
            FigurePlaceholder(
                figure_number=p["figure_number"],
                section_id=p["section_id"],
                description=p["description"],
                figure_type=p["figure_type"],
                generation_method=p["generation_method"],
            )
            for p in data["placeholders"]
        ]
        return FigureInventory(placeholders=placeholders)

    def write_cross_reference_log(self, log: CrossReferenceLog) -> None:
        """Write cross-reference log to cross-reference-log.json."""
        self._dir.mkdir(parents=True, exist_ok=True)
        path = self._dir / "cross-reference-log.json"
        data = {
            "entries": [
                {
                    "section_id": e.section_id,
                    "referenced_figure": e.referenced_figure,
                    "exists": e.exists,
                }
                for e in log.entries
            ],
            "all_valid": log.all_valid,
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def read_cross_reference_log(self) -> CrossReferenceLog:
        """Read cross-reference log from cross-reference-log.json."""
        path = self._dir / "cross-reference-log.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        entries = [
            CrossReferenceEntry(
                section_id=e["section_id"],
                referenced_figure=e["referenced_figure"],
                exists=e["exists"],
            )
            for e in data["entries"]
        ]
        return CrossReferenceLog(entries=entries)

    # --- FigurePersistence protocol methods ---

    def write_figure(self, figure: GeneratedFigure, content: str) -> None:
        """Write generated figure file to figures directory."""
        figures_dir = self._dir / "figures"
        figures_dir.mkdir(parents=True, exist_ok=True)
        path = figures_dir / figure.file_path
        path.write_text(content, encoding="utf-8")

    def write_external_brief(self, brief: ExternalBrief) -> None:
        """Write external brief as JSON to figures directory."""
        figures_dir = self._dir / "figures"
        figures_dir.mkdir(parents=True, exist_ok=True)
        path = figures_dir / f"figure-{brief.figure_number}-brief.json"
        data = {
            "figure_number": brief.figure_number,
            "section_id": brief.section_id,
            "content_description": brief.content_description,
            "dimensions": brief.dimensions,
            "resolution": brief.resolution,
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def replace_figure(self, figure_number: int, new_path: str) -> GeneratedFigure:
        """Replace a figure with a manual file path."""
        fmt = new_path.split(".")[-1] if "." in new_path else "unknown"
        return GeneratedFigure(
            figure_number=figure_number,
            section_id="replaced",
            file_path=new_path,
            format=fmt,
        )
