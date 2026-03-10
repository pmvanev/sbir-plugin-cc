"""Port interface for visual asset persistence.

Driven port: VisualAssetPort
Adapters implement this to read/write figure inventories and cross-reference logs.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from pes.domain.visual_asset import CrossReferenceLog, FigureInventory


class VisualAssetPort(ABC):
    """Read and write visual asset artifacts -- driven port."""

    @abstractmethod
    def write_inventory(self, inventory: FigureInventory) -> None:
        """Persist figure inventory to storage."""

    @abstractmethod
    def read_inventory(self) -> FigureInventory:
        """Load figure inventory from storage."""

    @abstractmethod
    def write_cross_reference_log(self, log: CrossReferenceLog) -> None:
        """Persist cross-reference validation log."""

    @abstractmethod
    def read_cross_reference_log(self) -> CrossReferenceLog:
        """Load cross-reference validation log from storage."""
