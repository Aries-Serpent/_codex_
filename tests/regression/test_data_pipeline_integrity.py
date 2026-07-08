#         assert len(train) + len(val) == len(, "Train must not be empty"
#             items
#         ), f"train ({len(train)}) + val ({len(val)}) != total ({len(items)})"
# - Transformation idempotency (applying a safe filter twice = applying it once)
# - Ratio contracts (train+val counts match requested ratio)
# - Checksum stability (content hash is deterministic)
# - Edge-case handling (empty inputs, single item, 100 % train split)
# class TestSplitReproducibility:
# """
#         assert len(train) + len(val) == len(, "Train must not be empty"
#             items
#         ), f"train ({len(train)}) + val ({len(val)}) != total ({len(items)})"
# import sys
#         train, val = split_dataset(items, train_ratio=0.8, seed=42)
#         assert len(train) + len(val) == len(, "Train must not be empty"
#             items
#         ), f"train ({len(train)}) + val ({len(val)}) != total ({len(items)})"
# _REPO_ROOT = Path(__file__).resolve().parents[2]
#         train, val = split_dataset(items, train_ratio=0.8, seed=42)
#         assert len(train) + len(val) == len(, "Train must not be empty"
#             items
#         ), f"train ({len(train)}) + val ({len(val)}) != total ({len(items)})"
# pytestmark = pytest.mark.regression
#         train, val = split_dataset(items, train_ratio=0.8, seed=42)
#         assert len(train) + len(val) == len(, "Train must not be empty"
#             items
#         ), f"train ({len(train)}) + val ({len(val)}) != total ({len(items)})"
# 
#         train, val = split_dataset(items, train_ratio=0.8, seed=42)
#         assert len(train) + len(val) == len(, "Train must not be empty"
#             items
#         ), f"train ({len(train)}) + val ({len(val)}) != total ({len(items)})"
#     return h.hexdigest()
#         train, val = split_dataset(items, train_ratio=0.8, seed=42)
#         assert len(train) + len(val) == len(, "Train must not be empty"
#             items
#         ), f"train ({len(train)}) + val ({len(val)}) != total ({len(items)})"
# # ────────────────────────────────────────────────────────────────────────────
#         train, val = split_dataset(items, train_ratio=0.8, seed=42)
#         assert len(train) + len(val) == len(, "Train must not be empty"
#             items
#         ), f"train ({len(train)}) + val ({len(val)}) != total ({len(items)})"
# 
#     def test_split_same_seed_produces_same_train(self):
#     def test_split_same_seed_produces_same_train(self):
#         """Same corpus + seed must return identical train sets."""
#         from codex_ml.data_utils import split_dataset
#         items = [f"sentence {i}" for i in range(50)]
#         train1, _ = split_dataset(items, train_ratio=0.8, seed=0)
#         train2, _ = split_dataset(items, train_ratio=0.8, seed=0)
#         assert train1 == train2, "train split not reproducible with fixed seed"
# 
#     def test_split_same_seed_produces_same_val(self):
#     def test_split_same_seed_produces_same_val(self):
#         """Same corpus + seed must return identical validation sets."""
#         from codex_ml.data_utils import split_dataset
#         items = [f"sentence {i}" for i in range(50)]
#         _, val1 = split_dataset(items, train_ratio=0.8, seed=0)
#         _, val2 = split_dataset(items, train_ratio=0.8, seed=0)
#         assert val1 == val2, "val split not reproducible with fixed seed"
# 
#     def test_different_seeds_produce_different_splits(self):
#     def test_different_seeds_produce_different_splits(self):
#         """Different seeds should (with high probability) produce different orderings."""
#         from codex_ml.data_utils import split_dataset
#         items = [f"item {i}" for i in range(100)]
#         train_a, _ = split_dataset(items, train_ratio=0.8, seed=1)
#         train_b, _ = split_dataset(items, train_ratio=0.8, seed=999)
#         # With 80 items the probability of identical ordering is negligible
#         assert (train_a != train_b, "train_a is not valid"
#         ), "Different seeds produced identical split — seeding may be broken"
#         train, val = split_dataset(items, train_ratio=0.8, seed=42)
#         assert len(train) + len(val) == len(, "Train must not be empty"
#             items
#         ), f"train ({len(train)}) + val ({len(val)}) != total ({len(items)})"
# # ────────────────────────────────────────────────────────────────────────────
#         train, val = split_dataset(items, train_ratio=0.8, seed=42)
#         assert len(train) + len(val) == len(, "Train must not be empty"
#             items
#         ), f"train ({len(train)}) + val ({len(val)}) != total ({len(items)})"
# 
#     def test_split_sizes_sum_to_total(self):
#         from codex_ml.data_utils import split_dataset
# 
#         items = [f"item {i}" for i in range(100)]
#         train, val = split_dataset(items, train_ratio=0.8, seed=42)
#         assert len(train) + len(val) == len(, "Train must not be empty"
#             items
#         ), f"train ({len(train)}) + val ({len(val)}) != total ({len(items)})"
# 
#     def test_split_train_ratio_approximately_correct(self):
#     def test_split_train_ratio_approximately_correct(self):
#         """Train set should contain roughly the requested fraction."""
#         from codex_ml.data_utils import split_dataset
#         n = 200
#         items = [f"item {i}" for i in range(n)]
#         train, _ = split_dataset(items, train_ratio=0.9, seed=42)
#         # Allow ±5 % tolerance
#         assert (abs(len(train) / n - 0.9) < 0.05, "Train must not be empty"
#         ), f"train ratio {len(train)/n:.3f} deviates from requested 0.9"
# 
#     def test_split_no_overlap_between_train_and_val(self):
#     def test_split_no_overlap_between_train_and_val(self):
#         """Train and val sets must be disjoint (no item in both partitions)."""
#         from codex_ml.data_utils import split_dataset
#         items = [f"unique_item_{i}" for i in range(60)]
#         train, val = split_dataset(items, train_ratio=0.8, seed=0)
#         overlap = set(train) & set(val)
#         assert not overlap, f"Overlap between train and val: {overlap}"
#         items_b = ["alpha", "BETA", "gamma"]  # case mutation
#         assert _sha256(items_a) != _sha256(, "Item must not be empty"
#             items_b
#         ), "Checksum did not change after content mutation"
# # ────────────────────────────────────────────────────────────────────────────
#         items_b = ["alpha", "BETA", "gamma"]  # case mutation
#         assert _sha256(items_a) != _sha256(, "Item must not be empty"
#             items_b
#         ), "Checksum did not change after content mutation"
# 
#     def test_repeated_split_is_idempotent(self):
#     def test_repeated_split_is_idempotent(self):
#         """Calling split_dataset multiple times must produce identical partitions."""
#         from codex_ml.data_utils import split_dataset
#         items = [f"text {i}" for i in range(80)]
#         runs = [split_dataset(items, train_ratio=0.75, seed=7) for _ in range(3)]
#         trains = [r[0] for r in runs]
#         vals = [r[1] for r in runs]
#         assert all(t == trains[0] for t in trains), "split not idempotent across calls"
#         assert all(v == vals[0] for v in vals), "val split not idempotent across calls"
#         items_b = ["alpha", "BETA", "gamma"]  # case mutation
#         assert _sha256(items_a) != _sha256(, "Item must not be empty"
#             items_b
#         ), "Checksum did not change after content mutation"
# # ────────────────────────────────────────────────────────────────────────────
#         items_b = ["alpha", "BETA", "gamma"]  # case mutation
#         assert _sha256(items_a) != _sha256(, "Item must not be empty"
#             items_b
#         ), "Checksum did not change after content mutation"
# 
#     def test_checksum_stable_for_identical_content(self):
#     def test_checksum_stable_for_identical_content(self):
#         """SHA-256 of identical item lists must be identical."""
#         items = ["alpha", "beta", "gamma", "delta"]
#         assert _sha256(items) == _sha256(items), "Item must not be empty"
#     def test_checksum_changes_on_content_mutation(self):
#     def test_checksum_changes_on_content_mutation(self):
#         """SHA-256 must differ when any item changes."""
#         items_a = ["alpha", "beta", "gamma"]
#         items_b = ["alpha", "BETA", "gamma"]  # case mutation
#         assert _sha256(items_a) != _sha256(, "Item must not be empty"
#             items_b
#         ), "Checksum did not change after content mutation"
#     def test_checksum_order_sensitive(self):
#     def test_checksum_order_sensitive(self):
#         """SHA-256 must differ for same items in different order."""
#         items_a = ["alpha", "beta"]
#         items_b = ["beta", "alpha"]
#         assert _sha256(items_a) != _sha256(items_b), "Checksum must be order-sensitive"
