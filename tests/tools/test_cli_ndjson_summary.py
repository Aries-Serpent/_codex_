"""Smoke tests for the ``codex_ml ndjson-summary`` CLI entrypoint."""

from __future__ import annotations

import json
import os
import subprocess as sp
import sys
from pathlib import Path


def _write_ndjson(path: Path, payloads: list[dict]) -> None:
    text = "\n".join(json.dumps(obj) for obj in payloads) + "\n"
    path.write_text(text, encoding="utf-8")


def test_package_cli_summarizes_metrics(tmp_path: Path) -> None:
    metrics = [
        {"key": "loss", "value": 2.0},
        {"key": "loss", "value": 1.0},
        {"key": "acc", "value": 0.5},
    ]
    target = tmp_path / "metrics.ndjson"
    _write_ndjson(target, metrics)

    env = os.environ.copy()
    src_root = Path(__file__).resolve().parents[2] / "src"
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = f"{src_root}{os.pathsep}{existing}" if existing else str(src_root)

    result = sp.run(
        [
            sys.executable,
            "-m",
            "codex_ml",
            "ndjson-summary",
            "--input",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["rows"] == len(metrics)
    assert payload["metrics"]["loss"]["min"] == 1.0
    assert payload["metrics"]["loss"]["max"] == 2.0
    assert payload["metrics"]["loss"]["count"] == 2
