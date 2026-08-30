"""
Test Codex Repro Manifest

Test module for codex repro manifest.
"""

import json
from pathlib import Path

import yaml

import tools.codex_repro_manifest as repro


def test_build_manifest_handles_missing_inputs(tmp_path: Path):
    repo_root = tmp_path
    env = tmp_path / "codex_env_snapshot.json"
    deps = tmp_path / "codex_dependency_report.json"
    gaps = tmp_path / "codex_gap_registry.yaml"
    exp = tmp_path / "codex_experiment_index.json"
    gate = tmp_path / "codex_local_gate_report.json"

    manifest = repro.build_manifest(
        repo_root=repo_root,
        env_snapshot_path=env,
        dep_report_path=deps,
        gap_registry_path=gaps,
        exp_index_path=exp,
        local_gate_path=gate,
    )
    assert "summary" in manifest, "Condition must be true"
    s = manifest["summary"]
    assert s["environment"]["available"] is False, "Condition must be true"
    assert s["dependencies"]["available"] is False, "Condition must be true"
    assert s["gaps"]["available"] is False, "Condition must be true"
    assert s["experiments"]["available"] is False, "Condition must be true"
    assert s["local_gate"]["available"] is False, "Condition must be true"


def test_build_manifest_with_minimal_inputs(tmp_path: Path):
    repo_root = tmp_path

    # Minimal env snapshot
    env = tmp_path / "codex_env_snapshot.json"
    env.write_text(
        json.dumps(
            {
                "python": {"version": "3.11.0"},
                "os": {"platform": "linux", "release": "5.x"},
                "env": {"CODEX_MODE": "test"},
            }
        ),
        encoding="utf-8",
    )

    # Minimal dependency report
    deps = tmp_path / "codex_dependency_report.json"
    deps.write_text(
        json.dumps(
            {
                "packages": [
                    {"name": "pytest", "version": "8.0.0", "kind": "direct"},
                    {"name": "yaml", "version": "6.0.0", "kind": "transitive"},
                ]
            }
        ),
        encoding="utf-8",
    )

    # Minimal gap registry
    gaps = tmp_path / "codex_gap_registry.yaml"
    gaps.write_text(
        yaml.safe_dump(
            {
                "gaps": [
                    {
                        "id": "GAP-0001",
                        "status": "open",
                        "risk_level": "high",
                    },
                    {
                        "id": "GAP-0002",
                        "status": "closed",
                        "risk_level": "low",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    # Minimal experiment index
    exp = tmp_path / "codex_experiment_index.json"
    exp.write_text(
        json.dumps(
            {
                "runs_dir": str(tmp_path / "runs"),
                "runs": [
                    {
                        "mode": "train",
                        "run_id": "train-run-1",
                        "config_path": "conf/train.yaml",
                    },
                    {
                        "mode": "eval",
                        "run_id": "eval-run-1",
                        "config_path": "conf/eval.yaml",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    # Minimal local gate report
    gate = tmp_path / "codex_local_gate_report.json"
    gate.write_text(
        json.dumps(
            {
                "overall_returncode": 1,
                "results": [
                    {"name": "pytest_tools", "returncode": 0},
                    {"name": "pytest_codex_ml", "returncode": 1},
                ],
            }
        ),
        encoding="utf-8",
    )

    manifest = repro.build_manifest(
        repo_root=repo_root,
        env_snapshot_path=env,
        dep_report_path=deps,
        gap_registry_path=gaps,
        exp_index_path=exp,
        local_gate_path=gate,
    )

    s = manifest["summary"]
    assert s["environment"]["available"] is True, "Condition must be true"
    assert s["environment"]["python_version"] == "3.11.0", "Condition must be true"
    assert "CODEX_MODE" in s["environment"]["codex_env_var_keys"], "Condition must be true"

    assert s["dependencies"]["available"] is True, "Condition must be true"
    assert s["dependencies"]["total_packages"] == 2, "Condition must be true"
    assert s["dependencies"]["direct_dependencies"] == 1, "Condition must be true"

    assert s["gaps"]["available"] is True, "Condition must be true"
    assert s["gaps"]["total_gaps"] == 2, "Condition must be true"
    assert s["gaps"]["by_status"]["open"] == 1, "Condition must be true"

    assert s["experiments"]["available"] is True, "Condition must be true"
    assert s["experiments"]["total_runs"] == 2, "Condition must be true"
    assert "conf/train.yaml" in s["experiments"]["unique_config_paths"], "Condition must be true"

    assert s["local_gate"]["available"] is True, "Condition must be true"
    assert s["local_gate"]["overall_returncode"] == 1, "Condition must be true"
    assert "pytest_codex_ml" in s["local_gate"]["failed_commands"], "Condition must be true"


def test_main_writes_files(tmp_path: Path, monkeypatch):
    repo_root = tmp_path
    json_out = tmp_path / "repro.json"
    md_out = tmp_path / "repro.md"

    # Patch cwd-style args by monkeypatching argv via direct call to main()
    rc = repro.main(
        [
            "--repo-root",
            str(repo_root),
            "--env-snapshot",
            str(tmp_path / "codex_env_snapshot.json"),
            "--dep-report",
            str(tmp_path / "codex_dependency_report.json"),
            "--gap-registry",
            str(tmp_path / "codex_gap_registry.yaml"),
            "--experiment-index",
            str(tmp_path / "codex_experiment_index.json"),
            "--local-gate",
            str(tmp_path / "codex_local_gate_report.json"),
            "--json-out",
            str(json_out),
            "--md-out",
            str(md_out),
        ]
    )
    assert rc == 0, "rc is not valid"
    assert json_out.exists(), "Condition must be true"
    assert md_out.exists(), "Condition must be true"

    data = json.loads(json_out.read_text(encoding="utf-8"))
    assert "summary" in data, "Data must not be empty"
