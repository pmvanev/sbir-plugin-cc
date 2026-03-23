"""Unit tests for rigor profile domain objects.

Test Budget: 8 behaviors x 2 = 16 max unit tests.
Actual: 8 tests (7 methods, 1 parametrized with 4 cases).
"""

import pytest

from pes.domain.rigor import (
    DEFAULT_PROFILE_NAME,
    DiffComputer,
    InvalidProfileError,
    ProfileValidator,
    RigorProfile,
    VALID_PROFILE_NAMES,
)


# ---------------------------------------------------------------------------
# RigorProfile value object
# ---------------------------------------------------------------------------

class TestRigorProfile:
    """RigorProfile is a frozen (immutable) value object."""

    def test_creates_frozen_value_object_with_all_fields(self):
        profile = RigorProfile(
            profile_name="standard",
            agent_roles={"writer": "standard", "reviewer": "basic"},
            review_passes=1,
            critique_max_iterations=2,
            iteration_cap=2,
        )
        assert profile.profile_name == "standard"
        assert profile.agent_roles == {"writer": "standard", "reviewer": "basic"}
        assert profile.review_passes == 1
        assert profile.critique_max_iterations == 2
        assert profile.iteration_cap == 2

    def test_frozen_dataclass_rejects_attribute_mutation(self):
        profile = RigorProfile(
            profile_name="lean",
            agent_roles={"writer": "basic"},
            review_passes=0,
            critique_max_iterations=0,
            iteration_cap=1,
        )
        with pytest.raises(AttributeError):
            profile.profile_name = "standard"


# ---------------------------------------------------------------------------
# ProfileValidator
# ---------------------------------------------------------------------------

class TestProfileValidator:
    """Validates profile names against the known set."""

    @pytest.mark.parametrize("name", ["lean", "standard", "thorough", "exhaustive"])
    def test_accepts_valid_profile_names(self, name):
        validator = ProfileValidator()
        # Should not raise
        validator.validate(name)

    def test_rejects_invalid_profile_name_with_valid_list(self):
        validator = ProfileValidator()
        with pytest.raises(InvalidProfileError) as exc_info:
            validator.validate("ultra")
        error = exc_info.value
        assert "ultra" in str(error)
        assert all(p in str(error) for p in VALID_PROFILE_NAMES)

    def test_rejects_empty_profile_name(self):
        validator = ProfileValidator()
        with pytest.raises(InvalidProfileError):
            validator.validate("")

    def test_default_profile_is_standard(self):
        assert DEFAULT_PROFILE_NAME == "standard"


# ---------------------------------------------------------------------------
# DiffComputer
# ---------------------------------------------------------------------------

class TestDiffComputer:
    """Computes differences between two RigorProfile instances."""

    def _make_profile(self, name, roles, review=1, critique=2, iteration=2):
        return RigorProfile(
            profile_name=name,
            agent_roles=roles,
            review_passes=review,
            critique_max_iterations=critique,
            iteration_cap=iteration,
        )

    def test_computes_role_tier_changes(self):
        old = self._make_profile("standard", {"writer": "standard", "reviewer": "basic"})
        new = self._make_profile("thorough", {"writer": "strongest", "reviewer": "basic"})
        diff = DiffComputer.compute(old, new)
        assert ("writer", "standard", "strongest") in diff.role_changes
        assert len(diff.role_changes) == 1  # reviewer unchanged

    def test_computes_behavioral_parameter_changes(self):
        old = self._make_profile("standard", {}, review=1, critique=2, iteration=2)
        new = self._make_profile("thorough", {}, review=2, critique=3, iteration=2)
        diff = DiffComputer.compute(old, new)
        assert ("review_passes", 1, 2) in diff.param_changes
        assert ("critique_max_iterations", 2, 3) in diff.param_changes
        # iteration_cap unchanged
        assert not any(c[0] == "iteration_cap" for c in diff.param_changes)

    def test_same_profile_produces_empty_diff(self):
        profile = self._make_profile("standard", {"writer": "standard"}, 1, 2, 2)
        diff = DiffComputer.compute(profile, profile)
        assert diff.role_changes == []
        assert diff.param_changes == []
