"""
Test Codex Env And Deps Tools

Test module for codex env and deps tools.
"""

import json
from pathlib import Path

import tools.codex_dependency_report as dep_report
import tools.codex_env_snapshot as env_snap
import tools.codex_mltest_runner as ml_runner


def test_env_snapshot_includes_environment_block(tmp_path: Path):
    out = tmp_path / "env.json"
    rc = env_snap.main(["--out", str(out)])
    assert rc == 0, "rc is not valid"
    data = json.loads(out.read_text(encoding="utf-8"))
    assert "environment" in data, "Data must not be empty"
    assert isinstance(data["environment"], dict)


def test_dependency_report_writes_packages(tmp_path: Path):
    out = tmp_path / "deps.json"
    rc = dep_report.main(["--out", str(out)])
    assert rc == 0, "rc is not valid"
    data = json.loads(out.read_text(encoding="utf-8"))
    assert "packages" in data, "Data must not be empty"
    assert isinstance(data["packages"], list)


def test_mltest_runner_executes_categories(tmp_path: Path):
    tests_dir = tmp_path / "tests" / "unit"
    tests_dir.mkdir(parents=True, exist_ok=True)
    (tests_dir / "test_sample.py").write_text(
        "def test_sample():\n    assert True\n", encoding="utf-8"
    )

    map_path = tmp_path / "codex_ml_test_map.yaml"
    map_path.write_text(
        json.dumps(
            {
                "categories": {
                    "unit": {
                        "description": "unit tests",
                        "tests": ["tests/unit/test_sample.py"],
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    summary_path = tmp_path / "summary.json"
    rc = ml_runner.main(
        [
            "--map",
            str(map_path),
            "--category",
            "unit",
            "--json-summary",
            str(summary_path),
            "--repo-root",
            str(tmp_path),
        ]
    )
    assert rc == 0, "rc is not valid"
    data = json.loads(summary_path.read_text(encoding="utf-8"))
    assert data["overall_returncode"] == 0, "Data must not be empty"
    assert data["results"][0]["category"] == "unit", "Result must not be empty"
