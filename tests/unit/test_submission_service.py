"""Unit tests for SubmissionService (driving port) -- submission packaging with portal rules.

Test Budget: 4 behaviors x 2 = 8 unit tests max.
Tests enter through driving port (SubmissionService).
Driven port (PortalRulesLoader) faked at port boundary.
Domain objects (PackageFile, PortalRules, PackageResult) are real collaborators.

Behaviors:
1. Portal identified from agency in proposal state
2. Portal-specific file naming applied to all package files
3. File sizes verified against portal limits
4. Missing required files block submission with actionable guidance
"""

from __future__ import annotations

import pytest

from pes.domain.submission import PackageFile, PortalRules
from pes.domain.submission_service import SubmissionService, UnknownAgencyError
from pes.ports.portal_rules_port import PortalRulesLoader

# ---------------------------------------------------------------------------
# Fake driven port (PortalRulesLoader) at port boundary
# ---------------------------------------------------------------------------


class FakePortalRulesLoader(PortalRulesLoader):
    """Fake driven port that returns deterministic portal rules."""

    def __init__(self) -> None:
        self._portals: dict[str, PortalRules] = {}
        self._agency_map: dict[str, str] = {}

    def add_portal(self, rules: PortalRules) -> None:
        self._portals[rules.portal_id] = rules
        for pattern in rules.agency_patterns:
            self._agency_map[pattern] = rules.portal_id

    def load_rules_for_portal(self, portal_id: str) -> PortalRules | None:
        return self._portals.get(portal_id)

    def identify_portal(self, agency: str) -> str | None:
        return self._agency_map.get(agency)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_DSIP_RULES = PortalRules(
    portal_id="DSIP",
    agency_patterns=["Air Force", "Army", "Navy"],
    naming_convention="{category}_{proposal_id}.pdf",
    max_file_size_mb=50.0,
    required_files=["technical_volume", "cost_volume", "firm_certification"],
    guidance={
        "firm_certification": (
            "Download Firm Certification from DSIP portal "
            "(https://www.dodsbirsttr.mil) under 'Forms & Templates'."
        ),
    },
)


def _make_loader(*, rules: PortalRules | None = None) -> FakePortalRulesLoader:
    loader = FakePortalRulesLoader()
    if rules is None:
        rules = _DSIP_RULES
    loader.add_portal(rules)
    return loader


def _make_service(loader: FakePortalRulesLoader | None = None) -> SubmissionService:
    if loader is None:
        loader = _make_loader()
    return SubmissionService(portal_rules_loader=loader)


def _make_files(*, include_all: bool = True) -> list[PackageFile]:
    """Build package files with all required files present."""
    files = [
        PackageFile(
            original_name="Technical_Volume.pdf",
            category="technical_volume",
            size_bytes=2_000_000,
        ),
        PackageFile(
            original_name="Cost_Volume.pdf",
            category="cost_volume",
            size_bytes=500_000,
        ),
    ]
    if include_all:
        files.append(
            PackageFile(
                original_name="Firm_Cert.pdf",
                category="firm_certification",
                size_bytes=100_000,
            ),
        )
    return files


# ---------------------------------------------------------------------------
# Behavior 1: Portal identified from agency in proposal state
# ---------------------------------------------------------------------------


class TestPortalIdentification:
    def test_identifies_dsip_for_air_force(self):
        service = _make_service()
        files = _make_files()

        result = service.prepare_package(agency="Air Force", files=files)

        assert result.portal_id == "DSIP"

    def test_raises_error_for_unknown_agency(self):
        service = _make_service()
        files = _make_files()

        with pytest.raises(UnknownAgencyError) as exc_info:
            service.prepare_package(agency="Unknown Agency", files=files)

        assert "unknown agency" in str(exc_info.value).lower()


# ---------------------------------------------------------------------------
# Behavior 2: Portal-specific file naming applied to all package files
# ---------------------------------------------------------------------------


class TestFileNaming:
    def test_applies_portal_naming_to_all_files(self):
        service = _make_service()
        files = _make_files()

        result = service.prepare_package(agency="Air Force", files=files)

        for pf in result.packaged_files:
            assert pf.portal_name is not None
            assert len(pf.portal_name) > 0
            # DSIP naming convention uses category
            assert pf.category in pf.portal_name

    def test_portal_name_includes_pdf_extension(self):
        service = _make_service()
        files = _make_files()

        result = service.prepare_package(agency="Air Force", files=files)

        for pf in result.packaged_files:
            assert pf.portal_name.endswith(".pdf")


# ---------------------------------------------------------------------------
# Behavior 3: File sizes verified against portal limits
# ---------------------------------------------------------------------------


class TestFileSizeVerification:
    @pytest.mark.parametrize(
        "size_bytes,max_mb,expect_pass",
        [
            (2_000_000, 50.0, True),       # 2 MB < 50 MB
            (60_000_000, 50.0, False),     # 60 MB > 50 MB
            (52_428_800, 50.0, False),     # exactly 50 MB = 50*1024*1024, over
        ],
    )
    def test_size_check_result(self, size_bytes, max_mb, expect_pass):
        rules = PortalRules(
            portal_id="DSIP",
            agency_patterns=["Air Force"],
            naming_convention="{category}_{proposal_id}.pdf",
            max_file_size_mb=max_mb,
            required_files=["technical_volume"],
            guidance={},
        )
        loader = _make_loader(rules=rules)
        service = _make_service(loader)
        files = [
            PackageFile(
                original_name="Technical_Volume.pdf",
                category="technical_volume",
                size_bytes=size_bytes,
            ),
        ]

        result = service.prepare_package(agency="Air Force", files=files)

        assert result.size_checks_passed is expect_pass


# ---------------------------------------------------------------------------
# Behavior 4: Missing required files block submission with actionable guidance
# ---------------------------------------------------------------------------


class TestMissingFilesBlocking:
    def test_missing_file_blocks_submission(self):
        service = _make_service()
        # Exclude firm_certification
        files = _make_files(include_all=False)

        result = service.prepare_package(agency="Air Force", files=files)

        assert result.blocked is True
        assert "firm_certification" in result.missing_files

    def test_missing_file_includes_guidance(self):
        service = _make_service()
        files = _make_files(include_all=False)

        result = service.prepare_package(agency="Air Force", files=files)

        assert len(result.guidance) > 0
        assert any("dsip" in g.lower() or "firm certification" in g.lower()
                    for g in result.guidance)
