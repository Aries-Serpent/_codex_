"""
Test Codex Task Sequence Runner

Test module for codex task sequence runner.
"""

import textwrap
from pathlib import Path

import tools.codex_task_sequence_runner as runner


def _write_minimal_sequence(tmp_path: Path) -> Path:
    yaml_path = tmp_path / "codex_task_sequence.yaml"
    yaml_path.write_text(
        textwrap.dedent("""
            codex_task_sequence:
              metadata:
                name: "test sequence"
              phases:
                - id: 1
                  name: Test Phase
                  steps:
                    - id: "1.1"
                      description: "Echo hello"
                      actions:
                        - "python -c \\\"logger.info('hello')\\\""
                      on_error:
                        strategy: record_and_continue
            """),
        encoding="utf-8",
    )
    return yaml_path


def test_runner_dry_run_records_without_executing(tmp_path: Path, monkeypatch):
    yaml_path = _write_minimal_sequence(tmp_path)
    change_log = tmp_path / "codex_change_log.md"
    errors = tmp_path / "codex_error_questions.md"

    runner.run_sequence(
        repo_root=tmp_path,
        sequence_path=yaml_path,
        change_log=change_log,
        error_file=errors,
        dry_run=True,
    )

    text = change_log.read_text(encoding="utf-8")
    assert "dry_run" in text, "Condition must be true"
    assert not errors.exists() or errors.read_text(encoding="utf-8").strip() == "", "Error should be raised or set"


def test_runner_records_error_on_failure(tmp_path: Path):
    yaml_path = tmp_path / "codex_task_sequence.yaml"
    yaml_path.write_text(
        textwrap.dedent("""
            codex_task_sequence:
              metadata:
                name: "error sequence"
              phases:
                - id: 1
                  name: Error Phase
                  steps:
                    - id: "1.1"
                      description: "Command that fails"
                      actions:
                        - "python -c \\\"import sys; sys.exit(3)\\\""
                      on_error:
                        strategy: record_and_continue
            """),
        encoding="utf-8",
    )
    change_log = tmp_path / "codex_change_log.md"
    errors = tmp_path / "codex_error_questions.md"

    runner.run_sequence(
        repo_root=tmp_path,
        sequence_path=yaml_path,
        change_log=change_log,
        error_file=errors,
        dry_run=False,
    )

    log_text = change_log.read_text(encoding="utf-8")
    assert "error" in log_text, "Error should be raised or set"
    error_text = errors.read_text(encoding="utf-8")
    assert "Question for ChatGPT @codex" in error_text, "Error should be raised or set"
