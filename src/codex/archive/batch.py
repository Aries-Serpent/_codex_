"""Batch restore operations with progress tracking and resume support."""

from __future__ import annotations

import csv
import json
import time
from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from .service import ArchiveService
from .util import append_evidence


@dataclass(slots=True)
class BatchItem:
    """Single item in a batch manifest."""

    tombstone: str
    output: str


@dataclass(slots=True)
class BatchResult:
    """Result of a batch restore operation."""

    item: BatchItem
    status: Literal["success", "failed", "skipped"]
    duration_ms: float
    error: str | None = None


class BatchManifest:
    """Batch manifest loader."""

    @staticmethod
    def load_json(path: str | Path) -> list[BatchItem]:
        """Load batch manifest from JSON file."""

        manifest_path = Path(path)
        if not manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found: {path}")
        with manifest_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if "items" not in payload:
            raise ValueError("Manifest must contain 'items' key")
        items: list[BatchItem] = []
        for entry in payload["items"]:
            if "tombstone" not in entry or "output" not in entry:
                raise ValueError("Each item must have 'tombstone' and 'output' keys")
            items.append(BatchItem(tombstone=entry["tombstone"], output=entry["output"]))
        return items

    @staticmethod
    def load_csv(path: str | Path) -> list[BatchItem]:
        """Load batch manifest from CSV file."""

        manifest_path = Path(path)
        if not manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found: {path}")
        with manifest_path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != ["tombstone", "output"]:
                raise ValueError("CSV must have columns: tombstone, output")
            return [BatchItem(tombstone=row["tombstone"], output=row["output"]) for row in reader]


class BatchRestore:
    """Batch restore orchestrator."""

    def __init__(
        self,
        service: ArchiveService,
        *,
        max_concurrent: int = 5,
        continue_on_error: bool = False,
    ) -> None:
        self.service = service
        self.max_concurrent = max_concurrent
        self.continue_on_error = continue_on_error
        self.results: list[BatchResult] = []

    def restore(
        self,
        items: Iterable[BatchItem],
        *,
        actor: str,
        resume_from: int = 0,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> list[BatchResult]:
        """Execute batch restore operation."""

        self.results = []
        enumerated = list(items)
        total = len(enumerated)
        for index, item in enumerate(enumerated):
            if index < resume_from:
                self.results.append(BatchResult(item=item, status="skipped", duration_ms=0.0))
                continue
            start = time.time()
            try:
                self.service.restore_to_path(
                    item.tombstone,
                    output_path=Path(item.output),
                    actor=actor,
                )
            except Exception as exc:  # pragma: no cover - error path exercised via tests
                duration_ms = (time.time() - start) * 1000
                result = BatchResult(
                    item=item,
                    status="failed",
                    duration_ms=duration_ms,
                    error=str(exc),
                )
                self.results.append(result)
                if not self.continue_on_error:
                    raise
            else:
                duration_ms = (time.time() - start) * 1000
                result = BatchResult(item=item, status="success", duration_ms=duration_ms)
                self.results.append(result)
            finally:
                if progress_callback:
                    progress_callback(index + 1, total)
        return self.results

    def save_results(self, output_path: str | Path) -> None:
        """Save batch results to JSON file and evidence log."""

        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        summary = {
            "total": len(self.results),
            "succeeded": sum(1 for r in self.results if r.status == "success"),
            "failed": sum(1 for r in self.results if r.status == "failed"),
            "skipped": sum(1 for r in self.results if r.status == "skipped"),
            "total_duration_ms": sum(r.duration_ms for r in self.results),
        }
        payload = {
            "items": [asdict(result) for result in self.results],
            "summary": summary,
        }
        destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        append_evidence(
            {
                "action": "BATCH_RESTORE_COMPLETE",
                "items_processed": summary["total"],
                "succeeded": summary["succeeded"],
                "failed": summary["failed"],
                "skipped": summary["skipped"],
                "total_duration_ms": summary["total_duration_ms"],
                "results_file": destination.as_posix(),
            }
        )
