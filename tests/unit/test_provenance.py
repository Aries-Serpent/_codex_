from __future__ import annotations

import json
from pathlib import Path

import pytest

import yaml
from common.provenance import collect_dvc_stage, write_provenance
from omegaconf import OmegaConf


def test_collect_dvc_stage_parses_lock_structure():
    lock = {
        "stages": {
            "prepare": {
                "outs": [
                    {"path": "data/processed/prepared", "md5": "abc", "size": 123},
                ],
                "deps": [
                    {"path": "data/raw/input.csv", "md5": "def"},
                ],
                "params": {"params.yaml": {"prepare": {"seed": 42}}},
            }
        }
    }

    stage = collect_dvc_stage(lock, stage="prepare")

    assert stage is not None
    assert stage.stage == "prepare"
    assert stage.outs["data/processed/prepared"]["md5"] == "abc"
    assert stage.deps["data/raw/input.csv"]["md5"] == "def"
    assert stage.params["prepare"]["seed"] == 42


def test_write_provenance_includes_dvc_metadata(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    lock = {
        "stages": {
            "prepare": {
                "outs": [
                    {"path": "data/processed/prepared", "md5": "abc123", "hash": "sha256:zzz"},
                ],
                "deps": [
                    {"path": "data/raw/input.csv", "md5": "def456"},
                ],
                "params": {"params.yaml": {"prepare": {"split": 0.2}}},
            }
        }
    }

    (tmp_path / "dvc.lock").write_text(yaml.safe_dump(lock))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GIT_COMMIT", "deadbeef")

    cfg = OmegaConf.create({"data": {"path": "data/raw/input.csv"}})

    provenance_path = write_provenance(cfg, stage="prepare")

    assert provenance_path.exists()

    payload = json.loads(provenance_path.read_text())
    assert payload["git_commit"] == "deadbeef"
    assert payload["dvc"]["outs"]["data/processed/prepared"]["md5"] == "abc123"
    assert payload["dvc"]["deps"]["data/raw/input.csv"]["md5"] == "def456"
    assert payload["config_fingerprint_sha256"]
