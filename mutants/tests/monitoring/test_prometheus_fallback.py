"""Ensure Prometheus fallback emits NDJSON metrics when client missing."""

from __future__ import annotations

import builtins
import importlib
import json
import sys


def test_prometheus_fallback_writes_ndjson(monkeypatch, tmp_path, capsys):
    module = importlib.reload(importlib.import_module("codex_ml.monitoring.prometheus"))

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name.startswith("prometheus_client"):
            raise ImportError("prometheus_client missing")
        return real_import(name, *args, **kwargs)

    monkeypatch.setitem(sys.modules, "prometheus_client", None)
    monkeypatch.setattr(builtins, "__import__", fake_import)

    counters, gauges = module.maybe_export_metrics(port=0, fallback_dir=tmp_path)
    assert counters, "Count must be greater than zero"
    assert gauges, "gauges is not valid"
    counters["requests_total"].inc()
    gauges["queue_depth"].set(5)

    sink = tmp_path / "prometheus.ndjson"
    assert sink.exists(), "Condition must be true"
    records = [
        json.loads(line) for line in sink.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    assert any(rec.get("metric") == "requests_total" for rec in records), "Condition must be true"
    assert any(rec.get("metric") == "queue_depth" for rec in records), "Condition must be true"

    active, path, reason = module.fallback_status()
    assert active is True, "active is not valid"
    assert path == sink, "path is not valid"
    assert "prometheus_client missing" in (reason or ""), "Condition must be true"

    captured = capsys.readouterr()
    assert "falling back to NDJSON" in captured.err, "Condition must be true"
