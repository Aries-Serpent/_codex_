"""Schema-tolerant Chronicle cost and standup analysis."""

from __future__ import annotations

import json
import re
import sqlite3
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from statistics import median
from typing import Any, Iterable

_UUID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}",
    re.IGNORECASE,
)
_COMMIT_RE = re.compile(
    r"\b(?:commit(?:ted)?|git\s+sha|sha|cherry[- ]pick)" r"[^\n]{0,80}?\b([0-9a-f]{7,40})\b",
    re.IGNORECASE,
)
_TEST_RE = re.compile(r"\b(?:pytest|nox|ruff|mypy|test(?:s|ed|ing)?)\b", re.IGNORECASE)
_BLOCKER_RE = re.compile(
    r"\b(?:blocked|blocker|failed|failure|error|incomplete|missing)\b", re.IGNORECASE
)


def _now() -> str:
    """Return a repository-standard UTC timestamp."""

    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _as_number(value: Any) -> int | float | None:
    if value is None or value == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return int(number) if number.is_integer() else number


def _as_int(value: Any, default: int = 0) -> int:
    number = _as_number(value)
    return int(number) if number is not None else default


def _prefer_int(value: Any, fallback: Any = 0) -> int:
    number = _as_number(value)
    return int(number) if number is not None else _as_int(fallback)


def _prefer_number(value: Any, fallback: Any = None) -> int | float | None:
    number = _as_number(value)
    return number if number is not None else _as_number(fallback)


def _first(row: sqlite3.Row, columns: set[str], *names: str) -> Any:
    for name in names:
        if name in columns:
            return row[name]
    return None


def _quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def extract_task_id(value: str) -> str:
    """Extract a task UUID from either a UUID or a task URL."""

    match = _UUID_RE.search(value)
    if not match:
        raise ValueError("task must contain a valid task UUID or task URL")
    return match.group(0)


def _normalise_task_id(value: Any) -> str | None:
    if value is None or value == "":
        return None
    try:
        return extract_task_id(str(value))
    except ValueError:
        return str(value)


@dataclass
class SessionRecord:
    """Normalized session data used by both Chronicle reports."""

    session_id: str
    task_id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    status: str | None = None
    agent_name: str | None = None
    repository: str | None = None
    branch: str | None = None
    summary: str | None = None
    tool_calls: int = 0
    input_tokens: int | float | None = None
    output_tokens: int | float | None = None
    credits: int | float | None = None
    duration_minutes: int | float | None = None
    commits: int = 0
    tests: int = 0
    blockers: list[str] = field(default_factory=list)
    uncommitted_changes: int | None = None
    checkpoints: int = 0
    repeated_tool_calls: int = 0


class ChronicleStore:
    """Read Chronicle data without assuming one database schema.

    The Copilot session store and the repository's local SQLite logger expose
    different column names.  This adapter detects available columns and keeps
    unavailable metrics explicit in ``diagnostics``.
    """

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.diagnostics: list[str] = []

    def _connect(self) -> sqlite3.Connection | None:
        if not self.db_path.exists():
            self.diagnostics.append(f"database not found: {self.db_path}")
            return None
        try:
            connection = sqlite3.connect(self.db_path)
            connection.row_factory = sqlite3.Row
            return connection
        except sqlite3.Error as exc:
            self.diagnostics.append(f"database unavailable: {exc}")
            return None

    @staticmethod
    def _tables(connection: sqlite3.Connection) -> set[str]:
        rows = connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
        return {str(row[0]) for row in rows}

    @staticmethod
    def _columns(connection: sqlite3.Connection, table: str) -> set[str]:
        rows = connection.execute(f"PRAGMA table_info({_quote_identifier(table)})").fetchall()
        return {str(row["name"]) for row in rows}

    def _session_task_ids(
        self,
        connection: sqlite3.Connection,
        tables: set[str],
        session_id: str,
    ) -> set[str]:
        if "session_refs" not in tables:
            return set()
        columns = self._columns(connection, "session_refs")
        session_column = next((name for name in ("session_id", "id") if name in columns), None)
        value_column = next(
            (name for name in ("ref_value", "value", "task_id") if name in columns),
            None,
        )
        if not session_column or not value_column:
            return set()
        conditions = [f"{_quote_identifier(session_column)} = ?"]
        parameters: list[str] = [session_id]
        if "ref_type" in columns:
            conditions.append('"ref_type" = ?')
            parameters.append("task")
        rows = connection.execute(
            f"SELECT {_quote_identifier(value_column)} AS value "
            f"FROM session_refs WHERE {' AND '.join(conditions)}",
            parameters,
        ).fetchall()
        return {
            task_id for row in rows if (task_id := _normalise_task_id(row["value"])) is not None
        }

    def _event_data(
        self,
        connection: sqlite3.Connection,
        tables: set[str],
        session_ids: set[str],
        *,
        start: str | None = None,
        end: str | None = None,
    ) -> dict[str, dict[str, Any]]:
        table = (
            "tool_calls"
            if "tool_calls" in tables
            else (
                "events"
                if "events" in tables
                else "session_events" if "session_events" in tables else None
            )
        )
        if table is None:
            self.diagnostics.append("tool/event table unavailable; tool metrics are unavailable")
            return {}

        columns = self._columns(connection, table)
        session_column = next((name for name in ("session_id", "id") if name in columns), None)
        if not session_column:
            self.diagnostics.append(f"{table} has no session identifier column")
            return {}
        conditions = [
            f"{_quote_identifier(session_column)} IN ({','.join('?' for _ in session_ids)})"
        ]
        parameters: list[str] = list(session_ids)
        timestamp_column = next(
            (name for name in ("timestamp", "created_at", "occurred_at") if name in columns),
            None,
        )
        if start and timestamp_column:
            conditions.append(f"{_quote_identifier(timestamp_column)} >= ?")
            parameters.append(start)
        if end and timestamp_column:
            conditions.append(f"{_quote_identifier(timestamp_column)} < ?")
            parameters.append(end)
        rows = connection.execute(
            f"SELECT * FROM {_quote_identifier(table)} WHERE {' AND '.join(conditions)}",
            parameters,
        ).fetchall()
        grouped: dict[str, list[sqlite3.Row]] = defaultdict(list)
        for row in rows:
            if row[session_column]:
                grouped[str(row[session_column])].append(row)

        result: dict[str, dict[str, Any]] = {}
        for session_id, session_rows in grouped.items():
            tool_rows = [
                row
                for row in session_rows
                if table == "tool_calls" or self._is_tool_row(row, columns)
            ]
            tool_names = [
                str(value)
                for row in tool_rows
                if (value := _first(row, columns, "tool_name", "name", "tool_start_name"))
            ]
            text_parts = []
            for row in session_rows:
                for name in (
                    "user_content",
                    "assistant_content",
                    "tool_complete_result_content",
                    "event_details",
                    "user_message",
                    "assistant_response",
                ):
                    value = _first(row, columns, name)
                    if value:
                        text_parts.append(str(value))
            text = "\n".join(text_parts)
            input_tokens = sum(
                (_as_number(_first(row, columns, "input_tokens", "usage_input_tokens")) or 0)
                for row in session_rows
            )
            output_tokens = sum(
                (_as_number(_first(row, columns, "output_tokens", "usage_output_tokens")) or 0)
                for row in session_rows
            )
            credits_values = [
                _as_number(
                    _first(row, columns, "credits", "ai_credits", "credit_usage", "total_credits")
                )
                for row in session_rows
            ]
            available_credits = [value for value in credits_values if value is not None]
            credits = sum(available_credits) if available_credits else None
            result[session_id] = {
                "tool_calls": len(tool_rows),
                "repeated_tool_calls": len(tool_names) - len(set(tool_names)),
                "input_tokens": (
                    input_tokens
                    if any(
                        value is not None
                        for value in (
                            _as_number(_first(row, columns, "input_tokens", "usage_input_tokens"))
                            for row in session_rows
                        )
                    )
                    else None
                ),
                "output_tokens": (
                    output_tokens
                    if any(
                        value is not None
                        for value in (
                            _as_number(_first(row, columns, "output_tokens", "usage_output_tokens"))
                            for row in session_rows
                        )
                    )
                    else None
                ),
                "credits": credits,
                "commits": len(set(_COMMIT_RE.findall(text))),
                "tests": len(_TEST_RE.findall(text)),
                "blockers": sorted(
                    {
                        line.strip()
                        for line in text.splitlines()
                        if line.strip() and _BLOCKER_RE.search(line)
                    }
                )[:10],
                "checkpoints": sum("checkpoint" in name.lower() for name in tool_names),
            }
        return result

    @staticmethod
    def _is_tool_row(row: sqlite3.Row, columns: set[str]) -> bool:
        event_type = _first(row, columns, "type", "event_type")
        if event_type and "tool" in str(event_type).lower():
            return True
        return any(
            _first(row, columns, name)
            for name in ("tool_name", "tool_start_name", "tool_call_id", "tool_complete_call_id")
        )

    def load_sessions(
        self,
        *,
        session_id: str | None = None,
        task_id: str | None = None,
        start: str | None = None,
        end: str | None = None,
    ) -> list[SessionRecord]:
        """Load normalized sessions using whichever compatible columns exist."""

        self.diagnostics = []
        connection = self._connect()
        if connection is None:
            return []
        try:
            tables = self._tables(connection)
            if "sessions" not in tables:
                self.diagnostics.append("sessions table unavailable")
                return []
            columns = self._columns(connection, "sessions")
            id_column = next((name for name in ("session_id", "id") if name in columns), None)
            if not id_column:
                self.diagnostics.append("sessions has no session identifier column")
                return []
            query = f"SELECT * FROM {_quote_identifier('sessions')}"
            conditions: list[str] = []
            parameters: list[str] = []
            if session_id:
                conditions.append(f"{_quote_identifier(id_column)} = ?")
                parameters.append(session_id)
            created_column = next(
                (name for name in ("created_at", "timestamp", "started_at") if name in columns),
                None,
            )
            if start and created_column:
                conditions.append(f"{_quote_identifier(created_column)} >= ?")
                parameters.append(start)
            if end and created_column:
                conditions.append(f"{_quote_identifier(created_column)} < ?")
                parameters.append(end)
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            rows = connection.execute(query, parameters).fetchall()

            matched_rows: list[tuple[sqlite3.Row, str, set[str]]] = []
            for row in rows:
                current_id = str(row[id_column])
                direct_task = _first(row, columns, "task_id", "task")
                ref_tasks = self._session_task_ids(connection, tables, current_id)
                record_task = _normalise_task_id(direct_task) or next(iter(ref_tasks), None)
                normalized_task_id = _normalise_task_id(task_id)
                if (
                    normalized_task_id
                    and record_task != normalized_task_id
                    and normalized_task_id not in ref_tasks
                ):
                    continue
                matched_rows.append((row, current_id, ref_tasks))

            event_data = (
                self._event_data(
                    connection,
                    tables,
                    {current_id for _, current_id, _ in matched_rows},
                    start=start,
                    end=end,
                )
                if matched_rows
                else {}
            )
            records: list[SessionRecord] = []
            for row, current_id, ref_tasks in matched_rows:
                direct_task = _first(row, columns, "task_id", "task")
                record_task = _normalise_task_id(direct_task) or next(iter(ref_tasks), None)
                data = event_data.get(current_id, {})
                record = SessionRecord(
                    session_id=current_id,
                    task_id=record_task,
                    created_at=_first(row, columns, "created_at", "timestamp", "started_at"),
                    updated_at=_first(row, columns, "updated_at", "ended_at", "completed_at"),
                    status=_first(row, columns, "status", "state"),
                    agent_name=_first(row, columns, "agent_name", "agent"),
                    repository=_first(row, columns, "repository", "repo"),
                    branch=_first(row, columns, "branch"),
                    summary=_first(row, columns, "summary", "task", "description"),
                    tool_calls=_as_int(
                        _first(row, columns, "tool_calls", "tool_call_count"),
                        _as_int(data.get("tool_calls")),
                    ),
                    input_tokens=_prefer_number(
                        _first(row, columns, "input_tokens"), data.get("input_tokens")
                    ),
                    output_tokens=_prefer_number(
                        _first(row, columns, "output_tokens"), data.get("output_tokens")
                    ),
                    credits=_prefer_number(
                        _first(
                            row, columns, "credits", "ai_credits", "credit_usage", "total_credits"
                        ),
                        data.get("credits"),
                    ),
                    duration_minutes=_as_number(
                        _first(row, columns, "duration_minutes", "duration", "duration_seconds")
                    ),
                    commits=_prefer_int(
                        _first(row, columns, "commits", "commit_count"),
                        data.get("commits", 0),
                    ),
                    tests=_prefer_int(
                        _first(row, columns, "tests", "test_count"),
                        data.get("tests", 0),
                    ),
                    blockers=list(data.get("blockers", [])),
                    uncommitted_changes=(
                        int(value)
                        if (
                            value := _as_number(
                                _first(row, columns, "uncommitted_changes", "dirty_files")
                            )
                        )
                        is not None
                        else None
                    ),
                    checkpoints=_prefer_int(
                        _first(row, columns, "checkpoints", "checkpoint_count"),
                        data.get("checkpoints", 0),
                    ),
                    repeated_tool_calls=int(data.get("repeated_tool_calls", 0)),
                )
                records.append(record)
            if task_id and not records:
                self.diagnostics.append(f"no sessions matched task: {task_id}")
            if not records and not session_id and not task_id:
                self.diagnostics.append("no sessions available in selected window")
            return records
        except sqlite3.Error as exc:
            self.diagnostics.append(f"session query failed: {exc}")
            return []
        finally:
            connection.close()


def _tip(
    category: str,
    title: str,
    description: str,
    evidence: str,
    savings: str,
    confidence: str,
) -> dict[str, str]:
    return {
        "category": category,
        "title": title,
        "description": description,
        "evidence": evidence,
        "estimated_savings": savings,
        "confidence": confidence,
    }


def analyze_costs(
    records: Iterable[SessionRecord],
    diagnostics: Iterable[str],
    *,
    warning_budget: int = 16_000,
    hard_budget: int = 20_000,
) -> dict[str, Any]:
    """Return evidence-backed cost tips without inventing unavailable credits."""

    diagnostics = list(diagnostics)
    sessions = sorted(records, key=lambda item: (item.created_at or "", item.session_id))
    tool_counts = [record.tool_calls for record in sessions if record.tool_calls]
    median_calls = median(tool_counts) if tool_counts else 0
    explicit_credits = [record.credits for record in sessions if record.credits is not None]
    total_credits = sum(explicit_credits) if explicit_credits else None
    tips: list[dict[str, str]] = []

    if total_credits is None:
        tips.append(
            _tip(
                "measurement",
                "Capture AI-credit usage",
                (
                    "The selected source does not expose AI credits. Preserve token or usage "
                    "fields in the session event store so budget warnings are evidence-based."
                ),
                "No credits/ai_credits/credit_usage column was available.",
                "Enables budget enforcement",
                "high",
            )
        )
    elif total_credits >= hard_budget:
        tips.append(
            _tip(
                "budget",
                "Hard budget exceeded",
                (
                    "Stop exploratory work and resume from a checkpoint in a new, narrowly "
                    "scoped session."
                ),
                f"{total_credits:g} credits >= hard threshold {hard_budget}",
                "Prevents further overrun",
                "high",
            )
        )
    elif total_credits >= warning_budget:
        tips.append(
            _tip(
                "budget",
                "Approaching session budget",
                (
                    "Switch to targeted searches, delegate only bounded work, and validate "
                    "once at the end."
                ),
                f"{total_credits:g} credits >= warning threshold {warning_budget}",
                "10-25% of remaining budget",
                "high",
            )
        )

    heavy_threshold = max(500, median_calls * 3 if median_calls else 500)
    heavy = [record for record in sessions if record.tool_calls >= heavy_threshold]
    if heavy:
        tips.append(
            _tip(
                "session-shape",
                "Split tool-heavy sessions",
                (
                    "Create checkpoint boundaries between exploration, implementation, and "
                    "validation instead of carrying every lane in one session."
                ),
                (
                    f"{len(heavy)} session(s) used at least {heavy_threshold:g} tool calls; "
                    f"median was {median_calls:g}."
                ),
                "20-40% fewer repeated calls",
                "high",
            )
        )

    repeated = sum(record.repeated_tool_calls for record in sessions)
    if repeated:
        tips.append(
            _tip(
                "redundancy",
                "Reduce repeated tool calls",
                (
                    "Cache file summaries and use one bounded search per question before "
                    "opening additional files."
                ),
                f"{repeated} repeated tool-name calls were observed.",
                "10-30% fewer tool calls",
                "medium",
            )
        )

    failures = sum(len(record.blockers) for record in sessions)
    if failures:
        tips.append(
            _tip(
                "recovery",
                "Stop and triage repeated failures",
                (
                    "Record the first failure, identify its root cause, and use a focused "
                    "continuation rather than rerunning the same command."
                ),
                f"{failures} failure/blocker signal(s) were observed.",
                "Reduces retry spend",
                "medium",
            )
        )

    without_checkpoints = [record for record in heavy if record.checkpoints == 0]
    if without_checkpoints:
        tips.append(
            _tip(
                "checkpointing",
                "Checkpoint before validation",
                (
                    "Persist a checkpoint after each independently verifiable lane and resume "
                    "it instead of reloading repository context."
                ),
                f"{len(without_checkpoints)} heavy session(s) had no checkpoint signal.",
                "15-35% lower context overhead",
                "high",
            )
        )

    input_values = [record.input_tokens for record in sessions if record.input_tokens is not None]
    output_values = [
        record.output_tokens for record in sessions if record.output_tokens is not None
    ]
    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "scope": {"sessions": len(sessions)},
        "metrics": {
            "sessions": len(sessions),
            "tool_calls": sum(record.tool_calls for record in sessions),
            "median_tool_calls": median_calls,
            "input_tokens": sum(input_values) if input_values else None,
            "output_tokens": sum(output_values) if output_values else None,
            "credits": total_credits,
            "credits_available": total_credits is not None,
            "warning_budget": warning_budget,
            "hard_budget": hard_budget,
        },
        "diagnostics": sorted(set(diagnostics)),
        "tips": tips,
    }


def format_cost_tips(report: dict[str, Any]) -> str:
    """Format a cost report for terminal use."""

    metrics = report["metrics"]
    lines = [
        "# Chronicle Cost Tips",
        f"Sessions: {metrics['sessions']}",
        f"Tool calls: {metrics['tool_calls']}",
        f"Median tool calls/session: {metrics['median_tool_calls']}",
    ]
    if metrics["credits_available"]:
        lines.append(f"Credits: {metrics['credits']}")
    else:
        lines.append("Credits: unavailable (tool-call proxies only)")
    if report["diagnostics"]:
        lines.append("Diagnostics: " + "; ".join(report["diagnostics"]))
    for index, tip in enumerate(report["tips"], 1):
        lines.extend(
            [
                f"\n{index}. {tip['title']} [{tip['category']}]",
                tip["description"],
                f"Evidence: {tip['evidence']}",
                f"Estimated savings: {tip['estimated_savings']} ({tip['confidence']} confidence)",
            ]
        )
    return "\n".join(lines)


def build_standup_report(
    records: Iterable[SessionRecord],
    diagnostics: Iterable[str],
    *,
    task_id: str | None = None,
) -> dict[str, Any]:
    """Build a task-scoped completion and gap report."""

    diagnostics = list(diagnostics)
    sessions = sorted(records, key=lambda item: (item.created_at or "", item.session_id))
    completed_statuses = {"complete", "completed", "succeeded", "success"}
    completed = [
        record for record in sessions if (record.status or "").lower() in completed_statuses
    ]
    blockers = sorted({blocker for record in sessions for blocker in record.blockers})
    missing_work = list(diagnostics)
    for record in sessions:
        if (record.status or "").lower() not in completed_statuses:
            missing_work.append(
                (
                    f"Session {record.session_id} is not complete "
                    f"(status: {record.status or 'unknown'})."
                )
            )
        if record.uncommitted_changes:
            missing_work.append(
                (
                    f"Session {record.session_id} reports {record.uncommitted_changes} "
                    "uncommitted change(s)."
                )
            )
    if not sessions:
        missing_work.append("No linked session records were found; completion cannot be confirmed.")

    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "task_id": task_id,
        "source_diagnostics": sorted(set(diagnostics)),
        "sessions": [asdict(record) for record in sessions],
        "summary": {
            "sessions": len(sessions),
            "completed_sessions": len(completed),
            "incomplete_sessions": len(sessions) - len(completed),
            "commits": sum(record.commits for record in sessions),
            "tests": sum(record.tests for record in sessions),
            "tool_calls": sum(record.tool_calls for record in sessions),
            "open_blockers": blockers,
            "uncommitted_changes": sum(record.uncommitted_changes or 0 for record in sessions),
        },
        "missing_work": sorted(set(missing_work)),
    }


def format_standup(report: dict[str, Any]) -> str:
    """Format a standup report for terminal use."""

    summary = report["summary"]
    lines = [
        "# Chronicle Standup",
        f"Task: {report['task_id'] or 'all available sessions'}",
        (
            f"Sessions: {summary['sessions']} ({summary['completed_sessions']} complete, "
            f"{summary['incomplete_sessions']} incomplete)"
        ),
        f"Commits: {summary['commits']}",
        f"Tests: {summary['tests']}",
        f"Tool calls: {summary['tool_calls']}",
        f"Uncommitted changes: {summary['uncommitted_changes']}",
        "Open blockers: "
        + (", ".join(summary["open_blockers"]) if summary["open_blockers"] else "none observed"),
        "Missing work: "
        + (", ".join(report["missing_work"]) if report["missing_work"] else "none observed"),
    ]
    return "\n".join(lines)


def build_chronicle_index(
    records: Iterable[SessionRecord],
    diagnostics: Iterable[str],
    *,
    scope: str = "local Chronicle session store",
) -> dict[str, Any]:
    """Build a deterministic, searchable summary from normalized sessions."""

    sessions = sorted(records, key=lambda item: (item.created_at or "", item.session_id), reverse=True)
    status_counts: dict[str, int] = defaultdict(int)
    branch_counts: dict[str, int] = defaultdict(int)
    for record in sessions:
        status_counts[record.status or "unknown"] += 1
        branch_counts[record.branch or "unknown"] += 1

    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "scope": scope,
        "summary": {
            "total_sessions": len(sessions),
            "commits": sum(record.commits for record in sessions),
            "tests": sum(record.tests for record in sessions),
            "tool_calls": sum(record.tool_calls for record in sessions),
            "status_distribution": dict(sorted(status_counts.items())),
            "branch_distribution": dict(sorted(branch_counts.items())),
        },
        "sessions": [asdict(record) for record in sessions],
        "source_diagnostics": list(diagnostics),
    }


def dump_json(payload: dict[str, Any]) -> str:
    """Serialize report data consistently for CLI and tests."""

    return json.dumps(payload, indent=2, sort_keys=True)
