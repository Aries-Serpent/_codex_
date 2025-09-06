from pathlib import Path

from codex_ml.tracking import init_experiment


def test_init_experiment_writes_ndjson(tmp_path: Path) -> None:
    tracker = init_experiment("exp", log_dir=tmp_path)
    tracker["log_metrics"](1, {"loss": 0.5})
    data = (tmp_path / "exp.ndjson").read_text().strip()
    assert '"loss": 0.5' in data
