import csv
from pathlib import Path

import pytest

from codex_ml.logging.run_logger import RunLogger
from codex_utils.cli import ndjson_summary


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_summarize_rotated_shards_to_csv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    run_dir = tmp_path / "run"
    monkeypatch.setenv("CODEX_TRACKING_NDJSON_MAX_BYTES", "200")
    monkeypatch.setenv("CODEX_TRACKING_NDJSON_BACKUP_COUNT", "8")

    logger = RunLogger(run_dir, "run-test")
    for step in range(5):
        logger.log_metric(
            step=step,
            split="train",
            metric="loss",
            value=1.0 / (step + 1),
            tags={"phase": "train"},
        )
    logger.log_metric(
        step=5,
        split="eval",
        metric="confusion",
        value={"path": "conf.npy", "shape": [2, 2]},
        tags={"phase": "eval"},
    )
    logger.close()

    rotated = sorted(run_dir.glob("metrics.ndjson.*"))
    assert rotated, "expected rotation to produce suffixed shards"

    exit_code = ndjson_summary.main(["summarize", "--input", str(run_dir), "--output", "csv"])
    assert exit_code == 0
    output_path = run_dir / "metrics_summary.csv"
    assert output_path.exists()

    rows = _read_csv(output_path)
    assert len(rows) == 2

    loss_row = next(row for row in rows if row["metric"] == "loss")
    assert loss_row["count"] == "5"
    assert loss_row["first_step"] == "0"
    assert loss_row["last_step"] == "4"
    assert loss_row["first_phase"] == "train"
    assert loss_row["last_phase"] == "train"
    assert loss_row["first_value"] == "1.0"
    assert loss_row["last_value"].startswith("0.")

    confusion_row = next(row for row in rows if row["metric"] == "confusion")
    assert confusion_row["last_manifest_id"], "structured metric should link manifest id"
    assert confusion_row["first_manifest_id"] == confusion_row["last_manifest_id"]
    assert confusion_row["first_phase"] == "eval"
    assert confusion_row["last_phase"] == "eval"
    assert confusion_row["first_value"] == ""
    assert confusion_row["last_value"] == ""


def test_summarize_to_parquet_when_available(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pandas = pytest.importorskip("pandas")
    run_dir = tmp_path / "run"
    monkeypatch.setenv("CODEX_TRACKING_NDJSON_MAX_BYTES", "128")
    logger = RunLogger(run_dir, "run-parquet")
    for step in range(3):
        logger.log_metric(step=step, split="train", metric="accuracy", value=0.8 + step * 0.01)
    logger.close()

    exit_code = ndjson_summary.main(["summarize", "--input", str(run_dir), "--output", "parquet"])
    assert exit_code == 0
    parquet_path = run_dir / "metrics_summary.parquet"
    assert parquet_path.exists()

    frame = pandas.read_parquet(parquet_path)
    assert set(frame["metric"]) == {"accuracy"}
    assert int(frame.iloc[0]["count"]) == 3
