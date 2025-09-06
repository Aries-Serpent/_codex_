import csv as csv_mod
import json

from typer.testing import CliRunner

from codex_ml.eval import eval_runner


def test_eval_runner_smoke(tmp_path):
    runner = CliRunner()
    # create dataset with mismatched predictions
    ds_path = tmp_path / "ds.jsonl"
    ds_path.write_text(json.dumps({"input": "a", "target": "b", "prediction": "c"}) + "\n")
    out_dir = tmp_path / "out"
    result = runner.invoke(
        eval_runner.app,
        [
            "--datasets",
            str(ds_path),
            "--metrics",
            "exact_match",
            "--output-dir",
            str(out_dir),
        ],
    )
    assert result.exit_code == 0
    ndjson_path = out_dir / "metrics.ndjson"
    csv_path = out_dir / "metrics.csv"
    assert ndjson_path.exists() and csv_path.exists()
    data = json.loads(ndjson_path.read_text().strip().splitlines()[0])
    assert {"run_id", "dataset", "split", "metric", "value"}.issubset(data)
    with csv_path.open() as fh:
        reader = csv_mod.DictReader(fh)
        row = next(reader)
    assert row["metric"] == data["metric"]
    assert float(row["value"]) == 0.0
