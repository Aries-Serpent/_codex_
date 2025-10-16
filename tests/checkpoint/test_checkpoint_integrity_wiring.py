from __future__ import annotations

from pathlib import Path

from codex_ml.utils import checkpoint_core


def test_save_checkpoint_attaches_integrity(monkeypatch, tmp_path: Path) -> None:
    calls: dict[str, object] = {}

    def _fake_attach(path: str | Path, *, metadata=None, relative_to=None):
        calls["path"] = Path(path)
        calls["metadata"] = metadata
        calls["relative_to"] = Path(relative_to) if relative_to is not None else None
        return {"sha256": "abc", "git_sha": "deadbeef"}

    monkeypatch.setattr(checkpoint_core, "attach_integrity", _fake_attach, raising=False)

    checkpoint_dir = tmp_path / "checkpoints"
    state = {"weights": [1, 2, 3]}
    cfg = {
        "model_name": "tiny",
        "epochs": 1,
        "batch_size": 2,
        "learning_rate": 1e-4,
        "seed": 42,
    }

    ckpt_path, meta = checkpoint_core.save_checkpoint(
        checkpoint_dir,
        state=state,
        config=cfg,
        metric_value=0.0,
    )

    assert ckpt_path.exists()
    assert isinstance(meta.config_snapshot, dict)
    assert calls["path"] == ckpt_path
    assert calls["relative_to"] == checkpoint_dir
    metadata = calls.get("metadata") or {}
    snapshot = metadata.get("config_snapshot", {})
    assert snapshot.get("model_name") == "tiny"
