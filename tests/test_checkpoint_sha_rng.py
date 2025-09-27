from __future__ import annotations

import json
from pathlib import Path

import pytest

from codex_ml.utils.checkpoint import load_checkpoint, save_checkpoint


class _Dummy:
    def __init__(self) -> None:
        self._state: dict[str, int] = {"value": 1}

    def state_dict(self) -> dict[str, int]:
        return dict(self._state)

    def load_state_dict(self, state: dict[str, int]) -> None:  # pragma: no cover - trivial
        self._state.update(state)


def test_checkpoint_writes_checksum_and_rng(tmp_path: Path) -> None:
    model = _Dummy()
    optimizer = _Dummy()

    ckpt_dir = save_checkpoint(
        model=model,
        optimizer=optimizer,
        scheduler=None,
        out_dir=tmp_path / "checkpoint",
        metadata={"epoch": 1},
    )

    sha_file = ckpt_dir / "model.pt.sha256"
    rng_file = ckpt_dir / "rng.json"
    assert sha_file.exists()
    assert rng_file.exists()

    payload = json.loads(rng_file.read_text())
    assert "python" in payload

    # Corrupt the checkpoint and ensure strict load fails
    (ckpt_dir / "model.pt").write_bytes(b"corrupted")
    with pytest.raises(ValueError):
        load_checkpoint(
            model=_Dummy(),
            optimizer=_Dummy(),
            scheduler=None,
            ckpt_dir=ckpt_dir,
            strict=True,
        )
