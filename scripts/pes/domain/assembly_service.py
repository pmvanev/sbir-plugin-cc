"""Assembly service -- driving port for volume assembly and final compliance check.

Orchestrates: final compliance matrix validation, volume assembly via
DocumentAssembler driven port, and human checkpoint presentation.
"""

from __future__ import annotations

from pes.domain.assembly import AssemblyResult, FinalComplianceResult
from pes.domain.compliance import ComplianceMatrix, CoverageStatus
from pes.ports.document_assembly_port import DocumentAssembler


class AssemblyService:
    """Driving port: assembles volumes and runs final compliance checks.

    Delegates volume assembly to DocumentAssembler driven port.
    Compliance checks operate on the in-memory ComplianceMatrix.
    """

    def __init__(
        self,
        document_assembler: DocumentAssembler | None = None,
    ) -> None:
        self._assembler = document_assembler

    def run_final_compliance_check(
        self, *, matrix: ComplianceMatrix
    ) -> FinalComplianceResult:
        """Run final compliance check on the matrix before assembly.

        Reports covered/waived/missing counts. Missing items block progression
        with guidance to provide content or request a waiver.
        """
        covered = sum(1 for i in matrix.items if i.status == CoverageStatus.COVERED)
        waived = sum(1 for i in matrix.items if i.status == CoverageStatus.WAIVED)
        missing = sum(1 for i in matrix.items if i.status == CoverageStatus.NOT_STARTED)
        total = matrix.item_count

        summary = (
            f"{covered}/{total} covered | {waived} waived (with reasons) | {missing} missing"
        )

        blocks = missing > 0
        guidance = ""
        if blocks:
            guidance = (
                "Provide content for missing compliance items or waive them "
                "with documented justification before proceeding."
            )

        return FinalComplianceResult(
            total=total,
            covered=covered,
            waived=waived,
            missing=missing,
            summary=summary,
            guidance=guidance,
            blocks_progression=blocks,
            artifact_written=True,
        )

    def assemble_volumes(
        self,
        *,
        sections: list[str],
        format_template_agency: str,
    ) -> AssemblyResult:
        """Assemble sections into proposal volumes.

        Delegates to DocumentAssembler driven port. Returns assembled volumes
        with a human checkpoint for review.
        """
        if self._assembler is None:
            msg = "DocumentAssembler required for volume assembly"
            raise RuntimeError(msg)

        volumes = self._assembler.assemble_volumes(
            sections=sections,
            format_template_agency=format_template_agency,
        )

        return AssemblyResult(
            volumes=volumes,
            artifact_written=True,
            checkpoint_required=True,
            checkpoint_type="assembled_package_review",
        )
