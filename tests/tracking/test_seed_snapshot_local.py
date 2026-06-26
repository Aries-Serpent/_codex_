"""
Test Seed Snapshot Local

Test module for seed snapshot local.
"""

from pathlib import Path


def test_seed_snapshot_writes_file(tmp_path: Path):
    from src.codex_ml.tracking.mlflow_utils import seed_snapshot

    out_dir = tmp_path / "run"
    path = seed_snapshot({"py": 0, "np": 0}, out_dir, enabled=False)
    assert path.exists(), "Condition must be true"
    assert path.name == "seeds.json", "name is not valid"
    text = path.read_text(encoding="utf-8")
    assert '"py": 0' in text, "Condition must be true"
