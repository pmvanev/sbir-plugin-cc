"""Acceptance test conftest -- fixtures for Visual Asset Quality BDD scenarios.

All acceptance tests invoke through driving ports only:
- VisualAssetService (figure generation routing)
- FileVisualAssetAdapter (figure persistence)
- Style profile and critique models (new domain utilities)

External dependencies:
- File system: real via tmp_path (integration_approach: mocks-for-external-only)
- Gemini API: mocked (external service)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from pes.domain.visual_asset import FigureInventory, FigurePlaceholder, GeneratedFigure


# ---------------------------------------------------------------------------
# Directory Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def artifacts_dir(tmp_path: Path) -> Path:
    """Temporary directory simulating wave-5-visuals artifact output."""
    d = tmp_path / "artifacts" / "wave-5-visuals"
    d.mkdir(parents=True)
    return d


@pytest.fixture()
def figures_dir(artifacts_dir: Path) -> Path:
    """Figures subdirectory within artifacts."""
    d = artifacts_dir / "figures"
    d.mkdir(exist_ok=True)
    return d


@pytest.fixture()
def style_profile_path(artifacts_dir: Path) -> Path:
    """Path to style-profile.yaml within artifact directory."""
    return artifacts_dir / "style-profile.yaml"


# ---------------------------------------------------------------------------
# Stub FigureGenerator (mock for external Gemini dependency)
# ---------------------------------------------------------------------------


class StubFigureGenerator:
    """Stub generator returning canned SVG/TikZ content.

    Gemini API is an external dependency -- mocked per integration_approach.
    """

    def generate_svg(self, placeholder: FigurePlaceholder) -> str:
        return f"<svg><text>Figure {placeholder.figure_number}</text></svg>"


@pytest.fixture()
def stub_generator() -> StubFigureGenerator:
    """Stub figure generator for acceptance tests."""
    return StubFigureGenerator()


# ---------------------------------------------------------------------------
# Stub PdcChecker
# ---------------------------------------------------------------------------


class StubPdcChecker:
    """Stub PDC checker that always passes the gate."""

    def all_sections_pdc_green(self) -> bool:
        return True

    def get_red_pdc_items(self) -> list[dict]:
        return []


@pytest.fixture()
def stub_pdc_checker() -> StubPdcChecker:
    """Stub PDC checker for acceptance tests."""
    return StubPdcChecker()


# ---------------------------------------------------------------------------
# Figure Placeholder Builders
# ---------------------------------------------------------------------------


def make_placeholder(
    figure_number: int = 1,
    section_id: str = "3.1",
    description: str = "Test figure",
    figure_type: str = "system-diagram",
    generation_method: str = "Mermaid",
) -> FigurePlaceholder:
    """Build a FigurePlaceholder with overridable defaults."""
    return FigurePlaceholder(
        figure_number=figure_number,
        section_id=section_id,
        description=description,
        figure_type=figure_type,
        generation_method=generation_method,
    )


# ---------------------------------------------------------------------------
# Style Profile Helpers
# ---------------------------------------------------------------------------


def make_style_profile(
    agency: str = "Navy",
    domain: str = "maritime/naval",
    primary: str = "#003366",
    secondary: str = "#6B7B8D",
    accent: str = "#FF6B35",
    highlight: str = "#2B7A8C",
    tone: str = "technical-authoritative",
    detail_level: str = "high",
    avoid: list[str] | None = None,
) -> dict[str, Any]:
    """Build a style profile dict for testing."""
    return {
        "solicitation_id": "N241-033",
        "agency": agency,
        "domain": domain,
        "palette": {
            "primary": primary,
            "secondary": secondary,
            "accent": accent,
            "highlight": highlight,
        },
        "tone": tone,
        "detail_level": detail_level,
        "avoid": avoid if avoid is not None else [
            "cartoon/sketch style",
            "excessive gradients",
        ],
        "notes": "",
        "user_adjustments": [],
    }


# ---------------------------------------------------------------------------
# Critique Rating Helpers
# ---------------------------------------------------------------------------


def make_critique_ratings(
    composition: int = 4,
    labels: int = 4,
    accuracy: int = 4,
    style_match: int = 4,
    scale_proportion: int = 4,
) -> dict[str, int]:
    """Build a critique ratings dict for testing."""
    return {
        "composition": composition,
        "labels": labels,
        "accuracy": accuracy,
        "style_match": style_match,
        "scale_proportion": scale_proportion,
    }


# ---------------------------------------------------------------------------
# Result Containers
# ---------------------------------------------------------------------------


@pytest.fixture()
def generation_result() -> dict[str, Any]:
    """Mutable container for figure generation results."""
    return {}


@pytest.fixture()
def style_context() -> dict[str, Any]:
    """Mutable container for style profile operations."""
    return {}


@pytest.fixture()
def critique_context() -> dict[str, Any]:
    """Mutable container for critique/rating operations."""
    return {}


@pytest.fixture()
def quality_context() -> dict[str, Any]:
    """Mutable container for quality summary operations."""
    return {}
