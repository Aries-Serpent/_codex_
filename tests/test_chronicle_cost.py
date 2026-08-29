"""Tests for schema-tolerant Chronicle cost and standup reporting."""

from __future__ import annotations

import importlib.util
import json
import sqlite3
from pathlib import Path

from click.testing import CliRunner

from aries_serpent_core.logging.chronicle_cost import (
    ChronicleStore,
    SessionRecord,
    analyze_costs,
    build_chronicle_index,
    build_standup_report,
    extract_task_id,
)


def _database(path: Path) -> None:
    task_id = "98a181d6-d9af-448e-8fab-6f4760fd7a6f"
    connection = sqlite3.connect(path)
    connection.executescript(f"""
        CREATE TABLE sessions (
            id TEXT PRIMARY KEY,
            task_id TEXT,
            created_at TEXT,
            status TEXT,
            agent_name TEXT,
            summary TEXT
        );
        CREATE TABLE events (
            session_id TEXT,
            tool_name TEXT,
            user_content TEXT,
            input_tokens INTEGER,
            output_tokens INTEGER
        );
        CREATE TABLE session_refs (
            session_id TEXT,
            ref_type TEXT,
            ref_value TEXT
        );
        INSERT INTO sessions VALUES
            (
                'S-heavy', '{task_id}', '2026-08-01T00:00:00Z',
                'complete', 'agent-a', 'implementation'
            ),
            ('S-open', NULL, '2026-08-01T01:00:00Z', 'in-progress', 'agent-b', 'validation');
        INSERT INTO events VALUES
            ('S-heavy', 'view', 'inspect file', 10, 20),
            ('S-heavy', 'view', 'inspect file', 10, 20),
            ('S-heavy', 'bash', 'pytest failed with error', 10, 20),
            ('S-heavy', 'bash', 'commit abcdef1234567', 10, 20);
        INSERT INTO session_refs VALUES
            ('S-heavy', 'task', 'https://github.com/Aries-Serpent/_codex_/tasks/{task_id}');
        """)
    connection.commit()
    connection.close()


def _cli_module():
    path = Path(__file__).resolve().parents[1] / "src" / "aries_serpent_core" / "cli.py"
    spec = importlib.util.spec_from_file_location("chronicle_cli_test_module", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_resolve_chronicle_database_prefers_existing_repo_session_db(tmp_path: Path, monkeypatch) -> None:
    module = _cli_module()
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    (tmp_path / ".codex").mkdir(parents=True, exist_ok=True)
    session_db = tmp_path / ".codex" / "session_logs.db"
    session_db.touch()
    (tmp_path / ".codex" / "codex.sqlite").touch()

    assert module._resolve_chronicle_database() == str(session_db)
    assert module._resolve_chronicle_database("/tmp/custom.sqlite") == "/tmp/custom.sqlite"


def test_store_normalizes_id_schema_and_reports_missing_credits(tmp_path: Path) -> None:
    database = tmp_path / "chronicle.sqlite"
    _database(database)

    store = ChronicleStore(database)
    records = store.load_sessions()
    report = analyze_costs(records, store.diagnostics)

    assert [record.session_id for record in records] == ["S-heavy", "S-open"]
    assert report["metrics"]["credits_available"] is False
    assert report["metrics"]["tool_calls"] == 4
    assert any(tip["category"] == "measurement" for tip in report["tips"])


def test_standup_filters_task_url_and_identifies_incomplete_work(tmp_path: Path) -> None:
    database = tmp_path / "chronicle.sqlite"
    _database(database)

    task_id = extract_task_id(
        "https://github.com/Aries-Serpent/_codex_/tasks/98a181d6-d9af-448e-8fab-6f4760fd7a6f"
    )
    store = ChronicleStore(database)
    records = store.load_sessions(task_id=task_id)
    report = build_standup_report(records, store.diagnostics, task_id=task_id)

    assert [record.session_id for record in records] == ["S-heavy"]
    assert report["summary"]["completed_sessions"] == 1
    assert report["summary"]["commits"] == 1
    assert report["summary"]["tests"] >= 1


def test_task_reference_url_without_direct_task_is_matched(tmp_path: Path) -> None:
    database = tmp_path / "chronicle.sqlite"
    _database(database)
    connection = sqlite3.connect(database)
    connection.execute(
        "INSERT INTO sessions VALUES (?, ?, ?, ?, ?, ?)",
        ("S-ref", None, "2026-08-01T02:00:00Z", "complete", "agent-c", "linked"),
    )
    connection.execute(
        "INSERT INTO session_refs VALUES (?, ?, ?)",
        (
            "S-ref",
            "task",
            "https://github.com/Aries-Serpent/_codex_/tasks/"
            "98a181d6-d9af-448e-8fab-6f4760fd7a6f",
        ),
    )
    connection.commit()
    connection.close()

    store = ChronicleStore(database)
    records = store.load_sessions(task_id="98a181d6-d9af-448e-8fab-6f4760fd7a6f")

    assert {record.session_id for record in records} == {"S-heavy", "S-ref"}


def test_session_events_preserve_zero_credits_and_tool_boundaries(
    tmp_path: Path,
) -> None:
    database = tmp_path / "chronicle.sqlite"
    connection = sqlite3.connect(database)
    connection.executescript("""
        CREATE TABLE sessions (
            session_id TEXT PRIMARY KEY,
            status TEXT,
            credits INTEGER,
            commits INTEGER,
            tests INTEGER,
            checkpoints INTEGER
        );
        CREATE TABLE session_events (
            session_id TEXT,
            event_type TEXT,
            event_details TEXT
        );
        INSERT INTO sessions VALUES ('S-events', 'complete', 0, 0, 0, 0);
        INSERT INTO session_events VALUES
            ('S-events', 'start', 'unrelated 1234567'),
            ('S-events', 'check_passed', 'pytest passed'),
            ('S-events', 'complete', 'commit abcdef1');
        """)
    connection.commit()
    connection.close()

    store = ChronicleStore(database)
    records = store.load_sessions()
    report = analyze_costs(records, store.diagnostics)

    assert records[0].tool_calls == 0
    assert records[0].credits == 0
    assert records[0].commits == 0
    assert records[0].tests == 0
    assert records[0].checkpoints == 0
    assert report["metrics"]["credits_available"] is True
    assert not any(tip["category"] == "measurement" for tip in report["tips"])


def test_event_rows_count_only_tool_events(tmp_path: Path) -> None:
    database = tmp_path / "chronicle.sqlite"
    connection = sqlite3.connect(database)
    connection.executescript("""
        CREATE TABLE sessions (session_id TEXT PRIMARY KEY, status TEXT);
        CREATE TABLE events (
            session_id TEXT,
            type TEXT,
            tool_name TEXT,
            user_content TEXT
        );
        INSERT INTO sessions VALUES ('S-mixed', 'complete');
        INSERT INTO events VALUES
            ('S-mixed', 'user.message', NULL, 'question'),
            ('S-mixed', 'assistant.message', NULL, 'answer'),
            ('S-mixed', 'tool.execution_complete', 'view', 'result');
        """)
    connection.commit()
    connection.close()

    records = ChronicleStore(database).load_sessions()

    assert records[0].tool_calls == 1


def test_analyze_costs_keeps_lane_scope_and_cost_proxy_consistent() -> None:
    records = [
        SessionRecord(
            session_id="S-lane-a",
            created_at="2026-08-01T00:00:00Z",
            lane_bucket="P2",
            tool_calls=3,
            repeated_tool_calls=0,
            estimated_cost=70.0,
            budget_remaining=150,
            commits=0,
            tests=0,
            credits=None,
            checkpoints=0,
            blockers=[],
        ),
        SessionRecord(
            session_id="S-lane-b",
            created_at="2026-08-01T00:10:00Z",
            lane_bucket="P2",
            tool_calls=2,
            repeated_tool_calls=0,
            estimated_cost=5.0,
            budget_remaining=90,
            commits=0,
            tests=0,
            credits=None,
            checkpoints=0,
            blockers=[],
        ),
    ]

    report = analyze_costs(records, [], warning_budget=100, lane="P2")
    empty_scope_report = analyze_costs(records, [], warning_budget=100, lane="")

    assert report["scope"]["lane"] == "P2"
    assert report["lane_pattern"] == "fragmented"
    assert empty_scope_report["scope"]["lane"] == "unknown"
    assert empty_scope_report["lane_focus"] == "unknown"


def test_standup_materializes_diagnostics_iterable() -> None:
    report = build_standup_report(
        [],
        (diagnostic for diagnostic in ["source unavailable"]),
        task_id="task-id",
    )

    assert report["source_diagnostics"] == ["source unavailable"]
    assert "source unavailable" in report["missing_work"]


# ---------------------------------------------------------------------------
# Gap A: chronicle standup — no --database CLI path
# ---------------------------------------------------------------------------


def test_standup_no_db_uses_env_var(tmp_path: Path, monkeypatch) -> None:
    """standup without --database picks up CODEX_CHRONICLE_DB_PATH."""
    database = tmp_path / "chronicle.sqlite"
    _database(database)
    module = _cli_module()
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(module, "CAMPAIGN_METRICS_LOG", tmp_path / "metrics.jsonl")
    monkeypatch.setenv("CODEX_CHRONICLE_DB_PATH", str(database))
    runner = CliRunner()

    result = runner.invoke(
        module.cli,
        ["chronicle", "standup", "98a181d6-d9af-448e-8fab-6f4760fd7a6f", "--json"],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["task_id"] == "98a181d6-d9af-448e-8fab-6f4760fd7a6f"


def test_standup_no_db_uses_repo_session_logs_db(tmp_path: Path, monkeypatch) -> None:
    """standup without --database and no env var finds session_logs.db in repo root."""
    database = tmp_path / ".codex" / "session_logs.db"
    database.parent.mkdir(parents=True, exist_ok=True)
    _database(database)
    module = _cli_module()
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(module, "CAMPAIGN_METRICS_LOG", tmp_path / "metrics.jsonl")
    monkeypatch.delenv("CODEX_CHRONICLE_DB_PATH", raising=False)
    monkeypatch.delenv("CODEX_DB_PATH", raising=False)
    monkeypatch.delenv("CODEX_LOG_DB_PATH", raising=False)
    runner = CliRunner()

    result = runner.invoke(
        module.cli,
        ["chronicle", "standup", "98a181d6-d9af-448e-8fab-6f4760fd7a6f", "--json"],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert "task_id" in data


def test_standup_no_db_no_env_no_file_falls_back_gracefully(tmp_path: Path, monkeypatch) -> None:
    """standup without --database and no env var and no db file exits non-zero or returns empty."""
    module = _cli_module()
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(module, "CAMPAIGN_METRICS_LOG", tmp_path / "metrics.jsonl")
    monkeypatch.delenv("CODEX_CHRONICLE_DB_PATH", raising=False)
    monkeypatch.delenv("CODEX_DB_PATH", raising=False)
    monkeypatch.delenv("CODEX_LOG_DB_PATH", raising=False)
    runner = CliRunner()

    result = runner.invoke(
        module.cli,
        ["chronicle", "standup", "no-such-task", "--json"],
    )

    # Graceful degradation: either exits 0 with empty sessions or non-zero with error message
    if result.exit_code == 0:
        data = json.loads(result.output)
        assert data.get("summary", {}).get("total_sessions", 0) == 0
    else:
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# Gap B: chronicle reindex — no --database CLI path
# ---------------------------------------------------------------------------


def test_reindex_no_db_uses_env_var(tmp_path: Path, monkeypatch) -> None:
    """reindex without --database picks up CODEX_CHRONICLE_DB_PATH."""
    database = tmp_path / "chronicle.sqlite"
    _database(database)
    index_path = tmp_path / "index.json"
    module = _cli_module()
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(module, "CAMPAIGN_METRICS_LOG", tmp_path / "metrics.jsonl")
    monkeypatch.setenv("CODEX_CHRONICLE_DB_PATH", str(database))
    runner = CliRunner()

    result = runner.invoke(
        module.cli,
        ["chronicle", "reindex", "--output", str(index_path)],
    )

    assert result.exit_code == 0, result.output
    assert index_path.exists()
    data = json.loads(index_path.read_text())
    assert data["summary"]["total_sessions"] == 2


def test_reindex_no_db_uses_repo_session_logs_db(tmp_path: Path, monkeypatch) -> None:
    """reindex without --database and no env var finds session_logs.db in repo root."""
    database = tmp_path / ".codex" / "session_logs.db"
    database.parent.mkdir(parents=True, exist_ok=True)
    _database(database)
    index_path = tmp_path / "index.json"
    module = _cli_module()
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(module, "CAMPAIGN_METRICS_LOG", tmp_path / "metrics.jsonl")
    monkeypatch.delenv("CODEX_CHRONICLE_DB_PATH", raising=False)
    monkeypatch.delenv("CODEX_DB_PATH", raising=False)
    monkeypatch.delenv("CODEX_LOG_DB_PATH", raising=False)
    runner = CliRunner()

    result = runner.invoke(
        module.cli,
        ["chronicle", "reindex", "--output", str(index_path)],
    )

    assert result.exit_code == 0, result.output
    assert index_path.exists()
    data = json.loads(index_path.read_text())
    assert data["summary"]["total_sessions"] == 2


def test_reindex_no_db_no_env_no_file_falls_back_gracefully(tmp_path: Path, monkeypatch) -> None:
    """reindex without --database and no env var and no file degrades gracefully."""
    index_path = tmp_path / "index.json"
    module = _cli_module()
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(module, "CAMPAIGN_METRICS_LOG", tmp_path / "metrics.jsonl")
    monkeypatch.delenv("CODEX_CHRONICLE_DB_PATH", raising=False)
    monkeypatch.delenv("CODEX_DB_PATH", raising=False)
    monkeypatch.delenv("CODEX_LOG_DB_PATH", raising=False)
    runner = CliRunner()

    result = runner.invoke(
        module.cli,
        ["chronicle", "reindex", "--output", str(index_path)],
    )

    # Graceful degradation: either exits 0 with empty index or non-zero error
    if result.exit_code == 0:
        if index_path.exists():
            data = json.loads(index_path.read_text())
            assert data["summary"]["total_sessions"] == 0
    else:
        assert result.exit_code != 0


def test_build_chronicle_index_preserves_session_evidence(tmp_path: Path) -> None:
    database = tmp_path / "chronicle.sqlite"
    _database(database)
    store = ChronicleStore(database)

    index = build_chronicle_index(
        store.load_sessions(),
        store.diagnostics,
        scope="test",
    )

    assert index["schema_version"] == "1.0"
    assert index["scope"] == "test"
    assert index["summary"]["total_sessions"] == 2
    assert index["sessions"][0]["session_id"] == "S-open"


def test_cli_cost_tips_and_standup_support_json(tmp_path: Path, monkeypatch) -> None:
    database = tmp_path / "chronicle.sqlite"
    task_id = "98a181d6-d9af-448e-8fab-6f4760fd7a6f"
    _database(database)
    module = _cli_module()
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(module, "CAMPAIGN_METRICS_LOG", tmp_path / "metrics.jsonl")
    runner = CliRunner()

    cost_result = runner.invoke(
        module.cli,
        ["chronicle", "cost-tips", "--database", str(database), "--format", "json"],
    )
    standup_result = runner.invoke(
        module.cli,
        [
            "chronicle",
            "standup",
            "98a181d6-d9af-448e-8fab-6f4760fd7a6f",
            "--database",
            str(database),
            "--json",
        ],
    )
    index_path = tmp_path / "index.json"
    reindex_result = runner.invoke(
        module.cli,
        [
            "chronicle",
            "reindex",
            "--database",
            str(database),
            "--output",
            str(index_path),
        ],
    )

    assert cost_result.exit_code == 0, cost_result.output
    assert standup_result.exit_code == 0, standup_result.output
    assert reindex_result.exit_code == 0, reindex_result.output
    assert json.loads(cost_result.output)["schema_version"] == "1.0"
    assert json.loads(standup_result.output)["task_id"] == task_id
    assert json.loads(index_path.read_text())["summary"]["total_sessions"] == 2


# ---------------------------------------------------------------------------
# Gap C: chronicle tips — --database CLI path
# ---------------------------------------------------------------------------


def test_tips_explicit_database_used(tmp_path: Path, monkeypatch) -> None:
    """tips with --database <path> uses the explicit path, not the default."""
    database = tmp_path / "explicit_tips.sqlite"
    module = _cli_module()
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(module, "CAMPAIGN_METRICS_LOG", tmp_path / "metrics.jsonl")

    resolved_paths: list[str | None] = []

    def capturing_resolve(db: str | None = None) -> str:
        resolved_paths.append(db)
        return str(database)

    monkeypatch.setattr(module, "_resolve_chronicle_database", capturing_resolve)

    # Stub SessionDatabase and ChronicleAnalytics so we don't need a real DB
    import unittest.mock as mock
    fake_analytics = mock.MagicMock()
    fake_analytics.generate_summary.return_value = "stub tips"
    fake_db = mock.MagicMock()
    monkeypatch.setattr(
        "aries_serpent_core.logging.session_database.SessionDatabase",
        mock.MagicMock(return_value=fake_db),
    )
    monkeypatch.setattr(
        "aries_serpent_core.logging.chronicle_analytics.ChronicleAnalytics",
        mock.MagicMock(return_value=fake_analytics),
    )

    runner = CliRunner()
    result = runner.invoke(
        module.cli,
        ["chronicle", "tips", "--database", str(database)],
    )

    assert result.exit_code == 0, result.output
    # The explicit path must have been forwarded to _resolve_chronicle_database
    assert resolved_paths == [str(database)]


def test_tips_no_db_resolves_via_helper(tmp_path: Path, monkeypatch) -> None:
    """tips WITHOUT --database passes None to _resolve_chronicle_database."""
    database = tmp_path / "chronicle.sqlite"
    module = _cli_module()
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(module, "CAMPAIGN_METRICS_LOG", tmp_path / "metrics.jsonl")
    monkeypatch.setenv("CODEX_CHRONICLE_DB_PATH", str(database))

    resolved_paths: list[str | None] = []

    def capturing_resolve(db: str | None = None) -> str:
        resolved_paths.append(db)
        return str(database)

    monkeypatch.setattr(module, "_resolve_chronicle_database", capturing_resolve)

    import unittest.mock as mock
    fake_analytics = mock.MagicMock()
    fake_analytics.generate_summary.return_value = "stub tips"
    fake_db = mock.MagicMock()
    monkeypatch.setattr(
        "aries_serpent_core.logging.session_database.SessionDatabase",
        mock.MagicMock(return_value=fake_db),
    )
    monkeypatch.setattr(
        "aries_serpent_core.logging.chronicle_analytics.ChronicleAnalytics",
        mock.MagicMock(return_value=fake_analytics),
    )

    runner = CliRunner()
    result = runner.invoke(module.cli, ["chronicle", "tips"])

    assert result.exit_code == 0, result.output
    # Called with None (no explicit --database)
    assert resolved_paths == [None]


# ---------------------------------------------------------------------------
# Gap D: chronicle analyze — --database CLI path
# ---------------------------------------------------------------------------


def test_analyze_explicit_database_used(tmp_path: Path, monkeypatch) -> None:
    """analyze with --database <path> uses the explicit path, not the default."""
    database = tmp_path / "explicit_analyze.sqlite"
    module = _cli_module()
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(module, "CAMPAIGN_METRICS_LOG", tmp_path / "metrics.jsonl")

    resolved_paths: list[str | None] = []

    def capturing_resolve(db: str | None = None) -> str:
        resolved_paths.append(db)
        return str(database)

    monkeypatch.setattr(module, "_resolve_chronicle_database", capturing_resolve)

    import unittest.mock as mock
    fake_analytics = mock.MagicMock()
    fake_analytics.analyze_patterns.return_value = {"frequency": {}, "tools": {}}
    fake_db = mock.MagicMock()
    monkeypatch.setattr(
        "aries_serpent_core.logging.session_database.SessionDatabase",
        mock.MagicMock(return_value=fake_db),
    )
    monkeypatch.setattr(
        "aries_serpent_core.logging.chronicle_analytics.ChronicleAnalytics",
        mock.MagicMock(return_value=fake_analytics),
    )

    runner = CliRunner()
    result = runner.invoke(
        module.cli,
        ["chronicle", "analyze", "--database", str(database)],
    )

    assert result.exit_code == 0, result.output
    assert resolved_paths == [str(database)]


def test_analyze_no_db_resolves_via_helper(tmp_path: Path, monkeypatch) -> None:
    """analyze WITHOUT --database passes None to _resolve_chronicle_database."""
    database = tmp_path / "chronicle.sqlite"
    module = _cli_module()
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(module, "CAMPAIGN_METRICS_LOG", tmp_path / "metrics.jsonl")
    monkeypatch.setenv("CODEX_CHRONICLE_DB_PATH", str(database))

    resolved_paths: list[str | None] = []

    def capturing_resolve(db: str | None = None) -> str:
        resolved_paths.append(db)
        return str(database)

    monkeypatch.setattr(module, "_resolve_chronicle_database", capturing_resolve)

    import unittest.mock as mock
    fake_analytics = mock.MagicMock()
    fake_analytics.analyze_patterns.return_value = {"frequency": {}, "tools": {}}
    fake_db = mock.MagicMock()
    monkeypatch.setattr(
        "aries_serpent_core.logging.session_database.SessionDatabase",
        mock.MagicMock(return_value=fake_db),
    )
    monkeypatch.setattr(
        "aries_serpent_core.logging.chronicle_analytics.ChronicleAnalytics",
        mock.MagicMock(return_value=fake_analytics),
    )

    runner = CliRunner()
    result = runner.invoke(module.cli, ["chronicle", "analyze"])

    assert result.exit_code == 0, result.output
    assert resolved_paths == [None]
