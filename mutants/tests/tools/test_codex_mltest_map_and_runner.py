"""
Test Codex Mltest Map And Runner

Test module for codex mltest map and runner.
"""

from pathlib import Path

import yaml

import tools.codex_mltest_map_validate as mv
import tools.codex_mltest_runner as mr


def test_ml_test_map_validator_accepts_valid_file(tmp_path: Path):
    path = tmp_path / "codex_ml_test_map.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "categories": {
                    "data": {
                        "description": "Data tests",
                        "tests": ["tests/codex_ml/test_dataloader_determinism.py"],
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    data = mv.load_ml_test_map(path)
    mv.validate_structure(data)  # should not raise


def test_collect_tests_merges_categories(tmp_path: Path):
    cats = {
        "data": {
            "description": "Data tests",
            "tests": ["tests/data_a.py", "tests/data_b.py"],
        },
        "model": {
            "description": "Model tests",
            "tests": ["tests/model_a.py", "tests/data_b.py"],
        },
    }

    tests = mr._collect_tests(cats, ["data", "model"])
    assert tests == ["tests/data_a.py", "tests/data_b.py", "tests/model_a.py"]


def test_mltest_runner_invokes_pytest(monkeypatch, tmp_path: Path):
    mlmap = tmp_path / "codex_ml_test_map.yaml"
    mlmap.write_text(
        yaml.safe_dump(
            {
                "categories": {
                    "infra": {
                        "description": "Infra tests",
                        "tests": ["tests/some_test.py"],
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    called = {}

    def fake_run(cmd, check=False):  # type: ignore[override]
        called["cmd"] = cmd

        class R:
            returncode = 0

        return R()

    monkeypatch.setattr(mr.subprocess, "run", fake_run)

    rc = mr.main(
        [
            "--map",
            str(mlmap),
            "--category",
            "infra",
            "--json-summary",
            str(tmp_path / "summary.json"),
        ]
    )

    assert rc == 0, "rc is not valid"
    assert "cmd" in called, "Condition must be true"
    assert called["cmd"][0] == "pytest", "Condition must be true"
    assert "tests/some_test.py" in called["cmd"], "Condition must be true"
    summary_path = tmp_path / "summary.json"
    assert summary_path.exists(), "Condition must be true"
    text = summary_path.read_text(encoding="utf-8")
    assert "infra" in text, "Condition must be true"
