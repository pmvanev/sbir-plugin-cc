"""Unit tests for assembly through AssemblyService driving port.

Test Budget: 4 behaviors x 2 = 8 unit tests max.
Current count: 8 tests (within budget).

Tests verify through driving port (AssemblyService):
1. Final compliance check reports covered/waived/missing counts
2. Missing compliance items block progression with guidance
3. Volumes assembled into required structure (3 volumes)
4. Human checkpoint presented for assembled package review
"""

from __future__ import annotations

from pes.domain.assembly_service import AssemblyService
from pes.domain.compliance import (
    ComplianceItem,
    ComplianceMatrix,
    CoverageStatus,
    RequirementType,
)
from pes.ports.document_assembly_port import AssembledVolume, DocumentAssembler

# --- Fake driven port for document assembly ---


class FakeDocumentAssembler(DocumentAssembler):
    """Fake driven port: returns pre-configured volumes."""

    def __init__(self, volumes: list[AssembledVolume] | None = None) -> None:
        self._volumes = volumes or [
            AssembledVolume(volume_number=1, title="Technical", content="tech", page_count=19),
            AssembledVolume(volume_number=2, title="Cost", content="cost", page_count=5),
            AssembledVolume(volume_number=3, title="Company Info", content="info", page_count=3),
        ]

    def assemble_volumes(
        self, *, sections: list[str], format_template_agency: str
    ) -> list[AssembledVolume]:
        return self._volumes


# --- Helpers ---


def _make_matrix(
    covered: int = 0, waived: int = 0, missing: int = 0
) -> ComplianceMatrix:
    """Build a compliance matrix with given status counts."""
    items: list[ComplianceItem] = []
    item_id = 1
    for _ in range(covered):
        items.append(ComplianceItem(
            item_id=item_id, text=f"Req {item_id}",
            requirement_type=RequirementType.SHALL,
            status=CoverageStatus.COVERED,
        ))
        item_id += 1
    for _ in range(waived):
        items.append(ComplianceItem(
            item_id=item_id, text=f"Req {item_id}",
            requirement_type=RequirementType.SHALL,
            status=CoverageStatus.WAIVED,
        ))
        item_id += 1
    for _ in range(missing):
        items.append(ComplianceItem(
            item_id=item_id, text=f"Req {item_id}",
            requirement_type=RequirementType.SHALL,
            status=CoverageStatus.NOT_STARTED,
        ))
        item_id += 1
    return ComplianceMatrix(items=items)


# ---------------------------------------------------------------------------
# Behavior 1: Final compliance check reports covered/waived/missing counts
# ---------------------------------------------------------------------------


class TestFinalComplianceCheckReporting:
    def test_reports_covered_waived_missing_counts(self):
        service = AssemblyService()
        matrix = _make_matrix(covered=45, waived=2, missing=0)

        result = service.run_final_compliance_check(matrix=matrix)

        assert result.covered == 45
        assert result.waived == 2
        assert result.missing == 0
        assert result.total == 47

    def test_formats_summary_with_counts(self):
        service = AssemblyService()
        matrix = _make_matrix(covered=45, waived=2, missing=0)

        result = service.run_final_compliance_check(matrix=matrix)

        assert "45/47 covered" in result.summary
        assert "2 waived" in result.summary
        assert "0 missing" in result.summary

    def test_marks_artifact_written(self):
        service = AssemblyService()
        matrix = _make_matrix(covered=45, waived=2, missing=0)

        result = service.run_final_compliance_check(matrix=matrix)

        assert result.artifact_written is True


# ---------------------------------------------------------------------------
# Behavior 2: Missing compliance items block progression with guidance
# ---------------------------------------------------------------------------


class TestMissingComplianceBlocking:
    def test_blocks_progression_when_items_missing(self):
        service = AssemblyService()
        matrix = _make_matrix(covered=46, waived=0, missing=1)

        result = service.run_final_compliance_check(matrix=matrix)

        assert result.blocks_progression is True
        assert result.missing == 1

    def test_provides_guidance_for_missing_items(self):
        service = AssemblyService()
        matrix = _make_matrix(covered=46, waived=0, missing=1)

        result = service.run_final_compliance_check(matrix=matrix)

        guidance_lower = result.guidance.lower()
        assert "content" in guidance_lower or "waive" in guidance_lower


# ---------------------------------------------------------------------------
# Behavior 3: Volumes assembled into required structure
# ---------------------------------------------------------------------------


class TestVolumeAssembly:
    def test_assembles_three_volumes_with_correct_titles(self):
        assembler = FakeDocumentAssembler()
        service = AssemblyService(document_assembler=assembler)

        result = service.assemble_volumes(
            sections=["technical", "cost", "company-info"],
            format_template_agency="dod",
        )

        assert len(result.volumes) == 3
        titles = [v.title for v in result.volumes]
        assert "Technical" in titles
        assert "Cost" in titles
        assert "Company Info" in titles

    def test_marks_assembly_artifact_written(self):
        assembler = FakeDocumentAssembler()
        service = AssemblyService(document_assembler=assembler)

        result = service.assemble_volumes(
            sections=["technical", "cost", "company-info"],
            format_template_agency="dod",
        )

        assert result.artifact_written is True


# ---------------------------------------------------------------------------
# Behavior 4: Human checkpoint presented for assembled package review
# ---------------------------------------------------------------------------


class TestHumanCheckpoint:
    def test_presents_checkpoint_for_assembly_review(self):
        assembler = FakeDocumentAssembler()
        service = AssemblyService(document_assembler=assembler)

        result = service.assemble_volumes(
            sections=["technical", "cost", "company-info"],
            format_template_agency="dod",
        )

        assert result.checkpoint_required is True
        assert result.checkpoint_type == "assembled_package_review"
