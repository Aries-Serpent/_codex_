from __future__ import annotations

import hashlib
import json

import pytest

from codex_ml.utils import provenance

pytest.importorskip("omegaconf")


def test_export_environment_creates_artifacts(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    hardware = {
        "cpu": {"brand": "UnitTest CPU", "logical_cores": 4},
        "gpu": {"devices": [{"name": "Mock GPU", "memory_total": "8 GiB"}]},
    }

    def _fake_environment_summary() -> dict[str, object]:
        return {
            "python": "3.12.0",
            "platform": "UnitTestOS",
            "processor": "UnitTest CPU",
            "pip_freeze": ["pkg==1.0"],
            "hardware": hardware,
            "gpus": ["Mock GPU"],
            "cuda_version": "12.1",
            "git_commit": "deadbeef",
        }

    monkeypatch.setattr(provenance, "environment_summary", _fake_environment_summary, raising=True)

    out_dir = tmp_path / "env"

    summary = provenance.export_environment(
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
    expected_serialized = json.dumps(hardware, sort_keys=True, default=repr, separators=(",", ":"))
    expected_fingerprint = hashlib.sha256(expected_serialized.encode("utf-8")).hexdigest()
    assert summary["hardware_fingerprint"] == expected_fingerprint

    loaded = provenance.load_environment_summary(out_dir)
    assert loaded == summary

    details = json.loads(env_json.read_text())
    assert "pip_freeze" in details
    assert isinstance(details["pip_freeze"], list)
    assert summary["pip_freeze_count"] == len(details["pip_freeze"])
    assert details.get("hardware") == hardware
