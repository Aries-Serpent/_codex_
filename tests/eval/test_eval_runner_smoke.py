import json

from codex_ml.eval.eval_runner import evaluate_datasets


def test_eval_runner_smoke(tmp_path):
    out = tmp_path
    evaluate_datasets(["toy_copy_task"], ["exact_match"], out)
    nd = out / "metrics.ndjson"
    csv = out / "metrics.csv"
    assert nd.exists()
    assert csv.exists()
    rec = json.loads(nd.read_text().strip().splitlines()[0])
    assert rec["dataset"] == "toy_copy_task"
    assert rec["metric"] == "exact_match"
