"""Root conftest -- session-scoped fixtures shared across all test tiers."""

from __future__ import annotations

import pytest


@pytest.fixture(scope="session")
def project_root(tmp_path_factory: pytest.TempPathFactory):
    """Temporary project root directory simulating a user's proposal workspace."""
    return tmp_path_factory.mktemp("proposal_project")
