"""Bounded behavior regressions for status scans and documentation planning."""

from __future__ import annotations

import ast
import json
import sqlite3
from pathlib import Path

import pytest

from tools.docs_agent import inventory
from tools.docs_agent.agent_execution_standard import AgentExecutionStandard
from tools.status import generate_status_update as status


@pytest.fixture
def scan_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point every repository scanner at a small, isolated synthetic checkout."""
    for name in ("src", "docs", "tests", ".codex"):
        (tmp_path / name).mkdir()
    for name, value in {
        "REPO_ROOT": tmp_path,
        "SRC_DIRS": (tmp_path / "src",),
        "DOCS_DIR": tmp_path / "docs",
        "TESTS_DIR": tmp_path / "tests",
        "CODEX_DIR": tmp_path / ".codex",
        "STATUS_DIR": tmp_path / ".codex/status",
        "ERROR_LOG_PATH": tmp_path / ".codex/errors.ndjson",
    }.items():
        monkeypatch.setattr(status, name, value)
    return tmp_path


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("def f():\n    pass", "stub-pass"),
        ("def f():\n    ...", "stub-pass"),
        ('def f():\n    "documentation only"', "stub-empty"),
        ('def f():\n    raise RuntimeError("disabled")', "disabled"),
        ("def f():\n    raise NotImplementedError()", "stub-todo"),
        ("def f():\n    raise", "implemented"),
        ("def f():\n    if True:\n        raise", "implemented"),
        ("def f():\n    return 1", "implemented"),
    ],
)
def test_cli_status_including_optional_raise(source: str, expected: str) -> None:
    function = ast.parse(source).body[0]
    assert isinstance(function, ast.FunctionDef)
    assert status.classify_cli_status(function.body) == expected
    assert status.get_attr_name(None) == ""
    assert status.extract_raise_message(None) is None


def test_status_scans_preserve_record_shapes_and_order(scan_root: Path) -> None:
    (scan_root / "src/demo.py").write_text(
        "import click\nimport package.child\n# TODO todo FIXME XXX\n"
        '@click.command("run", name="execute")\n'
        'def run():\n    raise NotImplementedError("coming soon")\n'
        "class Empty:\n    pass\n",
        encoding="utf-8",
    )
    (scan_root / "docs/guide.md").write_text(
        "run execute\nTyper\nLoRA and typer\n", encoding="utf-8"
    )
    (scan_root / "src/sample_registry.py").write_text(
        'REGISTRY = {"unset": None, "ready": object, **extras}\n'
        'REGISTRY["later"] = ...\n'
        '@REGISTRY.register("decorated")\ndef implementation():\n    return 1\n',
        encoding="utf-8",
    )
    (scan_root / "tests/test_demo.py").write_text("import demo\n", encoding="utf-8")
    files = status.load_python_files([scan_root / "src"])
    assert files[0].imports == {"click", "package"}
    findings = status.scan_stubs(files)
    assert [(row["symbol"], row["kind"], row["line"]) for row in findings] == [
        ("run", "NotImplementedError", 6),
        ("Empty", "TrivialBody", 7),
    ]
    assert status.count_todos(files) == [
        {"file": "src/demo.py", "todo": 2, "fixme": 1, "xxx": 1, "total": 4}
    ]
    docs = status.load_docs_texts()
    commands = status.discover_cli(files, docs)
    assert commands == [
        {
            "path": "src/demo.py",
            "function": "run",
            "cli_names": ["execute", "run"],
            "status": "stub-todo",
            "doc_references": ["docs/guide.md"],
            "decorators": ["click.command"],
        }
    ]
    registries = status.inspect_registries(files)
    assert registries[0]["status"] == "has-unresolved"
    assert [(entry["key"], entry["status"]) for entry in registries[0]["entries"]] == [
        ("decorated", "ok"),
        ("later", "unresolved"),
        ("ready", "ok"),
        ("unset", "unresolved"),
    ]
    assert status.map_tests(files) == {
        "total_modules": 2,
        "modules_without_tests": ["src/sample_registry.py"],
        "modules_without_tests_count": 1,
        "modules_with_tests_count": 1,
    }
    assert status.docs_crossreferences(docs) == [
        {
            "doc": "docs/guide.md",
            "topics": [
                {"topic": "LoRA", "lines": [3], "count": 1},
                {"topic": "Typer", "lines": [2, 3], "count": 2},
            ],
        }
    ]


def test_status_generate_snapshot_and_redacted_preview(
    scan_root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (scan_root / "src/demo.py").write_text("# TODO\nimport random\nrandom.seed(7)\n")
    (scan_root / "requirements.txt").write_text("Sample_Package>=1\n")
    (scan_root / "requirements-dev.txt").write_text("sample-package==2\n")
    (scan_root / "uv.lock").write_text("")
    (scan_root / "LICENSE").write_text("license text")
    (scan_root / "manifest.json").write_text("{}")
    (scan_root / "model.ckpt").write_bytes(b"checkpoint")
    report = status.generate("reviewer", "2026-10-22", write=False)
    preview = capsys.readouterr()
    assert preview.out == ""
    assert "[preview] Status update ready" in preview.err
    assert "Sample_Package" not in preview.err
    assert not report.exists()
    assert not (scan_root / ".codex/status_scan.json").exists()
    assert status.generate("reviewer", "2026-10-22", write=True) == report
    snapshot = json.loads((scan_root / ".codex/status_scan.json").read_text())
    assert snapshot["summary"]["todo_total"] == 1
    assert snapshot["summary"]["modules_scanned"] == 1
    assert snapshot["packaging"]["lock_file_present"] is True
    assert snapshot["packaging"]["duplicate_packages"] == [
        {
            "package": "sample-package",
            "files": ["requirements-dev.txt", "requirements.txt"],
            "specs": ["Sample_Package>=1", "sample-package==2"],
        }
    ]
    assert snapshot["repro"]["seed_calls"] == [{"file": "src/demo.py", "keywords": ["random.seed"]}]
    assert snapshot["repro"]["checkpoint_artifacts"] == ["model.ckpt"]
    assert "| TODO/FIXME/XXX occurrences | 1 across 1 files |" in report.read_text()
    assert "| .secrets.baseline present | [redacted] |" in report.read_text()


def test_empty_partial_reports_and_read_parse_failures(
    scan_root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (scan_root / "src/broken.py").write_text("def syntax error")
    empty = scan_root / "src/empty"
    empty.mkdir()
    (empty / "__init__.py").write_text("# only a comment\n")
    files = status.load_python_files([scan_root / "src"])
    assert files[0].parsed is False
    assert status.scan_stubs(files) == []
    assert status.safe_read_text(scan_root / "missing.py") == ("", False)
    errors = [
        json.loads(line) for line in (scan_root / ".codex/errors.ndjson").read_text().splitlines()
    ]
    assert [error["step"] for error in errors] == ["parse_ast", "read_text"]
    assert status.find_empty_packages() == [{"path": "src/empty", "reason": "trivial __init__.py"}]
    assert status.build_summary_counts({}) == {
        "stubs_total": 0,
        "stubs_by_kind": {},
        "todo_files": 0,
        "todo_total": 0,
        "empty_packages": 0,
        "cli_total": 0,
        "cli_status_counts": {},
        "registry_total": 0,
        "registry_status_counts": {},
        "modules_scanned": 0,
        "modules_without_tests": 0,
    }
    path = status.write_report("reviewer", "2026-10-22", {}, write=True)
    assert "| (none) |" in path.read_text()
    assert capsys.readouterr().out == ""
    assert status.sanitize_for_logging("token=abc123 password: hidden") == ("[redacted] [redacted]")


def test_inventory_reports_keep_precise_classifications(tmp_path: Path) -> None:
    docs_data = tmp_path / "docs-data"
    docs_data.mkdir()
    (docs_data / "machine-readable-policy.json").write_text(
        json.dumps(
            {
                "candidate_extensions": [".md", ".rst", ".blob"],
                "exempted_paths": ["docs/exempt.*"],
            }
        )
    )
    (docs_data / "allowed-source-exceptions.json").write_text(
        json.dumps({"exceptions": [{"path": "docs/keep.md"}]})
    )
    names = ["README.md", "docs/notes.md", "docs/keep.md", "docs/exempt.md", "plan.md", "x.blob"]
    for name in names:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("sample")
    workflows = tmp_path / ".github/workflows"
    workflows.mkdir(parents=True)
    (workflows / "docs-check.yml").write_text("name: docs")
    result = inventory.run_inventory(tmp_path)
    assert result["ok"] is True
    assert result["total_candidates"] == 6
    generated = docs_data / "generated"
    assert sorted(result["generated"]) == sorted(path.name for path in generated.iterdir())
    reports = {name: json.loads((generated / name).read_text()) for name in result["generated"]}
    rows = reports["candidate-inventory.json"]["candidates"]
    assert [row["path"] for row in rows] == sorted(names)
    by_path = {row["path"]: row for row in rows}
    assert by_path["docs/keep.md"]["exception"] is True
    assert by_path["docs/keep.md"]["requires_ingestion"] is False
    assert by_path["docs/exempt.md"]["classification"] == "exception_candidate"
    assert by_path["docs/exempt.md"]["exception"] is False
    assert by_path["x.blob"]["confidence"] == 0.4
    assert by_path["x.blob"]["size_bytes"] == 6
    discovery = reports["codebase-discovery-report.json"]
    assert discovery["files_recommended_for_conversion"] == [
        "README.md",
        "docs/notes.md",
        "plan.md",
    ]
    assert discovery["files_recommended_for_exception_handling"] == ["docs/keep.md"]
    assert discovery["files_recommended_for_quarantine"] == ["x.blob"]
    assert discovery["files_recommended_for_deletion_after_conversion"] == [
        "docs/notes.md",
        "plan.md",
    ]
    assert reports["migration-readiness-report.json"]["strict_mode_blocking"] is True
    assert reports["existing-automation-report.json"]["workflows"] == ["docs-check.yml"]
    assert len(reports["markdown-inventory.json"]["markdown_candidates"]) == 5


@pytest.fixture
def standard(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Exercise the real SQLite tool boundary without touching checkout campaign data."""
    database = tmp_path / "docs-data/generated/docs.sqlite"
    database.parent.mkdir(parents=True)
    with sqlite3.connect(database) as conn:
        conn.executescript("""
            CREATE TABLE campaign_phases (id TEXT, data TEXT);
            CREATE TABLE tracks (id TEXT, data TEXT);
            CREATE TABLE deliverables (id TEXT, track_id TEXT, data TEXT);
            CREATE TABLE agents (id TEXT);
            CREATE TABLE requirements (phase_id TEXT, data TEXT);
            CREATE TABLE relationships (source_id TEXT, target_id TEXT, data TEXT);
            CREATE VIRTUAL TABLE fts_phases USING fts5(id, name, description);
            CREATE VIRTUAL TABLE fts_tracks USING fts5(id, name, description);
            """)
        conn.execute(
            "INSERT INTO campaign_phases VALUES (?, ?)",
            ("P-1", json.dumps({"id": "P-1", "name": "Phase", "description": "campaign"})),
        )
        conn.execute(
            "INSERT INTO tracks VALUES (?, ?)",
            ("T-1", json.dumps({"id": "T-1", "name": "Track", "description": "delivery"})),
        )
        conn.execute(
            "INSERT INTO deliverables VALUES (?, ?, ?)",
            ("D-1", "T-1", json.dumps({"id": "D-1", "phase_id": "P-1", "status": "Pending"})),
        )
        conn.execute("INSERT INTO agents VALUES ('A-1')")
        conn.execute("INSERT INTO requirements VALUES ('P-1', '{\"id\": \"R-1\"}')")
        conn.execute("INSERT INTO relationships VALUES ('D-1', 'D-2', '{}')")
    monkeypatch.chdir(tmp_path)
    instance = AgentExecutionStandard()
    try:
        yield instance
    finally:
        instance.tools.conn.close()


@pytest.mark.parametrize(
    ("task_id", "changes", "expected_steps"),
    [
        (None, None, [1, 2, 5, 6, 7, 8]),
        ("D-1", None, [1, 2, 3, 5, 6, 7, 8]),
        ("D-1", {}, [1, 2, 3, 5, 6, 7, 8]),
        (None, {"status": "Complete"}, [1, 2, 5, 6, 7, 8]),
        ("D-1", {"status": "Complete"}, [1, 2, 3, 4, 5, 6, 7, 8]),
        ("missing", None, [1, 2, 3, 5, 6, 7, 8]),
    ],
)
def test_protocol_conditional_steps_and_sqlite_persistence(
    standard: AgentExecutionStandard,
    task_id: str | None,
    changes: dict[str, object] | None,
    expected_steps: list[int],
) -> None:
    execution = standard.execute_full_protocol(task_id, changes)
    assert [step["step"] for step in execution["steps"]] == expected_steps
    assert execution["protocol_name"] == "Agent Execution Standard"
    assert execution["version"] == "0.1.0"
    by_step = {step["step"]: step for step in execution["steps"]}
    assert by_step[5]["action"] == "Execute task-specific actions"
    assert by_step[7]["index_rebuild"]["status"] == "success"
    assert by_step[8]["validation"]["status"] == "valid"
    assert standard.tools.conn.execute("SELECT COUNT(*) FROM fts_phases").fetchone()[0] == 1
    task = json.loads(standard.tools.conn.execute("SELECT data FROM deliverables").fetchone()[0])
    assert task["status"] == "Pending"
    if 4 in by_step:
        assert by_step[4]["impact"]["affected_entities"]["direct"] == 1


def test_protocol_descriptive_steps_do_not_execute_or_update(
    standard: AgentExecutionStandard,
) -> None:
    actions = ["do not execute this command"]
    updates: dict[str, object] = {"status": "Complete"}
    assert standard.step_5_execute_task("D-1", actions)["task_execution"]["actions_executed"] is (
        actions
    )
    assert standard.step_6_update_records(updates)["record_updates"] is updates
    assert standard.step_1_get_context("unused")["campaign_summary"] == {
        "phases": 1,
        "tracks": 1,
        "deliverables": 1,
        "agents": 1,
    }
    assert "# PART 9: Agent Execution Standard" in standard.generate_agent_implementation_guide()


@pytest.mark.parametrize("identifier", ["D-1", 1])
def test_protocol_brief_task_id_narrowing(
    standard: AgentExecutionStandard, monkeypatch: pytest.MonkeyPatch, identifier: str | int
) -> None:
    monkeypatch.setattr(
        standard.tools, "get_task_brief", lambda task_id: {"task": {"id": identifier}}
    )
    if isinstance(identifier, str):
        execution = standard.execute_full_protocol()
        assert [step["step"] for step in execution["steps"]] == [1, 2, 3, 5, 6, 7, 8]
    else:
        with pytest.raises(TypeError, match="Task ID must be a string"):
            standard.execute_full_protocol()
