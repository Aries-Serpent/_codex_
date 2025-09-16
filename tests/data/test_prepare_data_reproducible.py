from __future__ import annotations

import json
import random

import pytest

pytest.importorskip("omegaconf")

try:  # optional dependency for RNG disturbance
    import numpy as np
except Exception:  # pragma: no cover - numpy unavailable
    np = None

from codex_ml.config import DataConfig
from codex_ml.data.loader import prepare_data_from_config
from codex_ml.utils.provenance import load_environment_summary


def _read_lines(path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def test_prepare_data_repeatable(tmp_path) -> None:
    source = tmp_path / "source.txt"
    source.write_text("alpha\nbeta\ngamma\n", encoding="utf-8")

    cfg_kwargs = {
        "source_path": str(source),
        "split_ratios": {"train": 0.6, "validation": 0.2, "test": 0.2},
        "shuffle_seed": 17,
        "manifest_path": None,
        "max_items": None,
    }

    cfg1 = DataConfig(cache_dir=str(tmp_path / "cache1"), **cfg_kwargs)
    cfg2 = DataConfig(cache_dir=str(tmp_path / "cache2"), **cfg_kwargs)

    result1 = prepare_data_from_config(cfg1)

    # Disturb RNG state to verify seeding resets deterministically.
    random.random()
    if np is not None:
        np.random.rand()

    result2 = prepare_data_from_config(cfg2)

    def _strip_paths(split_map: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
        return {
            name: {k: v for k, v in meta.items() if k != "path"} for name, meta in split_map.items()
        }

    assert _strip_paths(result1["splits"]) == _strip_paths(result2["splits"])

    for split in ("train", "validation", "test"):
        lines1 = _read_lines((tmp_path / "cache1" / f"{split}.txt"))
        lines2 = _read_lines((tmp_path / "cache2" / f"{split}.txt"))
        assert lines1 == lines2

    prov1 = load_environment_summary(tmp_path / "cache1" / "provenance")
    prov2 = load_environment_summary(tmp_path / "cache2" / "provenance")
    assert prov1["seed"] == prov2["seed"] == 17
    assert prov1["command"] == prov2["command"] == "prepare-data"

    manifest1 = json.loads((tmp_path / "cache1" / cfg1.cache_manifest_name).read_text())
    manifest2 = json.loads((tmp_path / "cache2" / cfg2.cache_manifest_name).read_text())
    assert manifest1["splits"]["train"]["checksum"] == manifest2["splits"]["train"]["checksum"]
