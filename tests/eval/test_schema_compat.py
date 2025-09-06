import csv
import json

from typer.testing import CliRunner

from codex_ml.eval import eval_runner


def test_schema_compat(tmp_path):
    runner = CliRunner()
    out_dir = tmp_path / "out"
    result = runner.invoke(
        eval_runner.app,
        [
            "--datasets",
            "toy_copy_task",
            "--metrics",
            "exact_match",
            "--output-dir",
            str(out_dir),
        ],
    )
    assert result.exit_code == 0
    ndjson_path = out_dir / "metrics.ndjson"
    csv_path = out_dir / "metrics.csv"
    nd = json.loads(ndjson_path.read_text().strip().splitlines()[0])
    with csv_path.open() as fh:
        reader = csv.DictReader(fh)
        row = next(reader)
    assert set(row) == {
        "run_id",
        "dataset",
        "split",
        "step",
        "metric",
        "value",
        "n",
        "timestamp",
        "notes",
    }
    assert float(row["value"]) == nd["value"]
