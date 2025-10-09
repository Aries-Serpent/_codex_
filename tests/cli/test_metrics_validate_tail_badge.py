from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("jsonschema")

from codex_ml.cli import metrics_cli


def _write_ndjson(path: Path, rows: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def test_validate_ok(tmp_path: Path) -> None:
    data = tmp_path / "metrics.ndjson"
    schema = Path("schemas/metrics.ndjson.schema.json").resolve()
    _write_ndjson(data, [{"epoch": 0, "loss": 2.0}, {"epoch": 1, "val_loss": 1.5}])
    code = metrics_cli.main(["validate", "--input", str(data), "--schema", str(schema)])
    assert code == 0


def test_tail_and_badge(tmp_path: Path) -> None:
    data = tmp_path / "metrics.ndjson"
    readme = tmp_path / "README.md"
    rows = [{"epoch": i, "val_loss": 1.0 / (i + 1)} for i in range(5)]
    _write_ndjson(data, rows)

    code = metrics_cli.main(["tail", "--input", str(data), "--n", "2"])
    assert code == 0

    code = metrics_cli.main(
        [
            "badge",
            "--input",
            str(data),
            "--readme",
            str(readme),
            "--metric",
            "val_loss",
            "--label",
            "val_loss",
            "--precision",
            "3",
        ]
    )
    assert code == 0

    content = readme.read_text(encoding="utf-8")
    assert "codex:metric-badge:start" in content
    assert "codex:metric-badge:end" in content
    assert "![val_loss]" in content
