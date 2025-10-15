from __future__ import annotations

import importlib
from pathlib import Path


def test_integrity_metadata_attached(monkeypatch, tmp_path: Path) -> None:
    """save_checkpoint should enrich metadata with config snapshots and call attach_integrity."""
    core = importlib.import_module("codex_ml.utils.checkpoint_core")
    recorded: dict[str, object] = {}

    def fake_attach(
        path: str | Path, metadata: dict | None = None, **kwargs: object
    ) -> dict[str, object]:
        recorded["path"] = Path(path)
        recorded["metadata"] = metadata
        recorded["kwargs"] = kwargs
        return {"sha256": "deadbeef", "size": 123}

    monkeypatch.setattr(core, "attach_integrity", fake_attach)

    state = {"weights": [1, 2, 3]}
    cfg = {"model": {"name": "tiny"}, "training": {"epochs": 1, "batch_size": 2}}
    ckpt_path, meta = core.save_checkpoint(tmp_path, state, config=cfg, metric_value=0.1)

    assert meta.config_snapshot is not None
    assert meta.config_snapshot["model"]["name"] == "tiny"
    assert recorded["path"] == ckpt_path
    metadata = recorded["metadata"]
    assert isinstance(metadata, dict)
    assert metadata["config_snapshot"]["model"]["name"] == "tiny"

    raw = core._read_bytes(ckpt_path)
    payload = core._deserialize_payload(raw)
    snapshot = payload["meta"].get("config_snapshot")
    assert snapshot["model"]["name"] == "tiny"
