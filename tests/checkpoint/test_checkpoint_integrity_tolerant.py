from __future__ import annotations

import json
from pathlib import Path


def test_save_checkpoint_tolerates_integrity_fail(monkeypatch, tmp_path: Path) -> None:
    import importlib

    core = importlib.import_module("codex_ml.utils.checkpoint_core")

    def _boom(*_args, **_kwargs):
        raise RuntimeError("integrity failure")

    monkeypatch.setattr(core, "attach_integrity", _boom, raising=True)

    ckpt_dir = tmp_path / "ckpts"
    ckpt_path, meta = core.save_checkpoint(str(ckpt_dir), {"w": 1})

    assert ckpt_path.exists()

    index_path = ckpt_dir / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    assert index.get("entries")

    assert getattr(meta, "sha256", None)
