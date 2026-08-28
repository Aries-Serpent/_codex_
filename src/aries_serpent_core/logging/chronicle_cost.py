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
    lane_bucket: str | None = None
    checkpoint_state: str | None = None
    budget_remaining: int | float | None = None
    estimated_cost: int | float | None = None
    cost_score: int | float | None = None
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
        table = self._select_event_table(tables)
        if table is None:
            self.diagnostics.append("tool/event table unavailable; tool metrics are unavailable")
            return {}

        columns = self._columns(connection, table)
        session_column = next((name for name in ("session_id", "id") if name in columns), None)
        if not session_column:
            self.diagnostics.append(f"{table} has no session identifier column")
            return {}

        rows = self._fetch_event_rows(
            connection, table, columns, session_column, session_ids, start=start, end=end
        )
        grouped = self._group_event_rows(rows, session_column)
        return {
            session_id: self._aggregate_event_rows(session_rows, columns, table)
            for session_id, session_rows in grouped.items()
        }

    def _select_event_table(self, tables: set[str]) -> str | None:
        for candidate in ("tool_calls", "events", "session_events"):
            if candidate in tables:
                return candidate
        return None

    def _fetch_event_rows(
        self,
        connection: sqlite3.Connection,
        table: str,
        columns: set[str],
        session_column: str,
        session_ids: set[str],
        *,
        start: str | None = None,
        end: str | None = None,
    ) -> list[sqlite3.Row]:
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
        return connection.execute(
            f"SELECT * FROM {_quote_identifier(table)} WHERE {' AND '.join(conditions)}",
            parameters,
        ).fetchall()

    @staticmethod
    def _group_event_rows(
        rows: list[sqlite3.Row], session_column: str
    ) -> dict[str, list[sqlite3.Row]]:
        grouped: dict[str, list[sqlite3.Row]] = defaultdict(list)
        for row in rows:
            if row[session_column]:
                grouped[str(row[session_column])].append(row)
        return grouped

    def _aggregate_event_rows(
        self,
        session_rows: list[sqlite3.Row],
        columns: set[str],
        table: str,
    ) -> dict[str, Any]:
        tool_rows = [
            row for row in session_rows if table == "tool_calls" or self._is_tool_row(row, columns)
        ]
        tool_names = [
            str(value)
            for row in tool_rows
            if (value := _first(row, columns, "tool_name", "name", "tool_start_name"))
        ]
        text = self._extract_event_text(session_rows, columns)
        input_tokens = self._sum_token_metric(session_rows, columns, "input_tokens", "usage_input_tokens")
        output_tokens = self._sum_token_metric(session_rows, columns, "output_tokens", "usage_output_tokens")
        lane_bucket = _first(
            session_rows[0] if session_rows else sqlite3.Row, columns, "lane_bucket", "lane", "lane_name", "lane_id"
        ) if session_rows else None
        checkpoint_state = _first(
            session_rows[0] if session_rows else sqlite3.Row, columns, "checkpoint_state", "checkpoint_status", "checkpoint"
        ) if session_rows else None
        budget_remaining = _first(
            session_rows[0] if session_rows else sqlite3.Row, columns, "budget_remaining", "remaining_budget", "remaining_credits"
        ) if session_rows else None
        estimated_cost = _first(
            session_rows[0] if session_rows else sqlite3.Row, columns, "estimated_cost", "cost_estimate", "session_cost"
        ) if session_rows else None
        cost_score = _first(
            session_rows[0] if session_rows else sqlite3.Row, columns, "cost_score", "budget_score", "cost"
        ) if session_rows else None
        return {
            "tool_calls": len(tool_rows),
            "repeated_tool_calls": len(tool_names) - len(set(tool_names)),
            "input_tokens": input_tokens if self._has_token_value(session_rows, columns, "input_tokens", "usage_input_tokens") else None,
            "output_tokens": output_tokens if self._has_token_value(session_rows, columns, "output_tokens", "usage_output_tokens") else None,
            "credits": self._sum_credits(session_rows, columns),
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
            "lane_bucket": lane_bucket,
            "checkpoint_state": checkpoint_state,
            "budget_remaining": budget_remaining,
            "estimated_cost": estimated_cost,
            "cost_score": cost_score,
        }

    @staticmethod
    def _extract_event_text(session_rows: list[sqlite3.Row], columns: set[str]) -> str:
        parts = []
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
                    parts.append(str(value))
        return "\n".join(parts)

    @staticmethod
    def _sum_token_metric(
        session_rows: list[sqlite3.Row], columns: set[str], *names: str
    ) -> int | float:
        return sum(
            (_as_number(_first(row, columns, *names)) or 0) for row in session_rows
        )

    @staticmethod
    def _has_token_value(
        session_rows: list[sqlite3.Row], columns: set[str], *names: str
    ) -> bool:
        return any(
            _as_number(_first(row, columns, *names)) is not None for row in session_rows
        )

    @staticmethod
    def _sum_credits(session_rows: list[sqlite3.Row], columns: set[str]) -> int | float | None:
        values = [
            _as_number(
                _first(row, columns, "credits", "ai_credits", "credit_usage", "total_credits")
            )
            for row in session_rows
        ]
        available = [value for value in values if value is not None]
        return sum(available) if available else None

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

            rows = self._fetch_session_rows(connection, columns, id_column, session_id, start, end)
            matched_rows = self._match_session_rows(connection, tables, columns, id_column, rows, task_id)
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
            records = [
                self._build_session_record(row, current_id, ref_tasks, columns, event_data)
                for row, current_id, ref_tasks in matched_rows
            ]

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

    def _fetch_session_rows(
        self,
        connection: sqlite3.Connection,
        columns: set[str],
        id_column: str,
        session_id: str | None,
        start: str | None,
        end: str | None,
    ) -> list[sqlite3.Row]:
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
        return connection.execute(query, parameters).fetchall()

    def _match_session_rows(
        self,
        connection: sqlite3.Connection,
        tables: set[str],
        columns: set[str],
        id_column: str,
        rows: list[sqlite3.Row],
        task_id: str | None,
    ) -> list[tuple[sqlite3.Row, str, set[str]]]:
        matched: list[tuple[sqlite3.Row, str, set[str]]] = []
        normalized_filter = _normalise_task_id(task_id)
        for row in rows:
            current_id = str(row[id_column])
            direct_task = _first(row, columns, "task_id", "task")
            ref_tasks = self._session_task_ids(connection, tables, current_id)
            record_task = _normalise_task_id(direct_task) or next(iter(ref_tasks), None)
            if (
                normalized_filter
                and record_task != normalized_filter
                and normalized_filter not in ref_tasks
            ):
                continue
            matched.append((row, current_id, ref_tasks))
        return matched

    def _build_session_record(
        self,
        row: sqlite3.Row,
        current_id: str,
        ref_tasks: set[str],
        columns: set[str],
        event_data: dict[str, dict[str, Any]],
    ) -> SessionRecord:
        direct_task = _first(row, columns, "task_id", "task")
        record_task = _normalise_task_id(direct_task) or next(iter(ref_tasks), None)
        data = event_data.get(current_id, {})
        lane_bucket = _first(
            row,
            columns,
            "lane_bucket",
            "lane",
            "lane_name",
            "lane_id",
        ) or data.get("lane_bucket")
        checkpoint_state = _first(
            row,
            columns,
            "checkpoint_state",
            "checkpoint_status",
        ) or data.get("checkpoint_state")
        budget_remaining = _first(
            row,
            columns,
            "budget_remaining",
            "remaining_budget",
            "remaining_credits",
        )
        if budget_remaining is None:
            budget_remaining = data.get("budget_remaining")
        estimated_cost = _first(
            row,
            columns,
            "estimated_cost",
            "cost_estimate",
            "session_cost",
        )
        if estimated_cost is None:
            estimated_cost = data.get("estimated_cost")
        cost_score = _first(
            row,
            columns,
            "cost_score",
            "budget_score",
            "cost",
        )
        if cost_score is None:
            cost_score = data.get("cost_score")
        return SessionRecord(
            session_id=current_id,
            task_id=record_task,
            created_at=_first(row, columns, "created_at", "timestamp", "started_at"),
            updated_at=_first(row, columns, "updated_at", "ended_at", "completed_at"),
            status=_first(row, columns, "status", "state"),
            agent_name=_first(row, columns, "agent_name", "agent"),
            repository=_first(row, columns, "repository", "repo"),
            branch=_first(row, columns, "branch"),
            summary=_first(row, columns, "summary", "task", "description"),
            lane_bucket=str(lane_bucket) if lane_bucket else None,
            checkpoint_state=str(checkpoint_state) if checkpoint_state else None,
            budget_remaining=_prefer_number(budget_remaining),
            estimated_cost=_prefer_number(estimated_cost),
            cost_score=_prefer_number(cost_score),
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


class _TipStrategy:
    """Base for pluggable cost-tip strategies."""

    category: str = ""
    title: str = ""
    description: str = ""
    savings: str = ""
    confidence: str = ""

    def applies(self, ctx: _CostContext) -> bool:
        raise NotImplementedError

    def evidence(self, ctx: _CostContext) -> str:
        raise NotImplementedError

    def build(self, ctx: _CostContext) -> dict[str, str]:
        return {
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "evidence": self.evidence(ctx),
            "estimated_savings": self.savings,
            "confidence": self.confidence,
        }


class _MeasurementTip(_TipStrategy):
    category = "measurement"
    title = "Capture AI-credit usage"
    description = (
        "The selected source does not expose AI credits. Preserve token or usage "
        "fields in the session event store so budget warnings are evidence-based."
    )
    savings = "Enables budget enforcement"
    confidence = "high"

    def applies(self, ctx: _CostContext) -> bool:
        return ctx.total_credits is None

    def evidence(self, ctx: _CostContext) -> str:
        return "No credits/ai_credits/credit_usage column was available."


class _HardBudgetTip(_TipStrategy):
    category = "budget"
    title = "Hard budget exceeded"
    description = (
        "Stop exploratory work and resume from a checkpoint in a new, narrowly scoped session."
    )
    savings = "Prevents further overrun"
    confidence = "high"

    def applies(self, ctx: _CostContext) -> bool:
        return ctx.total_credits is not None and ctx.total_credits >= ctx.hard_budget

    def evidence(self, ctx: _CostContext) -> str:
        return f"{ctx.total_credits:g} credits >= hard threshold {ctx.hard_budget}"


class _WarningBudgetTip(_TipStrategy):
    category = "budget"
    title = "Approaching session budget"
    description = (
        "Switch to targeted searches, delegate only bounded work, and validate once at the end."
    )
    savings = "10-25% of remaining budget"
    confidence = "high"

    def applies(self, ctx: _CostContext) -> bool:
        return (
            ctx.total_credits is not None
            and ctx.warning_budget <= ctx.total_credits < ctx.hard_budget
        )

    def evidence(self, ctx: _CostContext) -> str:
        return f"{ctx.total_credits:g} credits >= warning threshold {ctx.warning_budget}"


class _HeavySessionTip(_TipStrategy):
    category = "session-shape"
    title = "Split tool-heavy sessions"
    description = (
        "Create checkpoint boundaries between exploration, implementation, and validation "
        "instead of carrying every lane in one session."
    )
    savings = "20-40% fewer repeated calls"
    confidence = "high"

    def applies(self, ctx: _CostContext) -> bool:
        return bool(ctx.heavy)

    def evidence(self, ctx: _CostContext) -> str:
        return (
            f"{len(ctx.heavy)} session(s) used at least {ctx.heavy_threshold:g} tool calls; "
            f"median was {ctx.median_calls:g}."
        )


class _RepeatedCallsTip(_TipStrategy):
    category = "redundancy"
    title = "Reduce repeated tool calls"
    description = (
        "Cache file summaries and use one bounded search per question before opening "
        "additional files."
    )
    savings = "10-30% fewer tool calls"
    confidence = "medium"

    def applies(self, ctx: _CostContext) -> bool:
        return ctx.repeated > 0

    def evidence(self, ctx: _CostContext) -> str:
        return f"{ctx.repeated} repeated tool-name calls were observed."


class _FailureTip(_TipStrategy):
    category = "recovery"
    title = "Stop and triage repeated failures"
    description = (
        "Record the first failure, identify its root cause, and use a focused continuation "
        "rather than rerunning the same command."
    )
    savings = "Reduces retry spend"
    confidence = "medium"

    def applies(self, ctx: _CostContext) -> bool:
        return ctx.failures > 0

    def evidence(self, ctx: _CostContext) -> str:
        return f"{ctx.failures} failure/blocker signal(s) were observed."


class _CheckpointTip(_TipStrategy):
    category = "checkpointing"
    title = "Checkpoint before validation"
    description = (
        "Persist a checkpoint after each independently verifiable lane and resume it instead "
        "of reloading repository context."
    )
    savings = "15-35% lower context overhead"
    confidence = "high"

    def applies(self, ctx: _CostContext) -> bool:
        return bool(ctx.without_checkpoints)

    def evidence(self, ctx: _CostContext) -> str:
        return f"{len(ctx.without_checkpoints)} heavy session(s) had no checkpoint signal."


class _CostContext:
    """Shared data passed to each cost-tip strategy."""

    def __init__(
        self,
        records: list[SessionRecord],
        diagnostics: list[str],
        warning_budget: int,
        hard_budget: int,
    ) -> None:
        self.sessions = records
        self.diagnostics = diagnostics
        self.warning_budget = warning_budget
        self.hard_budget = hard_budget

        tool_counts = [record.tool_calls for record in records if record.tool_calls]
        self.median_calls = median(tool_counts) if tool_counts else 0
        explicit_credits = [record.credits for record in records if record.credits is not None]
        self.total_credits: int | float | None = sum(explicit_credits) if explicit_credits else None
        self.heavy_threshold = max(500, self.median_calls * 3 if self.median_calls else 500)
        self.heavy = [record for record in records if record.tool_calls >= self.heavy_threshold]
        self.repeated = sum(record.repeated_tool_calls for record in records)
        self.failures = sum(len(record.blockers) for record in records)
        self.without_checkpoints = [record for record in self.heavy if record.checkpoints == 0]

    @property
    def input_values(self) -> list[int | float]:
        return [record.input_tokens for record in self.sessions if record.input_tokens is not None]

    @property
    def output_values(self) -> list[int | float]:
        return [
            record.output_tokens for record in self.sessions if record.output_tokens is not None
        ]


def _normalize_lane(value: str | None) -> str:
    """Coerce lane values to the repo's canonical buckets."""

    if value is None:
        return "unknown"
    normalised = str(value).strip()
    if not normalised:
        return "unknown"
    upper = normalised.upper().replace(" ", "_")
    aliases = {
        "P1": "P1",
        "PRIMARY": "P1",
        "P2": "P2",
        "SECONDARY": "P2",
        "S1": "S1",
        "SUPPORT": "S1",
        "SEQ": "Seq",
        "SEQUENTIAL": "Seq",
        "VALIDATION": "Seq",
        "REVIEW": "Seq",
    }
    return aliases.get(upper, upper if upper else "unknown")


def analyze_costs(
    records: Iterable[SessionRecord],
    diagnostics: Iterable[str],
    *,
    warning_budget: int = 16_000,
    hard_budget: int = 20_000,
    lane: str | None = None,
) -> dict[str, Any]:
    """Return evidence-backed cost tips without inventing unavailable credits."""

    diagnostics = list(diagnostics)
    sessions = sorted(records, key=lambda item: (item.created_at or "", item.session_id))
    lane_filter = _normalize_lane(lane)
    if lane is not None:
        sessions = [record for record in sessions if _normalize_lane(record.lane_bucket) == lane_filter]
    ctx = _CostContext(sessions, diagnostics, warning_budget, hard_budget)

    strategies: list[_TipStrategy] = [
        _MeasurementTip(),
        _HardBudgetTip(),
        _WarningBudgetTip(),
        _HeavySessionTip(),
        _RepeatedCallsTip(),
        _FailureTip(),
        _CheckpointTip(),
    ]
    tips = [strategy.build(ctx) for strategy in strategies if strategy.applies(ctx)]

    lane_summary: dict[str, dict[str, Any]] = {}
    for record in sessions:
        bucket = _normalize_lane(record.lane_bucket)
        entry = lane_summary.setdefault(
            bucket,
            {
                "sessions": 0,
                "tool_calls": 0,
                "repeated_tool_calls": 0,
                "estimated_cost": 0.0,
                "budget_remaining": None,
                "warning_budget": warning_budget,
                "hard_budget": hard_budget,
                "heavy_sessions": [],
                "checkpoint_gap": 0,
            },
        )
        entry["sessions"] += 1
        entry["tool_calls"] += record.tool_calls
        entry["repeated_tool_calls"] += record.repeated_tool_calls
        entry["estimated_cost"] += float(record.estimated_cost or 0)
        if record.budget_remaining is not None:
            if entry["budget_remaining"] is None:
                entry["budget_remaining"] = float(record.budget_remaining)
            else:
                entry["budget_remaining"] += float(record.budget_remaining)
        if record.tool_calls >= max(500, int(ctx.median_calls * 3 if ctx.median_calls else 500)):
            entry["heavy_sessions"].append(record.session_id)
        if record.checkpoints == 0 and record.tool_calls >= max(500, int(ctx.median_calls * 3 if ctx.median_calls else 500)):
            entry["checkpoint_gap"] += 1

    heavy_by_lane = {
        bucket: details["heavy_sessions"]
        for bucket, details in lane_summary.items()
        if details["heavy_sessions"]
    }
    warning_budget_by_lane = {
        bucket: {
            "warning_budget": details["warning_budget"],
            "hard_budget": details["hard_budget"],
            "budget_remaining": details["budget_remaining"],
            "status": "warning" if details["budget_remaining"] is not None and details["budget_remaining"] <= details["warning_budget"] else "healthy",
        }
        for bucket, details in lane_summary.items()
    }

    report = {
        "schema_version": "1.0",
        "generated_at": _now(),
        "scope": {"sessions": len(sessions), "lane": lane_filter if lane else None},
        "metrics": {
            "sessions": len(sessions),
            "tool_calls": sum(record.tool_calls for record in sessions),
            "median_tool_calls": ctx.median_calls,
            "input_tokens": sum(ctx.input_values) if ctx.input_values else None,
            "output_tokens": sum(ctx.output_values) if ctx.output_values else None,
            "credits": ctx.total_credits,
            "credits_available": ctx.total_credits is not None,
            "warning_budget": warning_budget,
            "hard_budget": hard_budget,
        },
        "global_summary": {
            "sessions": len(sessions),
            "tool_calls": sum(record.tool_calls for record in sessions),
            "repeated_tool_calls": sum(record.repeated_tool_calls for record in sessions),
            "heavy_session_count": len(ctx.heavy),
            "checkpoint_gap_count": len(ctx.without_checkpoints),
            "estimated_cost": sum(float(record.estimated_cost or 0.0) for record in sessions),
        },
        "per_lane": lane_summary,
        "heavy_sessions_by_lane": heavy_by_lane,
        "warning_budget_by_lane": warning_budget_by_lane,
        "diagnostics": sorted(set(diagnostics)),
        "tips": tips,
    }
    if lane is not None:
        report["lane_focus"] = lane_filter
        report["lane_pattern"] = "fragmented" if len(sessions) > 1 and sum(r.tool_calls for r in sessions) >= warning_budget / 2 else "batchable"
    return report


def format_cost_tips(report: dict[str, Any]) -> str:
    """Format a cost report for terminal use."""

    metrics = report["metrics"]
    lines = [
        "# Chronicle Cost Tips",
        f"Sessions: {metrics['sessions']}",
        f"Tool calls: {metrics['tool_calls']}",
        f"Median tool calls/session: {metrics['median_tool_calls']}",
    ]
    if report.get("lane_focus"):
        lines.append(f"Lane focus: {report['lane_focus']}")
        lines.append(f"Lane pattern: {report.get('lane_pattern', 'batchable')}")
    if metrics["credits_available"]:
        lines.append(f"Credits: {metrics['credits']}")
    else:
        lines.append("Credits: unavailable (tool-call proxies only)")
    if report.get("per_lane"):
        lines.append("Per-lane summary:")
        for lane, summary in sorted(report["per_lane"].items()):
            lines.append(
                f"  - {lane}: {summary['sessions']} sessions, {summary['tool_calls']} tool calls, "
                f"checkpoint gap {summary['checkpoint_gap']}"
            )
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
    lane: str | None = None,
) -> dict[str, Any]:
    """Build a task-scoped completion and gap report."""

    diagnostics = list(diagnostics)
    sessions = sorted(records, key=lambda item: (item.created_at or "", item.session_id))
    if lane is not None:
        lane_filter = _normalize_lane(lane)
        sessions = [record for record in sessions if _normalize_lane(record.lane_bucket) == lane_filter]
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

    lane_pattern = "fragmented" if len(sessions) > 1 and sum(r.tool_calls for r in sessions) >= 500 else "batchable"
    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "task_id": task_id,
        "lane": _normalize_lane(lane) if lane else None,
        "lane_pattern": lane_pattern,
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
        f"Lane focus: {report.get('lane') or 'all'}",
        f"Lane pattern: {report.get('lane_pattern', 'batchable')}",
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
