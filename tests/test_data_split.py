"""
Tests for deterministic data splitting and reproducibility.

Ensures:
- Identical splits with same seed
- Correct proportions
- No data leakage between splits
- Complete coverage of all indices
"""

import importlib.util

import pytest

from codex_ml.data.splitting import split_indices

NUMPY_AVAILABLE = importlib.util.find_spec("numpy") is not None


class TestDeterministicSplits:
    """Tests for deterministic splitting."""

    def test_split_determinism(self):
        """Same seed should produce identical splits."""
        n = 1000
        seed = 42

        train1, val1, test1 = split_indices(n, 0.8, 0.1, seed=seed)
        train2, val2, test2 = split_indices(n, 0.8, 0.1, seed=seed)

        assert train1 == train2, "train1 is not valid"
        assert val1 == val2, "val1 is not valid"
        assert test1 == test2, "test1 is not valid"

        # Guard against trivial deterministic outputs.
        assert len(train1) > 0, "Train1 must not be empty"
        assert len(val1) > 0, "Val1 must not be empty"
        assert len(test1) > 0, "Test1 must not be empty"

        train_set = set(train1)
        val_set = set(val1)
        test_set = set(test1)

        assert len(train1) == len(train_set), "train indices must be unique"
        assert len(val1) == len(val_set), "validation indices must be unique"
        assert len(test1) == len(test_set), "test indices must be unique"
        assert len(train_set & val_set) == 0, "train and validation sets must not overlap"
        assert len(train_set & test_set) == 0, "train and test sets must not overlap"
        assert len(val_set & test_set) == 0, "validation and test sets must not overlap"
        assert len(train_set | val_set | test_set) == n, "all indices must be covered exactly once"

    def test_split_proportions(self):
        """Splits should match requested proportions."""
        n = 100
        train, val, test = split_indices(n, 0.6, 0.2, seed=0)

        assert len(train) == 60, "Train must not be empty"
        assert len(val) == 20, "Val must not be empty"
        assert len(test) == 20, "Test must not be empty"

    def test_no_overlap(self):
        """Splits should not overlap."""
        n = 500
        train, val, test = split_indices(n, 0.7, 0.15, seed=123)

        train_set = set(train)
        val_set = set(val)
        test_set = set(test)

        assert len(train_set & val_set) == 0, "Collection must not be empty"
        assert len(train_set & test_set) == 0, "Collection must not be empty"
        assert len(val_set & test_set) == 0, "Collection must not be empty"

    def test_complete_coverage(self):
        """All indices should be in exactly one split."""
        n = 200
        train, val, test = split_indices(n, 0.6, 0.2, seed=0)

        all_indices = set(train) | set(val) | set(test)
        assert all_indices == set(range(n)), "all_indices is not valid"

    def test_different_seeds_different_results(self):
        """Different seeds should produce different splits."""
        n = 100

        train1, _, _ = split_indices(n, 0.8, 0.1, seed=1)
        train2, _, _ = split_indices(n, 0.8, 0.1, seed=2)

        assert train1 != train2, "train1 is not valid"

    def test_various_split_ratios(self):
        """Test different split configurations."""
        test_cases = [
            (1000, 0.8, 0.1, 0.1),  # Standard 80/10/10
            (1000, 0.7, 0.2, 0.1),  # 70/20/10
            (1000, 0.6, 0.2, 0.2),  # 60/20/20
        ]

        for n, train_ratio, val_ratio, expected_test in test_cases:
            train, val, test = split_indices(n, train_ratio, val_ratio)

            # Check proportions (within 1 sample tolerance)
            assert abs(len(train) - n * train_ratio) <= 1, "Train must not be empty"
            assert abs(len(val) - n * val_ratio) <= 1, "Val must not be empty"

            # Check no overlap
            all_idx = set(train) | set(val) | set(test)
            assert len(all_idx) == n, "All_idx must not be empty"

    def test_small_dataset(self):
        """Test splitting on small datasets."""
        n = 10
        train, val, test = split_indices(n, 0.6, 0.2, seed=42)

        # Check all indices covered
        all_indices = set(train) | set(val) | set(test)
        assert all_indices == set(range(n)), "all_indices is not valid"

        # Check no overlap
        assert len(set(train) & set(val)) == 0, "Collection must not be empty"

    def test_edge_case_no_val(self):
        """Test with zero validation split."""
        n = 100
        train, val, test = split_indices(n, 0.8, 0.0, seed=42)

        assert len(train) == 80, "Train must not be empty"
        assert len(val) == 0, "Val must not be empty"
        assert len(test) == 20, "Test must not be empty"

    def test_reproducibility_across_runs(self):
        """Multiple runs with same seed should give same results."""
        n = 50
        seed = 12345

        results = []
        for _ in range(3):
            train, val, test = split_indices(n, 0.7, 0.15, seed=seed)
            results.append((train, val, test))

        # All results should be identical
        for i in range(1, len(results)):
            assert results[0] == results[i], "Result must not be empty"


class TestSplitIndicesAPI:
    """Test the API and error handling of split_indices."""

    def test_returns_three_lists(self):
        """Function should return three lists."""
        result = split_indices(100, 0.8, 0.1)

        assert isinstance(result, tuple)
        assert len(result) == 3, "Result must not be empty"
        assert all(isinstance(split, list) for split in result)

    def test_all_integer_indices(self):
        """All returned indices should be integers."""
        train, val, test = split_indices(50, 0.6, 0.2)

        all_idx = train + val + test
        assert all(isinstance(i, int) for i in all_idx)

    def test_indices_in_range(self):
        """All indices should be in valid range."""
        n = 100
        train, val, test = split_indices(n, 0.7, 0.15)

        all_idx = train + val + test
        assert all(0 <= i < n for i in all_idx), "0 is not valid"

    def test_invalid_train_ratio_negative(self):
        """Should raise ValueError for negative train ratio."""
        with pytest.raises(ValueError, match="Ratios must be between 0 and 1"):
            split_indices(100, -0.1, 0.1)

    def test_invalid_train_ratio_too_large(self):
        """Should raise ValueError for train ratio > 1."""
        with pytest.raises(ValueError, match="Ratios must be between 0 and 1"):
            split_indices(100, 1.5, 0.1)

    def test_invalid_val_ratio_negative(self):
        """Should raise ValueError for negative val ratio."""
        with pytest.raises(ValueError, match="Ratios must be between 0 and 1"):
            split_indices(100, 0.8, -0.1)

    def test_invalid_val_ratio_too_large(self):
        """Should raise ValueError for val ratio > 1."""
        with pytest.raises(ValueError, match="Ratios must be between 0 and 1"):
            split_indices(100, 0.5, 1.5)

    def test_ratios_sum_exceeds_one(self):
        """Should raise ValueError when ratios sum > 1."""
        with pytest.raises(ValueError, match="cannot exceed 1.0"):
            split_indices(100, 0.8, 0.3)


@pytest.mark.skipif(not NUMPY_AVAILABLE, reason="NumPy not available")
class TestWithNumPy:
    """Tests that specifically require NumPy."""

    def test_uses_numpy_rng(self, monkeypatch):
        """Verify NumPy backend is actually used."""
        np = pytest.importorskip("numpy")

        shuffle_calls = []
        original_default_rng = np.random.default_rng

        class TrackedRNG:
            def __init__(self, seed):
                self._rng = original_default_rng(seed)

            def shuffle(self, x):
                shuffle_calls.append(True)
                return self._rng.shuffle(x)

            def __getattr__(self, name):
                return getattr(self._rng, name)

        monkeypatch.setattr(np.random, "default_rng", TrackedRNG)

        train, val, test = split_indices(100, 0.8, 0.1, seed=42)
        assert len(shuffle_calls) > 0, "NumPy RNG should have been used"

        # Verify the split is reasonable
        assert len(train) == 80, "Train must not be empty"
        assert len(val) == 10, "Val must not be empty"
        assert len(test) == 10, "Test must not be empty"

        # Verify all indices are present
        all_indices = set(train + val + test)
        assert all_indices == set(range(100)), "all_indices is not valid"


class TestWithoutNumPy:
    """Tests for behavior when NumPy is not available."""

    def test_warns_when_numpy_unavailable(self, monkeypatch):
        """Test that a warning is issued when NumPy is not available."""
        # Mock NumPy as unavailable
        import warnings

        import codex_ml.data.splitting as splitting_module

        monkeypatch.setattr(splitting_module, "NUMPY_AVAILABLE", False)
        monkeypatch.setattr(splitting_module, "np", None)

        n = 100
        seed = 42

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            train, val, test = split_indices(n, 0.8, 0.1, seed=seed)

            # Should have issued a warning about NumPy not being available
            assert len(w) == 1, "W must not be empty"
            assert issubclass(w[0].category, UserWarning)
            assert "NumPy is not available" in str(w[0].message), "NumPy is not valid"
            assert "Falling back to Python's random module" in str(w[0].message), "Condition must be true"

        # Verify the split still works (with Python random)
        assert len(train) == 80, "Train must not be empty"
        assert len(val) == 10, "Val must not be empty"
        assert len(test) == 10, "Test must not be empty"

        # Verify all indices are present
        all_indices = set(train + val + test)
        assert all_indices == set(range(n)), "all_indices is not valid"
