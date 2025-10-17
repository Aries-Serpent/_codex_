"""Batch restore operations with progress tracking and resume support."""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from .service import ArchiveService
from .util import append_evidence


@dataclass
class BatchItem:
    """Single item in a batch manifest."""

    tombstone: str
    output: str


@dataclass
class BatchResult:
    """Result of a batch restore operation."""

    item: BatchItem
    status: Literal["success", "failed", "skipped"]
    duration_ms: float
    error: str | None = None


class BatchManifest:
    """Batch manifest loader and processor."""

    @staticmethod
    def load_json(path: str | Path) -> list[BatchItem]:
        """Load batch manifest from JSON file."""

        manifest_path = Path(path)
        if not manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found: {path}")
        with open(manifest_path, encoding="utf-8") as handle:
            data = json.load(handle)
        if "items" not in data:
            raise ValueError("Manifest must contain 'items' key")
        items: list[BatchItem] = []
        for item_dict in data["items"]:
            if "tombstone" not in item_dict or "output" not in item_dict:
                raise ValueError("Each item must have 'tombstone' and 'output' keys")
            items.append(BatchItem(**item_dict))
        return items

    @staticmethod
    def load_csv(path: str | Path) -> list[BatchItem]:
        """Load batch manifest from CSV file."""

        import csv

        manifest_path = Path(path)
        if not manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found: {path}")
        items: list[BatchItem] = []
        with open(manifest_path, encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != ["tombstone", "output"]:
                raise ValueError("CSV must have columns: tombstone, output")
            for row in reader:
                items.append(BatchItem(tombstone=row["tombstone"], output=row["output"]))
        return items


class BatchRestore:
    """Batch restore orchestrator."""

    def __init__(
        self,
        service: ArchiveService,
        max_concurrent: int = 5,
        continue_on_error: bool = False,
    ) -> None:
        self.service = service
        self.max_concurrent = max_concurrent
        self.continue_on_error = continue_on_error
        self.results: list[BatchResult] = []

    def restore(
        self,
        items: list[BatchItem],
        actor: str,
        resume_from: int = 0,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> list[BatchResult]:
        """Execute batch restore operation."""

        self.results = []
        for index, item in enumerate(items):
            if index < resume_from:
                continue
            start_time = time.time()
            try:
                self.service.restore_to_path(
                    item.tombstone,
                    output_path=Path(item.output),
                    actor=actor,
                )
                duration_ms = (time.time() - start_time) * 1000
                result = BatchResult(
                    item=item,
                    status="success",
                    duration_ms=duration_ms,
                )
                self.results.append(result)
            except Exception as exc:  # pragma: no cover - exercised via tests
                duration_ms = (time.time() - start_time) * 1000
                result = BatchResult(
                    item=item,
                    status="failed",
                    duration_ms=duration_ms,
                    error=str(exc),
                )
                self.results.append(result)
                if not self.continue_on_error:
                    raise
            if progress_callback:
                progress_callback(index + 1, len(items))
        return self.results

    def save_results(self, output_path: str | Path) -> None:
        """Save batch results to JSON file."""

        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        results_data = {
            "items": [asdict(result) for result in self.results],
            "summary": {
                "total": len(self.results),
                "succeeded": len([r for r in self.results if r.status == "success"]),
                "failed": len([r for r in self.results if r.status == "failed"]),
                "skipped": len([r for r in self.results if r.status == "skipped"]),
                "total_duration_ms": sum(result.duration_ms for result in self.results),
            },
        }
        with open(out_path, "w", encoding="utf-8") as handle:
            json.dump(results_data, handle, indent=2)
        append_evidence(
            {
                "action": "BATCH_RESTORE_COMPLETE",
                "items_processed": len(self.results),
                "succeeded": results_data["summary"]["succeeded"],
                "failed": results_data["summary"]["failed"],
                "total_duration_ms": results_data["summary"]["total_duration_ms"],
                "results_file": out_path.as_posix(),
            }
        )
