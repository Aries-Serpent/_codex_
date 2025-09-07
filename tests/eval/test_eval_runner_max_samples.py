import json
from pathlib import Path

from codex_ml.eval.eval_runner import evaluate_datasets


def test_evaluate_datasets_max_samples(tmp_path: Path):
    evaluate_datasets(["toy_copy_task"], ["exact_match"], tmp_path, max_samples=1)
    ndjson_path = tmp_path / "metrics.ndjson"
    record = json.loads(ndjson_path.read_text().strip().splitlines()[0])
    assert record["n"] == 1
