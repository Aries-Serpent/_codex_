import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


def _write_jsonl(path: Path) -> None:
    records = [
        {"text": "alpha beta", "target": "alpha"},
        {"input": "gamma", "target": "gamma"},
    ]
    path.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")


@pytest.mark.slow
def test_evaluate_cli_runs(tmp_path):
    data_path = tmp_path / "data.jsonl"
    _write_jsonl(data_path)
    output_dir = tmp_path / "eval"
    vocab_path = tmp_path / "vocab.json"
    vocab_path.write_text(
        json.dumps({"<unk>": 0, "alpha": 1, "beta": 2, "gamma": 3}), encoding="utf-8"
    )
    env = os.environ.copy()
    cmd = [
        sys.executable,
        "-m",
        "codex_ml.cli.evaluate",
        f"dataset.path={data_path}",
        f"output_dir={output_dir}",
        "dataset.loader=jsonl",
        "tokenizer.name=tiny-vocab",
        f"tokenizer.cfg.path={vocab_path}",
        "metrics=[accuracy]",
        "limit=2",
    ]
    subprocess.run(cmd, check=True, cwd=tmp_path, env=env)
    outputs_dir = Path(tmp_path) / "outputs"
    ndjson_files = list(outputs_dir.glob("**/predictions.ndjson"))
    assert ndjson_files
    summary = json.loads((ndjson_files[0].parent / "summary.json").read_text(encoding="utf-8"))
    assert "metrics" in summary
