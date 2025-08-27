import json
from pathlib import Path

from analysis.audit_pipeline import step_static_code_analysis


def test_static_code_analysis_logs(tmp_path: Path) -> None:
    metrics = tmp_path / "m.jsonl"
    repo_root = Path(__file__).resolve().parents[1]
    step_static_code_analysis(repo_root, metrics)
    data = metrics.read_text().strip().splitlines()
    assert data
    record = json.loads(data[-1])
    assert record["name"] == "static.analysis.errors"
    assert isinstance(record["value"], int)
    assert record["value"] >= 0
