"""Unit tests for rigor profile and model tier configuration files."""
import json
from pathlib import Path

import pytest

CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"

EXPECTED_PROFILES = {"lean", "standard", "thorough", "exhaustive"}
EXPECTED_TIERS = {"basic", "standard", "strongest"}
EXPECTED_ROLES = {
    "writer", "reviewer", "researcher", "strategist",
    "formatter", "orchestrator", "compliance", "analyst",
}


@pytest.fixture
def rigor_profiles():
    with open(CONFIG_DIR / "rigor-profiles.json") as f:
        return json.load(f)


@pytest.fixture
def model_tiers():
    with open(CONFIG_DIR / "model-tiers.json") as f:
        return json.load(f)


class TestRigorProfiles:
    def test_defines_all_four_profiles_with_schema_version(self, rigor_profiles):
        assert "schema_version" in rigor_profiles
        assert set(rigor_profiles["profiles"].keys()) == EXPECTED_PROFILES

    def test_each_profile_assigns_tier_to_all_eight_roles(self, rigor_profiles):
        for profile_name, profile in rigor_profiles["profiles"].items():
            role_tiers = profile["roles"]
            assert set(role_tiers.keys()) == EXPECTED_ROLES, (
                f"Profile '{profile_name}' missing roles: "
                f"{EXPECTED_ROLES - set(role_tiers.keys())}"
            )
            for role, tier in role_tiers.items():
                assert tier in EXPECTED_TIERS or tier is None, (
                    f"Profile '{profile_name}' role '{role}' has invalid tier '{tier}'"
                )

    @pytest.mark.parametrize("profile_name,expected_review,expected_critique,expected_iter", [
        ("lean", 0, 0, 1),
        ("standard", 1, 2, 2),
        ("thorough", 2, 3, 2),
        ("exhaustive", 2, 3, 2),
    ])
    def test_behavioral_parameters(
        self, rigor_profiles, profile_name, expected_review, expected_critique, expected_iter
    ):
        profile = rigor_profiles["profiles"][profile_name]
        assert profile["review_passes"] == expected_review
        assert profile["critique_max_iterations"] == expected_critique
        assert profile["iteration_cap"] == expected_iter


class TestModelTiers:
    def test_defines_all_three_tiers_with_schema_version(self, model_tiers):
        assert "schema_version" in model_tiers
        assert set(model_tiers["tiers"].keys()) == EXPECTED_TIERS

    def test_each_tier_maps_to_concrete_model_id(self, model_tiers):
        expected_models = {
            "basic": "claude-haiku-4-5-20251001",
            "standard": "claude-sonnet-4-6-20250514",
            "strongest": "claude-opus-4-6-20250514",
        }
        for tier, expected_model in expected_models.items():
            assert model_tiers["tiers"][tier]["model_id"] == expected_model


class TestCrossFileConsistency:
    def test_all_profile_tiers_exist_in_model_tiers(self, rigor_profiles, model_tiers):
        valid_tiers = set(model_tiers["tiers"].keys())
        for profile_name, profile in rigor_profiles["profiles"].items():
            for role, tier in profile["roles"].items():
                if tier is not None:
                    assert tier in valid_tiers, (
                        f"Profile '{profile_name}' role '{role}' references "
                        f"unknown tier '{tier}'"
                    )
