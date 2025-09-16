from __future__ import annotations

import json

import pytest

pytest.importorskip("omegaconf")

from codex_ml.utils.provenance import export_environment, load_environment_summary


def test_export_environment_creates_artifacts(tmp_path) -> None:
    out_dir = tmp_path / "env"

    summary = export_environment(
        out_dir,
        seed=123,
        command="unit-test",
        extras={"context": "pytest"},
    )

    # Files are written for downstream tooling.
    env_json = out_dir / "environment.json"
    freeze_txt = out_dir / "pip-freeze.txt"
    ndjson = out_dir / "environment.ndjson"

    assert env_json.exists()
    assert freeze_txt.exists()
    assert ndjson.exists()

    # Concise summary is returned and persisted as NDJSON.
    assert summary["seed"] == 123
    assert summary["command"] == "unit-test"
    loaded = load_environment_summary(out_dir)
    assert loaded == summary

    details = json.loads(env_json.read_text())
    assert "pip_freeze" in details
    assert isinstance(details["pip_freeze"], list)
    assert summary["pip_freeze_count"] == len(details["pip_freeze"])
