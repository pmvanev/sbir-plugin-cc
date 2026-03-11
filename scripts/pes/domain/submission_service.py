"""Submission service -- driving port for submission package preparation and confirmation.

Orchestrates: portal identification from agency, portal-specific file naming,
file size verification against portal limits, missing file detection,
human confirmation checkpoint, and immutable archive creation.
Delegates to PortalRulesLoader driven port for portal configuration
and ArchiveCreator driven port for archive operations.
"""

from __future__ import annotations

from datetime import UTC, datetime

from pes.domain.submission import (
    ConfirmationPrompt,
    PackageFile,
    PackageResult,
    SubmissionRecord,
)
from pes.ports.archive_port import ArchiveCreator
from pes.ports.portal_rules_port import PortalRulesLoader

# Bytes per megabyte for size comparison
_BYTES_PER_MB = 1_000_000


class UnknownAgencyError(Exception):
    """Raised when the agency does not map to any known submission portal."""


class SubmissionService:
    """Driving port: prepares submission packages with portal-specific rules.

    Delegates to PortalRulesLoader driven port for portal identification
    and rule loading, and ArchiveCreator driven port for archive operations.
    """

    def __init__(
        self,
        portal_rules_loader: PortalRulesLoader,
        archive_creator: ArchiveCreator,
    ) -> None:
        self._loader = portal_rules_loader
        self._archive_creator = archive_creator

    def prepare_package(
        self,
        *,
        agency: str,
        files: list[PackageFile],
    ) -> PackageResult:
        """Prepare a submission package applying portal-specific rules.

        Raises UnknownAgencyError if agency does not map to a portal.
        Returns PackageResult with portal ID, named files, size checks, and missing file info.
        """
        # 1. Identify portal from agency
        portal_id = self._loader.identify_portal(agency)
        if portal_id is None:
            raise UnknownAgencyError(
                f"Unknown agency '{agency}' -- no submission portal configured. "
                f"Check the agency name in the proposal topic."
            )

        # 2. Load portal rules
        rules = self._loader.load_rules_for_portal(portal_id)
        if rules is None:
            raise UnknownAgencyError(
                f"No portal rules found for portal '{portal_id}'. "
                f"Contact support to configure rules for this portal."
            )

        # 3. Apply portal-specific file naming
        for pf in files:
            pf.portal_name = rules.naming_convention.replace(
                "{category}", pf.category
            ).replace("{proposal_id}", "proposal")

        # 4. Verify file sizes against portal limits
        max_size_bytes = int(rules.max_file_size_mb * _BYTES_PER_MB)
        size_violations: list[str] = []
        for pf in files:
            if pf.size_bytes >= max_size_bytes:
                size_violations.append(
                    f"File '{pf.original_name}' ({pf.size_bytes / _BYTES_PER_MB:.1f} MB) "
                    f"exceeds portal limit of {rules.max_file_size_mb:.1f} MB"
                )

        size_checks_passed = len(size_violations) == 0

        # 5. Check for missing required files
        provided_categories = {pf.category for pf in files}
        missing_files: list[str] = []
        guidance_messages: list[str] = []

        for required in rules.required_files:
            if required not in provided_categories:
                missing_files.append(required)
                if required in rules.guidance:
                    guidance_messages.append(rules.guidance[required])

        blocked = len(missing_files) > 0

        return PackageResult(
            portal_id=portal_id,
            packaged_files=list(files),
            size_checks_passed=size_checks_passed,
            size_violations=size_violations,
            blocked=blocked,
            missing_files=missing_files,
            guidance=guidance_messages,
        )

    def confirm_submission(self) -> ConfirmationPrompt:
        """Present a confirmation prompt requiring explicit human approval.

        Returns ConfirmationPrompt with requires_confirmation=True.
        No state mutation occurs -- declining is always safe.
        """
        return ConfirmationPrompt(
            requires_confirmation=True,
            message=(
                "You are about to submit this proposal. "
                "This action is irreversible -- all artifacts will become read-only. "
                "Do you confirm?"
            ),
        )

    def record_submission(
        self,
        *,
        confirmation_number: str,
        package_dir: str,
        archive_dir: str,
    ) -> SubmissionRecord:
        """Record submission confirmation, create immutable archive.

        Raises ValueError if confirmation_number is empty.
        Copies all files from package_dir into archive_dir.
        Returns SubmissionRecord with immutable=True for PES enforcement.
        """
        if not confirmation_number.strip():
            raise ValueError(
                "A confirmation number is required to record the submission."
            )

        # Capture timestamp
        submitted_at = datetime.now(UTC).isoformat()

        # Create immutable archive by copying package files
        self._archive_creator.create_archive(package_dir, archive_dir)

        return SubmissionRecord(
            confirmation_number=confirmation_number,
            submitted_at=submitted_at,
            archive_path=archive_dir,
            immutable=True,
        )
