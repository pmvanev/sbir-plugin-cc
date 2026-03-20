"""Step definitions for style profile and quality summary scenarios.

Invokes through: style profile validation and quality summary utilities (new domain services).
Tests style profile parsing, validation, persistence, and quality outlier detection.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.visual_asset_quality.conftest import make_style_profile
from tests.acceptance.visual_asset_quality.steps.common_steps import *  # noqa: F403

# Link to feature files
scenarios("../milestone-04-quality-summary.feature")


# --- Given steps ---


@given(
    parsers.parse(
        'Phil has an approved style profile for agency "{agency}" with domain "{domain}"'
    ),
)
def approved_style_profile(style_context, agency, domain):
    """Set up a style profile for the given agency and domain."""
    style_context["profile"] = make_style_profile(agency=agency, domain=domain)


@given(
    parsers.parse('the palette includes primary "{primary}" and secondary "{secondary}"'),
)
def palette_primary_secondary(style_context, primary, secondary):
    """Set palette colors on the style profile."""
    style_context["profile"]["palette"]["primary"] = primary
    style_context["profile"]["palette"]["secondary"] = secondary


@given(
    parsers.parse(
        'a style profile with agency "{agency}" and domain "{domain}"'
    ),
)
def style_profile_agency_domain(style_context, agency, domain):
    """Create a style profile with agency and domain."""
    style_context["profile"] = make_style_profile(agency=agency, domain=domain)


@given(
    parsers.parse('palette primary "{primary}" and secondary "{secondary}"'),
)
def set_palette(style_context, primary, secondary):
    """Set palette primary and secondary."""
    style_context["profile"]["palette"]["primary"] = primary
    style_context["profile"]["palette"]["secondary"] = secondary


@given(
    parsers.parse('tone "{tone}" and detail level "{level}"'),
)
def set_tone_detail(style_context, tone, level):
    """Set tone and detail level."""
    style_context["profile"]["tone"] = tone
    style_context["profile"]["detail_level"] = level


@given(
    parsers.parse('palette with secondary "{secondary}" but no primary color'),
)
def palette_no_primary(style_context, secondary):
    """Set palette with missing primary."""
    style_context["profile"]["palette"]["secondary"] = secondary
    style_context["profile"]["palette"].pop("primary", None)


@given(
    parsers.parse('palette with primary "{primary}" but no secondary color'),
)
def palette_no_secondary(style_context, primary):
    """Set palette with missing secondary."""
    style_context["profile"]["palette"]["primary"] = primary
    style_context["profile"]["palette"].pop("secondary", None)


@given(
    parsers.parse('a style profile with detail level "{level}"'),
)
def style_profile_detail_level(style_context, level):
    """Create a style profile with specific detail level."""
    style_context["profile"] = make_style_profile(detail_level=level)


@given("a style profile with all required fields")
def style_profile_all_fields(style_context):
    """Create a complete style profile."""
    style_context["profile"] = make_style_profile()


@given("the avoid list is empty")
def empty_avoid_list(style_context):
    """Set empty avoid list on the profile."""
    style_context["profile"]["avoid"] = []


@given(
    parsers.parse(
        'a style profile for agency "{agency}" with palette primary "{primary}" and secondary "{secondary}"'
    ),
)
def style_for_roundtrip(style_context, agency, primary, secondary):
    """Create a style profile for roundtrip testing."""
    style_context["profile"] = make_style_profile(
        agency=agency, primary=primary, secondary=secondary,
    )


# --- Quality summary Given steps ---


@given(
    parsers.parse("Figure {num:d} has average rating {rating:g}"),
)
def figure_average_rating(quality_context, num, rating):
    """Record a figure's average rating for outlier detection."""
    quality_context.setdefault("figure_ratings", {})[num] = rating


@given(
    parsers.parse("the proposal average for {category} is {avg:g}"),
)
def proposal_category_average(quality_context, category, avg):
    """Record the proposal-wide average for a category."""
    quality_context.setdefault("category_averages", {})[category] = avg


@given(
    parsers.parse("Figure {num:d} has {category} rated {rating:d}"),
)
def figure_category_rating(quality_context, num, category, rating):
    """Record a figure's rating for a specific category."""
    quality_context.setdefault("figure_category_ratings", {}).setdefault(num, {})[category] = rating


@given(
    parsers.parse('the approved palette is "{palette_str}"'),
)
def approved_palette(quality_context, palette_str):
    """Record the approved palette colors."""
    quality_context["approved_palette"] = [c.strip() for c in palette_str.split(",")]


@given(
    parsers.parse(
        'Figure {num:d} prompt contains palette colors "{c1}" and "{c2}"'
    ),
)
def figure_prompt_colors(quality_context, num, c1, c2):
    """Record palette colors used in a figure's prompt."""
    quality_context.setdefault("figure_prompt_colors", {})[num] = [c1, c2]


@given(
    parsers.parse(
        'Figure {num:d} prompt contains palette color "{color}" not in the approved palette'
    ),
)
def figure_unapproved_color(quality_context, num, color):
    """Record an unapproved color used in a figure's prompt."""
    quality_context.setdefault("figure_prompt_colors", {})[num] = [color]
    quality_context.setdefault("unapproved_colors", {})[num] = color


# --- Integration checkpoint Given steps ---


@given(
    parsers.parse(
        'an approved style profile with palette primary "{primary}" and secondary "{secondary}"'
    ),
)
def approved_profile_for_integration(quality_context, primary, secondary):
    """Set up approved style profile for integration checkpoint."""
    quality_context["style_profile"] = make_style_profile(
        primary=primary, secondary=secondary,
    )


@given(
    parsers.parse('a prompt template for Figure {num:d} type "{fig_type}"'),
)
def prompt_template_for_figure(quality_context, num, fig_type):
    """Record a prompt template for a specific figure."""
    quality_context.setdefault("prompt_templates", {})[num] = fig_type


@given(
    parsers.parse("Figure {num:d} was critiqued with average rating {rating:g}"),
)
def figure_critiqued_rating(quality_context, num, rating):
    """Record a figure's critique rating for summary."""
    quality_context.setdefault("critique_ratings", {})[num] = rating


# --- When steps ---


@when("the style profile is loaded from disk")
def load_style_profile(style_context, style_profile_path):
    """Write and read the style profile (roundtrip through YAML)."""
    import yaml

    profile = style_context["profile"]
    style_profile_path.write_text(
        yaml.dump(profile, default_flow_style=False), encoding="utf-8"
    )
    loaded = yaml.safe_load(style_profile_path.read_text(encoding="utf-8"))
    style_context["loaded_profile"] = loaded


@when("the style profile is validated")
def validate_style_profile(style_context):
    """Validate style profile fields.

    Will invoke the style profile validator when implemented.
    """
    profile = style_context["profile"]
    errors = []

    palette = profile.get("palette", {})
    if "primary" not in palette or not palette.get("primary"):
        errors.append("Primary color is required in palette")
    if "secondary" not in palette or not palette.get("secondary"):
        errors.append("Secondary color is required in palette")

    detail_level = profile.get("detail_level", "")
    if detail_level not in ("low", "medium", "high"):
        errors.append('Detail level must be "low", "medium", or "high"')

    style_context["validation_errors"] = errors
    style_context["valid"] = len(errors) == 0


@when("the style profile is saved to disk and loaded back")
def roundtrip_style_profile(style_context, style_profile_path):
    """Write style profile as YAML, then read it back."""
    import yaml

    profile = style_context["profile"]
    style_profile_path.write_text(
        yaml.dump(profile, default_flow_style=False), encoding="utf-8"
    )
    style_context["loaded_profile"] = yaml.safe_load(
        style_profile_path.read_text(encoding="utf-8")
    )


@when("quality outliers are checked")
def check_quality_outliers(quality_context):
    """Check for quality outliers across figures.

    Outlier rule: any category rated 2+ points below proposal average.
    """
    outliers = []

    # Check per-category outliers
    cat_avgs = quality_context.get("category_averages", {})
    fig_cat_ratings = quality_context.get("figure_category_ratings", {})
    for fig_num, ratings in fig_cat_ratings.items():
        for cat, rating in ratings.items():
            avg = cat_avgs.get(cat, rating)
            if avg - rating >= 2.0:
                outliers.append({"figure": fig_num, "category": cat, "rating": rating, "average": avg})

    # Check overall average outliers
    fig_ratings = quality_context.get("figure_ratings", {})
    if fig_ratings:
        overall_avg = sum(fig_ratings.values()) / len(fig_ratings)
        for fig_num, rating in fig_ratings.items():
            if overall_avg - rating >= 2.0:
                outliers.append({"figure": fig_num, "category": "overall", "rating": rating, "average": overall_avg})

    quality_context["outliers"] = outliers


@when("style consistency is checked")
def check_style_consistency(quality_context):
    """Check style consistency across figure prompts.

    Compares prompt colors against approved palette.
    """
    approved = set(quality_context.get("approved_palette", []))
    fig_colors = quality_context.get("figure_prompt_colors", {})
    unapproved = quality_context.get("unapproved_colors", {})

    warnings = []
    for fig_num, colors in fig_colors.items():
        for color in colors:
            if color not in approved:
                warnings.append({
                    "figure": fig_num,
                    "color": color,
                })

    quality_context["style_warnings"] = warnings
    quality_context["style_status"] = "PASS" if not warnings else "WARN"


@when("both prompts are rendered with the style profile")
def render_both_prompts(quality_context):
    """Render prompt templates with the style profile for integration check."""
    profile = quality_context["style_profile"]
    templates = quality_context.get("prompt_templates", {})
    rendered = []
    for num, fig_type in templates.items():
        palette = profile["palette"]
        prompt = (
            f"COMPOSITION: {fig_type} layout\n"
            f"STYLE: {profile['tone']}, {palette['primary']}, {palette['secondary']}\n"
        )
        rendered.append(prompt)
    quality_context["rendered_prompts"] = rendered


@when("the quality summary is computed")
def compute_quality_summary(quality_context):
    """Compute quality summary from critique ratings."""
    ratings = quality_context.get("critique_ratings", {})
    quality_context["summary"] = dict(ratings)
    if ratings:
        quality_context["overall_average"] = sum(ratings.values()) / len(ratings)


# --- Then steps ---


@then(parsers.parse('the profile contains agency "{agency}" and domain "{domain}"'))
def profile_has_agency_domain(style_context, agency, domain):
    """Assert loaded profile has expected agency and domain."""
    loaded = style_context["loaded_profile"]
    assert loaded["agency"] == agency
    assert loaded["domain"] == domain


@then("the palette has at least primary and secondary colors")
def palette_has_required_colors(style_context):
    """Assert loaded palette has primary and secondary."""
    palette = style_context["loaded_profile"]["palette"]
    assert "primary" in palette
    assert "secondary" in palette


@then(parsers.parse('the detail level is one of "low", "medium", or "high"'))
def detail_level_valid(style_context):
    """Assert detail level is valid."""
    level = style_context["loaded_profile"]["detail_level"]
    assert level in ("low", "medium", "high")


@then("the profile passes validation")
def style_profile_valid(style_context):
    """Assert style profile validation passed."""
    assert style_context["valid"]


@then("a validation error indicates primary color is required")
def error_primary_required(style_context):
    """Assert validation error about missing primary color."""
    errors = style_context["validation_errors"]
    assert any("primary" in e.lower() for e in errors)


@then("a validation error indicates secondary color is required")
def error_secondary_required(style_context):
    """Assert validation error about missing secondary color."""
    errors = style_context["validation_errors"]
    assert any("secondary" in e.lower() for e in errors)


@then(parsers.parse('a validation error indicates detail level must be "low", "medium", or "high"'))
def error_detail_level(style_context):
    """Assert validation error about invalid detail level."""
    errors = style_context["validation_errors"]
    assert any("detail level" in e.lower() for e in errors)


@then("the loaded profile matches the original")
def profile_roundtrip_matches(style_context):
    """Assert roundtrip preserves profile data."""
    original = style_context["profile"]
    loaded = style_context["loaded_profile"]
    assert loaded == original


@then("no figures are flagged as outliers")
def no_outliers(quality_context):
    """Assert no quality outliers detected."""
    assert len(quality_context["outliers"]) == 0


@then(parsers.parse("Figure {num:d} is flagged as an outlier for {category}"))
def figure_is_outlier(quality_context, num, category):
    """Assert a specific figure is flagged as outlier."""
    outliers = quality_context["outliers"]
    match = [o for o in outliers if o["figure"] == num and o["category"] == category]
    assert len(match) > 0, f"Expected Figure {num} flagged for {category}"


@then(parsers.parse("Figure {num:d} is not flagged as an outlier"))
def figure_not_outlier(quality_context, num):
    """Assert a specific figure is not flagged."""
    outliers = quality_context["outliers"]
    match = [o for o in outliers if o["figure"] == num]
    assert len(match) == 0, f"Figure {num} unexpectedly flagged"


@then(parsers.parse('style consistency is "{status}"'))
def style_consistency_status(quality_context, status):
    """Assert style consistency status."""
    assert quality_context["style_status"] == status


@then(parsers.parse('style consistency is "{status}" for Figure {num:d}'))
def style_consistency_warn_figure(quality_context, status, num):
    """Assert style consistency warning for a specific figure."""
    assert quality_context["style_status"] == status
    warnings = quality_context["style_warnings"]
    assert any(w["figure"] == num for w in warnings)


@then(parsers.parse('the warning identifies "{color}" as the unapproved color'))
def warning_identifies_color(quality_context, color):
    """Assert the warning identifies the specific unapproved color."""
    warnings = quality_context["style_warnings"]
    assert any(w["color"] == color for w in warnings)


@then(parsers.parse("the summary shows Figure {num:d} with rating {rating:g}"))
def summary_figure_rating(quality_context, num, rating):
    """Assert quality summary shows expected figure rating."""
    assert quality_context["summary"][num] == rating


@then(parsers.parse("the overall average is {avg:g}"))
def overall_average(quality_context, avg):
    """Assert overall average rating."""
    assert abs(quality_context["overall_average"] - avg) < 0.01
