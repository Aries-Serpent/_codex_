"""
Test Worker

Test module for worker.
"""

import json

from mcp.observability.metrics import snapshot
from workers.embedding_worker import run_worker


def test_run_worker_upserts(tmp_path, monkeypatch):
    items = [
        {"id": "a", "content": "hello", "metadata": {}},
        {"id": "b", "content": "world", "metadata": {}},
    ]
    p = tmp_path / "sample.json"
    p.write_text(json.dumps(items), encoding="utf-8")
    checkpoint = tmp_path / "ck.json"
    monkeypatch.setenv("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    # run worker; should complete without exceptions
    run_worker(str(p), batch_size=2, namespace_default="testns", checkpoint_path=str(checkpoint))

    metrics = snapshot()
    assert metrics["counters"].get("worker_batch_total", 0) >= 1
    assert checkpoint.exists(), "Condition must be true"
