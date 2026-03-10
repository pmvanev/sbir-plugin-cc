"""Assembly domain model -- compliance final check and volume assembly result types."""

from __future__ import annotations

from dataclasses import dataclass, field

from pes.ports.document_assembly_port import AssembledVolume


@dataclass
class FinalComplianceResult:
    """Result of a final compliance check before assembly."""

    total: int = 0
    covered: int = 0
    waived: int = 0
    missing: int = 0
    summary: str = ""
    guidance: str = ""
    blocks_progression: bool = False
    artifact_written: bool = False


@dataclass
class AssemblyResult:
    """Result of assembling proposal volumes."""

    volumes: list[AssembledVolume] = field(default_factory=list)
    artifact_written: bool = False
    checkpoint_required: bool = False
    checkpoint_type: str = ""
