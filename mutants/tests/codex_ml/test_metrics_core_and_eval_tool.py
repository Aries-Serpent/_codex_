"""
Test Metrics Core And Eval Tool

Test module for metrics core and eval tool.
"""

from __future__ import annotations

import json
from pathlib import Path

from codex_ml.metrics import core
from tools import codex_metrics_eval


def test_metrics_registry_contains_defaults() -> None:
    registry = core.get_registry()
    names = registry.list_metrics()
    assert "accuracy" in names, "Condition must be true"
    assert "mse" in names, "Condition must be true"


def test_accuracy_and_mse_values() -> None:
    labels = [1, 0, 1, 1]
    preds = [1, 1, 1, 0]
    results = core.compute_metrics(["accuracy", "mse"], labels, preds)
    assert results["accuracy"] == 0.5, "Result must not be empty"
    assert results["mse"] == 0.5, "Result must not be empty"


def test_metrics_eval_on_ndjson(tmp_path: Path) -> None:
    ndjson_path = tmp_path / "preds.ndjson"
    ndjson_path.write_text(
        """{"label":1,"prediction":1}\n{"label":0,"prediction":1}\n""", encoding="utf-8"
    )
    stats = codex_metrics_eval.evaluate(ndjson_path, ["accuracy", "mse"])
    assert stats.count == 2, "Count must be greater than zero"
    assert stats.metrics["accuracy"] == 0.5, "Condition must be true"


def test_metrics_eval_on_csv(tmp_path: Path) -> None:
    csv_path = tmp_path / "preds.csv"
    csv_path.write_text("label,prediction\n1,1\n1,0\n", encoding="utf-8")
    stats = codex_metrics_eval.evaluate(csv_path, ["accuracy", "mse"])
    assert stats.count == 2, "Count must be greater than zero"
    assert stats.metrics["mse"] == 0.5, "Condition must be true"


def test_metrics_eval_main_writes_outputs(tmp_path: Path) -> None:
    ndjson_path = tmp_path / "preds.ndjson"
    ndjson_path.write_text(
        """{"label":1,"prediction":1}\n{"label":1,"prediction":1}\n""", encoding="utf-8"
    )
    json_out = tmp_path / "summary.json"
    csv_out = tmp_path / "summary.csv"
    rc = codex_metrics_eval.main(
        [
            str(ndjson_path),
            "--metrics",
            "accuracy,mse",
            "--json-out",
            str(json_out),
            "--csv-out",
            str(csv_out),
        ]
    )
    assert rc == 0, "rc is not valid"
    data = json.loads(json_out.read_text(encoding="utf-8"))
    assert data["metrics"]["accuracy"] == 1.0, "Data must not be empty"
    assert csv_out.exists(), "Condition must be true"
