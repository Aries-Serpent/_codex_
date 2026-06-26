"""
Test Worker Checkpoint

Test module for worker checkpoint.
"""

import json

from workers.embedding_worker import run_worker


def test_worker_checkpoint_resume(tmp_path, monkeypatch):
    items = [
        {"id": "a", "content": "hello", "metadata": {}},
        {"id": "b", "content": "world", "metadata": {}},
    ]
    payload = tmp_path / "sample.json"
    payload.write_text(json.dumps(items), encoding="utf-8")

    monkeypatch.setenv("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    monkeypatch.setenv("EMBEDDING_CHUNK_MAX_CHARS", "1000")
    monkeypatch.setenv("EMBEDDING_CHUNK_OVERLAP", "0")
    checkpoint = tmp_path / "ck.json"

    class FakeAdapter:
        def __init__(self):
            self.upsert_calls = []

        def connect(self):
            return None

        def upsert_batch(self, namespace, items):
            self.upsert_calls.append({"namespace": namespace, "items": list(items)})

    fake_adapter = FakeAdapter()

    def _load_adapter():
        return fake_adapter, "fake.adapter"

    monkeypatch.setattr("src.mcp.server.adapter_loader.load_adapter", _load_adapter)

    run_worker(
        str(payload),
        batch_size=2,
        namespace_default="testns",
        checkpoint_path=str(checkpoint),
    )
    assert checkpoint.exists(), "Condition must be true"
    seen_first = set(json.loads(checkpoint.read_text()))
    first_upserts = len(fake_adapter.upsert_calls)

    run_worker(
        str(payload),
        batch_size=2,
        namespace_default="testns",
        checkpoint_path=str(checkpoint),
    )
    seen_second = set(json.loads(checkpoint.read_text()))
    assert seen_second.issuperset(seen_first), "Condition must be true"
    assert len(fake_adapter.upsert_calls) == first_upserts, "Collection must not be empty"
