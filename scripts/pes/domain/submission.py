"""Submission domain model -- portal rules, package files, and packaging results."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PortalRules:
    """Portal-specific submission rules loaded from configuration."""

    portal_id: str
    agency_patterns: list[str]
    naming_convention: str
    max_file_size_mb: float
    required_files: list[str]
    guidance: dict[str, str] = field(default_factory=dict)


@dataclass
class PackageFile:
    """A file to be included in the submission package."""

    original_name: str
    category: str
    size_bytes: int
    portal_name: str | None = None


@dataclass
class PackageResult:
    """Result of preparing a submission package."""

    portal_id: str
    packaged_files: list[PackageFile] = field(default_factory=list)
    size_checks_passed: bool = True
    size_violations: list[str] = field(default_factory=list)
    blocked: bool = False
    missing_files: list[str] = field(default_factory=list)
    guidance: list[str] = field(default_factory=list)
