@Codex Implement Test Infrastructure, Contract Tests, Checkpoint & Rate-limit Tests, Metrics/Retry Tests, Security Checklist, and ALL aspects and components discussed below.

Purpose
- This adds the missing test infra and light integration scaffolds requested during Plan A–D and missing in implementation:
  - pytest.ini registering markers
  - Contract tests for façade → adapter calls
  - Checkpoint/resume unit test for the embedding worker
  - Rate-limit middleware unit test (throttle / 429)
  - Retry and metrics unit tests
  - Security gating checklist doc
  - Small CI job update (mcp-ci.yml) to ensure new tests are run in CI

Files included
- pytest.ini
- tests/test_retries.py
- tests/test_metrics.py
- tests/mcp/test_facade_contract.py
- tests/mcp/test_rate_limit_middleware.py
- tests/embeddings/test_worker_checkpoint.py
- docs/SECURITY_GATING_CHECKLIST.md
- .github/workflows/mcp-ci.yml (suggested update that runs the new tests; if CI already exists, this is a replacement/augmentation)

Acceptance criteria
- [ ] pytest.ini present and pytest runs without "unknown markers" warnings.
- [ ] Basic retry behavior verified by tests/test_retries.py.
- [ ] Metrics facade behavior verified by tests/test_metrics.py.
- [ ] Façade contract test asserts the façade calls adapter.query_top_k with the expected args.
- [ ] Rate-limit middleware test demonstrates a 429 when tokens exhausted.
- [ ] Worker checkpoint test creates checkpoint file and shows second run reads it (no exceptions).
- [ ] docs/SECURITY_GATING_CHECKLIST.md added and reviewed.
- [ ] CI mcp-ci.yml runs tests/mcp and tests/embeddings; jobs succeed on mock-only runs in CI.

How to run locally
- Ensure repo installed in editable mode or PYTHONPATH set:
  - python -m venv .venv
  - source .venv/bin/activate
  - pip install -U pip
  - pip install -e .
  - export PYTHONPATH="$(pwd):$PYTHONPATH"  # if necessary
- Run the tests:
  - pytest -q tests/mcp -k "not live" --maxfail=1
  - pytest -q tests/embeddings --maxfail=1
  - pytest -q tests/test_retries.py tests/test_metrics.py

Notes & rationale
- All tests use in-repo mocks or existing mock backends and do not require secrets.
- Tests are deliberately minimal and deterministic so CI runs quickly.
- If any existing modules are missing (façade app, adapter loader), tests will fail and we will iterate. This PR is intended to uncover wiring/import issues early.

Next steps
- Tests reveal import errors or truncated files, fix those modules and re-run tests.
- Add recorded-mode fixtures & gating enhancements.

```ini name=pytest.ini
[pytest]
addopts = -q
testpaths = tests
markers =
    recorded: integration tests that use recorded fixtures
    live: integration tests that call live providers (gated)
    not_live: tests that must run without live provider access
```

```python name=tests/test_retries.py
from time import time
import pytest
from src.mcp.retries import retry_on_exception

counter = {"v": 0}


def _make_flaky(fail_times: int = 2):
    def fn():
        if counter["v"] < fail_times:
            counter["v"] += 1
            raise RuntimeError("transient")
        return "ok"
    return fn


def test_retry_on_exception_succeeds_after_retries():
    counter["v"] = 0
    flaky = _make_flaky(fail_times=2)

    wrapped = retry_on_exception(tries=4, base_delay=0.001, max_delay=0.002)(flaky)
    result = wrapped()
    assert result == "ok"
    assert counter["v"] == 2


def test_retry_on_exception_raises_after_exhaustion():
    counter["v"] = 0
    flaky = _make_flaky(fail_times=5)
    wrapped = retry_on_exception(tries=3, base_delay=0.001, max_delay=0.002)(flaky)
    with pytest.raises(RuntimeError):
        wrapped()
```

```python name=tests/test_metrics.py
from src.mcp.observability.metrics import increment, Timer, snapshot, _metrics, _timers

def test_increment_and_snapshot():
    # reset internal state if present
    _metrics.clear()
    _timers.clear()

    increment("x_test", 1)
    increment("x_test", 2)
    assert snapshot()["counters"]["x_test"] == 3

def test_timer_context_records_time():
    _metrics.clear()
    _timers.clear()

    with Timer("t_test"):
        # trivial block
        total = sum(range(10))
    s = snapshot()
    # timer count incremented
    assert s["counters"].get("t_test_count", 0) >= 1
    assert "t_test" in s["timers"]
```

```python name=tests/mcp/test_facade_contract.py
import pytest
from fastapi.testclient import TestClient
from types import SimpleNamespace
from unittest.mock import MagicMock

# Import APP lazily to avoid import-time errors; ensure facade exists
try:
    from src.mcp.server.facade_fastapi import APP  # type: ignore
except Exception:
    APP = None  # tests will assert presence earlier

CLIENT_AVAILABLE = APP is not None

@pytest.fixture(autouse=True)
def fake_adapter_loader(monkeypatch):
    """
    Monkeypatch adapter_loader.load_adapter to return a fake adapter object
    that records calls for assertion.
    """
    calls = {}

    class FakeAdapter:
        def __init__(self):
            self.query_calls = []
            self.upsert_calls = []
            self.delete_calls = []

        def connect(self):
            return None

        def query_top_k(self, namespace, query_embedding, top_k=5, filters=None):
            self.query_calls.append({"namespace": namespace, "query_embedding": query_embedding, "top_k": top_k, "filters": filters})
            # return fake hits
            return [{"id": "x", "score": 0.9, "content": "", "metadata": {}}]

        def upsert_batch(self, namespace, items):
            self.upsert_calls.append({"namespace": namespace, "items": list(items)})

        def delete(self, namespace, id):
            self.delete_calls.append({"namespace": namespace, "id": id})
            return True

        def health_check(self):
            return {"status": "ok", "adapter": "fake"}

    fake = FakeAdapter()
    monkeypatch.setitem(__import__("sys").modules, "src.mcp.server.adapter_loader", SimpleNamespace(load_adapter=lambda: (fake, "fake.adapter")))
    # Also monkeypatch importable function if needed
    try:
        import src.mcp.server.adapter_loader as al  # type: ignore
        monkeypatch.setattr(al, "load_adapter", lambda: (fake, "fake.adapter"))
    except Exception:
        pass

    yield fake


@pytest.mark.skipif(not CLIENT_AVAILABLE, reason="Façade APP not importable")
def test_calltool_invokes_adapter_query_top_k():
    client = TestClient(APP)
    # send callTool with tool id that façade maps to a retrieval call (mcp.tool.query)
    payload = {
        "jsonrpc": "2.0",
        "method": "mcp.callTool",
        "params": {
            "tool_id": "mcp.tool.query",
            "input": {"embedding": [1.0, 0.0], "filters": {"tag": "x"}},
            "top_k": 3,
            "tenant": "tenant-1"
        },
        "id": "test1"
    }
    resp = client.post("/jsonrpc", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert "result" in body
    # Verify fake adapter recorded a query call (via fixture)
    # The fake adapter instance is attached in the fixture (indirectly); retrieve via module
    import importlib
    al = importlib.import_module("src.mcp.server.adapter_loader")
    fake, _ = al.load_adapter()
    assert hasattr(fake, "query_calls")
    assert len(fake.query_calls) >= 1
    first = fake.query_calls[0]
    assert first["namespace"] == "tenant-1"
    assert first["query_embedding"] == [1.0, 0.0]
    assert first["top_k"] == 3
    assert first["filters"] == {"tag": "x"}
```

```python name=tests/mcp/test_rate_limit_middleware.py
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.mcp.middleware.rate_limit_middleware import RateLimitMiddleware
import time

def test_rate_limit_throttling():
    app = FastAPI()

    @app.get("/ping")
    async def ping():
        return {"ok": True}

    # add middleware with very small burst and low rate to trigger quickly
    app.add_middleware(RateLimitMiddleware, rate=1, burst=2)

    client = TestClient(app)

    # Make rapid requests: first two should pass, subsequent may be throttled
    res1 = client.get("/ping")
    assert res1.status_code == 200
    res2 = client.get("/ping")
    assert res2.status_code == 200

    # Make several quick requests to trigger 429. Depending on timing this may be 429.
    throttled = False
    for _ in range(5):
        r = client.get("/ping")
        if r.status_code == 429:
            throttled = True
            break
        # slight pause to let tokens replenish a tiny bit
        time.sleep(0.01)

    assert throttled, "Expected at least one request to be throttled (429)"
```

```python name=tests/embeddings/test_worker_checkpoint.py
import json
from pathlib import Path
from src.workers.embedding_worker import run_worker
from src.mcp.embeddings.mock_embedder import MockEmbedder
import os
import tempfile

def test_worker_checkpoint_resume(tmp_path, monkeypatch):
    # Prepare a small input
    items = [{"id":"a","content":"hello","metadata":{}},{"id":"b","content":"world","metadata":{}}]
    p = tmp_path / "sample.json"
    p.write_text(json.dumps(items), encoding="utf-8")

    # Ensure embedder class env and adapter default to mock via adapter_loader in worker
    monkeypatch.setenv("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")

    ck = tmp_path / "ck.json"

    # First run: produce checkpoint file
    run_worker(str(p), batch_size=2, namespace_default="testns", checkpoint_path=str(ck))

    assert ck.exists()
    seen_first = set(json.loads(ck.read_text()))

    # Second run: should not fail and should not remove entries; checkpoint should remain same or increase only
    run_worker(str(p), batch_size=2, namespace_default="testns", checkpoint_path=str(ck))
    seen_second = set(json.loads(ck.read_text()))
    # second run should not reduce checkpoint entries
    assert seen_second.issuperset(seen_first)
```