from pathlib import Path

from codex_ml.cli import codex_env


def test_codex_env_health_invokes_env_check(monkeypatch, tmp_path: Path):
    calls = []

    def fake_run(cmd, cwd):
        calls.append((cmd, cwd))
        return 0

    monkeypatch.setattr(codex_env, "_run", fake_run)

    rc = codex_env.main(["--repo-root", str(tmp_path), "health"])
    assert rc == 0
    assert len(calls) == 1
    cmd, cwd = calls[0]
    assert "codex_ml.cli.env_check" in cmd
    assert cwd == tmp_path


def test_codex_env_task_sequence_invokes_runner(monkeypatch, tmp_path: Path):
    calls = []

    def fake_run(cmd, cwd):
        calls.append((cmd, cwd))
        return 0

    monkeypatch.setattr(codex_env, "_run", fake_run)

    rc = codex_env.main(
        [
            "--repo-root",
            str(tmp_path),
            "task-sequence",
            "--yaml",
            "custom_seq.yaml",
            "--change-log",
            "custom_log.md",
            "--errors",
            "custom_errors.md",
        ]
    )
    assert rc == 0
    assert len(calls) == 1
    cmd, cwd = calls[0]
    assert "codex_task_sequence_runner.py" in cmd
    assert "custom_seq.yaml" in cmd
    assert "custom_log.md" in cmd
    assert "custom_errors.md" in cmd
    assert cwd == tmp_path


def test_codex_env_mltests_invokes_mltest_runner(monkeypatch, tmp_path: Path):
    calls = []

    def fake_run(cmd, cwd):
        calls.append((cmd, cwd))
        return 0

    monkeypatch.setattr(codex_env, "_run", fake_run)

    rc = codex_env.main(
        [
            "--repo-root",
            str(tmp_path),
            "mltests",
            "--category",
            "infrastructure",
            "--category",
            "data",
            "--json-summary",
            "summary.json",
        ]
    )
    assert rc == 0
    assert len(calls) == 1
    cmd, cwd = calls[0]
    assert "codex_mltest_runner.py" in cmd
    assert "--category infrastructure" in cmd
    assert "--category data" in cmd
    assert "summary.json" in cmd
    assert cwd == tmp_path


def test_codex_env_bundle_invokes_reproducibility_bundle(monkeypatch, tmp_path: Path):
    calls = []

    def fake_run(cmd, cwd):
        calls.append((cmd, cwd))
        return 0

    monkeypatch.setattr(codex_env, "_run", fake_run)

    rc = codex_env.main(
        [
            "--repo-root",
            str(tmp_path),
            "bundle",
            "--audit",
            "_codex_status_update-2025-11-27.md",
            "--manifest-out",
            "bundle.json",
        ]
    )
    assert rc == 0
    assert len(calls) == 1
    cmd, cwd = calls[0]
    assert "codex_reproducibility_bundle.py" in cmd
    assert "_codex_status_update-2025-11-27.md" in cmd
    assert "bundle.json" in cmd
    assert cwd == tmp_path
