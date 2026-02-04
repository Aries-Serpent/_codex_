"""
Batch Module

This module provides functionality for batch.

Usage:
    from archive.batch import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)
"""Batch restoration utilities for the archive CLI."""


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
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


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

    def xǁBatchManifestǁ__init____mutmut_orig(self, items: Iterable[BatchItem], *, path: Path) -> None:
        self.items = list(items)
        self.path = path

    def xǁBatchManifestǁ__init____mutmut_1(self, items: Iterable[BatchItem], *, path: Path) -> None:
        self.items = None
        self.path = path

    def xǁBatchManifestǁ__init____mutmut_2(self, items: Iterable[BatchItem], *, path: Path) -> None:
        self.items = list(None)
        self.path = path

    def xǁBatchManifestǁ__init____mutmut_3(self, items: Iterable[BatchItem], *, path: Path) -> None:
        self.items = list(items)
        self.path = None
    
    xǁBatchManifestǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBatchManifestǁ__init____mutmut_1': xǁBatchManifestǁ__init____mutmut_1, 
        'xǁBatchManifestǁ__init____mutmut_2': xǁBatchManifestǁ__init____mutmut_2, 
        'xǁBatchManifestǁ__init____mutmut_3': xǁBatchManifestǁ__init____mutmut_3
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBatchManifestǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁBatchManifestǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁBatchManifestǁ__init____mutmut_orig)
    xǁBatchManifestǁ__init____mutmut_orig.__name__ = 'xǁBatchManifestǁ__init__'

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

    def xǁBatchRestoreǁ__init____mutmut_orig(
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

    def xǁBatchRestoreǁ__init____mutmut_1(
        self,
        service: Any,
        *,
        retry_config: RetryConfig | None = None,
        batch_config: BatchConfig | None = None,
        performance_config: PerformanceConfig | None = None,
        progress_callback: Callable[[int, int, dict[str, Any]], None] | None = None,
    ) -> None:
        self.service = None
        self.retry_config = retry_config or RetryConfig()
        self.batch_config = batch_config or BatchConfig()
        self.performance_config = performance_config or PerformanceConfig()
        self.progress_callback = progress_callback

    def xǁBatchRestoreǁ__init____mutmut_2(
        self,
        service: Any,
        *,
        retry_config: RetryConfig | None = None,
        batch_config: BatchConfig | None = None,
        performance_config: PerformanceConfig | None = None,
        progress_callback: Callable[[int, int, dict[str, Any]], None] | None = None,
    ) -> None:
        self.service = service
        self.retry_config = None
        self.batch_config = batch_config or BatchConfig()
        self.performance_config = performance_config or PerformanceConfig()
        self.progress_callback = progress_callback

    def xǁBatchRestoreǁ__init____mutmut_3(
        self,
        service: Any,
        *,
        retry_config: RetryConfig | None = None,
        batch_config: BatchConfig | None = None,
        performance_config: PerformanceConfig | None = None,
        progress_callback: Callable[[int, int, dict[str, Any]], None] | None = None,
    ) -> None:
        self.service = service
        self.retry_config = retry_config and RetryConfig()
        self.batch_config = batch_config or BatchConfig()
        self.performance_config = performance_config or PerformanceConfig()
        self.progress_callback = progress_callback

    def xǁBatchRestoreǁ__init____mutmut_4(
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
        self.batch_config = None
        self.performance_config = performance_config or PerformanceConfig()
        self.progress_callback = progress_callback

    def xǁBatchRestoreǁ__init____mutmut_5(
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
        self.batch_config = batch_config and BatchConfig()
        self.performance_config = performance_config or PerformanceConfig()
        self.progress_callback = progress_callback

    def xǁBatchRestoreǁ__init____mutmut_6(
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
        self.performance_config = None
        self.progress_callback = progress_callback

    def xǁBatchRestoreǁ__init____mutmut_7(
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
        self.performance_config = performance_config and PerformanceConfig()
        self.progress_callback = progress_callback

    def xǁBatchRestoreǁ__init____mutmut_8(
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
        self.progress_callback = None
    
    xǁBatchRestoreǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBatchRestoreǁ__init____mutmut_1': xǁBatchRestoreǁ__init____mutmut_1, 
        'xǁBatchRestoreǁ__init____mutmut_2': xǁBatchRestoreǁ__init____mutmut_2, 
        'xǁBatchRestoreǁ__init____mutmut_3': xǁBatchRestoreǁ__init____mutmut_3, 
        'xǁBatchRestoreǁ__init____mutmut_4': xǁBatchRestoreǁ__init____mutmut_4, 
        'xǁBatchRestoreǁ__init____mutmut_5': xǁBatchRestoreǁ__init____mutmut_5, 
        'xǁBatchRestoreǁ__init____mutmut_6': xǁBatchRestoreǁ__init____mutmut_6, 
        'xǁBatchRestoreǁ__init____mutmut_7': xǁBatchRestoreǁ__init____mutmut_7, 
        'xǁBatchRestoreǁ__init____mutmut_8': xǁBatchRestoreǁ__init____mutmut_8
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBatchRestoreǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁBatchRestoreǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁBatchRestoreǁ__init____mutmut_orig)
    xǁBatchRestoreǁ__init____mutmut_orig.__name__ = 'xǁBatchRestoreǁ__init__'

    def xǁBatchRestoreǁrestore__mutmut_orig(self, manifest: BatchManifest) -> BatchResult:
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

    def xǁBatchRestoreǁrestore__mutmut_1(self, manifest: BatchManifest) -> BatchResult:
        total = None
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

    def xǁBatchRestoreǁrestore__mutmut_2(self, manifest: BatchManifest) -> BatchResult:
        total = len(manifest.items)
        results: list[dict[str, Any]] = None
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

    def xǁBatchRestoreǁrestore__mutmut_3(self, manifest: BatchManifest) -> BatchResult:
        total = len(manifest.items)
        results: list[dict[str, Any]] = []
        succeeded = None
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

    def xǁBatchRestoreǁrestore__mutmut_4(self, manifest: BatchManifest) -> BatchResult:
        total = len(manifest.items)
        results: list[dict[str, Any]] = []
        succeeded = 1
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

    def xǁBatchRestoreǁrestore__mutmut_5(self, manifest: BatchManifest) -> BatchResult:
        total = len(manifest.items)
        results: list[dict[str, Any]] = []
        succeeded = 0
        failed = None
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

    def xǁBatchRestoreǁrestore__mutmut_6(self, manifest: BatchManifest) -> BatchResult:
        total = len(manifest.items)
        results: list[dict[str, Any]] = []
        succeeded = 0
        failed = 1
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

    def xǁBatchRestoreǁrestore__mutmut_7(self, manifest: BatchManifest) -> BatchResult:
        total = len(manifest.items)
        results: list[dict[str, Any]] = []
        succeeded = 0
        failed = 0
        performance_enabled = None
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

    def xǁBatchRestoreǁrestore__mutmut_8(self, manifest: BatchManifest) -> BatchResult:
        total = len(manifest.items)
        results: list[dict[str, Any]] = []
        succeeded = 0
        failed = 0
        performance_enabled = self.performance_config.enabled
        with _optional_timer(None, "batch_restore") as metrics:
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

    def xǁBatchRestoreǁrestore__mutmut_9(self, manifest: BatchManifest) -> BatchResult:
        total = len(manifest.items)
        results: list[dict[str, Any]] = []
        succeeded = 0
        failed = 0
        performance_enabled = self.performance_config.enabled
        with _optional_timer(performance_enabled, None) as metrics:
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

    def xǁBatchRestoreǁrestore__mutmut_10(self, manifest: BatchManifest) -> BatchResult:
        total = len(manifest.items)
        results: list[dict[str, Any]] = []
        succeeded = 0
        failed = 0
        performance_enabled = self.performance_config.enabled
        with _optional_timer("batch_restore") as metrics:
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

    def xǁBatchRestoreǁrestore__mutmut_11(self, manifest: BatchManifest) -> BatchResult:
        total = len(manifest.items)
        results: list[dict[str, Any]] = []
        succeeded = 0
        failed = 0
        performance_enabled = self.performance_config.enabled
        with _optional_timer(performance_enabled, ) as metrics:
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

    def xǁBatchRestoreǁrestore__mutmut_12(self, manifest: BatchManifest) -> BatchResult:
        total = len(manifest.items)
        results: list[dict[str, Any]] = []
        succeeded = 0
        failed = 0
        performance_enabled = self.performance_config.enabled
        with _optional_timer(performance_enabled, "XXbatch_restoreXX") as metrics:
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

    def xǁBatchRestoreǁrestore__mutmut_13(self, manifest: BatchManifest) -> BatchResult:
        total = len(manifest.items)
        results: list[dict[str, Any]] = []
        succeeded = 0
        failed = 0
        performance_enabled = self.performance_config.enabled
        with _optional_timer(performance_enabled, "BATCH_RESTORE") as metrics:
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

    def xǁBatchRestoreǁrestore__mutmut_14(self, manifest: BatchManifest) -> BatchResult:
        total = len(manifest.items)
        results: list[dict[str, Any]] = []
        succeeded = 0
        failed = 0
        performance_enabled = self.performance_config.enabled
        with _optional_timer(performance_enabled, "batch_restore") as metrics:
            for index, item in enumerate(None, start=1):
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

    def xǁBatchRestoreǁrestore__mutmut_15(self, manifest: BatchManifest) -> BatchResult:
        total = len(manifest.items)
        results: list[dict[str, Any]] = []
        succeeded = 0
        failed = 0
        performance_enabled = self.performance_config.enabled
        with _optional_timer(performance_enabled, "batch_restore") as metrics:
            for index, item in enumerate(manifest.items, start=None):
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

    def xǁBatchRestoreǁrestore__mutmut_16(self, manifest: BatchManifest) -> BatchResult:
        total = len(manifest.items)
        results: list[dict[str, Any]] = []
        succeeded = 0
        failed = 0
        performance_enabled = self.performance_config.enabled
        with _optional_timer(performance_enabled, "batch_restore") as metrics:
            for index, item in enumerate(start=1):
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

    def xǁBatchRestoreǁrestore__mutmut_17(self, manifest: BatchManifest) -> BatchResult:
        total = len(manifest.items)
        results: list[dict[str, Any]] = []
        succeeded = 0
        failed = 0
        performance_enabled = self.performance_config.enabled
        with _optional_timer(performance_enabled, "batch_restore") as metrics:
            for index, item in enumerate(manifest.items, ):
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

    def xǁBatchRestoreǁrestore__mutmut_18(self, manifest: BatchManifest) -> BatchResult:
        total = len(manifest.items)
        results: list[dict[str, Any]] = []
        succeeded = 0
        failed = 0
        performance_enabled = self.performance_config.enabled
        with _optional_timer(performance_enabled, "batch_restore") as metrics:
            for index, item in enumerate(manifest.items, start=2):
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

    def xǁBatchRestoreǁrestore__mutmut_19(self, manifest: BatchManifest) -> BatchResult:
        total = len(manifest.items)
        results: list[dict[str, Any]] = []
        succeeded = 0
        failed = 0
        performance_enabled = self.performance_config.enabled
        with _optional_timer(performance_enabled, "batch_restore") as metrics:
            for index, item in enumerate(manifest.items, start=1):
                entry = None
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

    def xǁBatchRestoreǁrestore__mutmut_20(self, manifest: BatchManifest) -> BatchResult:
        total = len(manifest.items)
        results: list[dict[str, Any]] = []
        succeeded = 0
        failed = 0
        performance_enabled = self.performance_config.enabled
        with _optional_timer(performance_enabled, "batch_restore") as metrics:
            for index, item in enumerate(manifest.items, start=1):
                entry = self._restore_single(None)
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

    def xǁBatchRestoreǁrestore__mutmut_21(self, manifest: BatchManifest) -> BatchResult:
        total = len(manifest.items)
        results: list[dict[str, Any]] = []
        succeeded = 0
        failed = 0
        performance_enabled = self.performance_config.enabled
        with _optional_timer(performance_enabled, "batch_restore") as metrics:
            for index, item in enumerate(manifest.items, start=1):
                entry = self._restore_single(item)
                if entry["XXstatusXX"] == "SUCCESS":
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

    def xǁBatchRestoreǁrestore__mutmut_22(self, manifest: BatchManifest) -> BatchResult:
        total = len(manifest.items)
        results: list[dict[str, Any]] = []
        succeeded = 0
        failed = 0
        performance_enabled = self.performance_config.enabled
        with _optional_timer(performance_enabled, "batch_restore") as metrics:
            for index, item in enumerate(manifest.items, start=1):
                entry = self._restore_single(item)
                if entry["STATUS"] == "SUCCESS":
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

    def xǁBatchRestoreǁrestore__mutmut_23(self, manifest: BatchManifest) -> BatchResult:
        total = len(manifest.items)
        results: list[dict[str, Any]] = []
        succeeded = 0
        failed = 0
        performance_enabled = self.performance_config.enabled
        with _optional_timer(performance_enabled, "batch_restore") as metrics:
            for index, item in enumerate(manifest.items, start=1):
                entry = self._restore_single(item)
                if entry["status"] != "SUCCESS":
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

    def xǁBatchRestoreǁrestore__mutmut_24(self, manifest: BatchManifest) -> BatchResult:
        total = len(manifest.items)
        results: list[dict[str, Any]] = []
        succeeded = 0
        failed = 0
        performance_enabled = self.performance_config.enabled
        with _optional_timer(performance_enabled, "batch_restore") as metrics:
            for index, item in enumerate(manifest.items, start=1):
                entry = self._restore_single(item)
                if entry["status"] == "XXSUCCESSXX":
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

    def xǁBatchRestoreǁrestore__mutmut_25(self, manifest: BatchManifest) -> BatchResult:
        total = len(manifest.items)
        results: list[dict[str, Any]] = []
        succeeded = 0
        failed = 0
        performance_enabled = self.performance_config.enabled
        with _optional_timer(performance_enabled, "batch_restore") as metrics:
            for index, item in enumerate(manifest.items, start=1):
                entry = self._restore_single(item)
                if entry["status"] == "success":
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

    def xǁBatchRestoreǁrestore__mutmut_26(self, manifest: BatchManifest) -> BatchResult:
        total = len(manifest.items)
        results: list[dict[str, Any]] = []
        succeeded = 0
        failed = 0
        performance_enabled = self.performance_config.enabled
        with _optional_timer(performance_enabled, "batch_restore") as metrics:
            for index, item in enumerate(manifest.items, start=1):
                entry = self._restore_single(item)
                if entry["status"] == "SUCCESS":
                    succeeded = 1
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

    def xǁBatchRestoreǁrestore__mutmut_27(self, manifest: BatchManifest) -> BatchResult:
        total = len(manifest.items)
        results: list[dict[str, Any]] = []
        succeeded = 0
        failed = 0
        performance_enabled = self.performance_config.enabled
        with _optional_timer(performance_enabled, "batch_restore") as metrics:
            for index, item in enumerate(manifest.items, start=1):
                entry = self._restore_single(item)
                if entry["status"] == "SUCCESS":
                    succeeded -= 1
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

    def xǁBatchRestoreǁrestore__mutmut_28(self, manifest: BatchManifest) -> BatchResult:
        total = len(manifest.items)
        results: list[dict[str, Any]] = []
        succeeded = 0
        failed = 0
        performance_enabled = self.performance_config.enabled
        with _optional_timer(performance_enabled, "batch_restore") as metrics:
            for index, item in enumerate(manifest.items, start=1):
                entry = self._restore_single(item)
                if entry["status"] == "SUCCESS":
                    succeeded += 2
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

    def xǁBatchRestoreǁrestore__mutmut_29(self, manifest: BatchManifest) -> BatchResult:
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
                    failed = 1
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

    def xǁBatchRestoreǁrestore__mutmut_30(self, manifest: BatchManifest) -> BatchResult:
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
                    failed -= 1
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

    def xǁBatchRestoreǁrestore__mutmut_31(self, manifest: BatchManifest) -> BatchResult:
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
                    failed += 2
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

    def xǁBatchRestoreǁrestore__mutmut_32(self, manifest: BatchManifest) -> BatchResult:
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
                results.append(None)
                if self.progress_callback:
                    self.progress_callback(index, total, entry)
        return BatchResult(
            total=total,
            succeeded=succeeded,
            failed=failed,
            results=results,
            metrics=metrics if performance_enabled else None,
        )

    def xǁBatchRestoreǁrestore__mutmut_33(self, manifest: BatchManifest) -> BatchResult:
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
                    self.progress_callback(None, total, entry)
        return BatchResult(
            total=total,
            succeeded=succeeded,
            failed=failed,
            results=results,
            metrics=metrics if performance_enabled else None,
        )

    def xǁBatchRestoreǁrestore__mutmut_34(self, manifest: BatchManifest) -> BatchResult:
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
                    self.progress_callback(index, None, entry)
        return BatchResult(
            total=total,
            succeeded=succeeded,
            failed=failed,
            results=results,
            metrics=metrics if performance_enabled else None,
        )

    def xǁBatchRestoreǁrestore__mutmut_35(self, manifest: BatchManifest) -> BatchResult:
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
                    self.progress_callback(index, total, None)
        return BatchResult(
            total=total,
            succeeded=succeeded,
            failed=failed,
            results=results,
            metrics=metrics if performance_enabled else None,
        )

    def xǁBatchRestoreǁrestore__mutmut_36(self, manifest: BatchManifest) -> BatchResult:
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
                    self.progress_callback(total, entry)
        return BatchResult(
            total=total,
            succeeded=succeeded,
            failed=failed,
            results=results,
            metrics=metrics if performance_enabled else None,
        )

    def xǁBatchRestoreǁrestore__mutmut_37(self, manifest: BatchManifest) -> BatchResult:
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
                    self.progress_callback(index, entry)
        return BatchResult(
            total=total,
            succeeded=succeeded,
            failed=failed,
            results=results,
            metrics=metrics if performance_enabled else None,
        )

    def xǁBatchRestoreǁrestore__mutmut_38(self, manifest: BatchManifest) -> BatchResult:
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
                    self.progress_callback(index, total, )
        return BatchResult(
            total=total,
            succeeded=succeeded,
            failed=failed,
            results=results,
            metrics=metrics if performance_enabled else None,
        )

    def xǁBatchRestoreǁrestore__mutmut_39(self, manifest: BatchManifest) -> BatchResult:
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
            total=None,
            succeeded=succeeded,
            failed=failed,
            results=results,
            metrics=metrics if performance_enabled else None,
        )

    def xǁBatchRestoreǁrestore__mutmut_40(self, manifest: BatchManifest) -> BatchResult:
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
            succeeded=None,
            failed=failed,
            results=results,
            metrics=metrics if performance_enabled else None,
        )

    def xǁBatchRestoreǁrestore__mutmut_41(self, manifest: BatchManifest) -> BatchResult:
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
            failed=None,
            results=results,
            metrics=metrics if performance_enabled else None,
        )

    def xǁBatchRestoreǁrestore__mutmut_42(self, manifest: BatchManifest) -> BatchResult:
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
            results=None,
            metrics=metrics if performance_enabled else None,
        )

    def xǁBatchRestoreǁrestore__mutmut_43(self, manifest: BatchManifest) -> BatchResult:
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
            metrics=None,
        )

    def xǁBatchRestoreǁrestore__mutmut_44(self, manifest: BatchManifest) -> BatchResult:
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
            succeeded=succeeded,
            failed=failed,
            results=results,
            metrics=metrics if performance_enabled else None,
        )

    def xǁBatchRestoreǁrestore__mutmut_45(self, manifest: BatchManifest) -> BatchResult:
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
            failed=failed,
            results=results,
            metrics=metrics if performance_enabled else None,
        )

    def xǁBatchRestoreǁrestore__mutmut_46(self, manifest: BatchManifest) -> BatchResult:
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
            results=results,
            metrics=metrics if performance_enabled else None,
        )

    def xǁBatchRestoreǁrestore__mutmut_47(self, manifest: BatchManifest) -> BatchResult:
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
            metrics=metrics if performance_enabled else None,
        )

    def xǁBatchRestoreǁrestore__mutmut_48(self, manifest: BatchManifest) -> BatchResult:
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
            )
    
    xǁBatchRestoreǁrestore__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBatchRestoreǁrestore__mutmut_1': xǁBatchRestoreǁrestore__mutmut_1, 
        'xǁBatchRestoreǁrestore__mutmut_2': xǁBatchRestoreǁrestore__mutmut_2, 
        'xǁBatchRestoreǁrestore__mutmut_3': xǁBatchRestoreǁrestore__mutmut_3, 
        'xǁBatchRestoreǁrestore__mutmut_4': xǁBatchRestoreǁrestore__mutmut_4, 
        'xǁBatchRestoreǁrestore__mutmut_5': xǁBatchRestoreǁrestore__mutmut_5, 
        'xǁBatchRestoreǁrestore__mutmut_6': xǁBatchRestoreǁrestore__mutmut_6, 
        'xǁBatchRestoreǁrestore__mutmut_7': xǁBatchRestoreǁrestore__mutmut_7, 
        'xǁBatchRestoreǁrestore__mutmut_8': xǁBatchRestoreǁrestore__mutmut_8, 
        'xǁBatchRestoreǁrestore__mutmut_9': xǁBatchRestoreǁrestore__mutmut_9, 
        'xǁBatchRestoreǁrestore__mutmut_10': xǁBatchRestoreǁrestore__mutmut_10, 
        'xǁBatchRestoreǁrestore__mutmut_11': xǁBatchRestoreǁrestore__mutmut_11, 
        'xǁBatchRestoreǁrestore__mutmut_12': xǁBatchRestoreǁrestore__mutmut_12, 
        'xǁBatchRestoreǁrestore__mutmut_13': xǁBatchRestoreǁrestore__mutmut_13, 
        'xǁBatchRestoreǁrestore__mutmut_14': xǁBatchRestoreǁrestore__mutmut_14, 
        'xǁBatchRestoreǁrestore__mutmut_15': xǁBatchRestoreǁrestore__mutmut_15, 
        'xǁBatchRestoreǁrestore__mutmut_16': xǁBatchRestoreǁrestore__mutmut_16, 
        'xǁBatchRestoreǁrestore__mutmut_17': xǁBatchRestoreǁrestore__mutmut_17, 
        'xǁBatchRestoreǁrestore__mutmut_18': xǁBatchRestoreǁrestore__mutmut_18, 
        'xǁBatchRestoreǁrestore__mutmut_19': xǁBatchRestoreǁrestore__mutmut_19, 
        'xǁBatchRestoreǁrestore__mutmut_20': xǁBatchRestoreǁrestore__mutmut_20, 
        'xǁBatchRestoreǁrestore__mutmut_21': xǁBatchRestoreǁrestore__mutmut_21, 
        'xǁBatchRestoreǁrestore__mutmut_22': xǁBatchRestoreǁrestore__mutmut_22, 
        'xǁBatchRestoreǁrestore__mutmut_23': xǁBatchRestoreǁrestore__mutmut_23, 
        'xǁBatchRestoreǁrestore__mutmut_24': xǁBatchRestoreǁrestore__mutmut_24, 
        'xǁBatchRestoreǁrestore__mutmut_25': xǁBatchRestoreǁrestore__mutmut_25, 
        'xǁBatchRestoreǁrestore__mutmut_26': xǁBatchRestoreǁrestore__mutmut_26, 
        'xǁBatchRestoreǁrestore__mutmut_27': xǁBatchRestoreǁrestore__mutmut_27, 
        'xǁBatchRestoreǁrestore__mutmut_28': xǁBatchRestoreǁrestore__mutmut_28, 
        'xǁBatchRestoreǁrestore__mutmut_29': xǁBatchRestoreǁrestore__mutmut_29, 
        'xǁBatchRestoreǁrestore__mutmut_30': xǁBatchRestoreǁrestore__mutmut_30, 
        'xǁBatchRestoreǁrestore__mutmut_31': xǁBatchRestoreǁrestore__mutmut_31, 
        'xǁBatchRestoreǁrestore__mutmut_32': xǁBatchRestoreǁrestore__mutmut_32, 
        'xǁBatchRestoreǁrestore__mutmut_33': xǁBatchRestoreǁrestore__mutmut_33, 
        'xǁBatchRestoreǁrestore__mutmut_34': xǁBatchRestoreǁrestore__mutmut_34, 
        'xǁBatchRestoreǁrestore__mutmut_35': xǁBatchRestoreǁrestore__mutmut_35, 
        'xǁBatchRestoreǁrestore__mutmut_36': xǁBatchRestoreǁrestore__mutmut_36, 
        'xǁBatchRestoreǁrestore__mutmut_37': xǁBatchRestoreǁrestore__mutmut_37, 
        'xǁBatchRestoreǁrestore__mutmut_38': xǁBatchRestoreǁrestore__mutmut_38, 
        'xǁBatchRestoreǁrestore__mutmut_39': xǁBatchRestoreǁrestore__mutmut_39, 
        'xǁBatchRestoreǁrestore__mutmut_40': xǁBatchRestoreǁrestore__mutmut_40, 
        'xǁBatchRestoreǁrestore__mutmut_41': xǁBatchRestoreǁrestore__mutmut_41, 
        'xǁBatchRestoreǁrestore__mutmut_42': xǁBatchRestoreǁrestore__mutmut_42, 
        'xǁBatchRestoreǁrestore__mutmut_43': xǁBatchRestoreǁrestore__mutmut_43, 
        'xǁBatchRestoreǁrestore__mutmut_44': xǁBatchRestoreǁrestore__mutmut_44, 
        'xǁBatchRestoreǁrestore__mutmut_45': xǁBatchRestoreǁrestore__mutmut_45, 
        'xǁBatchRestoreǁrestore__mutmut_46': xǁBatchRestoreǁrestore__mutmut_46, 
        'xǁBatchRestoreǁrestore__mutmut_47': xǁBatchRestoreǁrestore__mutmut_47, 
        'xǁBatchRestoreǁrestore__mutmut_48': xǁBatchRestoreǁrestore__mutmut_48
    }
    
    def restore(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBatchRestoreǁrestore__mutmut_orig"), object.__getattribute__(self, "xǁBatchRestoreǁrestore__mutmut_mutants"), args, kwargs, self)
        return result 
    
    restore.__signature__ = _mutmut_signature(xǁBatchRestoreǁrestore__mutmut_orig)
    xǁBatchRestoreǁrestore__mutmut_orig.__name__ = 'xǁBatchRestoreǁrestore'

    def xǁBatchRestoreǁsave_results__mutmut_orig(self, path: Path, result: BatchResult) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(result.to_dict(), handle, indent=2)
        return path

    def xǁBatchRestoreǁsave_results__mutmut_1(self, path: Path, result: BatchResult) -> Path:
        path.parent.mkdir(parents=None, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(result.to_dict(), handle, indent=2)
        return path

    def xǁBatchRestoreǁsave_results__mutmut_2(self, path: Path, result: BatchResult) -> Path:
        path.parent.mkdir(parents=True, exist_ok=None)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(result.to_dict(), handle, indent=2)
        return path

    def xǁBatchRestoreǁsave_results__mutmut_3(self, path: Path, result: BatchResult) -> Path:
        path.parent.mkdir(exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(result.to_dict(), handle, indent=2)
        return path

    def xǁBatchRestoreǁsave_results__mutmut_4(self, path: Path, result: BatchResult) -> Path:
        path.parent.mkdir(parents=True, )
        with path.open("w", encoding="utf-8") as handle:
            json.dump(result.to_dict(), handle, indent=2)
        return path

    def xǁBatchRestoreǁsave_results__mutmut_5(self, path: Path, result: BatchResult) -> Path:
        path.parent.mkdir(parents=False, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(result.to_dict(), handle, indent=2)
        return path

    def xǁBatchRestoreǁsave_results__mutmut_6(self, path: Path, result: BatchResult) -> Path:
        path.parent.mkdir(parents=True, exist_ok=False)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(result.to_dict(), handle, indent=2)
        return path

    def xǁBatchRestoreǁsave_results__mutmut_7(self, path: Path, result: BatchResult) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open(None, encoding="utf-8") as handle:
            json.dump(result.to_dict(), handle, indent=2)
        return path

    def xǁBatchRestoreǁsave_results__mutmut_8(self, path: Path, result: BatchResult) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding=None) as handle:
            json.dump(result.to_dict(), handle, indent=2)
        return path

    def xǁBatchRestoreǁsave_results__mutmut_9(self, path: Path, result: BatchResult) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open(encoding="utf-8") as handle:
            json.dump(result.to_dict(), handle, indent=2)
        return path

    def xǁBatchRestoreǁsave_results__mutmut_10(self, path: Path, result: BatchResult) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", ) as handle:
            json.dump(result.to_dict(), handle, indent=2)
        return path

    def xǁBatchRestoreǁsave_results__mutmut_11(self, path: Path, result: BatchResult) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("XXwXX", encoding="utf-8") as handle:
            json.dump(result.to_dict(), handle, indent=2)
        return path

    def xǁBatchRestoreǁsave_results__mutmut_12(self, path: Path, result: BatchResult) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("W", encoding="utf-8") as handle:
            json.dump(result.to_dict(), handle, indent=2)
        return path

    def xǁBatchRestoreǁsave_results__mutmut_13(self, path: Path, result: BatchResult) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="XXutf-8XX") as handle:
            json.dump(result.to_dict(), handle, indent=2)
        return path

    def xǁBatchRestoreǁsave_results__mutmut_14(self, path: Path, result: BatchResult) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="UTF-8") as handle:
            json.dump(result.to_dict(), handle, indent=2)
        return path

    def xǁBatchRestoreǁsave_results__mutmut_15(self, path: Path, result: BatchResult) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(None, handle, indent=2)
        return path

    def xǁBatchRestoreǁsave_results__mutmut_16(self, path: Path, result: BatchResult) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(result.to_dict(), None, indent=2)
        return path

    def xǁBatchRestoreǁsave_results__mutmut_17(self, path: Path, result: BatchResult) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(result.to_dict(), handle, indent=None)
        return path

    def xǁBatchRestoreǁsave_results__mutmut_18(self, path: Path, result: BatchResult) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(handle, indent=2)
        return path

    def xǁBatchRestoreǁsave_results__mutmut_19(self, path: Path, result: BatchResult) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(result.to_dict(), indent=2)
        return path

    def xǁBatchRestoreǁsave_results__mutmut_20(self, path: Path, result: BatchResult) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(result.to_dict(), handle, )
        return path

    def xǁBatchRestoreǁsave_results__mutmut_21(self, path: Path, result: BatchResult) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(result.to_dict(), handle, indent=3)
        return path
    
    xǁBatchRestoreǁsave_results__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBatchRestoreǁsave_results__mutmut_1': xǁBatchRestoreǁsave_results__mutmut_1, 
        'xǁBatchRestoreǁsave_results__mutmut_2': xǁBatchRestoreǁsave_results__mutmut_2, 
        'xǁBatchRestoreǁsave_results__mutmut_3': xǁBatchRestoreǁsave_results__mutmut_3, 
        'xǁBatchRestoreǁsave_results__mutmut_4': xǁBatchRestoreǁsave_results__mutmut_4, 
        'xǁBatchRestoreǁsave_results__mutmut_5': xǁBatchRestoreǁsave_results__mutmut_5, 
        'xǁBatchRestoreǁsave_results__mutmut_6': xǁBatchRestoreǁsave_results__mutmut_6, 
        'xǁBatchRestoreǁsave_results__mutmut_7': xǁBatchRestoreǁsave_results__mutmut_7, 
        'xǁBatchRestoreǁsave_results__mutmut_8': xǁBatchRestoreǁsave_results__mutmut_8, 
        'xǁBatchRestoreǁsave_results__mutmut_9': xǁBatchRestoreǁsave_results__mutmut_9, 
        'xǁBatchRestoreǁsave_results__mutmut_10': xǁBatchRestoreǁsave_results__mutmut_10, 
        'xǁBatchRestoreǁsave_results__mutmut_11': xǁBatchRestoreǁsave_results__mutmut_11, 
        'xǁBatchRestoreǁsave_results__mutmut_12': xǁBatchRestoreǁsave_results__mutmut_12, 
        'xǁBatchRestoreǁsave_results__mutmut_13': xǁBatchRestoreǁsave_results__mutmut_13, 
        'xǁBatchRestoreǁsave_results__mutmut_14': xǁBatchRestoreǁsave_results__mutmut_14, 
        'xǁBatchRestoreǁsave_results__mutmut_15': xǁBatchRestoreǁsave_results__mutmut_15, 
        'xǁBatchRestoreǁsave_results__mutmut_16': xǁBatchRestoreǁsave_results__mutmut_16, 
        'xǁBatchRestoreǁsave_results__mutmut_17': xǁBatchRestoreǁsave_results__mutmut_17, 
        'xǁBatchRestoreǁsave_results__mutmut_18': xǁBatchRestoreǁsave_results__mutmut_18, 
        'xǁBatchRestoreǁsave_results__mutmut_19': xǁBatchRestoreǁsave_results__mutmut_19, 
        'xǁBatchRestoreǁsave_results__mutmut_20': xǁBatchRestoreǁsave_results__mutmut_20, 
        'xǁBatchRestoreǁsave_results__mutmut_21': xǁBatchRestoreǁsave_results__mutmut_21
    }
    
    def save_results(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBatchRestoreǁsave_results__mutmut_orig"), object.__getattribute__(self, "xǁBatchRestoreǁsave_results__mutmut_mutants"), args, kwargs, self)
        return result 
    
    save_results.__signature__ = _mutmut_signature(xǁBatchRestoreǁsave_results__mutmut_orig)
    xǁBatchRestoreǁsave_results__mutmut_orig.__name__ = 'xǁBatchRestoreǁsave_results'

    def xǁBatchRestoreǁ_restore_single__mutmut_orig(self, item: BatchItem) -> dict[str, Any]:
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

    def xǁBatchRestoreǁ_restore_single__mutmut_1(self, item: BatchItem) -> dict[str, Any]:
        restore_fn = None
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

    def xǁBatchRestoreǁ_restore_single__mutmut_2(self, item: BatchItem) -> dict[str, Any]:
        restore_fn = self.service.restore_to_path
        decorated = None
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

    def xǁBatchRestoreǁ_restore_single__mutmut_3(self, item: BatchItem) -> dict[str, Any]:
        restore_fn = self.service.restore_to_path
        decorated = retry_with_backoff(self.retry_config)(None)
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

    def xǁBatchRestoreǁ_restore_single__mutmut_4(self, item: BatchItem) -> dict[str, Any]:
        restore_fn = self.service.restore_to_path
        decorated = retry_with_backoff(None)(restore_fn)
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

    def xǁBatchRestoreǁ_restore_single__mutmut_5(self, item: BatchItem) -> dict[str, Any]:
        restore_fn = self.service.restore_to_path
        decorated = retry_with_backoff(self.retry_config)(restore_fn)
        status = None
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

    def xǁBatchRestoreǁ_restore_single__mutmut_6(self, item: BatchItem) -> dict[str, Any]:
        restore_fn = self.service.restore_to_path
        decorated = retry_with_backoff(self.retry_config)(restore_fn)
        status = "XXSUCCESSXX"
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

    def xǁBatchRestoreǁ_restore_single__mutmut_7(self, item: BatchItem) -> dict[str, Any]:
        restore_fn = self.service.restore_to_path
        decorated = retry_with_backoff(self.retry_config)(restore_fn)
        status = "success"
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

    def xǁBatchRestoreǁ_restore_single__mutmut_8(self, item: BatchItem) -> dict[str, Any]:
        restore_fn = self.service.restore_to_path
        decorated = retry_with_backoff(self.retry_config)(restore_fn)
        status = "SUCCESS"
        detail: str | None = ""
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

    def xǁBatchRestoreǁ_restore_single__mutmut_9(self, item: BatchItem) -> dict[str, Any]:
        restore_fn = self.service.restore_to_path
        decorated = retry_with_backoff(self.retry_config)(restore_fn)
        status = "SUCCESS"
        detail: str | None = None
        metrics: TimingMetrics | None = ""
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

    def xǁBatchRestoreǁ_restore_single__mutmut_10(self, item: BatchItem) -> dict[str, Any]:
        restore_fn = self.service.restore_to_path
        decorated = retry_with_backoff(self.retry_config)(restore_fn)
        status = "SUCCESS"
        detail: str | None = None
        metrics: TimingMetrics | None = None
        performance_enabled = None
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

    def xǁBatchRestoreǁ_restore_single__mutmut_11(self, item: BatchItem) -> dict[str, Any]:
        restore_fn = self.service.restore_to_path
        decorated = retry_with_backoff(self.retry_config)(restore_fn)
        status = "SUCCESS"
        detail: str | None = None
        metrics: TimingMetrics | None = None
        performance_enabled = self.performance_config.enabled
        try:
            with _optional_timer(None, f"restore:{item.tombstone}") as metrics:
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

    def xǁBatchRestoreǁ_restore_single__mutmut_12(self, item: BatchItem) -> dict[str, Any]:
        restore_fn = self.service.restore_to_path
        decorated = retry_with_backoff(self.retry_config)(restore_fn)
        status = "SUCCESS"
        detail: str | None = None
        metrics: TimingMetrics | None = None
        performance_enabled = self.performance_config.enabled
        try:
            with _optional_timer(performance_enabled, None) as metrics:
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

    def xǁBatchRestoreǁ_restore_single__mutmut_13(self, item: BatchItem) -> dict[str, Any]:
        restore_fn = self.service.restore_to_path
        decorated = retry_with_backoff(self.retry_config)(restore_fn)
        status = "SUCCESS"
        detail: str | None = None
        metrics: TimingMetrics | None = None
        performance_enabled = self.performance_config.enabled
        try:
            with _optional_timer(f"restore:{item.tombstone}") as metrics:
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

    def xǁBatchRestoreǁ_restore_single__mutmut_14(self, item: BatchItem) -> dict[str, Any]:
        restore_fn = self.service.restore_to_path
        decorated = retry_with_backoff(self.retry_config)(restore_fn)
        status = "SUCCESS"
        detail: str | None = None
        metrics: TimingMetrics | None = None
        performance_enabled = self.performance_config.enabled
        try:
            with _optional_timer(performance_enabled, ) as metrics:
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

    def xǁBatchRestoreǁ_restore_single__mutmut_15(self, item: BatchItem) -> dict[str, Any]:
        restore_fn = self.service.restore_to_path
        decorated = retry_with_backoff(self.retry_config)(restore_fn)
        status = "SUCCESS"
        detail: str | None = None
        metrics: TimingMetrics | None = None
        performance_enabled = self.performance_config.enabled
        try:
            with _optional_timer(performance_enabled, f"restore:{item.tombstone}") as metrics:
                decorated(None, output_path=item.output, actor=item.actor)
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

    def xǁBatchRestoreǁ_restore_single__mutmut_16(self, item: BatchItem) -> dict[str, Any]:
        restore_fn = self.service.restore_to_path
        decorated = retry_with_backoff(self.retry_config)(restore_fn)
        status = "SUCCESS"
        detail: str | None = None
        metrics: TimingMetrics | None = None
        performance_enabled = self.performance_config.enabled
        try:
            with _optional_timer(performance_enabled, f"restore:{item.tombstone}") as metrics:
                decorated(item.tombstone, output_path=None, actor=item.actor)
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

    def xǁBatchRestoreǁ_restore_single__mutmut_17(self, item: BatchItem) -> dict[str, Any]:
        restore_fn = self.service.restore_to_path
        decorated = retry_with_backoff(self.retry_config)(restore_fn)
        status = "SUCCESS"
        detail: str | None = None
        metrics: TimingMetrics | None = None
        performance_enabled = self.performance_config.enabled
        try:
            with _optional_timer(performance_enabled, f"restore:{item.tombstone}") as metrics:
                decorated(item.tombstone, output_path=item.output, actor=None)
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

    def xǁBatchRestoreǁ_restore_single__mutmut_18(self, item: BatchItem) -> dict[str, Any]:
        restore_fn = self.service.restore_to_path
        decorated = retry_with_backoff(self.retry_config)(restore_fn)
        status = "SUCCESS"
        detail: str | None = None
        metrics: TimingMetrics | None = None
        performance_enabled = self.performance_config.enabled
        try:
            with _optional_timer(performance_enabled, f"restore:{item.tombstone}") as metrics:
                decorated(output_path=item.output, actor=item.actor)
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

    def xǁBatchRestoreǁ_restore_single__mutmut_19(self, item: BatchItem) -> dict[str, Any]:
        restore_fn = self.service.restore_to_path
        decorated = retry_with_backoff(self.retry_config)(restore_fn)
        status = "SUCCESS"
        detail: str | None = None
        metrics: TimingMetrics | None = None
        performance_enabled = self.performance_config.enabled
        try:
            with _optional_timer(performance_enabled, f"restore:{item.tombstone}") as metrics:
                decorated(item.tombstone, actor=item.actor)
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

    def xǁBatchRestoreǁ_restore_single__mutmut_20(self, item: BatchItem) -> dict[str, Any]:
        restore_fn = self.service.restore_to_path
        decorated = retry_with_backoff(self.retry_config)(restore_fn)
        status = "SUCCESS"
        detail: str | None = None
        metrics: TimingMetrics | None = None
        performance_enabled = self.performance_config.enabled
        try:
            with _optional_timer(performance_enabled, f"restore:{item.tombstone}") as metrics:
                decorated(item.tombstone, output_path=item.output, )
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

    def xǁBatchRestoreǁ_restore_single__mutmut_21(self, item: BatchItem) -> dict[str, Any]:
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
            status = None
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

    def xǁBatchRestoreǁ_restore_single__mutmut_22(self, item: BatchItem) -> dict[str, Any]:
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
            status = "XXFAILEDXX"
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

    def xǁBatchRestoreǁ_restore_single__mutmut_23(self, item: BatchItem) -> dict[str, Any]:
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
            status = "failed"
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

    def xǁBatchRestoreǁ_restore_single__mutmut_24(self, item: BatchItem) -> dict[str, Any]:
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
            detail = None
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

    def xǁBatchRestoreǁ_restore_single__mutmut_25(self, item: BatchItem) -> dict[str, Any]:
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
            detail = str(None)
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

    def xǁBatchRestoreǁ_restore_single__mutmut_26(self, item: BatchItem) -> dict[str, Any]:
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
        result = None
        if metrics is not None and performance_enabled:
            result["duration_ms"] = round(metrics.duration_ms, 3)
            result["metrics"] = metrics.to_dict()
        if detail:
            result["detail"] = detail
        return result

    def xǁBatchRestoreǁ_restore_single__mutmut_27(self, item: BatchItem) -> dict[str, Any]:
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
            "XXtombstoneXX": item.tombstone,
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

    def xǁBatchRestoreǁ_restore_single__mutmut_28(self, item: BatchItem) -> dict[str, Any]:
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
            "TOMBSTONE": item.tombstone,
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

    def xǁBatchRestoreǁ_restore_single__mutmut_29(self, item: BatchItem) -> dict[str, Any]:
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
            "XXoutputXX": item.output.as_posix(),
            "actor": item.actor,
            "status": status,
        }
        if metrics is not None and performance_enabled:
            result["duration_ms"] = round(metrics.duration_ms, 3)
            result["metrics"] = metrics.to_dict()
        if detail:
            result["detail"] = detail
        return result

    def xǁBatchRestoreǁ_restore_single__mutmut_30(self, item: BatchItem) -> dict[str, Any]:
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
            "OUTPUT": item.output.as_posix(),
            "actor": item.actor,
            "status": status,
        }
        if metrics is not None and performance_enabled:
            result["duration_ms"] = round(metrics.duration_ms, 3)
            result["metrics"] = metrics.to_dict()
        if detail:
            result["detail"] = detail
        return result

    def xǁBatchRestoreǁ_restore_single__mutmut_31(self, item: BatchItem) -> dict[str, Any]:
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
            "XXactorXX": item.actor,
            "status": status,
        }
        if metrics is not None and performance_enabled:
            result["duration_ms"] = round(metrics.duration_ms, 3)
            result["metrics"] = metrics.to_dict()
        if detail:
            result["detail"] = detail
        return result

    def xǁBatchRestoreǁ_restore_single__mutmut_32(self, item: BatchItem) -> dict[str, Any]:
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
            "ACTOR": item.actor,
            "status": status,
        }
        if metrics is not None and performance_enabled:
            result["duration_ms"] = round(metrics.duration_ms, 3)
            result["metrics"] = metrics.to_dict()
        if detail:
            result["detail"] = detail
        return result

    def xǁBatchRestoreǁ_restore_single__mutmut_33(self, item: BatchItem) -> dict[str, Any]:
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
            "XXstatusXX": status,
        }
        if metrics is not None and performance_enabled:
            result["duration_ms"] = round(metrics.duration_ms, 3)
            result["metrics"] = metrics.to_dict()
        if detail:
            result["detail"] = detail
        return result

    def xǁBatchRestoreǁ_restore_single__mutmut_34(self, item: BatchItem) -> dict[str, Any]:
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
            "STATUS": status,
        }
        if metrics is not None and performance_enabled:
            result["duration_ms"] = round(metrics.duration_ms, 3)
            result["metrics"] = metrics.to_dict()
        if detail:
            result["detail"] = detail
        return result

    def xǁBatchRestoreǁ_restore_single__mutmut_35(self, item: BatchItem) -> dict[str, Any]:
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
        if metrics is not None or performance_enabled:
            result["duration_ms"] = round(metrics.duration_ms, 3)
            result["metrics"] = metrics.to_dict()
        if detail:
            result["detail"] = detail
        return result

    def xǁBatchRestoreǁ_restore_single__mutmut_36(self, item: BatchItem) -> dict[str, Any]:
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
        if metrics is None and performance_enabled:
            result["duration_ms"] = round(metrics.duration_ms, 3)
            result["metrics"] = metrics.to_dict()
        if detail:
            result["detail"] = detail
        return result

    def xǁBatchRestoreǁ_restore_single__mutmut_37(self, item: BatchItem) -> dict[str, Any]:
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
            result["duration_ms"] = None
            result["metrics"] = metrics.to_dict()
        if detail:
            result["detail"] = detail
        return result

    def xǁBatchRestoreǁ_restore_single__mutmut_38(self, item: BatchItem) -> dict[str, Any]:
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
            result["XXduration_msXX"] = round(metrics.duration_ms, 3)
            result["metrics"] = metrics.to_dict()
        if detail:
            result["detail"] = detail
        return result

    def xǁBatchRestoreǁ_restore_single__mutmut_39(self, item: BatchItem) -> dict[str, Any]:
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
            result["DURATION_MS"] = round(metrics.duration_ms, 3)
            result["metrics"] = metrics.to_dict()
        if detail:
            result["detail"] = detail
        return result

    def xǁBatchRestoreǁ_restore_single__mutmut_40(self, item: BatchItem) -> dict[str, Any]:
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
            result["duration_ms"] = round(None, 3)
            result["metrics"] = metrics.to_dict()
        if detail:
            result["detail"] = detail
        return result

    def xǁBatchRestoreǁ_restore_single__mutmut_41(self, item: BatchItem) -> dict[str, Any]:
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
            result["duration_ms"] = round(metrics.duration_ms, None)
            result["metrics"] = metrics.to_dict()
        if detail:
            result["detail"] = detail
        return result

    def xǁBatchRestoreǁ_restore_single__mutmut_42(self, item: BatchItem) -> dict[str, Any]:
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
            result["duration_ms"] = round(3)
            result["metrics"] = metrics.to_dict()
        if detail:
            result["detail"] = detail
        return result

    def xǁBatchRestoreǁ_restore_single__mutmut_43(self, item: BatchItem) -> dict[str, Any]:
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
            result["duration_ms"] = round(metrics.duration_ms, )
            result["metrics"] = metrics.to_dict()
        if detail:
            result["detail"] = detail
        return result

    def xǁBatchRestoreǁ_restore_single__mutmut_44(self, item: BatchItem) -> dict[str, Any]:
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
            result["duration_ms"] = round(metrics.duration_ms, 4)
            result["metrics"] = metrics.to_dict()
        if detail:
            result["detail"] = detail
        return result

    def xǁBatchRestoreǁ_restore_single__mutmut_45(self, item: BatchItem) -> dict[str, Any]:
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
            result["metrics"] = None
        if detail:
            result["detail"] = detail
        return result

    def xǁBatchRestoreǁ_restore_single__mutmut_46(self, item: BatchItem) -> dict[str, Any]:
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
            result["XXmetricsXX"] = metrics.to_dict()
        if detail:
            result["detail"] = detail
        return result

    def xǁBatchRestoreǁ_restore_single__mutmut_47(self, item: BatchItem) -> dict[str, Any]:
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
            result["METRICS"] = metrics.to_dict()
        if detail:
            result["detail"] = detail
        return result

    def xǁBatchRestoreǁ_restore_single__mutmut_48(self, item: BatchItem) -> dict[str, Any]:
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
            result["detail"] = None
        return result

    def xǁBatchRestoreǁ_restore_single__mutmut_49(self, item: BatchItem) -> dict[str, Any]:
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
            result["XXdetailXX"] = detail
        return result

    def xǁBatchRestoreǁ_restore_single__mutmut_50(self, item: BatchItem) -> dict[str, Any]:
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
            result["DETAIL"] = detail
        return result
    
    xǁBatchRestoreǁ_restore_single__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBatchRestoreǁ_restore_single__mutmut_1': xǁBatchRestoreǁ_restore_single__mutmut_1, 
        'xǁBatchRestoreǁ_restore_single__mutmut_2': xǁBatchRestoreǁ_restore_single__mutmut_2, 
        'xǁBatchRestoreǁ_restore_single__mutmut_3': xǁBatchRestoreǁ_restore_single__mutmut_3, 
        'xǁBatchRestoreǁ_restore_single__mutmut_4': xǁBatchRestoreǁ_restore_single__mutmut_4, 
        'xǁBatchRestoreǁ_restore_single__mutmut_5': xǁBatchRestoreǁ_restore_single__mutmut_5, 
        'xǁBatchRestoreǁ_restore_single__mutmut_6': xǁBatchRestoreǁ_restore_single__mutmut_6, 
        'xǁBatchRestoreǁ_restore_single__mutmut_7': xǁBatchRestoreǁ_restore_single__mutmut_7, 
        'xǁBatchRestoreǁ_restore_single__mutmut_8': xǁBatchRestoreǁ_restore_single__mutmut_8, 
        'xǁBatchRestoreǁ_restore_single__mutmut_9': xǁBatchRestoreǁ_restore_single__mutmut_9, 
        'xǁBatchRestoreǁ_restore_single__mutmut_10': xǁBatchRestoreǁ_restore_single__mutmut_10, 
        'xǁBatchRestoreǁ_restore_single__mutmut_11': xǁBatchRestoreǁ_restore_single__mutmut_11, 
        'xǁBatchRestoreǁ_restore_single__mutmut_12': xǁBatchRestoreǁ_restore_single__mutmut_12, 
        'xǁBatchRestoreǁ_restore_single__mutmut_13': xǁBatchRestoreǁ_restore_single__mutmut_13, 
        'xǁBatchRestoreǁ_restore_single__mutmut_14': xǁBatchRestoreǁ_restore_single__mutmut_14, 
        'xǁBatchRestoreǁ_restore_single__mutmut_15': xǁBatchRestoreǁ_restore_single__mutmut_15, 
        'xǁBatchRestoreǁ_restore_single__mutmut_16': xǁBatchRestoreǁ_restore_single__mutmut_16, 
        'xǁBatchRestoreǁ_restore_single__mutmut_17': xǁBatchRestoreǁ_restore_single__mutmut_17, 
        'xǁBatchRestoreǁ_restore_single__mutmut_18': xǁBatchRestoreǁ_restore_single__mutmut_18, 
        'xǁBatchRestoreǁ_restore_single__mutmut_19': xǁBatchRestoreǁ_restore_single__mutmut_19, 
        'xǁBatchRestoreǁ_restore_single__mutmut_20': xǁBatchRestoreǁ_restore_single__mutmut_20, 
        'xǁBatchRestoreǁ_restore_single__mutmut_21': xǁBatchRestoreǁ_restore_single__mutmut_21, 
        'xǁBatchRestoreǁ_restore_single__mutmut_22': xǁBatchRestoreǁ_restore_single__mutmut_22, 
        'xǁBatchRestoreǁ_restore_single__mutmut_23': xǁBatchRestoreǁ_restore_single__mutmut_23, 
        'xǁBatchRestoreǁ_restore_single__mutmut_24': xǁBatchRestoreǁ_restore_single__mutmut_24, 
        'xǁBatchRestoreǁ_restore_single__mutmut_25': xǁBatchRestoreǁ_restore_single__mutmut_25, 
        'xǁBatchRestoreǁ_restore_single__mutmut_26': xǁBatchRestoreǁ_restore_single__mutmut_26, 
        'xǁBatchRestoreǁ_restore_single__mutmut_27': xǁBatchRestoreǁ_restore_single__mutmut_27, 
        'xǁBatchRestoreǁ_restore_single__mutmut_28': xǁBatchRestoreǁ_restore_single__mutmut_28, 
        'xǁBatchRestoreǁ_restore_single__mutmut_29': xǁBatchRestoreǁ_restore_single__mutmut_29, 
        'xǁBatchRestoreǁ_restore_single__mutmut_30': xǁBatchRestoreǁ_restore_single__mutmut_30, 
        'xǁBatchRestoreǁ_restore_single__mutmut_31': xǁBatchRestoreǁ_restore_single__mutmut_31, 
        'xǁBatchRestoreǁ_restore_single__mutmut_32': xǁBatchRestoreǁ_restore_single__mutmut_32, 
        'xǁBatchRestoreǁ_restore_single__mutmut_33': xǁBatchRestoreǁ_restore_single__mutmut_33, 
        'xǁBatchRestoreǁ_restore_single__mutmut_34': xǁBatchRestoreǁ_restore_single__mutmut_34, 
        'xǁBatchRestoreǁ_restore_single__mutmut_35': xǁBatchRestoreǁ_restore_single__mutmut_35, 
        'xǁBatchRestoreǁ_restore_single__mutmut_36': xǁBatchRestoreǁ_restore_single__mutmut_36, 
        'xǁBatchRestoreǁ_restore_single__mutmut_37': xǁBatchRestoreǁ_restore_single__mutmut_37, 
        'xǁBatchRestoreǁ_restore_single__mutmut_38': xǁBatchRestoreǁ_restore_single__mutmut_38, 
        'xǁBatchRestoreǁ_restore_single__mutmut_39': xǁBatchRestoreǁ_restore_single__mutmut_39, 
        'xǁBatchRestoreǁ_restore_single__mutmut_40': xǁBatchRestoreǁ_restore_single__mutmut_40, 
        'xǁBatchRestoreǁ_restore_single__mutmut_41': xǁBatchRestoreǁ_restore_single__mutmut_41, 
        'xǁBatchRestoreǁ_restore_single__mutmut_42': xǁBatchRestoreǁ_restore_single__mutmut_42, 
        'xǁBatchRestoreǁ_restore_single__mutmut_43': xǁBatchRestoreǁ_restore_single__mutmut_43, 
        'xǁBatchRestoreǁ_restore_single__mutmut_44': xǁBatchRestoreǁ_restore_single__mutmut_44, 
        'xǁBatchRestoreǁ_restore_single__mutmut_45': xǁBatchRestoreǁ_restore_single__mutmut_45, 
        'xǁBatchRestoreǁ_restore_single__mutmut_46': xǁBatchRestoreǁ_restore_single__mutmut_46, 
        'xǁBatchRestoreǁ_restore_single__mutmut_47': xǁBatchRestoreǁ_restore_single__mutmut_47, 
        'xǁBatchRestoreǁ_restore_single__mutmut_48': xǁBatchRestoreǁ_restore_single__mutmut_48, 
        'xǁBatchRestoreǁ_restore_single__mutmut_49': xǁBatchRestoreǁ_restore_single__mutmut_49, 
        'xǁBatchRestoreǁ_restore_single__mutmut_50': xǁBatchRestoreǁ_restore_single__mutmut_50
    }
    
    def _restore_single(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBatchRestoreǁ_restore_single__mutmut_orig"), object.__getattribute__(self, "xǁBatchRestoreǁ_restore_single__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _restore_single.__signature__ = _mutmut_signature(xǁBatchRestoreǁ_restore_single__mutmut_orig)
    xǁBatchRestoreǁ_restore_single__mutmut_orig.__name__ = 'xǁBatchRestoreǁ_restore_single'


@contextmanager
def _optional_timer(enabled: bool, name: str):
    if enabled:
        with timer(name) as metrics:
            yield metrics
    else:
        yield TimingMetrics(name=name, started_ns=0, finished_ns=0)
