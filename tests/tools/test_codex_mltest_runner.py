from pathlib import Path
import json

import yaml

import tools.codex_mltest_runner as runner


def test_mltest_runner_builds_summary(tmp_path: Path, monkeypatch):
    # Fake repo with a single trivial test file
    tests_dir = tmp_path / "tests" / "tools"
    tests_dir.mkdir(parents=True, exist_ok=True)
    (tests_dir / "test_dummy.py").write_text(
        "def test_dummy():\n    assert True\n", encoding="utf-8"
    )

    # Map that points to that test
    mlmap = {
        "tests": [
            {
                "id": "infra-tools-basic",
                "category": "infrastructure",
                "description": "dummy",
                "pytest_target": "tests/tools",
            }
        ]
    }
    (tmp_path / "codex_ml_test_map.yaml").write_text(yaml.safe_dump(mlmap), encoding="utf-8")

    rc = runner.main(
        [
            "--repo-root",
            str(tmp_path),
            "--category",
            "infrastructure",
            "--map",
            "codex_ml_test_map.yaml",
            "--json-summary",
            "summary.json",
        ]
    )
    assert rc == 0

    summary = json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
    assert summary["overall_returncode"] == 0
    assert len(summary["results"]) == 1
    assert summary["results"][0]["category"] == "infrastructure"
