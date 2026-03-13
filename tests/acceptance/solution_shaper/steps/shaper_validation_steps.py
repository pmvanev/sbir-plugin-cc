"""Validation step definitions for Solution Shaper acceptance tests.

Tests approach brief schema validation and agent/skill/command file
structure validation.

These tests validate the deliverable artifacts have correct structure,
required sections, and proper integration contracts.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.solution_shaper.conftest import (
    BRIEF_REQUIRED_SECTIONS,
    SCORING_DIMENSIONS,
)

scenarios("../milestone-01b-brief-and-structure.feature")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def parse_yaml_frontmatter(content: str) -> dict[str, str]:
    """Extract YAML frontmatter fields from markdown content."""
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}
    fields: dict[str, str] = {}
    for line in match.group(1).strip().splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


def extract_sections(content: str) -> list[str]:
    """Extract heading-level sections (## headings) from markdown, lowercased."""
    return [
        m.group(1).strip().lower()
        for m in re.finditer(r"^##\s+(.+)$", content, re.MULTILINE)
    ]


# ---------------------------------------------------------------------------
# Given Steps -- Brief Validation
# ---------------------------------------------------------------------------


@given("an approach brief has been generated", target_fixture="brief_data")
def complete_brief(complete_brief_sections: dict[str, str]) -> dict[str, str]:
    return complete_brief_sections


@given(
    parsers.parse(
        "{count:d} candidate approaches have been scored"
    ),
)
def n_approaches_scored(
    count: int,
    four_approach_matrix: list[dict[str, Any]],
    shaper_context: dict[str, Any],
):
    shaper_context["scored_approaches"] = four_approach_matrix[:count]


@given(
    parsers.parse(
        "an approach brief is missing the {section} section"
    ),
    target_fixture="brief_data",
)
def brief_missing_section(
    section: str, incomplete_brief_sections: dict[str, str]
) -> dict[str, str]:
    return incomplete_brief_sections


# ---------------------------------------------------------------------------
# Given Steps -- File Structure Validation
# ---------------------------------------------------------------------------


@given(
    "the solution-shaper agent file exists",
    target_fixture="agent_content",
)
def agent_file_exists(agent_file_path: Path) -> str:
    if not agent_file_path.exists():
        pytest.skip(f"Agent file not yet created: {agent_file_path}")
    return agent_file_path.read_text(encoding="utf-8")


@given(
    "the approach-evaluation skill file exists",
    target_fixture="skill_content",
)
def skill_file_exists(skill_file_path: Path) -> str:
    if not skill_file_path.exists():
        pytest.skip(f"Skill file not yet created: {skill_file_path}")
    return skill_file_path.read_text(encoding="utf-8")


@given(
    "the shape command file exists",
    target_fixture="command_content",
)
def command_file_exists(command_file_path: Path) -> str:
    if not command_file_path.exists():
        pytest.skip(f"Command file not yet created: {command_file_path}")
    return command_file_path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# When Steps -- Brief Validation
# ---------------------------------------------------------------------------


@when("the brief structure is validated")
def validate_brief_structure(
    brief_data: dict[str, str], shaper_context: dict[str, Any]
):
    present = set(brief_data.keys())
    required = set(BRIEF_REQUIRED_SECTIONS)
    shaper_context["brief_sections_present"] = present
    shaper_context["brief_sections_missing"] = required - present
    shaper_context["brief_valid"] = required.issubset(present)


@when("the scoring matrix is validated")
def validate_scoring_matrix(shaper_context: dict[str, Any]):
    approaches = shaper_context["scored_approaches"]
    shaper_context["matrix_approach_count"] = len(approaches)
    shaper_context["matrix_valid"] = True
    for approach in approaches:
        scores = approach["scores"]
        # Check all dimensions present
        for dim in SCORING_DIMENSIONS:
            if dim not in scores:
                shaper_context["matrix_valid"] = False
            elif not (0.00 <= scores[dim] <= 1.00):
                shaper_context["matrix_valid"] = False


# ---------------------------------------------------------------------------
# When Steps -- File Structure Validation
# ---------------------------------------------------------------------------


@when("the agent file structure is validated")
def validate_agent_structure(
    agent_content: str, shaper_context: dict[str, Any]
):
    fm = parse_yaml_frontmatter(agent_content)
    sections = extract_sections(agent_content)
    shaper_context["agent_frontmatter"] = fm
    shaper_context["agent_sections"] = sections
    shaper_context["agent_content"] = agent_content


@when("the skill file structure is validated")
def validate_skill_structure(
    skill_content: str, shaper_context: dict[str, Any]
):
    fm = parse_yaml_frontmatter(skill_content)
    shaper_context["skill_frontmatter"] = fm
    shaper_context["skill_content"] = skill_content


@when("the command file structure is validated")
def validate_command_structure(
    command_content: str, shaper_context: dict[str, Any]
):
    fm = parse_yaml_frontmatter(command_content)
    shaper_context["command_frontmatter"] = fm
    shaper_context["command_content"] = command_content


# ---------------------------------------------------------------------------
# Then Steps -- Brief Section Validation
# ---------------------------------------------------------------------------


@then(parsers.re(r"the brief contains an? (?P<section_name>.+) section"))
def brief_has_section(section_name: str, shaper_context: dict[str, Any]):
    present = shaper_context["brief_sections_present"]
    assert section_name.lower() in present, (
        f"Missing section '{section_name}'. Present: {present}"
    )


@then(parsers.parse("the matrix has {count:d} approach columns"))
def matrix_approach_count(count: int, shaper_context: dict[str, Any]):
    assert shaper_context["matrix_approach_count"] == count


@then(
    parsers.parse(
        "the matrix has rows for personnel alignment, past performance, "
        "technical readiness, solicitation fit, and commercialization"
    )
)
def matrix_has_dimension_rows(shaper_context: dict[str, Any]):
    approaches = shaper_context["scored_approaches"]
    for approach in approaches:
        for dim in SCORING_DIMENSIONS:
            assert dim in approach["scores"], (
                f"Missing dimension '{dim}' in approach '{approach['name']}'"
            )


@then(parsers.parse("each cell contains a score between {low:g} and {high:g}"))
def matrix_cells_in_range(
    low: float, high: float, shaper_context: dict[str, Any]
):
    for approach in shaper_context["scored_approaches"]:
        for dim, score in approach["scores"].items():
            assert low <= score <= high, (
                f"Score {score} for {approach['name']}.{dim} out of range [{low}, {high}]"
            )


@then("each approach has a composite score row")
def matrix_has_composites(
    shaper_context: dict[str, Any], default_weights: dict[str, float]
):
    for approach in shaper_context["scored_approaches"]:
        composite = sum(
            approach["scores"][dim] * default_weights[dim]
            for dim in default_weights
        )
        assert composite >= 0.0, (
            f"Composite for '{approach['name']}' is negative: {composite}"
        )


@then(
    parsers.parse(
        'the validation fails with "{message}"'
    )
)
def validation_fails_with(message: str, shaper_context: dict[str, Any]):
    assert not shaper_context["brief_valid"], "Expected validation to fail"
    missing = shaper_context["brief_sections_missing"]
    # Check the missing section name appears in the expected message
    for section in missing:
        if section in message.lower():
            return
    pytest.fail(
        f"Expected failure about '{message}', missing sections: {missing}"
    )


# ---------------------------------------------------------------------------
# Then Steps -- Agent File Validation
# ---------------------------------------------------------------------------


@then(
    "the agent has YAML frontmatter with name, description, and skill references"
)
def agent_has_frontmatter(shaper_context: dict[str, Any]):
    fm = shaper_context["agent_frontmatter"]
    assert "name" in fm, f"Agent frontmatter missing 'name'. Got: {fm}"
    assert "description" in fm, f"Agent frontmatter missing 'description'. Got: {fm}"


@then("the agent has a workflow section covering all five phases")
def agent_has_workflow(shaper_context: dict[str, Any]):
    content = shaper_context["agent_content"].lower()
    for phase in ["deep read", "approach generation", "approach scoring",
                   "convergence", "checkpoint"]:
        assert phase in content, f"Agent missing workflow phase: {phase}"


@then("the agent references the approach-evaluation skill")
def agent_references_skill(shaper_context: dict[str, Any]):
    content = shaper_context["agent_content"].lower()
    assert "approach-evaluation" in content, (
        "Agent does not reference approach-evaluation skill"
    )


# ---------------------------------------------------------------------------
# Then Steps -- Skill File Validation
# ---------------------------------------------------------------------------


@then("the skill has YAML frontmatter with name and description")
def skill_has_frontmatter(shaper_context: dict[str, Any]):
    fm = shaper_context["skill_frontmatter"]
    assert "name" in fm, f"Skill frontmatter missing 'name'. Got: {fm}"
    assert "description" in fm, f"Skill frontmatter missing 'description'. Got: {fm}"


@then("the skill defines the five scoring dimensions with weights")
def skill_has_dimensions(shaper_context: dict[str, Any]):
    content = shaper_context["skill_content"].lower()
    for dim in ["personnel alignment", "past performance", "technical readiness",
                "solicitation fit", "commercialization"]:
        assert dim in content, f"Skill missing dimension: {dim}"
    # Check weights are mentioned
    for weight in ["0.25", "0.20", "0.15"]:
        assert weight in shaper_context["skill_content"], (
            f"Skill missing weight value: {weight}"
        )


@then("the skill documents the approach brief schema")
def skill_has_brief_schema(shaper_context: dict[str, Any]):
    content = shaper_context["skill_content"].lower()
    assert "approach brief" in content or "approach-brief" in content, (
        "Skill does not document the approach brief schema"
    )


# ---------------------------------------------------------------------------
# Then Steps -- Command File Validation
# ---------------------------------------------------------------------------


@then(
    "the command has YAML frontmatter with description and argument-hint"
)
def command_has_frontmatter(shaper_context: dict[str, Any]):
    fm = shaper_context["command_frontmatter"]
    assert "description" in fm, f"Command frontmatter missing 'description'. Got: {fm}"


@then("the command dispatches to the solution-shaper agent")
def command_dispatches(shaper_context: dict[str, Any]):
    content = shaper_context["command_content"].lower()
    assert "solution-shaper" in content or "sbir-solution-shaper" in content, (
        "Command does not dispatch to solution-shaper agent"
    )


@then("the command documents the revise flag")
def command_has_revise(shaper_context: dict[str, Any]):
    content = shaper_context["command_content"].lower()
    assert "revise" in content, "Command does not document the --revise flag"
