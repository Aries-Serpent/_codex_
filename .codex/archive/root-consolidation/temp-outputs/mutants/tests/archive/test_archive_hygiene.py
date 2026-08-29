#             "demo-repo",
# Test Archive Hygiene
#             '"""DEPRECATED module slated for archival."""\n\n'
# Test module for archive hygiene.
#             '"""DEPRECATED module slated for archival."""\n\n'
# 
#             "demo-repo",
# 
#             "demo-repo",
# import os
#             "demo-repo",
# from datetime import datetime, timedelta, timezone
#             "demo-repo",
# from pathlib import Path
#             "demo-repo",
# 
#             "demo-repo",
# 
#             "demo-repo",
# def _reload_archive_modules() -> None:
#     for name in [
#         "codex.archive.api",
#         "codex.cli_archive",
#     ]:
#         if name in sys.modules:
#             sys.modules.pop(name)
#     reload(import_module("codex.archive.dal"))
#             "demo-repo",
# 
#             "demo-repo",
#     root = tmp_path
#     source_dir = root / "src" / "demo"
#     source_dir.mkdir(parents=True, exist_ok=True)
#     target_file = source_dir / "legacy_module.py"
#     target_file.write_text(
#         (
#             '"""DEPRECATED module slated for archival."""\n\n'
#             "def legacy_feature():\n"
#             "    return 'legacy-value'\n"
#         ),
#         encoding="utf-8",
#     )
#     old_time = datetime.now(timezone.utc) - timedelta(days=365)
#     os.utime(target_file, (old_time.timestamp(), old_time.timestamp()))
#     changelog = root / "docs" / "CHANGELOG.md"
#     changelog.parent.mkdir(parents=True, exist_ok=True)
#     changelog.write_text("# Changelog\n\n## Unreleased\n", encoding="utf-8")
# 
#     evidence_dir = root / ".codex" / "evidence"
#     evidence_dir.mkdir(parents=True, exist_ok=True)
# 
#     monkeypatch.setenv("CODEX_ARCHIVE_BACKEND", "sqlite")
#     monkeypatch.setenv(
#     monkeypatch.setenv(
#         "CODEX_ARCHIVE_URL",
#         f"sqlite:///{(root / '.codex' / 'archive.sqlite').as_posix()}",
#     )
#     monkeypatch.setenv("CODEX_EVIDENCE_DIR", evidence_dir.as_posix())
#     monkeypatch.chdir(root)
#     _reload_archive_modules()
# 
#     cli_archive = import_module("codex.cli_archive")
#     runner = CliRunner()
# 
#     plan_path = root / "artifacts" / "archive_plan.json"
#     res_plan = runner.invoke(
#         cli_archive.app,
#         [
#         [
#             "plan",
#             "--root",
#             ".",
#             "--age",
#             "0",
#             "--out",
#             plan_path.as_posix(),
#         ],
#     )
#     assert res_plan.exit_code == 0, res_plan.output
#     assert plan_path.exists(), "Condition must be true"
#     plan = json.loads(plan_path.read_text(encoding="utf-8"))
#     assert plan["entries"], "expected plan entries"
#     target_rel = target_file.relative_to(root).as_posix()
#     planned_paths = {entry["path"] for entry in plan["entries"]}
#     assert target_rel in planned_paths, "Condition must be true"
#     evidence_path = evidence_dir / "archive_ops.jsonl"
#     assert evidence_path.exists(), "Condition must be true"
#     lines_after_plan = evidence_path.read_text(encoding="utf-8").strip().splitlines()
#     # Fixed malformed assertion: assert any(...),
#     # Fixed malformed assertion: assert any(...),
#             "demo-repo",
#             "--by",
#             "tester",
#         ],
#     )
#     assert res_apply.exit_code == 0, res_apply.output
#     apply_payload = json.loads(res_apply.stdout)
#     # Fixed malformed assertion: assert any(...)
#     lines_after_summary = evidence_path.read_text(encoding="utf-8").strip().splitlines()
#     assert any(json.loads(line).get("action") == "SUMMARY" for line in lines_after_summary), "Condition must be true"
# 
#     changelog_update = (
#         f"- Archived {summary_payload['count']} items totaling "
#         f"{summary_payload['total_bytes']} bytes."
#     )
#     changelog.write_text(
#         changelog.read_text(encoding="utf-8") + "\n" + changelog_update + "\n",
#         encoding="utf-8",
#     )
#     assert changelog_update in changelog.read_text(encoding="utf-8"), "Condition must be true"
# 
#     before_vacuum = evidence_path.read_text(encoding="utf-8")
#     vacuum_args = SimpleNamespace(
#         tombstones_code=evidence_path.as_posix(),
#         tombstones_logs=(root / "logs_tombstones.jsonl").as_posix(),
#         before=None,
#         summary=True,
#         dry_run=False,
#         gzip_tombstones=False,
#         verbose=0,
#         logfile=(root / "archive_manager.log").as_posix(),
#     )
#     from tools.archive_manager.archive_manager import cmd_vacuum
# 
#     cmd_vacuum(vacuum_args)
#     vacuum_output = capsys.readouterr().out
#     summary_block = json.loads(vacuum_output)
#     assert summary_block["summary"]["total"] == len(lines_after_summary), "Lines_after_summary must not be empty"
#     assert summary_block["summary"]["unique_paths"] >= 1, "Value must be greater than zero"
#     assert evidence_path.read_text(encoding="utf-8") == before_vacuum, "Condition must be true"
