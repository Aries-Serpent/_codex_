"""Utilities for writing structured run parameter and metric logs."""

from __future__ import annotations

import json
import time
from collections.abc import Mapping as MappingABC
from collections.abc import Sequence as SequenceABC
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from codex_ml.tracking.writers import BaseWriter, NdjsonWriter

PARAMS_SCHEMA_URI = "https://codexml.ai/schemas/run_params.schema.json"
METRICS_SCHEMA_URI = "https://codexml.ai/schemas/run_metrics.schema.json"
DEFAULT_SCHEMA_VERSION = "v1"


def _jsonify(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, MappingABC):
        return {str(k): _jsonify(v) for k, v in value.items()}
    if isinstance(value, SequenceABC) and not isinstance(value, (str, bytes, bytearray)):
        return [_jsonify(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _normalize_mapping(value: Mapping[str, Any] | None) -> Dict[str, Any]:
    if value is None:
        return {}
    return {str(k): _jsonify(v) for k, v in value.items()}


def _normalize_cli(cli: Any) -> Dict[str, Any]:
    if cli is None:
        return {"argv": []}
    if isinstance(cli, SequenceABC) and not isinstance(cli, (str, bytes, bytearray)):
        return {"argv": [str(item) for item in cli]}
    if isinstance(cli, MappingABC):
        argv = cli.get("argv", [])  # type: ignore[arg-type]
        if isinstance(argv, SequenceABC) and not isinstance(argv, (str, bytes, bytearray)):
            argv_list = [str(item) for item in argv]
        elif argv is None:
            argv_list = []
        else:
            argv_list = [str(argv)]
        payload: Dict[str, Any] = {"argv": argv_list}
        options = cli.get("options")  # type: ignore[arg-type]
        if isinstance(options, MappingABC):
            payload["options"] = _normalize_mapping(options)
        for key, value in cli.items():
            if key in {"argv", "options"}:
                continue
            payload[str(key)] = _jsonify(value)
        return payload
    return {"argv": [str(cli)]}


class RunLogger:
    """Write params and metrics for a run using a shared schema."""

    def __init__(
        self,
        run_dir: str | Path,
        run_id: str,
        *,
        schema_version: str = DEFAULT_SCHEMA_VERSION,
        params_path: str | Path | None = None,
        metrics_path: str | Path | None = None,
    ) -> None:
        self.run_dir = Path(run_dir)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.run_id = str(run_id)
        self.schema_version = schema_version
        self.params_path = (
            Path(params_path) if params_path is not None else self.run_dir / "params.ndjson"
        )
        self.params_path.parent.mkdir(parents=True, exist_ok=True)
        self.metrics_path = (
            Path(metrics_path) if metrics_path is not None else self.run_dir / "metrics.ndjson"
        )
        self.metrics_path.parent.mkdir(parents=True, exist_ok=True)
        self._metrics_writer: BaseWriter = NdjsonWriter(
            self.metrics_path, schema_uri=METRICS_SCHEMA_URI, schema_version=schema_version
        )

    def log_params(
        self,
        *,
        cli: Any = None,
        config: Mapping[str, Any] | None = None,
        derived: Mapping[str, Any] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> Dict[str, Any]:
        record: Dict[str, Any] = {
            "$schema": PARAMS_SCHEMA_URI,
            "schema_version": self.schema_version,
            "timestamp": time.time(),
            "run_id": self.run_id,
            "cli": _normalize_cli(cli),
            "config": _normalize_mapping(config),
            "derived": _normalize_mapping(derived),
        }
        if metadata:
            record["metadata"] = _normalize_mapping(metadata)
        line = json.dumps(_jsonify(record), ensure_ascii=True)
        with self.params_path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
        return record

    def log_metric(
        self,
        *,
        step: int,
        split: str,
        metric: str,
        value: Any,
        dataset: Optional[str] = None,
        tags: Mapping[str, Any] | None = None,
    ) -> Dict[str, Any]:
        metric_value: Any
        if value is None:
            metric_value = None
        else:
            metric_value = float(value)
        record: Dict[str, Any] = {
            "$schema": METRICS_SCHEMA_URI,
            "schema_version": self.schema_version,
            "timestamp": time.time(),
            "run_id": self.run_id,
            "step": int(step),
            "split": str(split),
            "metric": str(metric),
            "value": metric_value,
            "dataset": None if dataset is None else str(dataset),
            "tags": _normalize_mapping(tags),
        }
        self._metrics_writer.log(record)
        return record

    def close(self) -> None:
        try:
            self._metrics_writer.close()
        except Exception:  # pragma: no cover - best effort
            pass


__all__ = ["RunLogger", "PARAMS_SCHEMA_URI", "METRICS_SCHEMA_URI", "DEFAULT_SCHEMA_VERSION"]
