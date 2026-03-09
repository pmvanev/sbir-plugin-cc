"""Unit tests for compliance check through ComplianceCheckService (driving port).

Test Budget: 4 behaviors x 2 = 8 unit tests max.
Tests enter through driving port (ComplianceCheckService).
Domain objects (ComplianceItem, ComplianceMatrix) are real collaborators.
"""

from __future__ import annotations

from pes.domain.compliance import (
    ComplianceItem,
    ComplianceMatrix,
    CoverageStatus,
    RequirementType,
)
from pes.domain.compliance_check_service import ComplianceCheckService

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _item(item_id: int, status: CoverageStatus) -> ComplianceItem:
    """Create a compliance item with the given status."""
    return ComplianceItem(
        item_id=item_id,
        text=f"Requirement {item_id}",
        requirement_type=RequirementType.SHALL,
        status=status,
    )


def _matrix_with_statuses(
    covered: int = 0,
    partial: int = 0,
    missing: int = 0,
    waived: int = 0,
) -> ComplianceMatrix:
    """Build a matrix with the specified status counts."""
    items: list[ComplianceItem] = []
    item_id = 1
    for _ in range(covered):
        items.append(_item(item_id, CoverageStatus.COVERED))
        item_id += 1
    for _ in range(partial):
        items.append(_item(item_id, CoverageStatus.PARTIAL))
        item_id += 1
    for _ in range(missing):
        items.append(_item(item_id, CoverageStatus.NOT_STARTED))
        item_id += 1
    for _ in range(waived):
        items.append(_item(item_id, CoverageStatus.WAIVED))
        item_id += 1
    return ComplianceMatrix(items=items)


# ---------------------------------------------------------------------------
# Behavior 1: Reports full coverage breakdown by status
# ---------------------------------------------------------------------------


class TestCoverageBreakdown:
    def test_reports_all_status_categories(self):
        matrix = _matrix_with_statuses(covered=32, partial=5, missing=8, waived=2)
        service = ComplianceCheckService()

        result = service.check(matrix)

        assert result.total == 47
        assert result.covered == 32
        assert result.partial == 5
        assert result.missing == 8
        assert result.waived == 2

    def test_formats_summary_line(self):
        matrix = _matrix_with_statuses(covered=32, partial=5, missing=8, waived=2)
        service = ComplianceCheckService()

        result = service.check(matrix)

        assert result.summary == "47 items | 32 covered | 5 partial | 8 missing | 2 waived"


# ---------------------------------------------------------------------------
# Behavior 2: Fresh matrix shows all not-started with zero waived
# ---------------------------------------------------------------------------


class TestFreshMatrix:
    def test_fresh_matrix_all_not_started(self):
        matrix = _matrix_with_statuses(missing=47)
        service = ComplianceCheckService()

        result = service.check(matrix)

        assert result.summary == "47 items | 0 covered | 0 partial | 47 not started | 0 waived"

    def test_waived_distinct_from_missing_in_count(self):
        matrix = _matrix_with_statuses(missing=10, waived=3)
        service = ComplianceCheckService()

        result = service.check(matrix)

        assert result.waived == 3
        assert result.missing == 10
        assert "3 waived" in result.summary
        assert "10" in result.summary


# ---------------------------------------------------------------------------
# Behavior 3: Missing matrix returns error with guidance
# ---------------------------------------------------------------------------


class TestMissingMatrix:
    def test_returns_not_found_message(self):
        service = ComplianceCheckService()

        result = service.check(None)

        assert result.summary == "No compliance matrix found"

    def test_includes_strategy_wave_guidance(self):
        service = ComplianceCheckService()

        result = service.check(None)

        assert "strategy" in result.guidance.lower()


# ---------------------------------------------------------------------------
# Behavior 4: Malformed matrix returns parse error with guidance
# ---------------------------------------------------------------------------


class TestMalformedMatrix:
    def test_returns_parse_error_for_invalid_matrix(self):
        service = ComplianceCheckService()

        result = service.check_raw("This is not a valid compliance matrix format.")

        assert result.summary == "Could not parse compliance matrix"

    def test_includes_format_verification_guidance(self):
        service = ComplianceCheckService()

        result = service.check_raw("This is not a valid compliance matrix format.")

        assert "format" in result.guidance.lower()
