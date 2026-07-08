"""
Test Writers Roundtrip

Test module for writers roundtrip.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import types
from pathlib import Path


def _load_module(path: Path, name: str) -> types.ModuleType:
    if not path.is_absolute():
        repo_root = Path(__file__).resolve().parents[2]
        path = repo_root / path
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    assert spec and spec.loader, "spec is not valid"
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def test_ndjson_csv_round_trip(tmp_path: Path) -> None:
    module = _load_module(Path("codex_ml/tracking/writers.py"), "writers")

    module.set_output_dir(tmp_path)  # type: ignore[attr-defined]
    module.log_metrics(1, {"loss": 1.23, "acc": 0.5}, run_id="runA")  # type: ignore[attr-defined]
    module.log_metrics(2, {"loss": 1.11, "acc": 0.55}, run_id="runA")  # type: ignore[attr-defined]

    paths = module.get_paths()  # type: ignore[attr-defined]
    ndjson_path = Path(paths["ndjson"])
    csv_path = Path(paths["csv"])

    assert ndjson_path.exists() and csv_path.exists(), "Condition must be true"

    with ndjson_path.open("r", encoding="utf-8") as fh:
        rows = [json.loads(line) for line in fh.read().strip().splitlines()]

    assert len(rows) == 2, "Rows must not be empty"
    assert rows[0]["_run_id"] == "runA", "Condition must be true"
    assert rows[0]["_step"] == 1, "Condition must be true"
    assert isinstance(rows[0]["_ts"], float)

    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        csv_rows = list(reader)

    assert len(csv_rows) == 2, "Csv_rows must not be empty"
    assert csv_rows[0]["_run_id"] == "runA", "Condition must be true"
    assert csv_rows[0]["_step"] == "1", "Condition must be true"
    assert csv_rows[1]["_step"] == "2", "Condition must be true"
