"""Acceptance test conftest -- fixtures for Solution Shaper BDD scenarios.

Solution-shaper is a markdown agent feature. Executable tests validate:
- Approach scoring model (composite calculation, weight validation)
- Approach brief schema (required sections, matrix structure)
- Agent/skill/command file structure (frontmatter, required sections)

Agent behavior scenarios are tagged @skip @agent_behavior and serve as
living documentation, not automated tests.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest


# ---------------------------------------------------------------------------
# Scoring Model Fixtures
# ---------------------------------------------------------------------------

# Default scoring weights per approach-evaluation skill
DEFAULT_WEIGHTS: dict[str, float] = {
    "personnel_alignment": 0.25,
    "past_performance": 0.20,
    "technical_readiness": 0.20,
    "solicitation_fit": 0.20,
    "commercialization": 0.15,
}

SCORING_DIMENSIONS: list[str] = [
    "personnel_alignment",
    "past_performance",
    "technical_readiness",
    "solicitation_fit",
    "commercialization",
]

# Required sections in approach-brief.md
BRIEF_REQUIRED_SECTIONS: list[str] = [
    "solicitation summary",
    "selected approach",
    "approach scoring matrix",
    "runner-up",
    "discrimination angles",
    "risks and open questions",
    "phase iii quick assessment",
]


@pytest.fixture()
def default_weights() -> dict[str, float]:
    """Default scoring weights from approach-evaluation skill."""
    return DEFAULT_WEIGHTS.copy()


@pytest.fixture()
def scoring_dimensions() -> list[str]:
    """List of the five scoring dimension names."""
    return SCORING_DIMENSIONS.copy()


@pytest.fixture()
def shaper_context() -> dict[str, Any]:
    """Mutable container to hold scoring results across steps."""
    return {}


# ---------------------------------------------------------------------------
# Sample Approach Scores Fixtures
# ---------------------------------------------------------------------------


def make_approach_scores(
    name: str,
    personnel: float = 0.50,
    past_performance: float = 0.50,
    technical_readiness: float = 0.50,
    solicitation_fit: float = 0.50,
    commercialization: float = 0.50,
) -> dict[str, Any]:
    """Build an approach with dimension scores for test scenarios."""
    return {
        "name": name,
        "scores": {
            "personnel_alignment": personnel,
            "past_performance": past_performance,
            "technical_readiness": technical_readiness,
            "solicitation_fit": solicitation_fit,
            "commercialization": commercialization,
        },
    }


@pytest.fixture()
def fiber_laser_approach() -> dict[str, Any]:
    """High-scoring fiber laser approach aligned with company strengths."""
    return make_approach_scores(
        "Fiber Laser Array",
        personnel=0.85,
        past_performance=0.80,
        technical_readiness=0.70,
        solicitation_fit=0.80,
        commercialization=0.75,
    )


@pytest.fixture()
def semiconductor_approach() -> dict[str, Any]:
    """Low-scoring approach with weak company alignment."""
    return make_approach_scores(
        "Direct Semiconductor",
        personnel=0.30,
        past_performance=0.20,
        technical_readiness=0.70,
        solicitation_fit=0.80,
        commercialization=0.75,
    )


@pytest.fixture()
def uniform_approach_alpha() -> dict[str, Any]:
    """Approach with all dimensions at 0.60."""
    return make_approach_scores("Alpha", 0.60, 0.60, 0.60, 0.60, 0.60)


@pytest.fixture()
def uniform_approach_beta() -> dict[str, Any]:
    """Approach with all dimensions at 0.60."""
    return make_approach_scores("Beta", 0.60, 0.60, 0.60, 0.60, 0.60)


# ---------------------------------------------------------------------------
# Approach Brief Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def complete_brief_sections() -> dict[str, str]:
    """Complete approach brief with all required sections populated."""
    return {
        "solicitation summary": (
            "Agency: Air Force\n"
            "Problem: Compact directed energy for maritime UAS defense\n"
            "Key objectives: Demonstrate TRL 4 prototype\n"
            "Evaluation criteria: Technical merit (40%), team (30%), cost (20%), schedule (10%)"
        ),
        "selected approach": (
            "Name: High-Power Fiber Laser Array\n"
            "Description: Coherently combined fiber laser array for counter-UAS.\n"
            "Key technical elements: fiber laser array, beam combining, tracking\n"
            "Why this approach: Highest personnel alignment and past performance scores"
        ),
        "approach scoring matrix": (
            "| Dimension | Fiber Laser | DPSSL | Hybrid | Semiconductor |\n"
            "|-----------|------------|-------|--------|---------------|\n"
            "| Personnel alignment | 0.85 | 0.40 | 0.55 | 0.30 |\n"
            "| Past performance | 0.80 | 0.30 | 0.45 | 0.20 |\n"
            "| Technical readiness | 0.70 | 0.60 | 0.50 | 0.70 |\n"
            "| Solicitation fit | 0.80 | 0.75 | 0.70 | 0.80 |\n"
            "| Commercialization | 0.75 | 0.60 | 0.55 | 0.75 |\n"
            "| **Composite** | **0.79** | **0.53** | **0.55** | **0.55** |"
        ),
        "runner-up": (
            "Name: Hybrid RF-Optical\n"
            "Why not selected: Lower personnel alignment and no direct past performance\n"
            "When to reconsider: If team adds RF-optical expertise or TPOC signals RF preference"
        ),
        "discrimination angles": (
            "- Dr. Chen's 12-year fiber laser track record\n"
            "- Phase I past performance on AF241-087\n"
            "- Existing lab prototype at TRL 3"
        ),
        "risks and open questions": (
            "- Beam combining efficiency in maritime atmosphere: Validate in Wave 2\n"
            "- SWaP constraints for shipboard mounting: Validate in Wave 1"
        ),
        "phase iii quick assessment": (
            "Primary pathway: dual-use (counter-UAS for military and commercial port security)\n"
            "Target programs: Navy PEO IWS, DHS port protection\n"
            "Estimated market relevance: high"
        ),
    }


@pytest.fixture()
def incomplete_brief_sections(complete_brief_sections: dict[str, str]) -> dict[str, str]:
    """Brief missing the discrimination angles section."""
    brief = complete_brief_sections.copy()
    del brief["discrimination angles"]
    return brief


# ---------------------------------------------------------------------------
# Scoring Matrix Fixture
# ---------------------------------------------------------------------------


@pytest.fixture()
def four_approach_matrix() -> list[dict[str, Any]]:
    """Scoring matrix with 4 approaches fully scored."""
    return [
        make_approach_scores("Fiber Laser Array", 0.85, 0.80, 0.70, 0.80, 0.75),
        make_approach_scores("DPSSL", 0.40, 0.30, 0.60, 0.75, 0.60),
        make_approach_scores("Hybrid RF-Optical", 0.55, 0.45, 0.50, 0.70, 0.55),
        make_approach_scores("Direct Semiconductor", 0.30, 0.20, 0.70, 0.80, 0.75),
    ]


# ---------------------------------------------------------------------------
# File Path Fixtures for Structure Validation
# ---------------------------------------------------------------------------


@pytest.fixture()
def project_root() -> Path:
    """Root of the sbir-plugin-cc project."""
    return Path(__file__).resolve().parents[3]


@pytest.fixture()
def agent_file_path(project_root: Path) -> Path:
    """Path to the solution-shaper agent file."""
    return project_root / "agents" / "sbir-solution-shaper.md"


@pytest.fixture()
def skill_file_path(project_root: Path) -> Path:
    """Path to the approach-evaluation skill file."""
    return project_root / "skills" / "solution-shaper" / "approach-evaluation.md"


@pytest.fixture()
def command_file_path(project_root: Path) -> Path:
    """Path to the shape command file."""
    return project_root / "commands" / "sbir-proposal-shape.md"
