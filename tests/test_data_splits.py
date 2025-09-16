import json
from pathlib import Path

from codex_ml.config import DataConfig
from codex_ml.data.loader import prepare_data_from_config


def test_prepare_data_deterministic(tmp_path: Path) -> None:
    dataset = tmp_path / "dataset.txt"
    dataset.write_text("\n".join([f"line-{i}" for i in range(10)]) + "\n", encoding="utf-8")
    cfg = DataConfig(
        source_path=str(dataset),
        cache_dir=str(tmp_path / "cache"),
        manifest_path=str(tmp_path / "cache" / "manifest.json"),
        split_ratios={"train": 0.7, "validation": 0.2, "test": 0.1},
        shuffle_seed=42,
    )
    first = prepare_data_from_config(cfg)
    second = prepare_data_from_config(cfg)
    train_path = Path(first["splits"]["train"]["path"])
    assert train_path.read_text(encoding="utf-8") == Path(
        second["splits"]["train"]["path"]
    ).read_text(encoding="utf-8")
    manifest = json.loads(Path(first["manifest"]).read_text(encoding="utf-8"))
    for name, meta in first["splits"].items():
        split_path = Path(meta["path"])
        lines = [ln for ln in split_path.read_text(encoding="utf-8").splitlines() if ln]
        assert len(lines) == meta["count"]
    assert manifest["splits"]["train"]["count"] == first["splits"]["train"]["count"]
