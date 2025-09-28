from __future__ import annotations

import random
from pathlib import Path

import pytest

from codex_ml.utils.checkpoint import load_checkpoint, save_checkpoint

np = pytest.importorskip("numpy")
torch = pytest.importorskip("torch")


def test_rng_restoration_roundtrip(tmp_path: Path) -> None:
    random.seed(2024)
    np.random.seed(2024)
    torch.manual_seed(2024)
    if torch.cuda.is_available():  # pragma: no cover - optional GPU paths
        torch.cuda.manual_seed_all(2024)

    expected_py = [random.random() for _ in range(4)]
    expected_np = np.random.random(4)
    expected_torch = torch.rand(4)

    random.seed(2024)
    np.random.seed(2024)
    torch.manual_seed(2024)
    if torch.cuda.is_available():  # pragma: no cover - optional GPU paths
        torch.cuda.manual_seed_all(2024)

    model = torch.nn.Linear(4, 2)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    ckpt_dir = save_checkpoint(
        model=model,
        optimizer=optimizer,
        scheduler=None,
        out_dir=tmp_path / "rng_ckpt",
        metadata={"epoch": 1},
    )

    # disturb the RNG state after saving
    random.random()
    np.random.random()
    torch.rand(1)

    restored_model = torch.nn.Linear(4, 2)
    restored_opt = torch.optim.Adam(restored_model.parameters(), lr=0.001)

    load_checkpoint(
        model=restored_model,
        optimizer=restored_opt,
        scheduler=None,
        ckpt_dir=ckpt_dir,
    )

    restored_py = [random.random() for _ in range(4)]
    restored_np = np.random.random(4)
    restored_torch = torch.rand(4)

    assert restored_py == expected_py
    np.testing.assert_allclose(restored_np, expected_np)
    assert torch.allclose(restored_torch, expected_torch)
