"""Visual asset domain models -- value objects for figure generation.

Pure domain objects with no infrastructure imports.
FigurePlaceholder captures a figure slot from the outline.
FigureInventory aggregates all placeholders for a proposal.
GeneratedFigure tracks a produced figure artifact.
CrossReferenceLog validates figure-to-text consistency.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FigurePlaceholder:
    """A figure slot extracted from the proposal outline.

    Frozen value object -- immutable after creation.
    """

    figure_number: int
    section_id: str
    description: str
    figure_type: str
    generation_method: str


@dataclass
class FigureInventory:
    """Collection of figure placeholders for a proposal."""

    placeholders: list[FigurePlaceholder] = field(default_factory=list)

    @property
    def count(self) -> int:
        """Number of figure placeholders in the inventory."""
        return len(self.placeholders)


@dataclass(frozen=True)
class GeneratedFigure:
    """A figure that has been produced from a placeholder.

    Frozen value object -- immutable after creation.
    """

    figure_number: int
    section_id: str
    file_path: str
    format: str


@dataclass(frozen=True)
class CrossReferenceEntry:
    """A single cross-reference between text and a figure.

    Frozen value object -- immutable after creation.
    """

    section_id: str
    referenced_figure: int
    exists: bool


@dataclass(frozen=True)
class ExternalBrief:
    """Brief for a figure that cannot be auto-generated.

    Frozen value object -- immutable after creation.
    Provides content description, dimensions, and resolution guidance
    for manual figure creation.
    """

    figure_number: int
    section_id: str
    content_description: str
    dimensions: str
    resolution: str


@dataclass
class CrossReferenceLog:
    """Validates figure-to-text reference consistency."""

    entries: list[CrossReferenceEntry] = field(default_factory=list)

    @property
    def orphaned_references(self) -> list[CrossReferenceEntry]:
        """References to figures that do not exist."""
        return [e for e in self.entries if not e.exists]

    @property
    def all_valid(self) -> bool:
        """True when all references resolve to existing figures."""
        return len(self.orphaned_references) == 0
