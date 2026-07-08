"""
Unit tests for overrides merging and missing-detector strict gate
"""

import json
from pathlib import Path

import pytest

from scripts.space_traversal import audit_runner as runner


def make_cfg(tmp_path):
    return {
        "output": {"artifacts_dir": str(tmp_path)},
        "weights": {
            "functionality": 0.25,
            "consistency": 0.2,
            "tests": 0.25,
            "safeguards": 0.15,
            "documentation": 0.15,
        },
        "capability_map": {"dynamic": False, "overrides": {"merged-cap": ["alias-a"]}},
        "options": {"fail_on_missing_detector": False},
        "scoring": {"thresholds": {"low": 0.7, "medium": 0.85}},
        "matrix_template": "templates/audit/capability_matrix.md.j2",
        "metrics_schema_version": "2.0.0",
    }


def test_overrides_merging(tmp_path):
    facets = {
        "generated": 0,
        "facets": {"train": ["src/train/foo.py"], "checkpoint": ["src/ckpt/a.py"]},
        "version": "1",
    }
    cfg = make_cfg(tmp_path)
    idx = {"generated": 0, "count": 0, "files": []}
    Path(cfg["output"]["artifacts_dir"]).mkdir(parents=True, exist_ok=True)
    (Path(cfg["output"]["artifacts_dir"]) / "context_index.json").write_text(json.dumps(idx))
    caps = runner.stage_s3_capabilities(cfg, facets)
    ids = [c["id"] for c in caps]
    assert "merged-cap" in ids, "Condition must be true"


def test_missing_detector_strict_fails(tmp_path):
    cfg = make_cfg(tmp_path)
    cfg["options"]["fail_on_missing_detector"] = True
    cfg["capability_map"]["overrides"] = {"canonical": ["nonexistent-alias"]}
    facets = {"generated": 0, "facets": {}}
    with pytest.raises(SystemExit) as exc:
        runner.stage_s3_capabilities(cfg, facets)
    assert exc.value.code == 5, "Value must be initialized"
