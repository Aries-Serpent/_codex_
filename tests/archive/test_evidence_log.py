from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Any

from click.testing import CliRunner


def _reload_archive_cli() -> Any:
    for name in ("codex.cli_archive", "codex.archive.api"):
        if name in sys.modules:
            sys.modules.pop(name)
    return importlib.import_module("codex.cli_archive")


def test_append_evidence_preserves_existing_lines(tmp_path: Path, monkeypatch) -> None:
    evidence_dir = tmp_path / ".codex" / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("CODEX_EVIDENCE_DIR", evidence_dir.as_posix())
    monkeypatch.chdir(tmp_path)

    log_file = evidence_dir / "archive_ops.jsonl"
    seed_lines = [
        '{"action":"BASE","note":"alpha"}',
        '{"action":"BASE","note":"beta"}',
    ]
    seed_text = "\n".join(seed_lines) + "\n"
    log_file.write_text(seed_text, encoding="utf-8")

    from codex.archive.util import append_evidence

    append_evidence({"action": "FIRST_APPEND", "detail": "one"})
    append_evidence({"action": "SECOND_APPEND", "detail": "two"})

    after_manual_appends = log_file.read_text(encoding="utf-8")
    assert after_manual_appends.startswith(seed_text)
    assert after_manual_appends[: len(seed_text)] == seed_text

    runner = CliRunner()
    cli_archive = _reload_archive_cli()

    workspace = tmp_path / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / "legacy.txt").write_text("LEGACY CONTENT\n", encoding="utf-8")
    plan_path = tmp_path / "artifacts" / "plan.json"
    plan_path.parent.mkdir(parents=True, exist_ok=True)

    result = runner.invoke(
        cli_archive.app,
        [
            "plan",
            "--root",
            workspace.as_posix(),
            "--age",
            "0",
            "--out",
            plan_path.as_posix(),
        ],
    )
    assert result.exit_code == 0, result.output

    final_text = log_file.read_text(encoding="utf-8")
    assert final_text.startswith(seed_text)
    assert final_text[: len(seed_text)] == seed_text

    parsed_actions = [json.loads(line)["action"] for line in final_text.strip().splitlines()]
    assert parsed_actions[: len(seed_lines)] == [json.loads(line)["action"] for line in seed_lines]
    assert parsed_actions[len(seed_lines) : len(seed_lines) + 2] == [
        "FIRST_APPEND",
        "SECOND_APPEND",
    ]
    assert parsed_actions[-1] == "PLAN_GENERATED"
