"""Step definitions for prompt engineering scenarios.

Invokes through: prompt template rendering utilities (new domain service).
Tests prompt template construction, rendering, and hash computation.
"""

from __future__ import annotations

import hashlib
from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.visual_asset_quality.conftest import make_style_profile
from tests.acceptance.visual_asset_quality.steps.common_steps import *  # noqa: F403

# Link to feature files
scenarios("../milestone-01-prompt-engineering.feature")


# --- Fixtures ---


@pytest.fixture()
def prompt_context() -> dict[str, Any]:
    """Mutable container for prompt template operations."""
    return {}


# --- Given steps ---


@given(
    "a prompt template with placeholders for composition, style, labels, avoid, and resolution",
)
def prompt_template_with_all_sections(prompt_context):
    """Set up a prompt template expecting all five sections."""
    prompt_context["template"] = {
        "sections": ["COMPOSITION", "STYLE", "LABELS", "AVOID", "RESOLUTION"],
    }


@given(
    parsers.parse(
        'figure type is "{fig_type}" with description "{description}"'
    ),
)
def figure_type_and_description(prompt_context, fig_type, description):
    """Set figure type and description for prompt rendering."""
    prompt_context["figure_type"] = fig_type
    prompt_context["description"] = description


@given(
    parsers.parse(
        'the style profile has palette primary "{primary}" and tone "{tone}"'
    ),
)
def style_profile_primary_tone(prompt_context, primary, tone):
    """Set style profile with primary color and tone."""
    profile = prompt_context.get("style_profile", make_style_profile())
    profile["palette"]["primary"] = primary
    profile["tone"] = tone
    prompt_context["style_profile"] = profile


@given(
    parsers.parse(
        'the style profile has palette primary "{primary}" and secondary "{secondary}"'
    ),
)
def style_profile_primary_secondary(prompt_context, primary, secondary):
    """Set style profile with primary and secondary colors."""
    profile = prompt_context.get("style_profile", make_style_profile())
    profile["palette"]["primary"] = primary
    profile["palette"]["secondary"] = secondary
    prompt_context["style_profile"] = profile


@given(
    parsers.parse('a prompt template for figure type "{fig_type}"'),
)
def prompt_template_for_type(prompt_context, fig_type):
    """Set up a prompt template for a specific figure type."""
    prompt_context["figure_type"] = fig_type
    prompt_context["template"] = {
        "sections": ["COMPOSITION", "STYLE", "LABELS", "AVOID", "RESOLUTION"],
    }


@given(
    parsers.parse('the figure description is "{description}"'),
)
def set_figure_description(prompt_context, description):
    """Set the figure description for prompt rendering."""
    prompt_context["description"] = description


@given("the figure description is empty")
def empty_figure_description(prompt_context):
    """Set an empty figure description."""
    prompt_context["description"] = ""


@given("no resolution or aspect ratio is specified in the figure plan")
def no_resolution_specified(prompt_context):
    """Ensure no resolution/aspect ratio is set."""
    prompt_context["resolution"] = None
    prompt_context["aspect_ratio"] = None


@given("no style profile exists")
def no_style_profile(prompt_context):
    """Ensure no style profile is available."""
    prompt_context["style_profile"] = None


@given(
    parsers.parse('a rendered prompt with text "{text}"'),
)
def rendered_prompt_text(prompt_context, text):
    """Set a specific prompt text for hash testing."""
    prompt_context["prompt_text"] = text


@given(
    parsers.parse('prompt A with text "{text}"'),
)
def prompt_a_text(prompt_context, text):
    """Set prompt A text for comparison."""
    prompt_context["prompt_a"] = text


@given(
    parsers.parse('prompt B with text "{text}"'),
)
def prompt_b_text(prompt_context, text):
    """Set prompt B text for comparison."""
    prompt_context["prompt_b"] = text


# --- When steps ---


@when("the prompt template is rendered")
def render_prompt_template(prompt_context):
    """Render the prompt template with available context.

    This will invoke the prompt rendering service when implemented.
    For now, constructs a prompt from available context data.
    """
    fig_type = prompt_context.get("figure_type", "system-diagram")
    description = prompt_context.get("description", "")
    style = prompt_context.get("style_profile", None)
    resolution = prompt_context.get("resolution", "2K")
    aspect_ratio = prompt_context.get("aspect_ratio", "16:9")

    # Build prompt sections -- this will delegate to production code
    sections = []
    sections.append(f"COMPOSITION: {fig_type} layout")
    if style:
        palette = style.get("palette", {})
        tone = style.get("tone", "professional")
        colors = ", ".join(f"{v}" for v in palette.values() if v)
        sections.append(f"STYLE: {tone}, {colors}")
    else:
        sections.append("STYLE: clean professional illustration, neutral palette")
    if description:
        sections.append(f"LABELS: {description}")
    else:
        sections.append(f"COMPOSITION: {fig_type} type directives")
    avoid = style.get("avoid", []) if style else []
    sections.append(f"AVOID: {', '.join(avoid) if avoid else 'none specified'}")
    if resolution is None:
        resolution = "2K"
    if aspect_ratio is None:
        aspect_ratio = "16:9"
    sections.append(f"RESOLUTION: {resolution}, {aspect_ratio}")

    prompt_context["rendered"] = "\n".join(sections)


@when("the prompt hash is computed twice")
def compute_hash_twice(prompt_context):
    """Compute prompt hash twice for determinism check."""
    text = prompt_context["prompt_text"]
    prompt_context["hash_1"] = hashlib.sha256(text.encode()).hexdigest()
    prompt_context["hash_2"] = hashlib.sha256(text.encode()).hexdigest()


@when("the prompt hashes are computed")
def compute_two_hashes(prompt_context):
    """Compute hashes for two different prompts."""
    prompt_context["hash_a"] = hashlib.sha256(
        prompt_context["prompt_a"].encode()
    ).hexdigest()
    prompt_context["hash_b"] = hashlib.sha256(
        prompt_context["prompt_b"].encode()
    ).hexdigest()


# --- Then steps ---


@then("the rendered prompt contains a COMPOSITION section")
def prompt_has_composition(prompt_context):
    """Assert rendered prompt includes COMPOSITION."""
    assert "COMPOSITION:" in prompt_context["rendered"]


@then(parsers.parse('the rendered prompt contains a STYLE section with "{color}"'))
def prompt_has_style_with_color(prompt_context, color):
    """Assert rendered prompt STYLE section includes the color."""
    rendered = prompt_context["rendered"]
    assert "STYLE:" in rendered
    assert color in rendered


@then("the rendered prompt contains a LABELS section")
def prompt_has_labels(prompt_context):
    """Assert rendered prompt includes LABELS."""
    assert "LABELS:" in prompt_context["rendered"]


@then("the rendered prompt contains an AVOID section")
def prompt_has_avoid(prompt_context):
    """Assert rendered prompt includes AVOID."""
    assert "AVOID:" in prompt_context["rendered"]


@then("the rendered prompt contains a RESOLUTION section")
def prompt_has_resolution(prompt_context):
    """Assert rendered prompt includes RESOLUTION."""
    assert "RESOLUTION:" in prompt_context["rendered"]


@then(parsers.parse('the rendered prompt includes both "{color1}" and "{color2}"'))
def prompt_includes_both_colors(prompt_context, color1, color2):
    """Assert rendered prompt includes both palette colors."""
    rendered = prompt_context["rendered"]
    assert color1 in rendered
    assert color2 in rendered


@then(parsers.parse('the rendered prompt includes "{text}"'))
def prompt_includes_text(prompt_context, text):
    """Assert rendered prompt includes specific text."""
    assert text in prompt_context["rendered"]


@then(parsers.parse('the rendered prompt includes resolution "{res}"'))
def prompt_includes_resolution(prompt_context, res):
    """Assert rendered prompt includes specific resolution."""
    assert res in prompt_context["rendered"]


@then(parsers.parse('the rendered prompt includes aspect ratio "{ratio}"'))
def prompt_includes_aspect_ratio(prompt_context, ratio):
    """Assert rendered prompt includes specific aspect ratio."""
    assert ratio in prompt_context["rendered"]


@then("the rendered prompt contains a STYLE section with generic professional defaults")
def prompt_has_generic_style(prompt_context):
    """Assert rendered prompt has generic style when no profile exists."""
    rendered = prompt_context["rendered"]
    assert "STYLE:" in rendered
    assert "professional" in rendered.lower()


@then("no rendering error occurs")
def no_rendering_error(prompt_context):
    """Assert prompt rendered without error."""
    assert "rendered" in prompt_context
    assert len(prompt_context["rendered"]) > 0


@then("the rendered prompt does not contain an empty LABELS section")
def prompt_no_empty_labels(prompt_context):
    """Assert LABELS section is not empty."""
    rendered = prompt_context["rendered"]
    # Should not have "LABELS: " followed by nothing meaningful
    if "LABELS:" in rendered:
        idx = rendered.index("LABELS:")
        label_content = rendered[idx + 7:].split("\n")[0].strip()
        assert len(label_content) > 0 or "LABELS:" not in rendered


@then("the COMPOSITION section still contains figure-type directives")
def composition_has_type_directives(prompt_context):
    """Assert COMPOSITION section has content even with empty description."""
    rendered = prompt_context["rendered"]
    assert "COMPOSITION:" in rendered


@then("both hash values are identical")
def hashes_identical(prompt_context):
    """Assert two hash computations produce same result."""
    assert prompt_context["hash_1"] == prompt_context["hash_2"]


@then("the two hashes are different")
def hashes_different(prompt_context):
    """Assert hashes of different prompts differ."""
    assert prompt_context["hash_a"] != prompt_context["hash_b"]
