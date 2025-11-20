"""
Unit tests for overrides merging and missing-detector strict gate.
Verifies capability override merging with aliases, and SystemExit on strict missing detector.
"""
import json
from pathlib import Path
import pytest

from scripts.space_traversal import audit_runner as runner

# Helper for manual sample capability instance
def sample_cap(cap_id, evidence, patterns):
    return {
        "id": cap_id,
        "evidence_files": evidence,
        "found_patterns": patterns,
        "required_patterns": patterns,
        "meta": {},
    }

def test_apply_overrides_merges_aliases():
    # The lower-level test for just apply_overrides logic
    capabilities = [
        sample_cap("train_loop", ["src/train.py"], ["train", "loop"]),
        sample_cap("training-engine", ["README.md"], ["train"]),
    ]
    overrides = {"training-engine": ["train_loop"]}

    merged, missing = runner.apply_overrides(capabilities, overrides, False)

    assert missing == []
    assert len(merged) == 1
    entry = merged[0]
    assert entry["id"] == "training-engine"
    assert sorted(entry["evidence_files"]) == ["README.md", "src/train.py"]
    assert set(entry["found_patterns"]) == {"train", "loop"}
    assert "override_aliases" in entry["meta"]

def test_apply_overrides_missing_alias_strict_exit():
    # The stricter test: should fail if missing alias in strict mode
    capabilities = [sample_cap("training-engine", ["README.md"], ["train"])]
    overrides = {"training-engine": ["train_loop"]}

    with pytest.raises(SystemExit) as excinfo:
        runner.apply_overrides(capabilities, overrides, True)
    assert excinfo.value.code == 5

# Higher-level integration: test with full stage logic (file and config paths)
def make_cfg(tmp_path):
    # Produces a config dict suitable for runner.stage_s3_capabilities etc.
    return {
        "output": {
            "artifacts_dir": str(tmp_path),
            "reports_dir": str(tmp_path / "reports"),
            "matrix_template": "templates/audit/capability_matrix.md.j2"
        },
        "weights": {
            "functionality": 0.25,
            "consistency": 0.2,
            "tests": 0.25,
            "safeguards": 0.15,
            "documentation": 0.15
        },
        "capability_map": {
            "dynamic": False,
            "overrides": {"merged-cap": ["alias-a"]}
        },
        "options": {
            "fail_on_missing_detector": False
        },
        "scoring": {
            "thresholds": {"low": 0.7, "medium": 0.85}
        },
        "metrics_schema_version": "2.0.0"
    }

def test_overrides_merging(tmp_path):
    facets = {
        "generated": 0,
        "facets": {"train": ["src/train/foo.py"], "checkpoint": ["src/ckpt/a.py"]},
        "version": "1"
    }
    cfg = make_cfg(tmp_path)
    idx = {"generated": 0, "count": 0, "files": []}
    Path(cfg["output"]["artifacts_dir"]).mkdir(parents=True, exist_ok=True)
    (Path(cfg["output"]["artifacts_dir"]) / "context_index.json").write_text(json.dumps(idx))
    caps_blob = runner.stage_s3_capabilities(cfg, facets)
    ids = [c["id"] for c in caps_blob["capabilities"]]
    assert "merged-cap" in ids

def test_missing_detector_strict_fails(tmp_path):
    cfg = make_cfg(tmp_path)
    cfg["options"]["fail_on_missing_detector"] = True
    cfg["capability_map"]["overrides"] = {"canonical": ["nonexistent-alias"]}
    facets = {"generated": 0, "facets": {}, "version": "1"}
    with pytest.raises(SystemExit) as exc:
        runner.stage_s3_capabilities(cfg, facets)
    assert exc.value.code == 5

# If __all__ is required by your codebase conventions:
# __all__ = [
#     "test_apply_overrides_merges_aliases",
#     "test_apply_overrides_missing_alias_strict_exit",
#     "test_overrides_merging",
#     "test_missing_detector_strict_fails",
# ]
