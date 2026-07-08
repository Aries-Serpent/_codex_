"""
Test Registry Logger

Test module for registry logger.
"""

from __future__ import annotations

import json
from types import SimpleNamespace

from codex_ml.logging import registry


def test_registry_ndjson_logger_includes_system_metrics(tmp_path, monkeypatch):
    path = tmp_path / "metrics.ndjson"

    class _DummyMem:
        rss = 64 * 1024 * 1024

    class _DummyProcess:
        def memory_info(self):
            return _DummyMem()

    fake_psutil = SimpleNamespace(
        Process=lambda: _DummyProcess(),
        cpu_percent=lambda interval=None: 12.5,
    )

    monkeypatch.setattr(registry, "psutil", fake_psutil, raising=False)
    monkeypatch.setattr(registry, "pynvml", None, raising=False)

    logger = registry.NDJSONLogger(
        path,
        sys_metrics=True,
        max_bytes=None,
        backup_count=1,
        max_age_s=None,
    )

    logger.log({"loss": 1.0})
    logger.close()

    payload = json.loads(path.read_text().splitlines()[0])
    assert payload["loss"] == 1.0, "Condition must be true"
    assert payload["mem_rss_mb"] == 64.0, "Condition must be true"
    assert payload["cpu_percent"] == 12.5, "Condition must be true"
    assert "gpu_mem_mb" not in payload, "Condition must be true"


def test_registry_ndjson_logger_rotates(tmp_path, monkeypatch):
    path = tmp_path / "metrics.ndjson"
    monkeypatch.setattr(registry, "psutil", None, raising=False)
    monkeypatch.setattr(registry, "pynvml", None, raising=False)

    logger = registry.NDJSONLogger(
        path,
        sys_metrics=False,
        max_bytes=60,
        backup_count=1,
        max_age_s=None,
    )

    for idx in range(8):
        logger.log({"idx": idx})

    logger.close()

    rotated = path.with_name("metrics.ndjson.1")
    assert rotated.exists(), "Condition must be true"
    assert path.exists(), "Condition must be true"
