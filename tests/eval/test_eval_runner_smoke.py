import json

from typer.testing import CliRunner

from codex_ml.eval import eval_runner


def test_eval_runner_smoke(tmp_path):
    runner = CliRunner()
    out_dir = tmp_path / "out"
    result = runner.invoke(
        eval_runner.app,
        [
            "--datasets",
            "toy_copy_task",
            "--metrics",
            "exact_match,accuracy@token",
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
    import csv as csv_mod

    with csv_path.open() as fh:
        reader = csv_mod.DictReader(fh)
        row = next(reader)
    assert row["metric"] == data["metric"]
