"""Batch restoration utilities for the archive CLI."""

from __future__ import annotations

import csv
import json
from collections.abc import Callable, Iterable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import BatchConfig, PerformanceConfig
from .perf import TimingMetrics, timer
from .retry import RetryConfig, retry_with_backoff


@dataclass(frozen=True)
class BatchItem:
    """Single manifest entry."""

    tombstone: str
    output: Path
    actor: str

    @classmethod
    def from_dict(
        cls,
        payload: dict[str, Any],
        *,
        manifest_dir: Path,
        default_actor: str,
    ) -> BatchItem:
        tombstone = str(payload.get("tombstone", "")).strip()
        if not tombstone:
            raise ValueError("Manifest entry missing tombstone identifier")
        output_raw = payload.get("output")
        if not output_raw:
            raise ValueError("Manifest entry missing output path")
        output_path = (manifest_dir / Path(output_raw)).expanduser().resolve()
        actor = str(payload.get("actor") or default_actor).strip()
        if not actor:
            raise ValueError("Actor must be provided either in manifest or via CLI")
        return cls(tombstone=tombstone, output=output_path, actor=actor)


@dataclass
class BatchResult:
    """Summary of a batch restore run."""

    total: int
    succeeded: int
    failed: int
    results: list[dict[str, Any]]
    metrics: TimingMetrics | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "succeeded": self.succeeded,
            "failed": self.failed,
            "results": self.results,
            "duration_ms": round(self.metrics.duration_ms, 3) if self.metrics else None,
        }


class BatchManifest:
    """Loader for CSV/JSON batch manifests."""

    def __init__(self, items: Iterable[BatchItem], *, path: Path) -> None:
        self.items = list(items)
        self.path = path

    @classmethod
    def from_path(
        cls,
        path: Path,
        *,
        default_actor: str,
    ) -> BatchManifest:
        manifest_path = path.resolve()
        if not manifest_path.exists():
            raise FileNotFoundError(f"Manifest file not found: {manifest_path}")
        manifest_dir = manifest_path.parent
        suffix = manifest_path.suffix.lower()
        if suffix in {".json", ".jsonl"}:
            entries = cls._load_json(manifest_path)
        elif suffix in {".csv"}:
            entries = cls._load_csv(manifest_path)
        else:
            raise ValueError("Manifest must be a JSON or CSV file")
        items = [
            BatchItem.from_dict(entry, manifest_dir=manifest_dir, default_actor=default_actor)
            for entry in entries
        ]
        if not items:
            raise ValueError("Manifest does not contain any restore entries")
        return cls(items, path=manifest_path)

    @staticmethod
    def _load_json(path: Path) -> Iterator[dict[str, Any]]:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if isinstance(payload, dict):
            payload = payload.get("items", [])
        if not isinstance(payload, list):
            raise ValueError("JSON manifest must contain a list of entries or an 'items' array")
        for entry in payload:
            if not isinstance(entry, dict):
                raise ValueError("Each manifest entry must be an object")
            yield entry

    @staticmethod
    def _load_csv(path: Path) -> Iterator[dict[str, Any]]:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                yield {k: v for k, v in row.items() if v is not None}


class BatchRestore:
    """Batch restore orchestrator."""

    def __init__(
        self,
        service: Any,
        *,
        retry_config: RetryConfig | None = None,
        batch_config: BatchConfig | None = None,
        performance_config: PerformanceConfig | None = None,
        progress_callback: Callable[[int, int, dict[str, Any]], None] | None = None,
    ) -> None:
        self.service = service
        self.retry_config = retry_config or RetryConfig()
        self.batch_config = batch_config or BatchConfig()
        self.performance_config = performance_config or PerformanceConfig()
        self.progress_callback = progress_callback

    def restore(self, manifest: BatchManifest) -> BatchResult:
        total = len(manifest.items)
        results: list[dict[str, Any]] = []
        succeeded = 0
        failed = 0
        performance_enabled = self.performance_config.enabled
        with _optional_timer(performance_enabled, "batch_restore") as metrics:
            for index, item in enumerate(manifest.items, start=1):
                entry = self._restore_single(item)
                if entry["status"] == "SUCCESS":
                    succeeded += 1
                else:
                    failed += 1
                results.append(entry)
                if self.progress_callback:
                    self.progress_callback(index, total, entry)
        return BatchResult(
            total=total,
            succeeded=succeeded,
            failed=failed,
            results=results,
            metrics=metrics if performance_enabled else None,
        )

    def save_results(self, path: Path, result: BatchResult) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(result.to_dict(), handle, indent=2)
        return path

    def _restore_single(self, item: BatchItem) -> dict[str, Any]:
        restore_fn = self.service.restore_to_path
        decorated = retry_with_backoff(self.retry_config)(restore_fn)
        status = "SUCCESS"
        detail: str | None = None
        metrics: TimingMetrics | None = None
        performance_enabled = self.performance_config.enabled
        try:
            with _optional_timer(performance_enabled, f"restore:{item.tombstone}") as metrics:
                decorated(item.tombstone, output_path=item.output, actor=item.actor)
        except Exception as exc:  # pragma: no cover - exercised in tests
            status = "FAILED"
            detail = str(exc)
        result = {
            "tombstone": item.tombstone,
            "output": item.output.as_posix(),
            "actor": item.actor,
            "status": status,
        }
        if metrics is not None and performance_enabled:
            result["duration_ms"] = round(metrics.duration_ms, 3)
            result["metrics"] = metrics.to_dict()
        if detail:
            result["detail"] = detail
        return result


@contextmanager
def _optional_timer(enabled: bool, name: str):
    if enabled:
        with timer(name) as metrics:
            yield metrics
    else:
        yield TimingMetrics(name=name, started_ns=0, finished_ns=0)
