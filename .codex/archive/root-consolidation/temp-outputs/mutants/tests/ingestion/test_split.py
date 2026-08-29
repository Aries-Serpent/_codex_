"""
Test Split

Test module for split.
"""

from __future__ import annotations

import pytest

from ingestion.split import SplitConfig, split_files


def test_split_files_is_deterministic_with_seed() -> None:
    files = [f"sample_{i}.txt" for i in range(10)]
    cfg = SplitConfig(train_ratio=0.6, val_ratio=0.2, seed=2024)

    first = split_files(files, cfg)
    second = split_files(files, cfg)

    assert first == second, "first is not valid"


def test_split_files_changes_with_different_seed() -> None:
    files = [f"sample_{i}.txt" for i in range(10)]
    base_cfg = SplitConfig(train_ratio=0.6, val_ratio=0.2, seed=7)
    alt_cfg = SplitConfig(train_ratio=0.6, val_ratio=0.2, seed=8)

    base_split = split_files(files, base_cfg)
    alt_split = split_files(files, alt_cfg)

    assert base_split != alt_split, "base_split is not valid"


def test_split_files_uses_default_configuration_when_none() -> None:
    files = [f"example_{i}.bin" for i in range(5)]

    train, val, test = split_files(files, None)

    assert len(train) == int(len(files) * SplitConfig().train_ratio), "Train must not be empty"
    assert len(val) == int(len(files) * SplitConfig().val_ratio), "Val must not be empty"
    assert len(test) == len(files) - len(train) - len(val), "Test must not be empty"
    assert sorted(train + val + test) == sorted(files), "s is not valid"


def test_split_files_handles_empty_input() -> None:
    assert split_files([], SplitConfig()) == ([], [], [])


@pytest.mark.parametrize(
    "cfg",
    [
        SplitConfig(),
        SplitConfig(train_ratio=0.5, val_ratio=0.3, seed=99),
    ],
)
def test_split_files_respects_ratios(cfg: SplitConfig) -> None:
    files = [f"item_{i}.json" for i in range(17)]

    train, val, test = split_files(files, cfg)

    expected_train = int(len(files) * cfg.train_ratio)
    expected_val = int(len(files) * cfg.val_ratio)
    expected_test = len(files) - expected_train - expected_val

    assert len(train) == expected_train, "Train must not be empty"
    assert len(val) == expected_val, "Val must not be empty"
    assert len(test) == expected_test, "Test must not be empty"
    assert sorted(train + val + test) == sorted(files), "s is not valid"
