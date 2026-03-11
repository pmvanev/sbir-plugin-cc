"""Fake portal rules loader for acceptance tests.

Provides in-memory DSIP portal rules without hitting the filesystem.
"""

from __future__ import annotations

from pes.domain.submission import PortalRules
from pes.ports.portal_rules_port import PortalRulesLoader

# Agency-to-portal mapping
_AGENCY_PORTAL_MAP: dict[str, str] = {
    "Air Force": "DSIP",
    "Army": "DSIP",
    "Navy": "DSIP",
    "DARPA": "DSIP",
    "NASA": "NSPIRES",
    "NSF": "Grants.gov",
    "DOE": "Grants.gov",
}

_DSIP_RULES = PortalRules(
    portal_id="DSIP",
    agency_patterns=["Air Force", "Army", "Navy", "DARPA"],
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


class FakePortalRulesLoader(PortalRulesLoader):
    """In-memory portal rules for acceptance testing."""

    def load_rules_for_portal(self, portal_id: str) -> PortalRules | None:
        if portal_id == "DSIP":
            return _DSIP_RULES
        return None

    def identify_portal(self, agency: str) -> str | None:
        return _AGENCY_PORTAL_MAP.get(agency)
