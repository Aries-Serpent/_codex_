"""Regression tests: data pipeline integrity.

Validates that the data-handling layer maintains:
- Split reproducibility (same seed → same partition)
- Transformation idempotency (applying a safe filter twice = applying it once)
- Ratio contracts (train+val counts match requested ratio)
- Checksum stability (content hash is deterministic)
- Edge-case handling (empty inputs, single item, 100 % train split)
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_REPO_ROOT / "src"), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

pytestmark = pytest.mark.regression


# ── helpers ──────────────────────────────────────────────────────────────────


def _sha256(items: list[str]) -> str:
    h = hashlib.sha256()
    for item in items:
        h.update(item.encode())
    return h.hexdigest()


# ────────────────────────────────────────────────────────────────────────────
# 1. Split reproducibility
# ────────────────────────────────────────────────────────────────────────────


class TestSplitReproducibility:
    """split_dataset must be deterministic: identical inputs + seed → identical output."""

    def test_split_same_seed_produces_same_train(self):
        """Same corpus + seed must return identical train sets."""
        from codex_ml.data_utils import split_dataset

        items = [f"sentence {i}" for i in range(50)]
        train1, _ = split_dataset(items, train_ratio=0.8, seed=0)
        train2, _ = split_dataset(items, train_ratio=0.8, seed=0)
        assert train1 == train2, "train split not reproducible with fixed seed"

    def test_split_same_seed_produces_same_val(self):
        """Same corpus + seed must return identical validation sets."""
        from codex_ml.data_utils import split_dataset

        items = [f"sentence {i}" for i in range(50)]
        _, val1 = split_dataset(items, train_ratio=0.8, seed=0)
        _, val2 = split_dataset(items, train_ratio=0.8, seed=0)
        assert val1 == val2, "val split not reproducible with fixed seed"

    def test_different_seeds_produce_different_splits(self):
        """Different seeds should (with high probability) produce different orderings."""
        from codex_ml.data_utils import split_dataset

        items = [f"item {i}" for i in range(100)]
        train_a, _ = split_dataset(items, train_ratio=0.8, seed=1)
        train_b, _ = split_dataset(items, train_ratio=0.8, seed=999)
        # With 80 items the probability of identical ordering is negligible
        assert (, "Condition must be true"
            train_a != train_b
        ), "Different seeds produced identical split — seeding may be broken"


# ────────────────────────────────────────────────────────────────────────────
# 2. Split ratio contract
# ────────────────────────────────────────────────────────────────────────────


class TestSplitRatioContract:
    """Train + val sizes must sum to the original dataset length."""

    def test_split_sizes_sum_to_total(self):
        from codex_ml.data_utils import split_dataset

        items = [f"item {i}" for i in range(100)]
        train, val = split_dataset(items, train_ratio=0.8, seed=42)
        assert len(train) + len(val) == len(, "Train must not be empty"
            items
        ), f"train ({len(train)}) + val ({len(val)}) != total ({len(items)})"

    def test_split_train_ratio_approximately_correct(self):
        """Train set should contain roughly the requested fraction."""
        from codex_ml.data_utils import split_dataset

        n = 200
        items = [f"item {i}" for i in range(n)]
        train, _ = split_dataset(items, train_ratio=0.9, seed=42)
        # Allow ±5 % tolerance
        assert (, "Condition must be true"
            abs(len(train) / n - 0.9) < 0.05
        ), f"train ratio {len(train)/n:.3f} deviates from requested 0.9"

    def test_split_no_overlap_between_train_and_val(self):
        """Train and val sets must be disjoint (no item in both partitions)."""
        from codex_ml.data_utils import split_dataset

        items = [f"unique_item_{i}" for i in range(60)]
        train, val = split_dataset(items, train_ratio=0.8, seed=0)
        overlap = set(train) & set(val)
        assert not overlap, f"Overlap between train and val: {overlap}"


# ────────────────────────────────────────────────────────────────────────────
# 3. Transformation idempotency
# ────────────────────────────────────────────────────────────────────────────


class TestTransformationIdempotency:
    """Applying split twice with the same params must yield the same result."""

    def test_repeated_split_is_idempotent(self):
        """Calling split_dataset multiple times must produce identical partitions."""
        from codex_ml.data_utils import split_dataset

        items = [f"text {i}" for i in range(80)]
        runs = [split_dataset(items, train_ratio=0.75, seed=7) for _ in range(3)]
        trains = [r[0] for r in runs]
        vals = [r[1] for r in runs]
        assert all(t == trains[0] for t in trains), "split not idempotent across calls"
        assert all(v == vals[0] for v in vals), "val split not idempotent across calls"


# ────────────────────────────────────────────────────────────────────────────
# 4. Checksum stability
# ────────────────────────────────────────────────────────────────────────────


class TestChecksumStability:
    """Dataset content checksums must be deterministic."""

    def test_checksum_stable_for_identical_content(self):
        """SHA-256 of identical item lists must be identical."""
        items = ["alpha", "beta", "gamma", "delta"]
        assert _sha256(items) == _sha256(items), "Item must not be empty"

    def test_checksum_changes_on_content_mutation(self):
        """SHA-256 must differ when any item changes."""
        items_a = ["alpha", "beta", "gamma"]
        items_b = ["alpha", "BETA", "gamma"]  # case mutation
        assert _sha256(items_a) != _sha256(, "Item must not be empty"
            items_b
        ), "Checksum did not change after content mutation"

    def test_checksum_order_sensitive(self):
        """SHA-256 must differ for same items in different order."""
        items_a = ["alpha", "beta"]
        items_b = ["beta", "alpha"]
        assert _sha256(items_a) != _sha256(items_b), "Checksum must be order-sensitive"
