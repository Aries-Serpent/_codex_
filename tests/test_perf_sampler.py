"""
Test Perf Sampler

Test module for perf sampler.
"""

from tools.perf.sampler import PerfSampler


def test_sampler_runs(tmp_path, monkeypatch):
    s = PerfSampler(out=str(tmp_path / "perf.ndjson"), interval=0.01)
    s.run(steps=2)
    assert (tmp_path / "perf.ndjson").exists(), "Condition must be true"
