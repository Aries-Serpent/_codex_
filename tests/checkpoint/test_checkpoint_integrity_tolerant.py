from __future__ import annotations

from pathlib import Path

from codex_ml.utils import checkpoint_core


def test_save_checkpoint_integrity_failure_is_tolerated(monkeypatch, tmp_path: Path) -> None:
    def _boom(*_args, **_kwargs):
        raise RuntimeError("integrity failure")

    monkeypatch.setattr(checkpoint_core, "attach_integrity", _boom, raising=False)

    checkpoint_dir = tmp_path / "outputs"
    checkpoint_dir.mkdir()

    ckpt_path, meta = checkpoint_core.save_checkpoint(
        checkpoint_dir,
        state={"weights": [1]},
        config={"model": "tiny"},
        metric_value=None,
    )

    assert ckpt_path.exists()
    assert meta.sha256 is not None
