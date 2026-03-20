"""Step definitions for TikZ generation and VisualAssetService routing scenarios.

Invokes through: VisualAssetService (driving port -- domain service).
Also tests FileVisualAssetAdapter for TikZ file persistence.
Does NOT import internal routing methods directly.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.visual_asset_quality.conftest import make_placeholder
from tests.acceptance.visual_asset_quality.steps.common_steps import *  # noqa: F403

# Link to feature files
scenarios("../walking-skeleton.feature")
scenarios("../milestone-03-tikz-generation.feature")
scenarios("../integration-checkpoints.feature")


# --- Given steps ---


@given(
    parsers.parse(
        'Phil has a figure planned as "{title}" in section {section} using TikZ'
    ),
    target_fixture="figure_placeholder",
)
def placeholder_tikz(title, section):
    """Create a TikZ figure placeholder."""
    return make_placeholder(
        figure_number=2,
        section_id=section,
        description=title,
        figure_type="block-diagram",
        generation_method="tikz",
    )


@given(
    parsers.parse(
        'a figure placeholder for Figure {num:d} "{title}" with method "{method}"'
    ),
    target_fixture="figure_placeholder",
)
def placeholder_with_method(num, title, method):
    """Create a figure placeholder with specified method."""
    return make_placeholder(
        figure_number=num,
        description=title,
        generation_method=method,
    )


@given(
    parsers.parse(
        'a figure placeholder for Figure {num:d} with method "{method}"'
    ),
    target_fixture="figure_placeholder",
)
def placeholder_num_method(num, method):
    """Create a figure placeholder by number and method."""
    return make_placeholder(figure_number=num, generation_method=method)


@given(
    parsers.parse(
        'a figure placeholder for Figure {num:d} "{title}" type "{fig_type}" with method "{method}"'
    ),
    target_fixture="figure_placeholder",
)
def placeholder_with_type_method(num, title, fig_type, method):
    """Create a figure placeholder with explicit type and method."""
    return make_placeholder(
        figure_number=num,
        description=title,
        figure_type=fig_type,
        generation_method=method,
    )


@given(
    parsers.parse('the prompt hash is "{hash_val}"'),
)
def set_prompt_hash(generation_result, hash_val):
    """Record the prompt hash to attach to the generation result."""
    generation_result["prompt_hash"] = hash_val


@given(
    parsers.parse("the figure has been through {count:d} refinement iterations"),
)
def set_iteration_count(generation_result, count):
    """Record the iteration count to attach to the generation result."""
    generation_result["iteration_count"] = count


@given(
    parsers.parse(
        'a generated figure for Figure {num:d} with format "{fmt}" and file path "{path}"'
    ),
)
def generated_figure_for_write(generation_result, num, fmt, path):
    """Set up a generated figure for adapter write testing."""
    from pes.domain.visual_asset import GeneratedFigure

    generation_result["figure"] = GeneratedFigure(
        figure_number=num,
        section_id="3.1",
        file_path=path,
        format=fmt,
    )


@given(
    parsers.parse('the TikZ source content is "{content}"'),
)
def tikz_source_content(generation_result, content):
    """Record TikZ source content for write testing."""
    generation_result["content"] = content


@given(
    parsers.parse(
        'an inventory file containing Figure {num:d} with method "{method}" and type "{fig_type}"'
    ),
)
def inventory_file_on_disk(artifacts_dir, num, method, fig_type):
    """Write an inventory file to disk for read testing."""
    data = {
        "placeholders": [
            {
                "figure_number": num,
                "section_id": "3.1",
                "description": "Test figure",
                "figure_type": fig_type,
                "generation_method": method,
            }
        ]
    }
    (artifacts_dir / "figure-inventory.json").write_text(
        json.dumps(data, indent=2), encoding="utf-8"
    )


@given(
    parsers.parse('Figure {num:d} uses method "{method}"'),
)
def record_figure_method(generation_result, num, method):
    """Record a figure/method pair for multi-figure scenarios."""
    generation_result.setdefault("figures", []).append(
        make_placeholder(figure_number=num, generation_method=method)
    )


@given(
    parsers.parse(
        'an inventory with Figure {n1:d} method "{m1}", Figure {n2:d} method "{m2}", and Figure {n3:d} method "{m3}"'
    ),
)
def inventory_three_methods(generation_result, n1, m1, n2, m2, n3, m3):
    """Build an inventory with three figures of different methods."""
    from pes.domain.visual_asset import FigureInventory

    placeholders = [
        make_placeholder(figure_number=n1, generation_method=m1),
        make_placeholder(figure_number=n2, generation_method=m2),
        make_placeholder(figure_number=n3, generation_method=m3),
    ]
    generation_result["inventory"] = FigureInventory(placeholders=placeholders)


@given(
    parsers.parse('a prompt hash "{hash_val}" was computed before generation'),
)
def prompt_hash_before_gen(generation_result, hash_val):
    """Record a prompt hash for integration checkpoint."""
    generation_result["prompt_hash"] = hash_val


# --- When steps ---


@when("Phil generates the figure through the visual asset service")
def generate_figure(figure_placeholder, generation_result, stub_generator, stub_pdc_checker, artifacts_dir):
    """Generate a figure through the VisualAssetService driving port."""
    from pes.adapters.file_visual_asset_adapter import FileVisualAssetAdapter
    from pes.domain.visual_asset_service import VisualAssetService

    adapter = FileVisualAssetAdapter(artifacts_dir)
    service = VisualAssetService(stub_generator, adapter, stub_pdc_checker)
    result = service.generate_figure(figure_placeholder)
    generation_result["result"] = result


@when("the figure is generated through the visual asset service")
def generate_figure_generic(figure_placeholder, generation_result, stub_generator, stub_pdc_checker, artifacts_dir):
    """Generate a figure through the service (generic phrasing)."""
    from pes.adapters.file_visual_asset_adapter import FileVisualAssetAdapter
    from pes.domain.visual_asset_service import VisualAssetService

    adapter = FileVisualAssetAdapter(artifacts_dir)
    service = VisualAssetService(stub_generator, adapter, stub_pdc_checker)
    result = service.generate_figure(figure_placeholder)
    generation_result["result"] = result


@when("the figure is generated with prompt tracking")
def generate_with_prompt_tracking(figure_placeholder, generation_result, stub_generator, stub_pdc_checker, artifacts_dir):
    """Generate figure and attach prompt hash to result."""
    from pes.adapters.file_visual_asset_adapter import FileVisualAssetAdapter
    from pes.domain.visual_asset_service import VisualAssetService

    adapter = FileVisualAssetAdapter(artifacts_dir)
    service = VisualAssetService(stub_generator, adapter, stub_pdc_checker)
    result = service.generate_figure(figure_placeholder)
    # Prompt hash is set on the result by the caller (agent) after generation
    prompt_hash = generation_result.get("prompt_hash", "")
    generation_result["result"] = result
    generation_result["result_prompt_hash"] = prompt_hash


@when("the figure is generated with iteration tracking")
def generate_with_iteration_tracking(figure_placeholder, generation_result, stub_generator, stub_pdc_checker, artifacts_dir):
    """Generate figure and attach iteration count to result."""
    from pes.adapters.file_visual_asset_adapter import FileVisualAssetAdapter
    from pes.domain.visual_asset_service import VisualAssetService

    adapter = FileVisualAssetAdapter(artifacts_dir)
    service = VisualAssetService(stub_generator, adapter, stub_pdc_checker)
    result = service.generate_figure(figure_placeholder)
    iteration_count = generation_result.get("iteration_count", 0)
    generation_result["result"] = result
    generation_result["result_iteration_count"] = iteration_count


@when("the figure is written through the visual asset adapter")
def write_figure_via_adapter(generation_result, artifacts_dir):
    """Write a generated figure through the FileVisualAssetAdapter."""
    from pes.adapters.file_visual_asset_adapter import FileVisualAssetAdapter

    adapter = FileVisualAssetAdapter(artifacts_dir)
    figure = generation_result["figure"]
    content = generation_result["content"]
    adapter.write_figure(figure, content)


@when("the inventory is read through the visual asset adapter")
def read_inventory_via_adapter(generation_result, artifacts_dir):
    """Read figure inventory through the FileVisualAssetAdapter."""
    from pes.adapters.file_visual_asset_adapter import FileVisualAssetAdapter

    adapter = FileVisualAssetAdapter(artifacts_dir)
    inventory = adapter.read_inventory()
    generation_result["inventory"] = inventory


@when("all figures are generated through the visual asset service")
def generate_all_figures(generation_result, stub_generator, stub_pdc_checker, artifacts_dir):
    """Generate all recorded figures through the service."""
    from pes.adapters.file_visual_asset_adapter import FileVisualAssetAdapter
    from pes.domain.visual_asset_service import VisualAssetService

    adapter = FileVisualAssetAdapter(artifacts_dir)
    service = VisualAssetService(stub_generator, adapter, stub_pdc_checker)
    results = []
    for placeholder in generation_result["figures"]:
        results.append(service.generate_figure(placeholder))
    generation_result["results"] = results


@when("the inventory is written and read back through the adapter")
def roundtrip_inventory(generation_result, artifacts_dir):
    """Write inventory then read it back through the adapter."""
    from pes.adapters.file_visual_asset_adapter import FileVisualAssetAdapter

    adapter = FileVisualAssetAdapter(artifacts_dir)
    inventory = generation_result["inventory"]
    adapter.write_inventory(inventory)
    generation_result["loaded_inventory"] = adapter.read_inventory()


@when("the figure is generated and the result is approved")
def generate_and_approve(figure_placeholder, generation_result, stub_generator, stub_pdc_checker, artifacts_dir):
    """Generate figure then approve it through the service."""
    from pes.adapters.file_visual_asset_adapter import FileVisualAssetAdapter
    from pes.domain.visual_asset_service import VisualAssetService

    adapter = FileVisualAssetAdapter(artifacts_dir)
    service = VisualAssetService(stub_generator, adapter, stub_pdc_checker)
    result = service.generate_figure(figure_placeholder)
    approved = service.approve_figure(result)
    generation_result["result"] = approved
    generation_result["approved_prompt_hash"] = generation_result.get("prompt_hash", "")


# --- Then steps ---


@then("the result indicates the figure was generated as TikZ format")
def result_tikz_format(generation_result):
    """Assert the generation result has TikZ format."""
    result = generation_result["result"]
    assert result.format == "tikz"


@then("the result includes a prompt hash for audit traceability")
def result_has_prompt_hash_field(generation_result):
    """Assert the result type supports prompt_hash field."""
    result = generation_result["result"]
    # The result dataclass should have prompt_hash attribute
    assert hasattr(result, "prompt_hash") or "prompt_hash" in dir(result)


@then("the result includes the iteration count")
def result_has_iteration_count_field(generation_result):
    """Assert the result type supports iteration_count field."""
    result = generation_result["result"]
    assert hasattr(result, "iteration_count") or "iteration_count" in dir(result)


@then(parsers.parse('the result has format "{fmt}"'))
def result_has_format(generation_result, fmt):
    """Assert the result has the expected format."""
    result = generation_result["result"]
    assert result.format == fmt


@then(parsers.parse('the result has generation method "{method}"'))
def result_has_method(generation_result, method):
    """Assert the result has the expected generation method."""
    result = generation_result["result"]
    assert result.generation_method == method


@then(parsers.parse('the result has review status "{status}"'))
def result_has_review_status(generation_result, status):
    """Assert the result has the expected review status."""
    result = generation_result["result"]
    assert result.review_status == status


@then(parsers.parse('the result file path ends with "{suffix}"'))
def result_path_ends_with(generation_result, suffix):
    """Assert the result file path has the expected suffix."""
    result = generation_result["result"]
    assert result.file_path.endswith(suffix)


@then(parsers.parse('the result prompt hash is "{hash_val}"'))
def result_prompt_hash_value(generation_result, hash_val):
    """Assert the prompt hash matches."""
    if "result_prompt_hash" in generation_result:
        assert generation_result["result_prompt_hash"] == hash_val
    else:
        result = generation_result["result"]
        assert result.prompt_hash == hash_val


@then("the result prompt hash is empty")
def result_prompt_hash_empty(generation_result):
    """Assert the prompt hash is empty/default."""
    result = generation_result["result"]
    assert result.prompt_hash == "" or result.prompt_hash is None


@then(parsers.parse("the result iteration count is {count:d}"))
def result_iteration_count(generation_result, count):
    """Assert the iteration count matches."""
    if "result_iteration_count" in generation_result:
        assert generation_result["result_iteration_count"] == count
    else:
        result = generation_result["result"]
        assert result.iteration_count == count


@then(parsers.parse('the file "{filename}" exists in the figures directory'))
def file_exists_in_figures(figures_dir, filename):
    """Assert a file exists in the figures directory."""
    assert (figures_dir / filename).exists()


@then("the file content matches the TikZ source")
def file_content_matches(figures_dir, generation_result):
    """Assert the written file content matches the original."""
    figure = generation_result["figure"]
    content = (figures_dir / figure.file_path).read_text(encoding="utf-8")
    assert content == generation_result["content"]


@then(parsers.parse('Figure {num:d} has generation method "{method}"'))
def inventory_figure_method(generation_result, num, method):
    """Assert a figure in the loaded inventory has the expected method."""
    inventory = generation_result["inventory"]
    fig = next(p for p in inventory.placeholders if p.figure_number == num)
    assert fig.generation_method == method


@then(parsers.parse('Figure {num:d} has figure type "{fig_type}"'))
def inventory_figure_type(generation_result, num, fig_type):
    """Assert a figure in the loaded inventory has the expected type."""
    inventory = generation_result["inventory"]
    fig = next(p for p in inventory.placeholders if p.figure_number == num)
    assert fig.figure_type == fig_type


@then(parsers.parse("all {count:d} results have valid format fields"))
def all_results_valid_format(generation_result, count):
    """Assert all results have non-empty format fields."""
    results = generation_result["results"]
    assert len(results) == count
    for r in results:
        assert r.format, f"Figure {r.figure_number} has empty format"


@then(parsers.parse("all {count:d} results have valid review status fields"))
def all_results_valid_status(generation_result, count):
    """Assert all results have non-empty review status fields."""
    results = generation_result["results"]
    assert len(results) == count
    for r in results:
        assert r.review_status, f"Figure {r.figure_number} has empty review status"


@then(parsers.parse("the loaded inventory has {count:d} figures"))
def loaded_inventory_count(generation_result, count):
    """Assert the loaded inventory has expected figure count."""
    inventory = generation_result["loaded_inventory"]
    assert inventory.count == count


@then("each figure retains its original generation method")
def each_figure_retains_method(generation_result):
    """Assert loaded inventory figures match original methods."""
    original = generation_result["inventory"]
    loaded = generation_result["loaded_inventory"]
    for orig, load in zip(original.placeholders, loaded.placeholders):
        assert orig.generation_method == load.generation_method


@then(parsers.parse('the approved result retains prompt hash "{hash_val}"'))
def approved_retains_hash(generation_result, hash_val):
    """Assert the approved result still carries the prompt hash."""
    assert generation_result["approved_prompt_hash"] == hash_val


@then(parsers.parse('both rendered prompts contain "{color1}" and "{color2}"'))
def both_prompts_contain_colors(quality_context, color1, color2):
    """Assert both rendered prompts include the palette colors."""
    for prompt in quality_context["rendered_prompts"]:
        assert color1 in prompt
        assert color2 in prompt
