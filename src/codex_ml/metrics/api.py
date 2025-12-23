"""Public metrics facade for codex_ml.

Re-export stable metric utilities here to avoid import churn downstream.
Keep imports lazy/minimal to prevent import-time cost.

This module provides:
1. Re-exports of metric registry functions
2. NDJSON log summarization utilities (to CSV/SQLite)
3. Public API for metric computation and tracking
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

import csv
import json
from pathlib import Path
from typing import Any, Callable, Optional, Sequence

__all__ = [
    # Registry functions
    "register_metric",
    "get_metric",
    "list_metrics",
    "init_metric_plugins",
    # NDJSON utilities
    "summarize_ndjson_logs",
    "summarize_ndjson_to_csv",
    "summarize_ndjson_to_sqlite",
    "load_ndjson_logs",
    # Built-in metrics
    "token_accuracy",
    "perplexity",
    "exact_match",
    "f1",
]


# Lazy imports to avoid circular dependencies and reduce import cost
def register_metric(
    name: str,
    fn: Optional[Callable[..., object]] = None,
    *,
    override: bool = False,
) -> Callable[..., object]:
    """Register a metric function.

    Args:
        name: Metric name for lookup
        fn: Metric function (preds, targets, **kwargs) -> float | dict | None
        override: Whether to override existing metric with same name

    Returns:
        The registered metric function (decorator compatible)
    """
    from codex_ml.metrics.registry import metric_registry

    return metric_registry.register(name, fn, override=override)


def get_metric(name: str) -> Callable[..., object]:
    """Get a registered metric by name.

    Args:
        name: Metric name

    Returns:
        Metric function

    Raises:
        KeyError: If metric not found
    """
    from codex_ml.metrics.registry import metric_registry

    return metric_registry.get(name)


def list_metrics() -> list[str]:
    """List all registered metric names.

    Returns:
        List of metric names
    """
    from codex_ml.metrics.registry import metric_registry

    return metric_registry.list()


def init_metric_plugins(*, force: bool = False) -> int:
    """Initialize metric plugins from entry points.

    Args:
        force: Force re-initialization even if already loaded

    Returns:
        Number of plugins loaded
    """
    from codex_ml.metrics.registry import init_metric_plugins as _init

    return _init(force=force)


# Built-in metrics (lazy loaded)
def token_accuracy(preds: Sequence[Any], targets: Sequence[Any], **kwargs: Any) -> float:
    """Calculate token-level accuracy.

    Args:
        preds: Predicted tokens
        targets: Target tokens
        **kwargs: Additional arguments

    Returns:
        Accuracy score (0.0 to 1.0)
    """
    from codex_ml.metrics.registry import token_accuracy as _impl

    return _impl(preds, targets, **kwargs)


def perplexity(preds: Sequence[Any], targets: Sequence[Any], **kwargs: Any) -> float:
    """Calculate perplexity metric.

    Args:
        preds: Predicted tokens/logits
        targets: Target tokens
        **kwargs: Additional arguments

    Returns:
        Perplexity score
    """
    from codex_ml.metrics.registry import perplexity as _impl

    return _impl(preds, targets, **kwargs)


def exact_match(preds: Sequence[Any], targets: Sequence[Any], **kwargs: Any) -> float:
    """Calculate exact match score.

    Args:
        preds: Predicted sequences
        targets: Target sequences
        **kwargs: Additional arguments

    Returns:
        Exact match score (0.0 to 1.0)
    """
    from codex_ml.metrics.registry import exact_match as _impl

    return _impl(preds, targets, **kwargs)


def f1(preds: Sequence[Any], targets: Sequence[Any], **kwargs: Any) -> float:
    """Calculate F1 score.

    Args:
        preds: Predicted labels
        targets: Target labels
        **kwargs: Additional arguments

    Returns:
        F1 score (0.0 to 1.0)
    """
    from codex_ml.metrics.registry import f1 as _impl

    return _impl(preds, targets, **kwargs)


# NDJSON log summarization utilities
def load_ndjson_logs(path: str | Path) -> list[dict[str, Any]]:
    """Load NDJSON logs from a file.

    Args:
        path: Path to NDJSON file

    Returns:
        List of log entries as dictionaries
    """
    logs: list[dict[str, Any]] = []
    path_obj = Path(path)

    if not path_obj.exists():
        return logs

    with path_obj.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                logs.append(json.loads(line))
            except json.JSONDecodeError:
                # Skip malformed lines
                continue

    return logs


def summarize_ndjson_logs(path: str | Path) -> dict[str, float]:
    """Summarize NDJSON logs by computing mean of numeric fields.

    Flattens nested dictionaries using dot notation and computes the mean
    for all numeric fields across all log entries.

    Args:
        path: Path to NDJSON file

    Returns:
        Dictionary mapping field names to their mean values

    Raises:
        ValueError: If the file contains invalid JSON
    """
    logs = []
    path_obj = Path(path)

    if not path_obj.exists():
        return {}

    with path_obj.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                logs.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON on line {line_num}: {e}") from e

    if not logs:
        return {}

    # Flatten nested dictionaries and collect numeric values
    def flatten_dict(d: dict[str, Any], prefix: str = "") -> dict[str, Any]:
        """Flatten nested dictionary with dot notation."""
        result = {}
        for key, value in d.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                result.update(flatten_dict(value, full_key))
            else:
                result[full_key] = value
        return result

    # Collect all values for each field
    field_values: dict[str, list[float]] = {}
    for log in logs:
        flat_log = flatten_dict(log)
        for key, value in flat_log.items():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                if key not in field_values:
                    field_values[key] = []
                field_values[key].append(float(value))

    # Compute means
    return {key: sum(values) / len(values) for key, values in field_values.items()}


def summarize_ndjson_to_csv(
    ndjson_path: str | Path,
    csv_path: str | Path,
    *,
    columns: Optional[list[str]] = None,
) -> int:
    """Summarize NDJSON logs to CSV format.

    Args:
        ndjson_path: Path to input NDJSON file
        csv_path: Path to output CSV file
        columns: Optional list of columns to include (default: all unique keys)

    Returns:
        Number of rows written
    """
    logs = load_ndjson_logs(ndjson_path)

    if not logs:
        # Create empty CSV file
        Path(csv_path).write_text("", encoding="utf-8")
        return 0

    # Determine columns if not specified
    if columns is None:
        # Collect all unique keys from all log entries
        all_keys: set[str] = set()
        for log in logs:
            all_keys.update(log.keys())
        columns = sorted(all_keys)

    # Write CSV
    csv_path_obj = Path(csv_path)
    csv_path_obj.parent.mkdir(parents=True, exist_ok=True)

    with csv_path_obj.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(logs)

    return len(logs)


def summarize_ndjson_to_sqlite(
    ndjson_path: str | Path,
    db_path: str | Path,
    *,
    table_name: str = "metrics",
) -> int:
    """Summarize NDJSON logs to SQLite database.

    Args:
        ndjson_path: Path to input NDJSON file
        db_path: Path to output SQLite database file
        table_name: Name of table to create/insert into

    Returns:
        Number of rows inserted

    Raises:
        ImportError: If sqlite3 is not available
    """
    try:
        import sqlite3
    except ImportError as exc:
        logger.debug(f"ImportError: {exc}")
        raise ImportError("sqlite3 is required for SQLite export") from exc

    logs = load_ndjson_logs(ndjson_path)

    if not logs:
        return 0

    # Collect all unique columns
    all_keys: set[str] = set()
    for log in logs:
        all_keys.update(log.keys())
    columns = sorted(all_keys)

    # Create database and table
    db_path_obj = Path(db_path)
    db_path_obj.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path_obj))
    try:
        # Create table with TEXT columns (flexible schema)
        columns_def = ", ".join(
            f'"{col}" TEXT' for col in columns
        )  # nosec B608        conn.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns_def})')

        # Insert rows
        placeholders = ", ".join("?" * len(columns))
        column_names = ", ".join(f'"{c}"' for c in columns)
        insert_sql = (
            f'INSERT INTO "{table_name}" ({column_names}) VALUES ({placeholders})'  # nosec B608
        )
        for log in logs:
            # Convert values to strings for TEXT columns
            values = [
                (
                    json.dumps(log.get(col))
                    if isinstance(log.get(col), (dict, list))
                    else str(log.get(col, ""))
                )
                for col in columns
            ]
            conn.execute(insert_sql, values)

        conn.commit()
        return len(logs)

    finally:
        conn.close()
