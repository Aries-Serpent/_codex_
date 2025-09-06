import csv
import json

from codex_ml.eval.eval_runner import evaluate_datasets


def test_schema_round_trip(tmp_path):
    out = tmp_path
    evaluate_datasets(["toy_copy_task"], ["exact_match"], out)
    ndjson_path = out / "metrics.ndjson"
    csv_path = out / "metrics.csv"

    record = json.loads(ndjson_path.read_text().splitlines()[0])
    required = {"run_id", "dataset", "split", "step", "metric", "value", "n", "timestamp"}
    assert required.issubset(record)
    assert record["value"] == 1.0

    with csv_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    assert float(rows[0]["value"]) == 1.0
    assert rows[0]["metric"] == "exact_match"
