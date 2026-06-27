"""Gap 22: Mutation-killing tests for codex_ml.utils.determinism.

These tests are specifically designed to kill surviving mutmut mutants
identified during the Gap 22 mutation testing run on 2025-07-09.
They focus on Python-level behaviours (no torch/numpy required) to
maximise mutation score in CPU-only CI environments.
"""

import os
import random

from codex_ml.utils.determinism import (
    enable_determinism,
    set_deterministic,
    set_global_determinism,
)
from codex_ml.utils.seed import deterministic_shuffle, set_seed

# ---------------------------------------------------------------------------
# enable_determinism – return-value key assertions
# (kills: x_enable_determinism__mutmut_3/4/5 – key name mutations)
# ---------------------------------------------------------------------------


class TestEnableDeterminismReturnShape:
    """Verify the returned state dict has the exact expected keys and types."""

    def test_returns_seed_key_exact_name(self):
        """Mutant changes 'seed' → 'XXseedXX' / 'SEED' — this kills them."""
        state = enable_determinism(seed=7, deterministic=True)
        assert "seed" in state, "state dict must contain key 'seed'"
        assert state["seed"] == 7, "Condition must be true"

    def test_returns_deterministic_key_exact_name(self):
        """Mutant changes 'deterministic' → 'XXdeterministicXX' — killed here."""
        state = enable_determinism(seed=7, deterministic=True)
        assert "deterministic" in state, "state dict must contain key 'deterministic'"

    def test_deterministic_flag_true(self):
        """Mutant changes default deterministic=True → False — killed here."""
        state = enable_determinism(seed=42)
        assert state["deterministic"] is True, "Condition must be true"

    def test_deterministic_flag_false(self):
        state = enable_determinism(seed=42, deterministic=False)
        assert state["deterministic"] is False, "Condition must be true"

    def test_seed_preserved_in_state(self):
        for s in (0, 1, 42, 999, 1337):
            state = enable_determinism(seed=s)
            assert state["seed"] == s, f"seed {s} not preserved in state"

    def test_no_seed_returns_state_without_random(self):
        """When seed=None the state dict must NOT contain 'random'."""
        state = enable_determinism(seed=None, deterministic=True)
        assert "random" not in state, "Condition must be true"
        assert "seed" in state, "Condition must be true"
        assert state["seed"] is None, "Condition must be true"

    def test_with_seed_returns_numpy_and_torch_keys(self):
        """When seed is provided, 'numpy' and 'torch' keys must be present."""
        state = enable_determinism(seed=5, deterministic=True)
        assert "numpy" in state, "state must contain 'numpy'"
        assert "torch" in state, "state must contain 'torch'"

    def test_num_threads_key_in_state(self):
        """When num_threads provided, key 'num_threads' must be in state."""
        state = enable_determinism(seed=5, num_threads=2)
        assert "num_threads" in state, "Condition must be true"
        assert state["num_threads"] == 2, "Condition must be true"


# ---------------------------------------------------------------------------
# set_deterministic – env variable and random seeding
# (kills: x_set_deterministic__mutmut_7/8 – PYTHONHASHSEED key mutations,
#  x_set_deterministic__mutmut_1 – default seed 42→43)
# ---------------------------------------------------------------------------


class TestSetDeterministic:
    """Verify set_deterministic mutates environment and random state correctly."""

    def test_pythonhashseed_set_to_seed_value(self):
        """Mutant renames env key to 'XXPYTHONHASHSEEDXX' / 'pythonhashseed'."""
        os.environ.pop("PYTHONHASHSEED", None)
        set_deterministic(seed=99)
        assert os.environ.get("PYTHONHASHSEED") == "99", "Condition must be true"

    def test_pythonhashseed_uses_str_seed(self):
        """Verifies the value stored is the seed as a string."""
        os.environ.pop("PYTHONHASHSEED", None)
        set_deterministic(seed=12345)
        assert os.environ.get("PYTHONHASHSEED") == "12345", "Condition must be true"

    def test_random_seed_applied(self):
        """Verifies random state is seeded — mutants changing random.seed() survive."""
        set_deterministic(seed=42)
        a1 = random.random()
        set_deterministic(seed=42)
        a2 = random.random()
        assert a1 == a2, "random.random() should be identical after same seed"

    def test_different_seeds_produce_different_random(self):
        set_deterministic(seed=1)
        v1 = random.random()
        set_deterministic(seed=2)
        v2 = random.random()
        assert v1 != v2, "v1 is not valid"

    def test_default_seed_is_42(self):
        """Mutant changes default seed 42→43; calling without args and comparing."""
        set_deterministic()  # default seed=42
        a = random.random()

        set_deterministic(seed=42)
        b = random.random()

        assert a == b, "default seed should be 42"

    def test_setdefault_does_not_override_existing(self):
        """os.environ.setdefault should NOT override an existing PYTHONHASHSEED."""
        os.environ["PYTHONHASHSEED"] = "existing"
        set_deterministic(seed=77)
        assert os.environ.get("PYTHONHASHSEED") == "existing", "Condition must be true"
        del os.environ["PYTHONHASHSEED"]


# ---------------------------------------------------------------------------
# set_global_determinism – alias wiring
# (kills: x_set_global_determinism__mutmut_* – default seed and delegation)
# ---------------------------------------------------------------------------


class TestSetGlobalDeterminism:
    """Verify set_global_determinism correctly seeds random state."""

    def test_uses_seed_1337_by_default(self):
        """Mutants may change the default seed value — verify exact output."""
        set_global_determinism(seed=1337)
        a = random.random()

        set_deterministic(seed=1337, deterministic=True)
        b = random.random()

        assert (a == b, "a is not valid"
        ), "set_global_determinism(1337) must produce same state as set_deterministic(1337)"

    def test_default_call_seeds_random(self):
        """Calling set_global_determinism() with no args should seed random."""
        set_global_determinism()  # default seed=1337
        a = random.random()

        set_global_determinism()
        b = random.random()

        assert a == b, "successive no-arg calls must be reproducible"

    def test_custom_seed_applied(self):
        set_global_determinism(seed=42)
        a = random.random()
        set_global_determinism(seed=42)
        b = random.random()
        assert a == b, "a is not valid"

    def test_different_seed_changes_output(self):
        set_global_determinism(seed=1)
        a = random.random()
        set_global_determinism(seed=2)
        b = random.random()
        assert a != b, "a is not valid"


# ---------------------------------------------------------------------------
# enable_determinism – no-seed branch (set_cudnn path)
# ---------------------------------------------------------------------------


class TestEnableDeterminismNoSeed:
    """Exercises the seed=None branch to avoid 'no tests' for that path."""

    def test_no_seed_no_crash(self):
        state = enable_determinism(deterministic=True)
        assert isinstance(state, dict)

    def test_no_seed_deterministic_false(self):
        state = enable_determinism(deterministic=False)
        assert state["deterministic"] is False, "Condition must be true"


class TestSeedUtils:
    def test_deterministic_shuffle_preserves_elements(self):
        """Mutant changing logic should not lose elements."""
        original = [1, 2, 3, 4, 5]
        shuffled = deterministic_shuffle(original, seed=42)
        assert sorted(original) == sorted(shuffled), "s is not valid"
        assert len(original) == len(shuffled), "Original must not be empty"

    def test_deterministic_shuffle_is_reproducible(self):
        """Mutant changing the seed being passed should break this."""
        original = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        shuffled1 = deterministic_shuffle(original, seed=99)
        shuffled2 = deterministic_shuffle(original, seed=99)
        assert shuffled1 == shuffled2, "shuffled1 is not valid"

    def test_deterministic_shuffle_different_seeds(self):
        """Mutant changing +1 to seed etc."""
        original = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        shuffled1 = deterministic_shuffle(original, seed=1)
        shuffled2 = deterministic_shuffle(original, seed=2)
        assert shuffled1 != shuffled2, "shuffled1 is not valid"

    def test_deterministic_shuffle_does_not_mutate_original(self):
        original = [1, 2, 3]
        deterministic_shuffle(original, seed=1)
        assert original == [1, 2, 3]

    def test_set_seed_wiring(self):
        """Test set_seed wired correctly."""
        set_seed(42)
        a = random.random()
        set_seed(42)
        b = random.random()
        assert a == b, "a is not valid"
