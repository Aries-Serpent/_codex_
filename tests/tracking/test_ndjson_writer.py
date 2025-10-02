import json
from pathlib import Path

from codex_ml.tracking import init_experiment


class DummyCfg:
    def __init__(self, outdir: Path) -> None:
        self.experiment = "exp"
        self.tracking = type(
            "T",
            (),
            {
                "tensorboard": False,
                "mlflow": False,
                "wandb": False,
                "output_dir": str(outdir),
            },
        )()


def test_ndjson_basic(tmp_path: Path) -> None:
    cfg = DummyCfg(tmp_path)
    ctx = init_experiment(cfg)
    ctx.log_metric(step=1, split="train", metric="loss", value=1.23)
    ctx.finalize()
    data = ctx.metrics_path.read_text(encoding="utf-8").strip().splitlines()
    row = json.loads(data[0])
    assert row["metric"] == "loss"
    assert row["value"] == 1.23
    assert row["schema_version"] == "v1"
    assert row["$schema"].endswith("run_metrics.schema.json")
    assert "timestamp" in row


def test_structured_metric_produces_manifest(tmp_path: Path) -> None:
    from codex_ml.logging.run_logger import RunLogger

    run_logger = RunLogger(tmp_path, "run-structured")
    run_logger.log_metric(
        step=5,
        split="eval",
        metric="confusion",
        value={"path": "confusion.npy", "shape": [2, 2]},
    )
    metrics_path = run_logger.metrics_path
    manifest_path = metrics_path.with_name("metrics_manifest.ndjson")
    metrics_rows = [
        json.loads(line) for line in metrics_path.read_text().splitlines() if line.strip()
    ]
    manifest_rows = [
        json.loads(line) for line in manifest_path.read_text().splitlines() if line.strip()
    ]
    assert metrics_rows and metrics_rows[0]["value"] is None
    assert manifest_rows and manifest_rows[0]["descriptor"]["path"] == "confusion.npy"
    assert manifest_rows[0]["descriptor"]["shape"] == [2, 2]
    assert manifest_rows[0]["run_id"] == "run-structured"
    assert "timestamp" in manifest_rows[0]
    run_logger.close()
