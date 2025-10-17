from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from importlib import import_module, reload
from pathlib import Path
from types import SimpleNamespace

from click.testing import CliRunner


def _reload_archive_modules() -> None:
    for name in [
        "codex.archive.api",
        "codex.cli_archive",
    ]:
        if name in sys.modules:
            sys.modules.pop(name)
    reload(import_module("codex.archive.dal"))


def test_archive_hygiene(tmp_path: Path, monkeypatch, capsys) -> None:
    root = tmp_path
    source_dir = root / "src" / "demo"
    source_dir.mkdir(parents=True, exist_ok=True)
    target_file = source_dir / "legacy_module.py"
    target_file.write_text(
        (
            '"""DEPRECATED module slated for archival."""\n\n'
            "def legacy_feature():\n"
            "    return 'legacy-value'\n"
        ),
        encoding="utf-8",
    )
    old_time = datetime.now(timezone.utc) - timedelta(days=365)
    os.utime(target_file, (old_time.timestamp(), old_time.timestamp()))

    changelog = root / "CHANGELOG.md"
    changelog.write_text("# Changelog\n\n## Unreleased\n", encoding="utf-8")

    evidence_dir = root / ".codex" / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("CODEX_ARCHIVE_BACKEND", "sqlite")
    monkeypatch.setenv(
        "CODEX_ARCHIVE_URL",
        f"sqlite:///{(root / '.codex' / 'archive.sqlite').as_posix()}",
    )
    monkeypatch.setenv("CODEX_EVIDENCE_DIR", evidence_dir.as_posix())
    monkeypatch.chdir(root)

    _reload_archive_modules()

    cli_archive = import_module("codex.cli_archive")
    runner = CliRunner()

    plan_path = root / "artifacts" / "archive_plan.json"
    res_plan = runner.invoke(
        cli_archive.app,
        [
            "plan",
            "--root",
            ".",
            "--age",
            "0",
            "--out",
            plan_path.as_posix(),
        ],
    )
    assert res_plan.exit_code == 0, res_plan.output
    assert plan_path.exists()
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    assert plan["entries"], "expected plan entries"
    target_rel = target_file.relative_to(root).as_posix()
    planned_paths = {entry["path"] for entry in plan["entries"]}
    assert target_rel in planned_paths

    evidence_path = evidence_dir / "archive_ops.jsonl"
    assert evidence_path.exists()
    lines_after_plan = evidence_path.read_text(encoding="utf-8").strip().splitlines()
    assert any(
        json.loads(line).get("action") == "PLAN_GENERATED"
        and json.loads(line).get("plan") == plan_path.as_posix()
        for line in lines_after_plan
    )

    res_apply = runner.invoke(
        cli_archive.app,
        [
            "apply-plan",
            plan_path.as_posix(),
            "--repo",
            "demo-repo",
            "--by",
            "tester",
        ],
    )
    assert res_apply.exit_code == 0, res_apply.output
    apply_payload = json.loads(res_apply.stdout)
    assert any(
        item["path"] in {target_file.as_posix(), target_rel} for item in apply_payload["applied"]
    )

    lines_after_apply = evidence_path.read_text(encoding="utf-8").strip().splitlines()
    actions_after_apply = [json.loads(line).get("action") for line in lines_after_apply]
    assert {"PLAN_APPLY", "ARCHIVE"}.issubset(set(actions_after_apply))

    res_summary = runner.invoke(cli_archive.app, ["summarize"])
    assert res_summary.exit_code == 0, res_summary.output
    summary_payload = json.loads(res_summary.stdout)
    assert summary_payload["count"] >= 1
    assert summary_payload["total_bytes"] >= len("return 'legacy-value'\n")

    lines_after_summary = evidence_path.read_text(encoding="utf-8").strip().splitlines()
    assert any(json.loads(line).get("action") == "SUMMARY" for line in lines_after_summary)

    changelog_update = (
        f"- Archived {summary_payload['count']} items totaling "
        f"{summary_payload['total_bytes']} bytes."
    )
    changelog.write_text(
        changelog.read_text(encoding="utf-8") + "\n" + changelog_update + "\n",
        encoding="utf-8",
    )
    assert changelog_update in changelog.read_text(encoding="utf-8")

    before_vacuum = evidence_path.read_text(encoding="utf-8")
    vacuum_args = SimpleNamespace(
        tombstones_code=evidence_path.as_posix(),
        tombstones_logs=(root / "logs_tombstones.jsonl").as_posix(),
        before=None,
        summary=True,
        dry_run=False,
        gzip_tombstones=False,
        verbose=0,
        logfile=(root / "archive_manager.log").as_posix(),
    )
    from tools.archive_manager.archive_manager import cmd_vacuum

    cmd_vacuum(vacuum_args)
    vacuum_output = capsys.readouterr().out
    summary_block = json.loads(vacuum_output)
    assert summary_block["summary"]["total"] == len(lines_after_summary)
    assert summary_block["summary"]["unique_paths"] >= 1
    assert evidence_path.read_text(encoding="utf-8") == before_vacuum
