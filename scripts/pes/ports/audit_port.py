"""Port interface for audit logging.

Driven port: AuditLogger
Adapters implement this to persist audit entries (file, database, etc.).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AuditLogger(ABC):
    """Record enforcement decisions -- driven port."""

    @abstractmethod
    def log(self, entry: dict[str, Any]) -> None:
        """Write an audit entry with timestamp and decision details."""
