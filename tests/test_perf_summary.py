"""
Test Perf Summary

Test module for perf summary.
"""
import pytest
import json
    from tools.perf.summarize import main as summarize



def test_perf_summary(tmp_path, monkeypatch):
    d = tmp_path / "artifacts" / "logs"
    d.mkdir(parents=True, exist_ok=True)
    (d / "perf.ndjson").write_text(
        '{"cpu":10,"mem":{"percent":30}}\n{"cpu":20,"mem":{"percent":40}}\n'
    )
    monkeypatch.chdir(tmp_path)

    summarize()
    out = json.loads((tmp_path / "audit_artifacts/perf_summary.json").read_text())
    assert out["cpu_mean"] == 15.0 and out["mem_mean"] == 35.0, "Condition must be true"
