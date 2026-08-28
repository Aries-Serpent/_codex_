"""Tests for Phase 3 Chronicle CLI gap adapters (`improve`, `search`)."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from click.testing import CliRunner

from aries_serpent_core.cli import cli


def _get_command(group_name: str, command_name: str):
    """Resolve a nested Click command from the top-level CLI group."""

    group = cli.commands[group_name]
    return group.commands[command_name]


chronicle_improve = _get_command("chronicle", "improve")
chronicle_search = _get_command("chronicle", "search")
chronicle_cost_tips = _get_command("chronicle", "cost-tips")
chronicle_standup = _get_command("chronicle", "standup")


class TestChronicleImprove:
    """Tests for the read-only `/chronicle improve` adapter."""

    def test_improve_missing_database_returns_empty_state(self, tmp_path: Path) -> None:
        """When the Chronicle DB is missing, improve returns an empty-state JSON."""

        runner = CliRunner()
        missing_db = tmp_path / "missing.sqlite"
        result = runner.invoke(
            chronicle_improve,
            ["--database", str(missing_db)],
        )
        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["state"] == "empty"
        assert payload["database"] == str(missing_db)
        assert "Chronicle database not found" in payload["diagnostics"][0]
        assert payload["cost_report"] == {}
        assert payload["pattern_observations"] == {}

    def test_improve_with_valid_database_returns_roadmap(self, tmp_path: Path) -> None:
        """When a valid Chronicle DB exists, improve returns a roadmap with expected keys."""

        db_path = tmp_path / "chronicle.sqlite"
        connection = sqlite3.connect(db_path)
        # Schema compatible with both ChronicleStore and SessionDatabase/ChronicleAnalytics.
        connection.execute(
            "CREATE TABLE sessions ("
            "session_id TEXT PRIMARY KEY, pr_number INTEGER, branch TEXT, "
            "timestamp TEXT, git_sha TEXT, "
            "status TEXT NOT NULL CHECK (status IN "
            "('pending', 'in-progress', 'complete', 'failed')), "
            "agent_name TEXT, duration_minutes INTEGER, "
            "created_at DATETIME DEFAULT CURRENT_TIMESTAMP, "
            "updated_at DATETIME DEFAULT CURRENT_TIMESTAMP, "
            "UNIQUE(session_id)"
            ")"
        )
        connection.execute(
            "INSERT INTO sessions (session_id, timestamp, status, agent_name, branch) "
            "VALUES (?, ?, ?, ?, ?)",
            ("session-1", "2026-08-01T00:00:00Z", "complete", "copilot-coding-agent", "main"),
        )
        connection.commit()
        connection.close()

        runner = CliRunner()
        result = runner.invoke(
            chronicle_improve,
            ["--database", str(db_path), "--warning-budget", "50", "--hard-budget", "100"],
        )
        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["state"] == "available"
        assert payload["database"] == str(db_path)
        assert payload["cost_report"]["metrics"]["sessions"] == 1
        assert "tips" in payload["cost_report"]
        assert "pattern_observations" in payload
        assert payload["pattern_observations"]["agents"]["total_agents_used"] == 1
        assert payload["repository"]["branch"] is not None

    def test_improve_budget_validation(self, tmp_path: Path) -> None:
        """Improve rejects a hard budget below the warning budget."""

        runner = CliRunner()
        result = runner.invoke(
            chronicle_improve,
            [
                "--database",
                str(tmp_path / "missing.sqlite"),
                "--warning-budget",
                "100",
                "--hard-budget",
                "50",
            ],
        )
        assert result.exit_code != 0
        assert "--hard-budget must be greater than or equal to --warning-budget" in result.output


class TestChronicleSearch:
    """Tests for the read-only `/chronicle search` adapter."""

    def test_search_missing_index_returns_empty_state(self, tmp_path: Path) -> None:
        """When the search index is missing, search returns an empty-state JSON."""

        runner = CliRunner()
        missing_index = tmp_path / "missing.json"
        result = runner.invoke(
            chronicle_search,
            ["test", "--index", str(missing_index), "--json"],
        )
        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["state"] == "empty"
        assert payload["hit_count"] == 0
        assert payload["hits"] == []
        assert "Search index not found" in payload["diagnostics"][0]

    def test_search_empty_index_returns_empty_state(self, tmp_path: Path) -> None:
        """When the search index has no sessions, search returns an empty-state JSON."""

        index_path = tmp_path / "chronicle_search_index.json"
        index_path.write_text(
            json.dumps({"schema_version": "1.0", "sessions": []}), encoding="utf-8"
        )

        runner = CliRunner()
        result = runner.invoke(chronicle_search, ["test", "--index", str(index_path), "--json"])
        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["state"] == "empty"
        assert payload["hit_count"] == 0

    def test_search_returns_matching_hits(self, tmp_path: Path) -> None:
        """Search returns hits ranked by local relevance."""

        index_path = tmp_path / "chronicle_search_index.json"
        sessions = [
            {
                "session_id": "lane-5-docs",
                "summary": "Documentation consolidation for Lane 5",
                "branch": "copilot/multi-lane-campaign-execution",
                "status": "active",
            },
            {
                "session_id": "security-factory-run",
                "summary": "Security factory S1 ingest and clustering",
                "branch": "main",
                "status": "complete",
            },
            {
                "session_id": "unrelated-session",
                "summary": "Miscellaneous cleanup",
                "branch": "main",
                "status": "complete",
            },
        ]
        index_path.write_text(
            json.dumps({"schema_version": "1.0", "sessions": sessions}),
            encoding="utf-8",
        )

        runner = CliRunner()
        result = runner.invoke(
            chronicle_search, ["lane docs", "--index", str(index_path), "--json"]
        )
        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["state"] == "available"
        assert payload["hit_count"] >= 1
        hits = payload["hits"]
        assert hits[0]["session_id"] == "lane-5-docs"
        assert "lane" in [t.lower() for t in hits[0]["matched_terms"]]

    def test_search_no_query_returns_empty_results(self, tmp_path: Path) -> None:
        """Search without a query returns empty results and a diagnostic."""

        runner = CliRunner()
        result = runner.invoke(
            chronicle_search, ["--index", str(tmp_path / "missing.json"), "--json"]
        )
        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["state"] == "empty"
        assert payload["hit_count"] == 0
        assert "No search query provided" in payload["diagnostics"][0]


class TestChronicleLaneFilters:
    """Lane-aware CLI entries should accept lane filters without breaking output."""

    def test_cost_tips_accepts_lane_filter(self, tmp_path: Path) -> None:
        db_path = tmp_path / "chronicle.sqlite"
        connection = sqlite3.connect(db_path)
        connection.execute(
            "CREATE TABLE sessions ("
            "session_id TEXT PRIMARY KEY, pr_number INTEGER, branch TEXT, "
            "timestamp TEXT, git_sha TEXT, status TEXT, agent_name TEXT, "
            "duration_minutes INTEGER, lane_bucket TEXT, checkpoint_state TEXT, "
            "budget_remaining REAL, estimated_cost REAL, cost_score REAL, "
            "tool_name TEXT, tool_complete_call_id TEXT, usage_input_tokens INTEGER, "
            "usage_output_tokens INTEGER, credits REAL, blockers TEXT, "
            "checkpoint_markers TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, "
            "updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
        )
        connection.execute(
            "INSERT INTO sessions (session_id, timestamp, status, lane_bucket, tool_name, "
            "credits, estimated_cost, budget_remaining) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("lane-p1", "2026-08-01T00:00:00Z", "complete", "P1", "grep", 1200, 700, 1500),
        )
        connection.commit()
        connection.close()

        runner = CliRunner()
        result = runner.invoke(
            chronicle_cost_tips,
            ["--database", str(db_path), "--lane", "P1", "--format", "json"],
        )
        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["scope"]["lane"] == "P1"
        assert payload["lane_focus"] == "P1"

    def test_standup_accepts_lane_filter(self, tmp_path: Path) -> None:
        db_path = tmp_path / "chronicle.sqlite"
        connection = sqlite3.connect(db_path)
        connection.execute(
            "CREATE TABLE sessions ("
            "session_id TEXT PRIMARY KEY, pr_number INTEGER, branch TEXT, "
            "timestamp TEXT, git_sha TEXT, status TEXT, agent_name TEXT, "
            "duration_minutes INTEGER, lane_bucket TEXT, checkpoint_state TEXT, "
            "budget_remaining REAL, estimated_cost REAL, cost_score REAL, "
            "tool_name TEXT, tool_complete_call_id TEXT, usage_input_tokens INTEGER, "
            "usage_output_tokens INTEGER, credits REAL, blockers TEXT, "
            "checkpoint_markers TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, "
            "updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
        )
        connection.execute(
            "INSERT INTO sessions (session_id, timestamp, status, lane_bucket) "
            "VALUES (?, ?, ?, ?)",
            ("lane-s1", "2026-08-01T00:00:00Z", "complete", "S1"),
        )
        connection.commit()
        connection.close()

        runner = CliRunner()
        result = runner.invoke(
            chronicle_standup,
            ["--database", str(db_path), "--lane", "S1", "--json"],
        )
        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["lane"] == "S1"
        assert payload["lane_pattern"] in {"fragmented", "batchable"}
