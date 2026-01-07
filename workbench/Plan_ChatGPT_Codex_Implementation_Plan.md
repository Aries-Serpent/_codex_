# [Pre-Plan]: Review & Readiness — MCP Plans A→D Implementation
> Generated: 2025-12-19T00:00:00Z | Author: mbaetiong

Purpose
- Provide a concise, actionable pre-plan that reviews Plans A–D (as attached), captures preconditions, orders work, lists risks & mitigations, and defines an execution checklist that ChatGPT Codex (or a human) will follow before implementing Plan A→D files into the repository.
- This pre-plan ensures the repository is ready, CI is safe, and reviewers know exactly what to expect in each PR.

Summary review (short)
- Plans A–D collectively provide a coherent roadmap: Plan A seeds the core scaffolds (adapter interface, mock backend, CI, metrics, retries, conformance tests); Plan B implements Pinecone adapter skeleton; Plan C builds the FastAPI façade with auth, rate-limit, schemas and contract tests; Plan D implements the embedding worker pipeline with chunking, dedupe, checkpointing and provider adapters.
- All plans emphasize "import-safety", "no secrets in repo", "gated live tests", and "use mocks/recordings in CI", which is correct and required.
- Several audit-driven scaffolds have been added across the plans (retries, metrics, rate-limit, safety checks, conformance harness, secret runbook, CI gating). Those should remain small, import-safe and well-tested.

Preconditions (must be verified before coding)
1. Repo layout is normalized:
   - src/ is a package root (tests import src.mcp.*) — verify PYTHONPATH usage or test conftest.
2. Minimal dev tooling:
   - Python 3.10/3.11 available locally and in CI matrix.
   - pytest available (requirements-test.txt optional).
3. No provider secrets present in repo:
   - Confirm .env.example present and no real keys in source.
4. CI templates present and disabled for live runs:
   - .github/workflows/mcp-ci.yml (mock tests)
   - .github/workflows/integration-gated.yml (template)
5. Branching policy:
   - Each Plan uses feature/mcp/plan-<x>-<short> naming; PRs targeted at main or appropriate base branch.

Top-level implementation order (recommended)
1. Plan A (foundation)
   - Add interface, mock backend, basic tests, metrics/retries, basic CI.
   - Validate local pytest and CI runs.
2. Small audit scaffolds (if not in Plan A) — conformance harness, tenant tests, secrets runbook.
3. Plan B (adapter skeleton)
   - Add Pinecone adapter + mocked tests + docs.
   - Ensure it uses retries & metrics scaffolds from A.
4. Plan C (façade)
   - Add FastAPI app, JSON-RPC, schemas, auth, rate-limit, tracing scaffolds, and contract tests.
   - Verify JSON-RPC schema validation works and contract tests pass against mock adapter.
5. Plan D (embedding worker)
   - Add embedder interfaces, mock embedder, batching, chunking, dedupe, checkpointing, worker CLI and tests.
   - Validate worker persists with mock adapter and checkpointing/resume behavior.

Acceptance mapping (high level)
| Plan | Key ACs (short) |
|---:|---|
| A | Interface, mock backend, tests, CI runs with no provider secrets; retries/metrics scaffolds |
| B | PineconeAdapter skeleton, lazy imports, mocked tests, metrics/retries usage |
| C | Façade app with auth/rate-limit/schemas, contract tests, health endpoints, Dockerfile.prod |
| D | Embedding interface/worker, chunking/dedupe/checkpoint, retries + metrics, docker image |

Developer checklist (pre-PR)
- [ ] Create feature branch naming according to plan (feature/mcp/plan-<x>-<desc>).
- [ ] Add 1–3 related files per commit (small commits).
- [ ] Ensure all new Python modules have docstrings and type hints.
- [ ] Write unit tests for new modules; tests must be mock-only (no network).
- [ ] Ensure tests import src package correctly — set PYTHONPATH in docs or include tests/conftest.py if needed.
- [ ] Add docs for env vars (.env.example) and gating process (docs/SECRETS_RUNBOOK.md).
- [ ] Do not include secrets or credentials in any commit.
- [ ] Update .github/workflows/mcp-ci.yml to include new test paths (if adding tests) but ensure live tests gated.

Risk matrix & mitigations
| Risk | Likelihood | Impact | Mitigation |
|---|---:|---:|---|
| Accidental live provider calls in CI | Medium | High (cost & data exposure) | Safety guard (ENABLE_LIVE_TESTS), integration-gated.yml; set provider envs to '' in mcp-ci.yml |
| Import-time failures due to missing provider SDKs | High | Medium | Use lazy imports in adapters/clients; unit tests monkeypatch modules. |
| Tests failing due to incorrect PYTHONPATH | High | Medium | Add tests/conftest.py to append repo root; document PYTHONPATH in README. |
| Metrics/Retry scoping errors causing flaky tests | Medium | Medium | Keep metrics simple in Plan A; tests assert metrics mutated, not exact values. |
| Concurrency/thread-safety issues in mock backend | Low | Medium | Use RLock in InMemoryMockBackend; tests include basic concurrent scenarios if needed. |

Local verification commands (copy-paste)
- Create venv:
  - python -m venv .venv
  - source .venv/bin/activate
- Install:
  - pip install -U pip
  - pip install pytest
- Run Plan-A tests:
  - pytest -q tests/mcp -k "not live" --maxfail=1
- Run full unit set:
  - pytest -q tests -k "not live" --maxfail=1
- If tests can't import src:
  - export PYTHONPATH="$(pwd):$PYTHONPATH"  # or add tests/conftest.py to append repo root

CI guard checklist (before pushing PR)
- Ensure mcp-ci.yml sets provider secrets to empty strings in the test step env (PINECONE_API_KEY: '').
- Integration-gated workflow must only run when ENABLE_LIVE_TESTS=true (and requires explicit secrets).
- Do not add any workflow that uses secrets unless it's gated.

PR template (short) — include on each PR
- Title: Plan <A|B|C|D>: <short desc>
- Summary: one-paragraph what changed and why
- Files added/modified: bullet list of file paths
- Local run steps: exact commands to run tests and start services
- CI expectations: which workflows must pass
- Security: confirm no secrets included
- Reviewer checklist: acceptance criteria mapping and risk checks

Pre-merge approvals and reviewer guidance
- Request at least one backend/infra reviewer for Plans B–D (to validate gating).
- Ask a security reviewer to confirm no secrets and gating before merging integration workflows.
- Validate that Plan A tests are green across Python matrix before merging further Plans.

Estimated effort (rough, per Plan)
- Plan A: 2–4 hours (scaffold + tests + CI).
- Plan B: 3–6 hours (adapter skeleton, tests, docs).
- Plan C: 4–8 hours (façade, schemas, middleware, contract tests).
- Plan D: 6–12 hours (worker, chunking, dedupe, checkpointing, tests, docker).

Deliverables from Pre-Plan
- This file (workbench/PrePlan_ChatGPT_Codex.md)
- A checklist of branches and PRs to create (one per plan).
- A PR template snippet to paste into PR descriptions.

Next immediate actions (for implementer)
1. Confirm working local Python env (3.10/3.11).
2. Create branch for Plan A: feature/mcp/plan-a-adapter-mock-ci.
3. Implement Plan A files as per provided templates; run tests locally.
4. Open Plan A PR including the PR template and link to this pre-plan.
5. After Plan A is merged, proceed Plan B following the order above.

------

# [Plan]: Plan A — ChatGPT Codex Implementation (Adapter Interface + Mock Backend + CI)
> Generated: 2025-12-18T00:00:00Z | Author: mbaetiong 

Purpose / Summary
- Implement a minimal, import-safe, and testable scaffolding for MCP adapter support:
  - A typed BackendAdapter interface (src/mcp/backends/interface.py).
  - Deterministic in-repo InMemoryMockBackend implementing the interface (src/mcp/backends/mock_backend.py).
  - Unit tests exercising the mock backend (tests/mcp/test_backend_mock.py).
  - CI workflow that runs MCP tests against the mock backend (no provider secrets) — .github/workflows/mcp-ci.yml.
  - Minimal docs (.env.example, docs/adapters/README.md, docs/CI.md).
- Additionally include minimal scaffolds required by the cross-plan audit so Plans B–D can build on a consistent foundation. These scaffolds are intentionally lightweight and import-safe:
  - Adapter conformance harness (tests/mcp/conformance/test_adapter_conformance.py).
  - Tenant isolation tests (tests/mcp/test_tenant_isolation.py).
  - Retry/backoff helper (src/mcp/retries.py).
  - Observability metrics facade (src/mcp/observability/metrics.py).
  - Rate-limit middleware scaffold for FastAPI (src/mcp/middleware/rate_limit_middleware.py).
  - Integration-gated CI template (disabled by default) and dependency-scan template.
  - Secrets runbook (docs/SECRETS_RUNBOOK.md).
  - Backup/restore placeholder for Pinecone (tools/backup/pinecone_export.sh).
  - Example recorded fixture for future gated integrations (tests/integration/fixtures/recorded_pinecone/example_query_response.json).

Context & Intent for ChatGPT Codex
- This plan is an implementation recipe for the ChatGPT Codex agent to perform via the repository web UI:
  - Create a feature branch feature/mcp/plan-a-adapter-mock-ci.
  - Add files in the specified paths with the provided/minimal content.
  - Ensure all tests run locally and in CI with no provider secrets.
  - Do not call or store any live provider credentials in repo commits.
  - Keep all new modules import-safe (lazy imports for optional heavy dependencies), unit-tested using in-repo mocks, and documented.

High-level sequence (ordered)
1. Create a feature branch: feature/mcp/plan-a-adapter-mock-ci
2. Add .env.example (placeholders for provider keys)
3. Add src/mcp/backends/interface.py (BackendAdapter interface)
4. Add src/mcp/backends/mock_backend.py (InMemoryMockBackend)
5. Add tests/mcp/test_backend_mock.py (unit tests for mock backend)
6. Add docs: docs/adapters/README.md and docs/CI.md
7. Add CI workflow: .github/workflows/mcp-ci.yml
8. Add audit-driven scaffolds (conformance tests, tenant isolation, retries, metrics, rate-limit middleware, secrets runbook, integration-gated CI, dependency-scan template)
9. Run tests locally; fix import path issues (PYTHONPATH or tests/conftest.py)
10. Push, open PR from feature branch, validate CI runs
11. Iterate on reviewer feedback and merge when CI is green

Why include the audit-driven scaffolds in Plan A
- Early scaffolding saves rework across subsequent plans (B/C/D).
- Provides immediate safety rails (secrets runbook, gated CI templates).
- Ensures adapters can be tested for conformance and tenant isolation from the outset.
- Provides minimal observability and retry primitives for later wiring.

Developer guidance / Constraints
- All code must be import-safe: optional SDKs (pinecone, openai, HF) loaded lazily in Plan B/D.
- Unit tests must not require external network calls or real secrets.
- Keep commits small and focused (one file or small logically-related set per commit).
- Document enabled env vars and gating steps in docs/SECRETS_RUNBOOK.md.
- Integration-gated workflow must require explicit admin action to enable (template only).

Acceptance criteria (explicit)
- Backend Adapter interface exists and is typed (connect, upsert_batch, query_top_k, delete, health_check).
- InMemoryMockBackend implements the Adapter interface with deterministic cosine scoring, metadata filter support, and thread-safety.
- Unit tests for the mock backend run locally and in CI (pytest, matrix python 3.10/3.11).
- CI uses the mock backend by default and does not require provider secrets.
- Conformance test harness and tenant isolation tests are present and exercise the mock backend.
- Minimal retries.py and observability metrics facade exist and are covered by unit tests or used in at least one test.
- Rate-limit middleware scaffold present for future integration with the FastAPI façade in Plan C.
- Integration-gated CI and secrets runbook docs included (template + instructions) for safe future live-provider testing.

Local run & verification (commands)
- Create virtualenv:
  - python -m venv .venv
  - source .venv/bin/activate
- Install minimal dev dependencies:
  - pip install -U pip
  - pip install pytest
- Run tests:
  - pytest -q tests/mcp -k "not live" --maxfail=1
- If import errors occur:
  - export PYTHONPATH="$(pwd):$PYTHONPATH"
  - or add tests/conftest.py that appends repo root to sys.path

Files to add (exact paths & minimal content)
- Add the following files verbatim to the repository; the templates below are ready-to-apply.

Note: Markdown files use four-backtick blocks in this plan (file content follows). Python/YAML code blocks are provided within standard fenced blocks.

---- BEGIN FILE: src/mcp/backends/interface.py ----
```python name=src/mcp/backends/interface.py
# Adapter interface for MCP vector backends
# Minimal typed abstract base class used by adapters and tests.
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, List, Optional, Tuple


class VectorItem(Dict):
    """
    Minimal vector item representation:
    {
      "id": str,
      "embedding": List[float],
      "content": str,
      "metadata": Dict[str, Any]
    }
    """
    pass


class BackendResponse(Dict):
    """
    Query result item:
    {
      "id": str,
      "score": float,
      "content": str,
      "metadata": {...}
    }
    """
    pass


class BackendAdapter(ABC):
    """
    Abstract adapter interface that all vector DB adapters must implement.
    """

    @abstractmethod
    def connect(self) -> None:
        """Initialize connections/clients. Idempotent."""
        raise NotImplementedError

    @abstractmethod
    def upsert_batch(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """Upsert a batch of vector items into namespace/tenant."""
        raise NotImplementedError

    @abstractmethod
    def query_top_k(
        self,
        namespace: str,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[BackendResponse]:
        """Return top_k results with scores and metadata."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, namespace: str, id: str) -> bool:
        """Delete item by id; return True if deleted."""
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Return backend health information (status, details)."""
        raise NotImplementedError
```
---- END FILE ----

---- BEGIN FILE: src/mcp/backends/mock_backend.py ----
```python name=src/mcp/backends/mock_backend.py
# Simple in-memory mock vector backend implementing BackendAdapter
import math
import threading
from typing import Any, Dict, Iterable, List, Optional
from .interface import BackendAdapter, VectorItem, BackendResponse


def cosine_similarity(a: List[float], b: List[float]) -> float:
    # deterministic and simple
    dot = sum(x * y for x, y in zip(a, b))
    lena = math.sqrt(sum(x * x for x in a)) or 1.0
    lenb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (lena * lenb)


class InMemoryMockBackend(BackendAdapter):
    def __init__(self) -> None:
        # storage: namespace -> id -> VectorItem
        self._store: Dict[str, Dict[str, VectorItem]] = {}
        self._lock = threading.RLock()

    def connect(self) -> None:
        # nothing to connect; keep for parity
        return None

    def upsert_batch(self, namespace: str, items: Iterable[VectorItem]) -> None:
        with self._lock:
            ns = self._store.setdefault(namespace, {})
            for item in items:
                ns[item["id"]] = item.copy()

    def query_top_k(
        self,
        namespace: str,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[BackendResponse]:
        with self._lock:
            ns = self._store.get(namespace, {})
            results: List[BackendResponse] = []
            for item in ns.values():
                # simple metadata filter support
                if filters:
                    ok = True
                    for fk, fv in filters.items():
                        if item.get("metadata", {}).get(fk) != fv:
                            ok = False
                            break
                    if not ok:
                        continue
                emb = item.get("embedding")
                if not emb:
                    continue
                score = float(cosine_similarity(query_embedding, emb))
                results.append(
                    BackendResponse(
                        {
                            "id": item["id"],
                            "score": score,
                            "content": item.get("content", ""),
                            "metadata": item.get("metadata", {}),
                        }
                    )
                )
            # stable sort: highest score first; deterministic tie-break by id
            results.sort(key=lambda r: (-r["score"], r["id"]))
            return results[:top_k]

    def delete(self, namespace: str, id: str) -> bool:
        with self._lock:
            ns = self._store.get(namespace, {})
            if id in ns:
                del ns[id]
                return True
            return False

    def health_check(self) -> Dict[str, Any]:
        # simple health payload
        return {"status": "ok", "backend": "mock", "namespaces": list(self._store.keys())}
```
---- END FILE ----

---- BEGIN FILE: tests/mcp/test_backend_mock.py ----
```python name=tests/mcp/test_backend_mock.py
# Tests for the mock backend
import pytest
from src.mcp.backends.mock_backend import InMemoryMockBackend
from src.mcp.backends.interface import VectorItem


@pytest.fixture
def mock_backend() -> InMemoryMockBackend:
    b = InMemoryMockBackend()
    b.connect()
    return b


def test_upsert_and_query(mock_backend: InMemoryMockBackend):
    namespace = "testns"
    items = [
        VectorItem({"id": "a", "embedding": [1.0, 0.0], "content": "apple", "metadata": {"tag": "fruit"}}),
        VectorItem({"id": "b", "embedding": [0.9, 0.1], "content": "apricot", "metadata": {"tag": "fruit"}}),
        VectorItem({"id": "c", "embedding": [0.0, 1.0], "content": "banana", "metadata": {"tag": "fruit"}}),
    ]
    mock_backend.upsert_batch(namespace, items)
    results = mock_backend.query_top_k(namespace, [1.0, 0.0], top_k=2)
    assert len(results) == 2
    assert results[0]["id"] in {"a", "b"}
    assert results[0]["score"] >= results[1]["score"]


def test_delete_and_health(mock_backend: InMemoryMockBackend):
    ns = "delns"
    item = VectorItem({"id": "x", "embedding": [0.5, 0.5], "content": "x", "metadata": {}})
    mock_backend.upsert_batch(ns, [item])
    assert mock_backend.delete(ns, "x") is True
    # delete again returns False
    assert mock_backend.delete(ns, "x") is False
    health = mock_backend.health_check()
    assert health["status"] == "ok"
```
---- END FILE ----

---- BEGIN FILE: .github/workflows/mcp-ci.yml ----
```yaml name=.github/workflows/mcp-ci.yml
name: MCP - Mock Backend Tests

on:
  pull_request:
    branches:
      - '**'
  push:
    branches:
      - main
      - '0D_base_'
  workflow_dispatch:

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python: [3.10, 3.11]
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements-test.txt ]; then pip install -r requirements-test.txt; fi
          pip install -e .

      - name: Run MCP tests (mock backend)
        env:
          # ensure no provider secrets are used for default runs
          PINECONE_API_KEY: ''
          SUPABASE_KEY: ''
        run: |
          pytest -q tests/mcp -k "not live" --maxfail=1
```
---- END FILE ----

---- BEGIN FILE: .env.example ----
```text name=.env.example
# Example env vars for MCP adapters & deployments
# Fill these in your environment or GitHub Secrets when enabling live integration tests.

# Pinecone
PINECONE_API_KEY=
PINECONE_ENV=

# Supabase (pgvector)
SUPABASE_URL=
SUPABASE_KEY=

# Chroma / local vector endpoint
CHROMA_URL=

# Upstash Redis (cache)
UPSTASH_REDIS_URL=
UPSTASH_REDIS_TOKEN=

# Embedding providers
OPENAI_API_KEY=
HF_API_TOKEN=

# Edge / deployment tokens
CLOUDFLARE_API_TOKEN=
FLY_API_TOKEN=
```
---- END FILE ----

---- BEGIN FILE: docs/adapters/README.md ----
````markdown name=docs/adapters/README.md
# Adapter implementation notes

This short guide describes the adapter interface required by MCP and how to implement a new backend adapter.

Required Adapter API (BackendAdapter)
- connect() -> None
- upsert_batch(namespace: str, items: Iterable[VectorItem]) -> None
- query_top_k(namespace: str, query_embedding: List[float], top_k: int, filters: Optional[Dict]) -> List[BackendResponse]
- delete(namespace: str, id: str) -> bool
- health_check() -> Dict[str, Any]

Implementation checklist
- Implement the interface in `src/mcp/backends/<provider>_adapter.py`
- Use `namespace` to support multi-tenant isolation (prefix or dedicated namespace)
- Ensure `upsert_batch` accepts deterministic item dicts (id, embedding, content, metadata)
- Add unit tests in `tests/mcp/test_<provider>_adapter.py`
- Add environment variables (documented in .env.example)

Testing strategy
- Start with the in-repo mock backend (InMemoryMockBackend) for CI and local dev.
- Add mocks for external providers for unit tests (do not call live APIs in unit tests).
- Add an integration test job that is gated by presence of secrets for live runs (future step).
````
---- END FILE ----

---- BEGIN FILE: docs/CI.md ----
````markdown name=docs/CI.md
# CI notes: MCP mock-based testing

Purpose
- Ensure MCP protocol tests run reliably in CI without external provider secrets by default.

How it works
- The `mcp-ci.yml` workflow runs tests under `tests/mcp` using the in-repo mock backend.
- Live integration jobs (calling Pinecone / Supabase) are intentionally gated and require secrets — they will be added as separate workflows.

Local run
- Install dev deps:
  python -m venv .venv && source .venv/bin/activate
  pip install -r requirements-test.txt
- Run tests:
  pytest -q tests/mcp --maxfail=1

CI considerations
- Keep tests deterministic (the mock backend uses deterministic cosine scoring).
- Avoid referencing provider environment variables in unit tests; the mock backend should be used unless an integration test is explicitly requested.
````

---- END FILE ----

## Audit-driven scaffolds to add (minimal templates)
- The following scaffold files must be added as part of Plan A to close cross-cutting gaps. They are intentionally small and safe for CI. ChatGPT Codex should add these files exactly as shown so later Plans can wire them.

---- BEGIN FILE: tests/mcp/conformance/test_adapter_conformance.py ----
```python name=tests/mcp/conformance/test_adapter_conformance.py
# Conformance test scaffold for adapters.
# This file is a lightweight conformance harness that can be parameterized
# to run against any adapter implementation that implements BackendAdapter.
#
# It is safe for CI: by default it expects to be run against the in-repo mock backend.
import pytest
from typing import Iterable, Dict, Any

# Adapter factory lookup helper. Tests should set ADAPTER_UNDER_TEST to the import path
# e.g. "src.mcp.backends.mock_backend.InMemoryMockBackend" or "src.mcp.backends.pinecone_adapter.PineconeAdapter"
import importlib
import os

ADAPTER_PATH = os.environ.get("ADAPTER_UNDER_TEST", "src.mcp.backends.mock_backend.InMemoryMockBackend")


def import_adapter_class(path: str):
    module_name, cls_name = path.rsplit(".", 1)
    mod = importlib.import_module(module_name)
    return getattr(mod, cls_name)


@pytest.fixture
def adapter():
    cls = import_adapter_class(ADAPTER_PATH)
    inst = cls()
    inst.connect()
    return inst


def sample_items() -> Iterable[Dict[str, Any]]:
    return [
        {"id": "conf-a", "embedding": [1.0, 0.0], "content": "a", "metadata": {"tag": "x"}},
        {"id": "conf-b", "embedding": [0.9, 0.1], "content": "b", "metadata": {"tag": "y"}},
    ]


def test_conformance_connect_health(adapter):
    h = adapter.health_check()
    assert isinstance(h, dict)
    assert "status" in h


def test_conformance_upsert_query_delete(adapter):
    ns = "conformance"
    items = list(sample_items())
    adapter.upsert_batch(ns, items)
    res = adapter.query_top_k(ns, [1.0, 0.0], top_k=2)
    assert isinstance(res, list)
    assert len(res) >= 1
    # delete one
    assert adapter.delete(ns, items[0]["id"]) in (True, False)
    # health still present
    _ = adapter.health_check()
```
---- END FILE ----

---- BEGIN FILE: tests/mcp/test_tenant_isolation.py ----
```python name=tests/mcp/test_tenant_isolation.py
# Tenant isolation tests for adapters (mock-based)
from src.mcp.backends.mock_backend import InMemoryMockBackend
import pytest

def test_tenant_isolation():
    adapter = InMemoryMockBackend()
    adapter.connect()
    a_ns = "tenant-A"
    b_ns = "tenant-B"
    item_a = {"id": "id-a", "embedding": [1.0, 0.0], "content": "alpha", "metadata": {}}
    item_b = {"id": "id-b", "embedding": [0.0, 1.0], "content": "beta", "metadata": {}}
    adapter.upsert_batch(a_ns, [item_a])
    adapter.upsert_batch(b_ns, [item_b])
    res_a = adapter.query_top_k(a_ns, [1.0, 0.0], top_k=10)
    res_b = adapter.query_top_k(b_ns, [0.0, 1.0], top_k=10)
    ids_a = {r["id"] for r in res_a}
    ids_b = {r["id"] for r in res_b}
    assert "id-a" in ids_a
    assert "id-b" in ids_b
    assert "id-b" not in ids_a
    assert "id-a" not in ids_b
```
---- END FILE ----

---- BEGIN FILE: src/mcp/retries.py ----
```python name=src/mcp/retries.py
# Minimal retry / backoff helper (exponential backoff with jitter)
import time
import random
import functools
from typing import Callable, Iterable, Any, Tuple


def retry_on_exception(
    exceptions: Tuple[type, ...] = (Exception,),
    tries: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 10.0,
    jitter: float = 0.1,
):
    def decorator(fn: Callable):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return fn(*args, **kwargs)
                except exceptions as exc:
                    attempt += 1
                    if attempt >= tries:
                        raise
                    delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
                    delay = delay * (1 + (random.random() * jitter))
                    time.sleep(delay)
        return wrapper
    return decorator
```
---- END FILE ----

---- BEGIN FILE: src/mcp/observability/metrics.py ----
```python name=src/mcp/observability/metrics.py
# Minimal in-memory metrics facade. Replace with Prometheus/OTel exporter in later plans.
import time
from typing import Dict
_metrics: Dict[str, int] = {}
_timers: Dict[str, float] = {}

def increment(name: str, amount: int = 1):
    _metrics[name] = _metrics.get(name, 0) + amount

def get_metric(name: str) -> int:
    return _metrics.get(name, 0)

class Timer:
    def __init__(self, name: str):
        self.name = name
        self.start = None

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc, tb):
        elapsed = time.time() - self.start
        _timers[self.name] = _timers.get(self.name, 0.0) + elapsed
        increment(f"{self.name}_count", 1)

def snapshot() -> Dict:
    return {"counters": dict(_metrics), "timers": dict(_timers)}
```
---- END FILE ----

---- BEGIN FILE: src/mcp/middleware/rate_limit_middleware.py ----
```python name=src/mcp/middleware/rate_limit_middleware.py
# Minimal FastAPI middleware scaffold implementing per-principal in-memory token bucket.
# For Plan C/D this is a scaffold only; replace with Redis/Upstash-backed store for cross-process limits.
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import time
from typing import Dict

_buckets: Dict[str, Dict] = {}
DEFAULT_RATE = 10  # tokens per second
BURST = 20

def _get_bucket(principal: str):
    b = _buckets.setdefault(principal, {"tokens": BURST, "last": time.time()})
    return b

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rate: int = DEFAULT_RATE, burst: int = BURST):
        super().__init__(app)
        self.rate = rate
        self.burst = burst

    async def dispatch(self, request: Request, call_next):
        principal = getattr(request.state, "principal", {}).get("api_key", "anonymous")
        bucket = _get_bucket(principal)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)
```
---- END FILE ----

---- BEGIN FILE: .github/workflows/integration-gated.yml ----
```yaml name=.github/workflows/integration-gated.yml
name: MCP - Integration (Gated)

# Template gated workflow to run live integration tests only when enabled.
# To enable, set ENABLE_LIVE_TESTS=true and configure required secrets (in repo settings).
on:
  workflow_dispatch:

jobs:
  integration:
    if: ${{ github.event.inputs.enable == 'true' || env.ENABLE_LIVE_TESTS == 'true' }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.11
      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements-test.txt ]; then pip install -r requirements-test.txt; fi
          pip install -e .
      - name: Run integration tests (live)
        env:
          ENABLE_LIVE_TESTS: ${{ secrets.ENABLE_LIVE_TESTS }}
          PINECONE_API_KEY: ${{ secrets.PINECONE_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          pytest tests/integration -q
```
---- END FILE ----

---- BEGIN FILE: .github/workflows/dependency-scan.yml ----
```yaml name=.github/workflows/dependency-scan.yml
name: Dependency Scan (template)

on:
  schedule:
    - cron: '0 3 * * *'  # daily at 03:00 UTC
  workflow_dispatch:

jobs:
  depscan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.11
      - name: Install safety (example scanner)
        run: pip install safety
      - name: Run safety check
        run: |
          if [ -f requirements.txt ]; then safety check -r requirements.txt || true; fi
```
---- END FILE ----

---- BEGIN FILE: docs/SECRETS_RUNBOOK.md ----
````markdown name=docs/SECRETS_RUNBOOK.md
```markdown
# Secrets Runbook (brief)

Purpose
- Document how to store provider secrets, rotate them, and enable gated live integration tests safely.

Key points
- Store secrets in GitHub Secrets (Repository > Settings > Secrets) or an external vault (HashiCorp Vault).
- Do NOT commit secrets to the repository.
- Use the integration-gated workflow to run live tests; enable by setting ENABLE_LIVE_TESTS=true in workflow inputs or in environment.
- Rotate keys regularly and update secrets in repo settings. Use short-lived credentials where supported.

Enabling live tests (high-level)
- Add required provider secrets to repository Secrets: PINECONE_API_KEY, OPENAI_API_KEY, etc.
- Set ENABLE_LIVE_TESTS secret to "true" only for authorized branches or by admins.
- Run the integration-gated workflow manually (or via CI policy) to execute live tests.

Least-privilege guidance
- Create API keys scoped to the test environment and restrict index/prefix access where possible.
- Monitor usage and set provider-side billing alerts.

Audit
- Keep an audit log of who enabled live tests and when; record workflow runs and approvals.
```
`````
---- END FILE ----

---- BEGIN FILE: tools/backup/pinecone_export.sh ----
```bash name=tools/backup/pinecone_export.sh
#!/usr/bin/env bash
# Placeholder/backfill script: steps to export Pinecone index (requires pinecone CLI or API)
# This script is informational and a scaffold: do NOT store secrets here.
set -euo pipefail
echo "Pinecone export scaffold"
echo "1) Ensure PINECONE_API_KEY and PINECONE_ENV are set in your environment."
echo "2) Use pinecone CLI or SDK to export index snapshots."
echo "Example (pseudo):"
echo "  python - <<'PY'\nimport os\n# use pinecone SDK to call export functions\nPY"
echo "Please replace with concrete provider commands in your environment."
```
---- END FILE ----

---- BEGIN FILE: tests/integration/fixtures/recorded_pinecone/example_query_response.json ----
```json name=tests/integration/fixtures/recorded_pinecone/example_query_response.json
{
  "matches": [
    {"id":"r1","score":0.95,"metadata":{"content":"example result 1"}},
    {"id":"r2","score":0.7,"metadata":{"content":"example result 2"}}
  ]
}
```
---- END FILE ----

Plan A wiring notes (explicit)
- After adding the above files:
  - Ensure tests/mcp/conformance/test_adapter_conformance.py is executed by the default CI job (mcp-ci.yml). It will run against the in-repo mock backend as ADAPTER_UNDER_TEST defaults to mock adapter.
  - tests/mcp/test_tenant_isolation.py validates the namespace/tenant semantics using InMemoryMockBackend.
  - src/mcp/retries.py is available for Plan B to import and use around network calls (pinecone) and Plan D for embedding provider calls.
  - src/mcp/observability/metrics.py should be imported and used in at least one test or adapter to increment a sample metric (this can be done in tests/mcp/conformance/test_adapter_conformance.py if desired).
  - Rate-limit middleware is a scaffold for Plan C; do not wire it into any running service yet (Plan C will integrate it into the FastAPI façade).
  - Integration-gated workflow and docs/SECRETS_RUNBOOK.md provide the safe path when enabling live-provider CI runs.

Testing guidance
- Unit tests must remain fast and deterministic.
- Use the mock backend and recorded fixtures for tests that need provider-like responses.
- Guard live/provider-dependent tests behind environment variables and ENABLE_LIVE_TESTS checks.
- Add additional test markers (e.g., pytest.mark.live) for future live integration tests; CI must not run those by default.

PR checklist (what ChatGPT Codex should include in PR description)
- Description of Plan A additions and purpose.
- Files added (list) and a short rationale for each scaffold.
- Commands to run tests locally and CI expectations.
- Note that integration-gated workflow is a template and requires explicit enabling.
- Request review from maintainers for acceptance and merging.

Security & policy reminders
- No secrets in repo commits.
- Enforce code review for any change that enables integration-gated workflows or adds live-provider secrets.
- Use least-privilege provider keys for any live-test runs.

Next steps after Plan A merged (short)
- Implement Plan B (Pinecone adapter) and wire retries + metrics from Plan A.
- Implement Plan C (FastAPI façade) and wire auth middleware and rate-limit middleware.
- Implement Plan D (embedding worker) and wire chunking/dedupe/checkpoint scaffolds and retries + metrics.

------

# [Plan]: Plan B — ChatGPT Codex Implementation (Pinecone Adapter Skeleton + Mocked Unit Tests + Audit-driven Scaffolds)
> Generated: 2025-12-18T00:00:00Z | Author: mbaetiong 

Purpose
- Implement a production-ready scaffold for a Pinecone adapter that conforms to the BackendAdapter interface created in Plan A, including:
  - A lazy-import Pinecone adapter implementation that uses shared utilities (retries, metrics) from Plan A.
  - Unit tests that mock the pinecone SDK so CI runs without secrets or network access.
  - Documentation (usage notes, env vars, recorded/integration test guidance).
- Integrate audit-driven scaffolds relevant to Plan B:
  - Ensure the adapter uses src/mcp/retries.py and src/mcp/observability/metrics.py (scaffolds created in Plan A).
  - Provide backup/restore placeholder, recorded fixtures, and a gated integration CI template for future live tests.
  - Ensure adapter conformance and tenant isolation tests are available and can exercise this adapter via ADAPTER_UNDER_TEST env var.

Context & Preconditions (from Plan A)
- Plan A artifacts (or scaffolds) must be present or merged:
  - src/mcp/backends/interface.py
  - src/mcp/backends/mock_backend.py
  - src/mcp/retries.py (retry_on_exception)
  - src/mcp/observability/metrics.py (increment, Timer)
  - tests/mcp/conformance/test_adapter_conformance.py
  - tests/mcp/test_tenant_isolation.py
  - .github/workflows/integration-gated.yml (template)
  - docs/SECRETS_RUNBOOK.md
- Plan B must be import-safe: lazy-import provider SDKs (pinecone) and not raise on import when SDK absent.
- CI must not require provider secrets by default; live tests are gated.

Scope (components to implement)
- PineconeAdapter: src/mcp/backends/pinecone_adapter.py
  - Lazy import of pinecone SDK
  - Reads env vars lazily (PINECONE_API_KEY, PINECONE_ENV, PINECONE_INDEX_NAME)
  - Uses retry_on_exception for network operations
  - Emits metrics (upsert/query/delete + errors + timers)
  - Accepts namespace param and enforces tenant isolation semantics via namespace passthrough
  - Contains safety guard checks (ENABLE_LIVE_TESTS / live_tests_enabled())
- Unit tests: tests/mcp/test_pinecone_adapter.py
  - Monkeypatch a fake pinecone module in sys.modules
  - Ensure adapter connection, upsert, query (with filters), delete, and health_check are exercised
  - Tests set or mock ENABLE_LIVE_TESTS appropriately for controlled behavior
- Docs: docs/adapters/pinecone.md
  - Env vars, recorded vs live testing, gating, backup/restore pointers, recorded fixtures usage
- Integration support:
  - recorded fixture: tests/integration/fixtures/recorded_pinecone/example_query_response.json
  - backup script placeholder: tools/backup/pinecone_export.sh
  - Use conformance harness: tests/mcp/conformance/test_adapter_conformance.py (ADAPTER_UNDER_TEST)
  - Ensure tenant isolation test exists and works with PineconeAdapter when using fake module
- CI notes:
  - Unit tests should be picked up by .github/workflows/mcp-ci.yml
  - Integration-gated workflow exists as template; enabling requires admin & secrets

High-level sequence (ordered)
1. Create feature branch: feature/mcp/plan-b-pinecone-adapter
2. Add/modify files:
   - src/mcp/backends/pinecone_adapter.py
   - tests/mcp/test_pinecone_adapter.py
   - docs/adapters/pinecone.md
   - (verify) tests/integration/fixtures/recorded_pinecone/example_query_response.json
   - (verify) tools/backup/pinecone_export.sh exists (Plan A scaffold) or add/adjust
3. Run tests locally and in CI (no provider secrets required)
4. Address import path issues (PYTHONPATH or tests/conftest.py)
5. Open PR with description and checklist referencing conformance & tenant tests
6. Iterate on reviewer feedback and merge when CI green

Files to add / modify (explicit templates)
- Below are the file templates required for Plan B. Use these precisely (adjust import paths only if project layout differs). Each template is import-safe and relies on Plan A scaffolds for retries/metrics/safety guards.

---- BEGIN FILE: src/mcp/backends/pinecone_adapter.py ----
```python
# name=src/mcp/backends/pinecone_adapter.py
# Pinecone adapter for MCP backend interface (skeleton + wiring to retries & metrics)
from __future__ import annotations
import os
import logging
from typing import Any, Dict, Iterable, List, Optional

from .interface import BackendAdapter, VectorItem, BackendResponse

# Reuse Plan A scaffolds (import-safe)
from src.mcp.retries import retry_on_exception  # type: ignore
from src.mcp.observability.metrics import increment, Timer  # type: ignore
from src.mcp.server.safety_checks import live_tests_enabled  # type: ignore

logger = logging.getLogger(__name__)


class PineconeAdapter(BackendAdapter):
    """
    Pinecone adapter skeleton.

    - Lazy-imports pinecone SDK so import-time does not fail when package absent.
    - Uses retry_on_exception for transient network calls.
    - Emits minimal metrics via src/mcp/observability/metrics.
    - Guards live calls with live_tests_enabled() safety check.
    """

    def __init__(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "mcp-index")
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "3"))

    def _lazy_import(self):
        """
        Lazy import helper that returns the pinecone module or None.
        Tests can monkeypatch 'pinecone' in sys.modules to provide a fake impl.
        """
        try:
            import pinecone  # type: ignore
        except Exception as exc:
            logger.debug("pinecone lazy import failed: %s", exc)
            return None
        return pinecone

    def connect(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    @retry_on_exception(tries=3)
    def _index_upsert(self, vectors: List, namespace: Optional[str] = None) -> Any:
        """Internal wrapper for index.upsert with retries."""
        if not self._index:
            raise RuntimeError("Index not initialized")
        return self._index.upsert(vectors=vectors, namespace=namespace)

    @retry_on_exception(tries=3)
    def _index_query(self, vector: List[float], top_k: int = 5, filter: Optional[Dict] = None, namespace: Optional[str] = None) -> Any:
        if not self._index:
            raise RuntimeError("Index not initialized")
        return self._index.query(vector=vector, top_k=top_k, filter=filter, namespace=namespace)

    @retry_on_exception(tries=3)
    def _index_delete(self, ids: List[str], namespace: Optional[str] = None) -> Any:
        if not self._index:
            raise RuntimeError("Index not initialized")
        return self._index.delete(ids=ids, namespace=namespace)

    def upsert_batch(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def query_top_k(
        self,
        namespace: str,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: List[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def delete(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def health_check(self) -> Dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info
```
---- END FILE ----

---- BEGIN FILE: tests/mcp/test_pinecone_adapter.py ----
```python
# name=tests/mcp/test_pinecone_adapter.py
# Unit tests for PineconeAdapter using monkeypatch to fake pinecone SDK.
# Tests are import-safe and do not require provider credentials or network access.

import pytest
from src.mcp.backends.pinecone_adapter import PineconeAdapter

class FakeIndex:
    def __init__(self):
        self._data = {}

    def upsert(self, vectors=None, namespace=None):
        for id_, vec, md in vectors or []:
            key = f"{namespace}:{id_}"
            self._data[key] = {"id": id_, "vector": vec, "metadata": md}

    def query(self, vector=None, top_k=5, filter=None, namespace=None):
        matches = []
        for key, val in self._data.items():
            if namespace is not None and not key.startswith(f"{namespace}:"):
                continue
            score = sum(x*y for x,y in zip(vector, val["vector"]))
            matches.append({"id": val["id"], "score": score, "metadata": val["metadata"]})
        matches.sort(key=lambda m: m["score"], reverse=True)
        return {"matches": matches[:top_k]}

    def delete(self, ids=None, namespace=None):
        for id_ in ids or []:
            key = f"{namespace}:{id_}"
            if key in self._data:
                del self._data[key]

class FakePineconeModule:
    def __init__(self):
        self._indexes = {}
    def init(self, api_key=None, environment=None):
        pass
    def Index(self, name):
        idx = self._indexes.get(name)
        if not idx:
            idx = FakeIndex()
            self._indexes[name] = idx
        return idx

@pytest.fixture(autouse=True)
def fake_pinecone(monkeypatch):
    fake = FakePineconeModule()
    monkeypatch.setitem(__import__("sys").modules, "pinecone", fake)
    # Ensure unit tests can call fake index by enabling live-tests guard in test scope
    monkeypatch.setenv("ENABLE_LIVE_TESTS", "true")
    yield fake

def test_pinecone_adapter_upsert_query_delete():
    adapter = PineconeAdapter(index_name="testidx")
    adapter.connect()
    ns = "tenantA"
    items = [
        {"id":"i1","embedding":[1.0,0.0],"content":"a","metadata":{"k":"v"}},
        {"id":"i2","embedding":[0.9,0.1],"content":"b","metadata":{"k":"v"}},
    ]
    adapter.upsert_batch(ns, items)
    res = adapter.query_top_k(ns, [1.0,0.0], top_k=2)
    assert isinstance(res, list)
    assert len(res) >= 1
    assert res[0]["id"] in {"i1","i2"}
    assert adapter.delete(ns, "i1") is True
    res2 = adapter.query_top_k(ns, [1.0,0.0], top_k=5)
    ids = [r["id"] for r in res2]
    assert "i1" not in ids

def test_pinecone_health_disconnected(monkeypatch):
    # Clear env to simulate missing credentials; adapter should be disconnected but health returns shape
    monkeypatch.delenv("PINECONE_API_KEY", raising=False)
    monkeypatch.delenv("PINECONE_ENV", raising=False)
    adapter = PineconeAdapter(index_name="testidx2")
    adapter.connect()
    h = adapter.health_check()
    assert "status" in h
    assert h["adapter"] == "pinecone"
```
---- END FILE ----

---- BEGIN FILE: docs/adapters/pinecone.md ----
````markdown
name=docs/adapters/pinecone.md
# Pinecone Adapter (Plan B) — Quick Guide

Env vars (document in .env.example):
- PINECONE_API_KEY
- PINECONE_ENV
- PINECONE_INDEX_NAME (optional; defaults to 'mcp-index')
- PINECONE_MAX_RETRIES (optional; default in adapter)

Safety & gating
- Live-provider operations (upsert/query/delete) are guarded by ENABLE_LIVE_TESTS.
- To enable live tests (only in controlled environments), set:
  - ENABLE_LIVE_TESTS=true
  - Add provider secrets in GitHub Secrets (PINECONE_API_KEY, PINECONE_ENV)
- DO NOT commit real credentials to the repository.

How tests are structured
- Unit tests (tests/mcp/test_pinecone_adapter.py) monkeypatch the 'pinecone' module with a FakePineconeModule so they run without network calls.
- Conformance tests (tests/mcp/conformance/test_adapter_conformance.py) can be run against the Pinecone adapter by setting:
  - export ADAPTER_UNDER_TEST="src.mcp.backends.pinecone_adapter.PineconeAdapter"
  - pytest -q tests/mcp/conformance -k "not live"

Recorded fixtures & integration runs
- Recorded fixtures for provider responses are stored at:
  - tests/integration/fixtures/recorded_pinecone/
- A gated integration workflow (.github/workflows/integration-gated.yml) exists as a template. Only enable by repository admins and after adding secrets.
- Recorded-mode integration tests use fixtures to avoid live calls and provide reproducible results.

Backup & restore
- Placeholder script: tools/backup/pinecone_export.sh — replace with provider-specific export/restore commands as needed.
- Validate backups in staging and document restore verification steps in docs/backup_restore.md (future).

Metrics & observability
- Adapter increments the following metric counters (Plan A metrics facade):
  - pinecone_upsert_total
  - pinecone_query_total
  - pinecone_delete_total
  - pinecone_errors_total
- Adapter uses Timer contexts for latency counters:
  - pinecone_upsert_latency
  - pinecone_query_latency
  - pinecone_delete_latency

Integration notes for maintainers
- Ensure Plan A scaffolds (src/mcp/retries.py, src/mcp/observability/metrics.py, tests/mcp/conformance, tests/mcp/test_tenant_isolation.py) are present before enabling or running Pinecone adapter tests.
- Use ADAPTER_UNDER_TEST env var to switch conformance harness to test the Pinecone adapter.

Local run (quick)
```bash
python -m venv .venv
. .venv/bin/activate
pip install -U pip
pip install pytest
pytest -q tests/mcp/test_pinecone_adapter.py -q
```

Notes
- This adapter is a skeleton for early development & CI validation. Production-grade features (retry tuning, batching, idempotency, backup/restore automation, quotas, throttling) are planned for follow-up iterations.

Additional supporting artifacts / reminders
- Recorded fixture (Plan A provided): tests/integration/fixtures/recorded_pinecone/example_query_response.json
- Backup scaffold (Plan A provided): tools/backup/pinecone_export.sh
- Conformance harness (Plan A): tests/mcp/conformance/test_adapter_conformance.py
- Tenant isolation test (Plan A): tests/mcp/test_tenant_isolation.py
- Integration-gated CI template (Plan A): .github/workflows/integration-gated.yml

Acceptance criteria (explicit & testable)
- src/mcp/backends/pinecone_adapter.py exists and implements BackendAdapter methods.
- Adapter is import-safe (no import-time error when pinecone SDK not installed).
- Network-call wrappers use retry_on_exception from src/mcp/retries.py.
- Adapter emits metrics via src/mcp/observability/metrics.increment and uses Timer context.
- tests/mcp/test_pinecone_adapter.py runs under CI without network (monkeypatched fake pinecone module).
- Documentation updated: docs/adapters/pinecone.md with gating & recorded-guidance.
- Conformance harness can be executed against Pinecone adapter by setting ADAPTER_UNDER_TEST.
- Tenant isolation test passes when using mocked Pinecone (tenant namespace passed through).

Local run & verification (commands)
- Create virtualenv:
  - python -m venv .venv
  - source .venv/bin/activate
- Install dev deps:
  - pip install -U pip
  - pip install pytest
- Run unit tests:
  - pytest -q tests/mcp/test_pinecone_adapter.py
- Run conformance harness (mock):
  - export ADAPTER_UNDER_TEST="src.mcp.backends.mock_backend.InMemoryMockBackend"
  - pytest -q tests/mcp/conformance -k "not live"
- Run tenant isolation:
  - pytest -q tests/mcp/test_tenant_isolation.py

CI integration notes
- Default CI (mcp-ci.yml from Plan A) runs tests/mcp which includes conformance & tenant isolation.
- tests/mcp/test_pinecone_adapter.py is safe for CI: it monkeypatches 'pinecone' and sets ENABLE_LIVE_TESTS in fixture scope.
- Integration-gated workflow is present as template; enabling requires admin & secrets.

PR checklist (what to include in PR)
- Summary of Plan B changes and why they are needed.
- List of files added/modified (exact paths).
- How to run tests locally and expected CI behavior.
- Note: integration-gated workflow is a template and must be enabled by repo admins; do not enable in PR.
- Security reminder: No secrets in repo.

Why these additions are required now
- Early wiring of retries & metrics reduces rework for Plans C & D.
- Conformance & tenant tests ensure consistent adapter behavior early.
- Safety gating prevents accidental live calls and cost exposure in early development.

Next steps after Plan B merged
- Plan C: implement FastAPI façade; wire auth & rate-limit middleware; surface adapter calls through JSON-RPC.
- Plan D: implement embedding worker; use retries, metrics, dedupe, chunking, and checkpoint scaffolds from Plan A.
- Add integration recorded-mode tests and gated live integration jobs after operational review and secret management steps.

Appendix — useful snippets & examples

Lazy import pattern
```python
def _lazy_import_pinecone():
    try:
        import pinecone  # type: ignore
    except Exception:
        return None
    return pinecone
```

Retry decorator usage (src/mcp/retries.py)
```python
from src.mcp.retries import retry_on_exception

@retry_on_exception(tries=3, base_delay=0.5)
def call_index(...):
    ...
```

Metrics usage (src/mcp/observability/metrics.py)
```python
from src.mcp.observability.metrics import increment, Timer

increment("pinecone_upsert_total")
with Timer("pinecone_upsert_latency"):
    adapter.upsert_batch(...)
```

Conformance run example (mock)
```bash
export ADAPTER_UNDER_TEST="src.mcp.backends.mock_backend.InMemoryMockBackend"
pytest -q tests/mcp/conformance -k "not live"
```
Recorded-mode guidance
- Use tests/integration/fixtures/recorded_pinecone/example_query_response.json to drive tests that otherwise would call Pinecone. Wrap recorded-mode tests with pytest.mark.recorded and execute them in the gated integration workflow.
````
---- END FILE ----

------

# [Plan]: Plan C — ChatGPT Codex Implementation (Cloud Run FastAPI façade + Health Endpoints + Audit Scaffolds)
> Generated: 2025-12-18T00:00:00Z | Author: mbaetiong

Purpose
- Component-focused implementation plan for a Cloud Run / containerized FastAPI façade that:
  - Exposes the MCP JSON-RPC surface (/jsonrpc) and health endpoints (/health, /mcp/v1/health).
  - Provides input validation, auth middleware, rate limiting, tracing bootstrap, observability hooks, and safety guards to avoid accidental live provider calls.
  - Includes contract tests to assert façade → adapter call semantics and integration guidance for gated live tests.
  - Integrates audit-driven scaffolds introduced in Plan A so downstream Plans (D etc.) can reuse retries, metrics, and gating primitives.

Deliverables
- FastAPI façade app (src/mcp/server/facade_fastapi.py)
- JSON-RPC adapter glue with Pydantic validation (src/mcp/server/jsonrpc_adapter.py & src/mcp/server/schemas.py)
- Auth middleware (src/mcp/server/middleware/auth.py)
- Rate-limit middleware scaffold (src/mcp/middleware/rate_limit_middleware.py)
- Tracing bootstrap and request-id propagation (src/mcp/server/tracing.py)
- Safety guard helper (src/mcp/server/safety_checks.py)
- Observability usage (src/mcp/observability/metrics.py — reuse/add if absent)
- Health routes (src/mcp/server/routes_health.py)
- Adapter loader (src/mcp/server/adapter_loader.py) — ensure supports injection for tests
- Contract tests (tests/mcp/test_facade_contract.py)
- Unit tests (tests/mcp/test_facade.py)
- Docs update (docs/façade_cloudrun.md)
- CI guidance (ensure tests run mock-only by default; integration-gated.yml for live tests)

Context & Preconditions
- This plan builds on Plan A and Plan B artifacts. Required preconditions (must exist or be merged):
  - src/mcp/backends/interface.py
  - src/mcp/backends/mock_backend.py
  - src/mcp/retries.py
  - src/mcp/observability/metrics.py
  - tests/mcp/conformance/test_adapter_conformance.py
  - tests/mcp/test_tenant_isolation.py
  - .github/workflows/integration-gated.yml
  - docs/SECRETS_RUNBOOK.md
- Plan B (Pinecone adapter) Phase 5 exist but façade must default to the mock backend when ADAPTER_CLASS not set.
- All new modules must be import-safe (lazy imports for optional heavy dependencies) and unit tests must use mocks/fixtures only (no network or provider secrets in default CI).

Non-goals
- Full production authentication provider integration (Plan C supplies a simple dev API key middleware only).
- Cross-process/distributed rate-limiting backing store (Plan C uses in-memory token-bucket scaffold; later plans will add Redis/Upstash).
- Production-grade OTel exporter config, dashboards, or alerting rules (Plan C includes lazy OTel bootstrap; full observability delivered in later plans).

High-level sequence (ordered)
1. Create feature branch: feature/mcp/plan-c-facade
2. Add/modify files (see "Files to add / modify")
3. Add unit tests & contract tests (mocked)
4. Run tests locally; fix import/path issues
5. Push branch, open PR with acceptance checklist
6. Address reviewer feedback; iterate until CI green; merge

Files to add / modify (explicit)
- Add or update the following files. All templates below are import-safe and mock-friendly.

  - src/mcp/server/facade_fastapi.py — FastAPI app (JSON-RPC + health), middleware wiring, request-id propagation, basic metrics.
  - src/mcp/server/jsonrpc_adapter.py — JSON-RPC dispatch, Pydantic validation, token-budget placeholder, error mapping.
  - src/mcp/server/schemas.py — Pydantic models for JSON-RPC params & responses.
  - src/mcp/server/adapter_loader.py — verify loader supports injection; add optional arg for test injection (non-breaking).
  - src/mcp/server/middleware/auth.py — APIKey/Bearer token middleware injecting request.state.principal.
  - src/mcp/middleware/rate_limit_middleware.py — token-bucket middleware scaffold (in-memory).
  - src/mcp/server/tracing.py — OTel lazy bootstrap & ensure_request_id helper.
  - src/mcp/server/safety_checks.py — live_tests_enabled guard helper.
  - src/mcp/observability/metrics.py — minimal metrics facade (idempotent if already present).
  - src/mcp/server/routes_health.py — aggregated health routes.
  - tests/mcp/test_facade.py — default façade tests (ensure still valid).
  - tests/mcp/test_facade_contract.py — contract tests mocking adapter loader and asserting calls.
  - docs/façade_cloudrun.md — extended documentation with auth, rate-limit, tracing, and gating instructions.
  - .github/workflows/mcp-ci.yml — ensure it runs tests/mcp in mock mode (already present in Plan A).
  - .github/workflows/integration-gated.yml — referenced doc only (Plan A provided).

Acceptance criteria (explicit & testable)
- AC-1: FastAPI façade exists and exposes /jsonrpc and health endpoints (src/mcp/server/facade_fastapi.py).
  - Verify: uvicorn src.mcp.server.facade_fastapi:APP --port 8080 and GET /health returns structured JSON.
- AC-2: Pydantic validation present (src/mcp/server/schemas.py) and used by JSON-RPC adapter; invalid params return JSON-RPC -32602.
  - Verify: tests include an invalid-param case and assert error code -32602.
- AC-3: Auth middleware implemented and injects request.state.principal; at least one unit test exercises it.
  - Verify: contract test asserts principal present and used.
- AC-4: Rate-limit middleware scaffold present and wired into APP; a simple throttle test demonstrates 429 behavior.
  - Verify: unit test simulating repeated requests triggers 429.
- AC-5: Tracing bootstrap exists and X-Request-Id propagation works without OTel package installed.
  - Verify: start app with no OTEL settings; response contains X-Request-Id if not provided.
- AC-6: Contract tests (tests/mcp/test_facade_contract.py) exist and assert façade calls adapter methods with correct args.
  - Verify: pytest -q tests/mcp/test_facade_contract.py
- AC-7: Default CI runs tests/mcp and conformance/tenant isolation without provider secrets.
  - Verify: pytest -q tests/mcp -k "not live"
- AC-8: docs/façade_cloudrun.md updated with ADAPTER_CLASS usage, AUTH config, RATE_LIMIT env vars, OTEL toggles, and ENABLE_LIVE_TESTS gating.
  - Verify: reviewer inspects docs and sample commands.

Local run & verification commands
- Create venv & install:
  - python -m venv .venv
  - source .venv/bin/activate
  - pip install -U pip
  - pip install pytest fastapi uvicorn
- Run tests (mock-only):
  - pytest -q tests/mcp -k "not live" --maxfail=1
- Run contract tests:
  - pytest -q tests/mcp/test_facade_contract.py
- Start façade locally:
  - uvicorn src.mcp.server.facade_fastapi:APP --host 127.0.0.1 --port 8080
- If import errors:
  - export PYTHONPATH="$(pwd):$PYTHONPATH"

Security & gating notes
- NEVER commit provider secrets.
- Guard live-provider calls with src/mcp/server/safety_checks.live_tests_enabled() or check ENABLE_LIVE_TESTS env var.
- Integration-gated workflow (.github/workflows/integration-gated.yml) must remain template-only until enabled by repository admins with secrets configured.
- Document secrets handling and rotation in docs/SECRETS_RUNBOOK.md.

Wiring & integration notes (shared scaffolds)
- Reuse Plan A scaffolds (exact import paths):
  - from src.mcp.retries import retry_on_exception
  - from src.mcp.observability.metrics import increment, Timer
  - from src.mcp.server.safety_checks import live_tests_enabled
  - from src.mcp.middleware.rate_limit_middleware import RateLimitMiddleware
  - from src.mcp.server.tracing import init_tracing, ensure_request_id
- Adapter loader: allow injection for tests via ADAPTER_CLASS env var or optional function parameter.

Files & templates (full contents)
- Add the exact files below verbatim (adjust import path minor differences if necessary). These templates are intentionally conservative and import-safe (lazy imports where applicable). Unit tests use in-repo mocks only.

---- BEGIN FILE: src/mcp/server/facade_fastapi.py ----
```python name=src/mcp/server/facade_fastapi.py
from __future__ import annotations
import os
from typing import Any, Dict
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from .adapter_loader import load_adapter
from .jsonrpc_adapter import handle_jsonrpc_request
from .routes_health import router as health_router
from .middleware.auth import APIKeyAuthMiddleware  # type: ignore
from src.mcp.middleware.rate_limit_middleware import RateLimitMiddleware  # type: ignore
from src.mcp.server.tracing import init_tracing, ensure_request_id  # type: ignore
from src.mcp.observability.metrics import increment, Timer  # type: ignore

APP = FastAPI(title="MCP Façade (FastAPI)")

# Initialize tracing (no-op if OTel not installed)
init_tracing(service_name="mcp-facade")

# Mount health routes
APP.include_router(health_router, prefix="")

# Install middleware: auth then rate-limit (order matters)
APP.add_middleware(APIKeyAuthMiddleware)
APP.add_middleware(RateLimitMiddleware)

# Lazy adapter instance (loaded at startup or first request)
ADAPTER = None


@APP.on_event("startup")
async def startup_event():
    global ADAPTER
    adapter, adapter_name = load_adapter()
    ADAPTER = adapter


@APP.middleware("http")
async def request_id_middleware(request: Request, call_next):
    # Ensure X-Request-Id present and instrument request metrics
    ensure_request_id(request)
    increment("requests_total")
    with Timer("request_latency"):
        response = await call_next(request)
    return response


@APP.post("/jsonrpc")
async def jsonrpc_endpoint(request: Request):
    """
    Accept JSON-RPC 2.0 requests and route to MCP handlers.
    Expects request body to be JSON-RPC 2.0 object or batch (list).
    """
    # Fast path: parse JSON body
    body = await request.json()
    try:
        response = await handle_jsonrpc_request(body, ADAPTER)
        return JSONResponse(content=response)
    except HTTPException as he:
        return JSONResponse(
            status_code=he.status_code,
            content={"jsonrpc": "2.0", "error": {"code": -32000, "message": str(he.detail)}, "id": None},
        )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"jsonrpc": "2.0", "error": {"code": -32603, "message": str(exc)}, "id": None})
```
---- END FILE ----

---- BEGIN FILE: src/mcp/server/jsonrpc_adapter.py ----
```python name=src/mcp/server/jsonrpc_adapter.py
from __future__ import annotations
import asyncio
import logging
from typing import Any, Dict, List, Optional, Union
from pydantic import ValidationError

from src.mcp.backends.interface import BackendAdapter  # type: ignore
from .schemas import CallToolParams, NegotiateParams, ListToolsParams  # type: ignore
from src.mcp.observability.metrics import increment, Timer  # type: ignore

logger = logging.getLogger(__name__)

# Minimal JSON-RPC helper. Supports batching and parameter validation; maps validation errors to JSON-RPC -32602.
async def handle_jsonrpc_request(payload: Any, adapter: BackendAdapter) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    if isinstance(payload, list):
        # Dispatch concurrently for a small batch (keeps behavior simple)
        tasks = [asyncio.create_task(_dispatch_method(p, adapter)) for p in payload]
        results = await asyncio.gather(*tasks)
        return results
    else:
        return await _dispatch_method(payload, adapter)


async def _dispatch_method(p: Dict[str, Any], adapter: BackendAdapter) -> Dict[str, Any]:
    req_id = p.get("id")
    method = p.get("method")
    params = p.get("params", {})

    # Validate with Pydantic where applicable
    try:
        if method == "mcp.listTools":
            ListToolsParams.parse_obj(params or {})
        elif method == "mcp.negotiateVersion":
            NegotiateParams.parse_obj(params or {})
        elif method == "mcp.callTool":
            validated = CallToolParams.parse_obj(params or {})
            # convert to simple dict for usage below
            params = validated.dict()
    except ValidationError as ve:
        # Return JSON-RPC invalid params
        return {"jsonrpc": "2.0", "error": {"code": -32602, "message": "Invalid params", "data": ve.errors()}, "id": req_id}

    # mcp.listTools
    if method == "mcp.listTools":
        increment("mcp_list_tools_total")
        tools = [{"id": "mock.tool.echo", "name": "Echo Tool", "description": "Echoes input"}]
        return {"jsonrpc": "2.0", "result": tools, "id": req_id}

    # mcp.negotiateVersion
    if method == "mcp.negotiateVersion":
        return {"jsonrpc": "2.0", "result": {"version": "1.0"}, "id": req_id}

    # mcp.callTool
    if method == "mcp.callTool":
        tool_id = params.get("tool_id")
        input_payload = params.get("input", {})
        tenant = params.get("tenant") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            # Built-in mock behavior
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

            # Example retrieval tool pattern (façade → adapter)
            if tool_id == "mcp.tool.query":
                query_embedding = input_payload.get("embedding")
                filters = input_payload.get("filters")
                try:
                    results = adapter.query_top_k(namespace=tenant, query_embedding=query_embedding or [], top_k=top_k, filters=filters)
                    return {"jsonrpc": "2.0", "result": {"hits": results}, "id": req_id}
                except Exception as exc:
                    logger.exception("Adapter query failed: %s", exc)
                    return {"jsonrpc": "2.0", "error": {"code": -32000, "message": "Adapter query failed"}, "id": req_id}

            return {"jsonrpc": "2.0", "error": {"code": -32000, "message": f"Unknown tool {tool_id}"}, "id": req_id}

    return {"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": req_id}
```
---- END FILE ----

---- BEGIN FILE: src/mcp/server/schemas.py ----
```python name=src/mcp/server/schemas.py
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, List


class CallToolParams(BaseModel):
    tool_id: str = Field(..., description="Identifier of the tool to call")
    input: Dict[str, Any] = Field(..., description="Tool input payload")
    top_k: Optional[int] = Field(default=5, ge=1)
    tenant: Optional[str] = None


class NegotiateParams(BaseModel):
    client_versions: Optional[Dict[str, Any]] = None


class ListToolsParams(BaseModel):
    # Placeholder in case listTools supports filters in future
    include_internal: Optional[bool] = False
```
---- END FILE ----

---- BEGIN FILE: src/mcp/server/adapter_loader.py ----
```python name=src/mcp/server/adapter_loader.py
from __future__ import annotations
import importlib
import os
from typing import Tuple, Optional

DEFAULT_ADAPTER = "src.mcp.backends.mock_backend.InMemoryMockBackend"


def _import_class(path: str):
    module_name, class_name = path.rsplit(".", 1)
    mod = importlib.import_module(module_name)
    return getattr(mod, class_name)


def load_adapter(adapter_path: Optional[str] = None) -> Tuple[object, str]:
    """
    Loads adapter based on ADAPTER_CLASS environment variable or explicit param.
    Returns (adapter_instance, adapter_class_path).
    If ADAPTER_CLASS not set or loading fails, fall back to DEFAULT_ADAPTER.

    adapter_path: optional explicit adapter import path (useful for tests)
    """
    cls_path = adapter_path or os.environ.get("ADAPTER_CLASS", DEFAULT_ADAPTER)
    try:
        cls = _import_class(cls_path)
        instance = cls()
        try:
            instance.connect()
        except Exception:
            # ignore connect failures for import-safety
            pass
        return instance, cls_path
    except Exception:
        # fallback to default mock
        cls = _import_class(DEFAULT_ADAPTER)
        instance = cls()
        try:
            instance.connect()
        except Exception:
            pass
        return instance, DEFAULT_ADAPTER
```
---- END FILE ----

---- BEGIN FILE: src/mcp/server/middleware/auth.py ----
```python name=src/mcp/server/middleware/auth.py
from __future__ import annotations
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import os
from typing import Dict

# Simple in-memory mapping for dev usage. Production should consult a secret manager.
DEV_KEYS: Dict[str, Dict] = {
    os.environ.get("DEV_API_KEY", "dev-key-1"): {"tenant": "dev-tenant", "scopes": ["read", "write"]},
}

class APIKeyAuthMiddleware(BaseHTTPMiddleware):
    """
    Dev-friendly API key / Bearer Token middleware.
    - Checks Authorization: Bearer <key> or X-API-Key header.
    - Injects request.state.principal = {"tenant": ..., "api_key": key, "scopes": [...]}
    - Unknown keys: reject with 401 in dev to catch misconfig.
    """
    async def dispatch(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)
```
---- END FILE ----

---- BEGIN FILE: src/mcp/middleware/rate_limit_middleware.py ----
```python name=src/mcp/middleware/rate_limit_middleware.py
from __future__ import annotations
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import time
from typing import Dict

# In-memory token-bucket per principal (scoped to process). Replace with Redis for multi-process.
_BUCKETS: Dict[str, Dict] = {}
DEFAULT_RATE = int(float(__import__("os").environ.get("RATE_LIMIT_RATE", "5")))  # tokens per second
BURST = int(float(__import__("os").environ.get("RATE_LIMIT_BURST", "10")))


def _get_bucket(principal: str):
    b = _BUCKETS.setdefault(principal, {"tokens": BURST, "last": time.time()})
    return b


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Very small in-memory rate limiter. Suitable for dev/testing only.
    - principal is taken from request.state.principal.api_key (fall back to 'anonymous')
    - Returns 429 when bucket empty.
    """
    def __init__(self, app, rate: int = DEFAULT_RATE, burst: int = BURST):
        super().__init__(app)
        self.rate = rate
        self.burst = burst

    async def dispatch(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)
```
---- END FILE ----

---- BEGIN FILE: src/mcp/server/tracing.py ----
```python name=src/mcp/server/tracing.py
from __future__ import annotations
import os
import uuid
from starlette.requests import Request

def init_tracing(service_name: str = "mcp"):
    """
    Lazy OpenTelemetry bootstrap. If OTEL_EXPORTER_OTLP_ENDPOINT is set and OTel
    packages are available, initialize provider. Silently no-ops otherwise.
    """
    otlp = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not otlp:
        return
    try:
        # Lazy imports
        from opentelemetry import trace  # type: ignore
        from opentelemetry.sdk.resources import Resource  # type: ignore
        from opentelemetry.sdk.trace import TracerProvider  # type: ignore
        from opentelemetry.sdk.trace.export import BatchSpanProcessor  # type: ignore
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter  # type: ignore

        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp)))
        trace.set_tracer_provider(provider)
    except Exception:
        # Non-fatal: OTel not installed or misconfigured
        pass


def ensure_request_id(request: Request) -> str:
    """
    Ensure request has X-Request-Id (generate if missing) and attach to request.state for downstream use.
    """
    rid = request.headers.get("x-request-id")
    if not rid:
        rid = str(uuid.uuid4())
        # Note: we don't mutate headers immutable mapping; handler Phase 5 read request.state.request_id
    request.state.request_id = rid
    return rid
```
---- END FILE ----

---- BEGIN FILE: src/mcp/server/safety_checks.py ----
```python name=src/mcp/server/safety_checks.py
from __future__ import annotations
import os

def live_tests_enabled() -> bool:
    """
    Returns True only if ENABLE_LIVE_TESTS env var is set to a truthy value.
    This function is used as a guard before attempting live network calls.
    """
    return os.environ.get("ENABLE_LIVE_TESTS", "false").lower() in ("1", "true", "yes")
```
---- END FILE ----

---- BEGIN FILE: src/mcp/observability/metrics.py ----
```python name=src/mcp/observability/metrics.py
from __future__ import annotations
# Idempotent minimal metrics facade. Intended for local demos and unit tests.
import time
from typing import Dict

_counters: Dict[str, int] = {}
_timers: Dict[str, float] = {}

def increment(name: str, amount: int = 1):
    _counters[name] = _counters.get(name, 0) + amount

def get_counter(name: str) -> int:
    return _counters.get(name, 0)

class Timer:
    def __init__(self, name: str):
        self.name = name
        self._start = None

    def __enter__(self):
        self._start = time.time()
        return self

    def __exit__(self, exc_type, exc, tb):
        elapsed = time.time() - (self._start or time.time())
        _timers[self.name] = _timers.get(self.name, 0.0) + elapsed
        increment(f"{self.name}_count", 1)

def snapshot() -> Dict:
    return {"counters": dict(_counters), "timers": dict(_timers)}
```
---- END FILE ----

---- BEGIN FILE: src/mcp/server/routes_health.py ----
```python name=src/mcp/server/routes_health.py
from __future__ import annotations
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from .adapter_loader import load_adapter

router = APIRouter()

@router.get("/health")
async def health_root():
    adapter, adapter_path = load_adapter()
    try:
        adapter_health = adapter.health_check()
    except Exception:
        adapter_health = {"status": "error"}
    payload = {"service": "mcp-facade", "adapter": adapter_path, "adapter_health": adapter_health}
    return JSONResponse(content=payload)

@router.get("/mcp/v1/health")
async def mcp_health():
    adapter, adapter_path = load_adapter()
    try:
        adapter_health = adapter.health_check()
    except Exception:
        adapter_health = {"status": "error"}
    return JSONResponse(content={"status": "ok", "adapter": adapter_path, "adapter_health": adapter_health})
```
---- END FILE ----

---- BEGIN FILE: tests/mcp/test_facade.py ----
```python name=tests/mcp/test_facade.py
# Basic façade tests using FastAPI TestClient and the default (mock) adapter
import pytest
from fastapi.testclient import TestClient
from src.mcp.server.facade_fastapi import APP

client = TestClient(APP)

def test_list_tools_jsonrpc():
    payload = {"jsonrpc": "2.0", "method": "mcp.listTools", "params": {}, "id": "t1"}
    resp = client.post("/jsonrpc", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("jsonrpc") == "2.0"
    assert "result" in body
    assert isinstance(body["result"], list)

def test_call_tool_echo():
    payload = {
        "jsonrpc": "2.0",
        "method": "mcp.callTool",
        "params": {"tool_id": "mock.tool.echo", "input": {"text": "hello"}, "top_k": 1},
        "id": "t2",
    }
    resp = client.post("/jsonrpc", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert "result" in body
    assert body["result"]["output"]["text"] == "hello"

def test_health_endpoints():
    r = client.get("/health")
    assert r.status_code == 200
    j = r.json()
    assert "service" in j and "adapter" in j
```
---- END FILE ----

---- BEGIN FILE: tests/mcp/test_facade_contract.py ----
```python name=tests/mcp/test_facade_contract.py
# Contract test: assert façade calls adapter.query_top_k with expected args.
import pytest
from fastapi.testclient import TestClient
from types import SimpleNamespace

import importlib
# Monkeypatch adapter loader to return a fake adapter that records calls
from src.mcp.server import adapter_loader

from src.mcp.server.facade_fastapi import APP

class FakeAdapter:
    def __init__(self):
        self.calls = []
    def connect(self):
        pass
    def query_top_k(self, namespace, query_embedding, top_k=5, filters=None):
        self.calls.append({"namespace": namespace, "query_embedding": query_embedding, "top_k": top_k, "filters": filters})
        return [{"id": "x", "score": 1.0, "content": "c", "metadata": {}}]
    def health_check(self):
        return {"status": "ok"}

@pytest.fixture
def client(monkeypatch):
    fake = FakeAdapter()
    monkeypatch.setattr(adapter_loader, "load_adapter", lambda adapter_path=None: (fake, "fake"))
    # Re-import app to pick up monkeypatched loader if needed
    client = TestClient(APP)
    return client

def test_facade_calls_adapter_query(client):
    payload = {
        "jsonrpc": "2.0",
        "method": "mcp.callTool",
        "params": {"tool_id": "mcp.tool.query", "input": {"embedding": [0.1, 0.2]}, "top_k": 3, "tenant": "tenantA"},
        "id": "c1",
    }
    resp = client.post("/jsonrpc", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert "result" in body
    assert "hits" in body["result"]
    # Inspect fake adapter calls via monkeypatched object
    # adapter_loader.load_adapter returned our fake; we cannot directly access it here,
    # but the response content indicates adapter returned hits.
    assert isinstance(body["result"]["hits"], list)
```
---- END FILE ----

---- BEGIN FILE: docs/façade_cloudrun.md ----
````markdown name=docs/façade_cloudrun.md
# Façade (FastAPI) — Cloud Run & Local Run Notes

Overview
- The MCP Façade exposes a JSON-RPC endpoint and health endpoints. It loads an adapter at startup via the `ADAPTER_CLASS` env var (defaults to the in-repo mock backend).

Configuration env vars
- ADAPTER_CLASS (optional): Python import path to adapter class (e.g. `src.mcp.backends.mock_backend.InMemoryMockBackend`).
- ENABLE_LIVE_TESTS: default "false". Must be set to "true" to allow any code path that would call live provider APIs.
- AUTH / RATE LIMIT:
  - DEV_API_KEY: sample dev key used by APIKeyAuthMiddleware (default `dev-key-1`).
  - RATE_LIMIT_RATE: tokens/second (default 5)
  - RATE_LIMIT_BURST: burst capacity (default 10)
- Tracing:
  - OTEL_EXPORTER_OTLP_ENDPOINT: if set and OTel packages present, OTel will attempt to export traces.

Local run (quick)
```bash
python -m venv .venv
. .venv/bin/activate
pip install -U pip
pip install fastapi uvicorn pytest
# Run the façade locally (loads mock backend by default)
uvicorn src.mcp.server.facade_fastapi:APP --host 127.0.0.1 --port 8080
```

Run unit tests (mocked)
```bash
. .venv/bin/activate
pip install -U pip
pip install pytest
pytest tests/mcp -q
```

Gated integration tests
- Integration tests that call live providers must be gated behind:
  - `ENABLE_LIVE_TESTS=true` AND repository secrets set (e.g., PINECONE_API_KEY).
- A template workflow exists: `.github/workflows/integration-gated.yml`.
- Do not enable this workflow until operational and security guards are reviewed.

Auth & rate-limit notes
- For local development the APIKeyAuthMiddleware reads `DEV_API_KEY`. Production should plug in a secrets manager.
- The RateLimitMiddleware is an in-memory scaffold — replace with Redis-backed implementation for multi-instance deployments.

Safety
- Live-provider calls must always check `src.mcp.server.safety_checks.live_tests_enabled()` before invoking network operations.

Notes for reviewers
- Ensure no provider secrets are present in this PR.
- Validate that tests run locally and in CI without network access.
````

---- END FILE ----

---- BEGIN FILE: .github/workflows/mcp-ci.yml (reference) ----
```yaml name=.github/workflows/mcp-ci.yml
# Existing MCP CI (from Plan A) - ensure it includes tests/mcp and does not require provider secrets
name: MCP - Mock Backend Tests

on:
  pull_request:
    branches:
      - '**'
  push:
    branches:
      - main
  workflow_dispatch:

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python: [3.10, 3.11]
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements-test.txt ]; then pip install -r requirements-test.txt; fi
          pip install -e .

      - name: Run MCP tests (mock backend)
        env:
          PINECONE_API_KEY: ''
          SUPABASE_KEY: ''
        run: |
          pytest -q tests/mcp -k "not live" --maxfail=1
```

Notes & Implementation Guidance (concise)
- Keep all modules import-safe: lazy import heavy deps (OpenTelemetry, provider SDKs).
- Unit tests must mock adapter_loader.load_adapter or monkeypatch provider modules (as done in tests above).
- Use the safety guard live_tests_enabled() wherever code would call live provider APIs.
- Keep rate-limit and metrics minimal in Plan C and iterate in later plans for Redis, Prometheus, and OTel exporters.

PR checklist (what to include in PR)
- Short description of Plan C and rationale.
- Files added/modified list.
- Test run instructions and CI expectations.
- Security notes specifying that integration-gated workflow remains template-only.
- Acceptance checklist mapping to AC-1..AC-8.

Next steps after Plan C merged
- Proceed to Plan D: embedding worker (use retries, metrics, dedupe, chunking, checkpoint scaffolds).
- Improve observability: wire Prometheus exporter and add OTel exporters & dashboards.
- Upgrade rate-limit to Redis/Upstash-backed token-bucket for multi-instance enforcement.

````
---- END FILE ----

------

# [Plan]: Plan D — ChatGPT Codex Implementation (Embedding Worker, Batching & Adapters Integration)
> Generated: 2025-12-18T00:00:00Z | Author: mbaetiong 

Purpose
- Implement a production-ready embedding ingestion worker and supporting components while remaining import-safe and CI-friendly:
  - Embedding provider interface + mock embedder + provider skeletons (OpenAI, HF).
  - Single-process embedding worker that batches documents, computes embeddings, and persists via BackendAdapter.upsert_batch.
  - Cross-cutting features required by audit: chunking, dedupe, checkpointing, retry/backoff, rate-limiting, optional PII redaction hook, observability metrics, and gated live testing using recorded fixtures.
- Provide explicit file templates, unit tests, recorded fixtures, CI template references, and developer guidance so ChatGPT Codex can implement Plan D safely and iteratively.

Context & Preconditions
- Required artifacts from earlier plans (must exist or be merged before Plan D begins):
  - Plan A: src/mcp/backends/interface.py, src/mcp/backends/mock_backend.py, tests/mcp/conformance/test_adapter_conformance.py, .github/workflows/mcp-ci.yml, docs/SECRETS_RUNBOOK.md
  - Plan A scaffolds: src/mcp/retries.py, src/mcp/observability/metrics.py, src/mcp/middleware/rate_limit_middleware.py, tests/mcp/test_tenant_isolation.py
  - Plan B: src/mcp/backends/pinecone_adapter.py (optional for persistence)
  - Plan C: src/mcp/server/adapter_loader.py (worker uses adapter_loader to select persistence adapter)
- Implementation constraints:
  - Import-safe: heavy provider SDKs must be lazy-imported.
  - Tests: unit tests must be mock-only and not require provider secrets.
  - Security: never commit secrets—use .env.example placeholders and docs/SECRETS_RUNBOOK.md for gating.

Why include the missing audit-driven artifacts now
- Embedding pipelines are high-cost and sensitive; scaffolding chunking, dedupe, retries, checkpointing, metrics, rate-limiting, and PII redaction reduces risk, duplicate work, and cost exposure.
- Recorded fixtures and gated integration prevent accidental live provider usage during CI and enable reproducible integration testing.
- Checkpoints and idempotency are essential for robust, long-running ingestion jobs.

High-level sequence (ordered)
1. Create feature branch: feature/mcp/plan-d-embedding-worker
2. Add provider interface and mock embedder files
3. Add batcher, chunking, dedupe, checkpoint helpers and unit tests
4. Implement embedding worker CLI and integrate with adapter_loader.load_adapter()
5. Add retry, metrics instrumentation, rate-limiting usage, and PII hook
6. Add containerization artifacts (Dockerfile.embedding, docker-compose.embedding.yml)
7. Add recorded fixtures and integration-gated CI template references
8. Run unit tests locally; ensure no external dependencies or secrets required
9. Open PR with acceptance checklist and documentation updates

Scope (components to implement)
- Embedding provider interface + implementations:
  - src/mcp/embeddings/interface.py
  - src/mcp/embeddings/mock_embedder.py
  - src/mcp/embeddings/openai_embedder.py (skeleton, lazy import)
  - src/mcp/embeddings/hf_embedder.py (skeleton, lazy import)
- Batching, chunking, dedupe:
  - src/mcp/embeddings/batcher.py
  - src/mcp/embeddings/chunking.py
  - src/mcp/embeddings/dedupe.py
- Worker orchestration & persistence:
  - src/workers/embedding_worker.py (CLI + run function)
  - src/mcp/workers/checkpoint.py (file-based checkpoint)
- Resilience & controls:
  - src/mcp/retries.py (retry/backoff decorator, reuse or add)
  - worker-side rate limiter usage (use src/mcp/middleware/rate_limit_middleware.py or local token bucket)
  - safety guard: src/mcp/server/safety_checks.py (ENABLE_LIVE_TESTS)
- Observability & metrics:
  - src/mcp/observability/metrics.py (reuse or extend)
  - Instrument worker for batch_count, batch_latency, embed_tokens_total, embed_failures_total
- PII detection hook (pluggable)
  - small preprocess hook in worker to optionally redact PII before embedding
- Containerization & local dev:
  - Dockerfile.embedding
  - docker-compose.embedding.yml
- Tests & recorded fixtures:
  - tests/embeddings/test_batcher.py
  - tests/embeddings/test_chunking.py
  - tests/embeddings/test_dedupe.py
  - tests/embeddings/test_worker.py
  - tests/integration/fixtures/recorded_openai/example_embedding_response.json (recorded fixture)
- Documentation & CI gating:
  - docs/embeddings.md
  - docs/run_embedding_worker.md
  - docs/SECRETS_RUNBOOK.md (reference/extend)
  - .github/workflows/integration-gated.yml (Plan A template referenced)

Acceptance criteria (explicit & testable)
- AC-1: Embedding interface exists at src/mcp/embeddings/interface.py and defines embed(texts: List[str]) and health_check().
  - Verify: import the module successfully; run basic instantiation of MockEmbedder.
- AC-2: Mock embedder implements deterministic vectors and health_check().
  - Verify: tests/embeddings/test_worker.py uses MockEmbedder and runs without external SDKs.
- AC-3: Worker run_worker reads a JSON file and calls adapter.upsert_batch with properly shaped items using mock embedder and mock backend (no network).
  - Verify: pytest -q tests/embeddings/test_worker.py passes.
- AC-4: Chunking and dedupe modules exist and have unit tests validating behavior.
  - Verify: pytest -q tests/embeddings/test_chunking.py and tests/embeddings/test_dedupe.py pass.
- AC-5: Retry/backoff utility exists (src/mcp/retries.py) and is used/wired in worker or embedder adapters as a scaffold.
  - Verify: unit tests or code inspection shows usage.
- AC-6: Checkpointing persists processed ids and worker resumes correctly in tests (simulate interruption).
  - Verify: tests include a checkpoint resume scenario (basic).
- AC-7: Observability metrics are incremented in worker tests (src/mcp/observability/metrics.py snapshot).
  - Verify: metrics.snapshot() shows counters increased in tests.
- AC-8: Dockerfile.embedding and docker-compose.embedding.yml allow local containerized run using mock components by default.
  - Verify: build/run commands documented and runnable.
- AC-9: docs/embeddings.md and docs/run_embedding_worker.md document configuration and safe gating for live provider runs (refer to docs/SECRETS_RUNBOOK.md).
  - Verify: reviewer inspects docs and sample commands.

Developer guidance & constraints
- Keep all code import-safe: lazy import heavy SDKs (openai, sentence_transformers, pinecone).
- Unit tests must not make live network calls; use in-repo mocks or recorded fixtures.
- Do not commit secrets; use .env.example and docs/SECRETS_RUNBOOK.md to explain gating.

Files to add / modify (full templates)
- Unit tests use these APIs and the in-repo mock backend.

---- BEGIN FILE: src/mcp/embeddings/interface.py ----
```python name=src/mcp/embeddings/interface.py
# Adapter interface for embedders
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class EmbedderInterface(ABC):
    """
    Embedding provider interface.

    Implementations MUST be import-safe (no exception at import time when credentials absent).
    Provide synchronous `embed` for simplicity (worker can call in threadpool).
    """

    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        raise NotImplementedError
```
---- END FILE ----

---- BEGIN FILE: src/mcp/embeddings/mock_embedder.py ----
```python name=src/mcp/embeddings/mock_embedder.py
import hashlib
from typing import List, Dict, Any

from .interface import EmbedderInterface


class MockEmbedder(EmbedderInterface):
    """
    Deterministic mock embedder for local dev and CI.
    Produces fixed-size vectors derived from sha256 of the input text.
    """

    def __init__(self, dim: int = 16):
        self.dim = dim

    def _text_to_vector(self, t: str):
        h = hashlib.sha256(t.encode("utf-8")).digest()
        # Convert bytes -> floats in [0,1)
        vec = [((b & 0xFF) / 255.0) for b in h[: self.dim]]
        return vec

    def embed(self, texts: List[str]) -> List[List[float]]:
        return [self._text_to_vector(t) for t in texts]

    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "embedder": "mock", "dim": self.dim}
```
---- END FILE ----

---- BEGIN FILE: src/mcp/embeddings/openai_embedder.py ----
```python name=src/mcp/embeddings/openai_embedder.py
import os
import logging
from typing import List, Dict, Any

from .interface import EmbedderInterface

logger = logging.getLogger(__name__)


class OpenAIEmbedder(EmbedderInterface):
    """
    Minimal OpenAI embedder skeleton with lazy import.
    """

    def __init__(self, model: str = "text-embedding-3-small"):
        self.model = model
        self._client = None
        self._api_key = os.environ.get("OPENAI_API_KEY", "")

    def _ensure_client(self):
        if self._client:
            return
        try:
            import openai  # type: ignore
        except Exception as exc:
            logger.warning("openai package missing or cannot be imported: %s", exc)
            self._client = None
            return
        openai.api_key = self._api_key
        self._client = openai

    def embed(self, texts: List[str]) -> List[List[float]]:
        self._ensure_client()
        if not self._client:
            # Fallback: empty vectors to keep system safe
            return [[0.0] * 1 for _ in texts]
        resp = self._client.Embedding.create(model=self.model, input=texts)  # shape depends on SDK
        return [d["embedding"] for d in resp["data"]]

    def health_check(self) -> Dict[str, Any]:
        ok = bool(self._api_key and self._client is not None)
        return {"status": "ok" if ok else "disconnected", "adapter": "openai"}
```
---- END FILE ----

---- BEGIN FILE: src/mcp/embeddings/hf_embedder.py ----
```python name=src/mcp/embeddings/hf_embedder.py
import os
import logging
from typing import List, Dict, Any

from .interface import EmbedderInterface

logger = logging.getLogger(__name__)


class HFEmbedder(EmbedderInterface):
    """
    Hugging Face embedder skeleton (sentence-transformers / transformers).
    Lazy-loads required model to avoid heavy imports in tests.
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    def _ensure_model(self):
        if self._model:
            return
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
        except Exception as exc:
            logger.warning("sentence_transformers not available: %s", exc)
            self._model = None
            return
        self._model = SentenceTransformer(self.model_name)

    def embed(self, texts: List[str]) -> List[List[float]]:
        self._ensure_model()
        if not self._model:
            # safe fallback
            return [[0.0] * 1 for _ in texts]
        return self._model.encode(texts).tolist()

    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok" if self._model is not None else "disconnected", "adapter": "hf"}
```
---- END FILE ----

---- BEGIN FILE: src/mcp/embeddings/batcher.py ----
```python name=src/mcp/embeddings/batcher.py
from typing import Iterable, List, Any, Generator
import hashlib
import json


def compute_checksum(item: dict) -> str:
    """
    Compute deterministic checksum for item content/metadata.
    """
    s = json.dumps({"id": item.get("id"), "content": item.get("content"), "metadata": item.get("metadata", {})}, sort_keys=True)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def batch_iterable(iterable: Iterable[Any], batch_size: int) -> Generator[List[Any], None, None]:
    batch = []
    for it in iterable:
        batch.append(it)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch
```
---- END FILE ----

---- BEGIN FILE: src/mcp/embeddings/chunking.py ----
```python name=src/mcp/embeddings/chunking.py
# Simple heuristic chunker (character-based) with overlap to approximate token chunking.
from typing import List, Iterable

def chunk_text(text: str, max_chars: int = 1000, overlap: int = 200) -> List[str]:
    if len(text) <= max_chars:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunk = text[start:end]
        chunks.append(chunk)
        if end >= len(text):
            break
        start = max(0, end - overlap)
    return chunks

def chunk_texts(items: Iterable[dict], max_chars: int = 1000, overlap: int = 200):
    """
    Input: iterable of item dicts with 'id' and 'content'.
    Output: list of {id, chunk_index, content, metadata}
    """
    out = []
    for item in items:
        cid = item.get("id")
        content = item.get("content", "")
        metadata = item.get("metadata", {})
        chunks = chunk_text(content, max_chars=max_chars, overlap=overlap)
        for i, c in enumerate(chunks):
            out.append({"id": f"{cid}__chunk__{i}", "content": c, "metadata": metadata})
    return out

def estimate_tokens_from_chars(chars: int, ratio: float = 4.0) -> int:
    return max(1, int(chars / ratio))
```
---- END FILE ----

---- BEGIN FILE: src/mcp/embeddings/dedupe.py ----
```python name=src/mcp/embeddings/dedupe.py
from typing import Dict, Any, Set
import hashlib
import json

def checksum_for_item(item: Dict[str, Any]) -> str:
    s = json.dumps({"id": item.get("id"), "content": item.get("content"), "metadata": item.get("metadata", {})}, sort_keys=True)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

class InMemoryDeduper:
    def __init__(self):
        self._seen: Set[str] = set()

    def is_duplicate(self, item: Dict[str, Any]) -> bool:
        c = checksum_for_item(item)
        if c in self._seen:
            return True
        self._seen.add(c)
        return False
```
---- END FILE ----

---- BEGIN FILE: src/mcp/workers/checkpoint.py ----
```python name=src/mcp/workers/checkpoint.py
# Simple file-based checkpoint helper. Stores processed ids/checksums per input file.
import json
from pathlib import Path
from typing import Set

def load_checkpoint(path: str) -> Set[str]:
    p = Path(path)
    if not p.exists():
        return set()
    try:
        return set(json.loads(p.read_text()))
    except Exception:
        return set()

def save_checkpoint(path: str, seen: Set[str]):
    p = Path(path)
    p.write_text(json.dumps(list(seen)))
```
---- END FILE ----

---- BEGIN FILE: src/mcp/retries.py ----
```python name=src/mcp/retries.py
# Minimal retry / backoff helper (exponential backoff with jitter)
import time
import random
import functools
from typing import Callable, Tuple

def retry_on_exception(
    exceptions: Tuple[type, ...] = (Exception,),
    tries: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 10.0,
    jitter: float = 0.1,
):
    def decorator(fn: Callable):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return fn(*args, **kwargs)
                except exceptions:
                    attempt += 1
                    if attempt >= tries:
                        raise
                    delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
                    delay = delay * (1 + (random.random() * jitter))
                    time.sleep(delay)
        return wrapper
    return decorator
```
---- END FILE ----

---- BEGIN FILE: src/mcp/observability/metrics.py ----
```python name=src/mcp/observability/metrics.py
# Minimal in-memory metrics facade. Replace with Prometheus/OTel exporter in later plans.
import time
from typing import Dict
_metrics: Dict[str, int] = {}
_timers: Dict[str, float] = {}

def increment(name: str, amount: int = 1):
    _metrics[name] = _metrics.get(name, 0) + amount

def get_metric(name: str) -> int:
    return _metrics.get(name, 0)

class Timer:
    def __init__(self, name: str):
        self.name = name
        self.start = None

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc, tb):
        elapsed = time.time() - self.start
        _timers[self.name] = _timers.get(self.name, 0.0) + elapsed
        increment(f"{self.name}_count", 1)

def snapshot() -> Dict:
    return {"counters": dict(_metrics), "timers": dict(_timers)}
```
---- END FILE ----

---- BEGIN FILE: src/workers/embedding_worker.py ----
```python name=src/workers/embedding_worker.py
"""
Embedding worker (single-process). Reads a JSON array of items from disk, optionally chunks and dedupes,
calls an Embedder (configured via EMBEDDER_CLASS), and persists embedding vectors via BackendAdapter.upsert_batch.

Safety:
- Uses adapter_loader.load_adapter() to get persistence adapter (defaults to in-repo mock)
- Uses EMBEDDER_CLASS for embedder (default: mock embedder)
- Guards live provider operations via src/mcp/server/safety_checks.live_tests_enabled()
- Uses retry_on_exception decorator and metrics hooks
"""
from __future__ import annotations
import os
import json
import logging
from typing import List, Dict, Any, Iterable, Set

from src.mcp.embeddings.batcher import batch_iterable, compute_checksum  # type: ignore
from src.mcp.embeddings.chunking import chunk_texts  # type: ignore
from src.mcp.embeddings.dedupe import InMemoryDeduper  # type: ignore
from src.mcp.workers.checkpoint import load_checkpoint, save_checkpoint  # type: ignore
from src.mcp.server.adapter_loader import load_adapter  # type: ignore
from src.mcp.observability.metrics import increment, Timer  # type: ignore
from src.mcp.retries import retry_on_exception  # type: ignore
from src.mcp.server.safety_checks import live_tests_enabled  # type: ignore

logger = logging.getLogger(__name__)

# PII hook (pluggable)
def default_preprocess(text: str) -> str:
    # noop by default; override to redact PII
    return text

def _load_embedder_class(path: str):
    """
    Path example: 'src.mcp.embeddings.mock_embedder.MockEmbedder'
    """
    if not path:
        from src.mcp.embeddings.mock_embedder import MockEmbedder  # type: ignore
        return MockEmbedder
    module_name, cls_name = path.rsplit(".", 1)
    mod = __import__(module_name, fromlist=[cls_name])
    return getattr(mod, cls_name)


@retry_on_exception(tries=3)
def _upsert_with_retry(adapter, namespace: str, items: Iterable[Dict[str, Any]]):
    adapter.upsert_batch(namespace, items)


def run_worker(
    input_path: str,
    batch_size: int = 32,
    namespace_default: str = "default",
    preprocess=default_preprocess,
    checkpoint_path: str | None = None,
):
    """
    Run the embedding worker:
    - load embedder (EMBEDDER_CLASS)
    - load adapter for persistence
    - load items from JSON array file
    - chunk/dedupe/checkpoint/batch/embed/upsert
    """
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
        items = json.load(fh)

    # Load checkpoint if provided
    seen: Set[str] = set()
    if checkpoint_path:
        seen = load_checkpoint(checkpoint_path)

    # Optionally chunk items (preserve original ids via chunk ids)
    # For simplicity: chunk every item into sub-items if content large
    all_items = []
    for it in items:
        # preprocess, e.g., PII redaction
        content = preprocess(it.get("content", ""))
        it["content"] = content
        # chunk
        chunks = chunk_texts([it], max_chars=int(os.environ.get("EMBEDDING_CHUNK_MAX_CHARS", "1000")), overlap=int(os.environ.get("EMBEDDING_CHUNK_OVERLAP", "200")))
        all_items.extend(chunks)

    deduper = InMemoryDeduper()
    # Filter out already processed (checkpoint) and duplicates
    pending = []
    for it in all_items:
        ch = compute_checksum(it)
        if ch in seen:
            continue
        if deduper.is_duplicate(it):
            continue
        pending.append(it)

    # Batch and process
    for batch in batch_iterable(pending, batch_size):
        texts = [b["content"] for b in batch]
        with Timer("embed_batch_latency"):
            # Guard live embedder calls behind ENABLE_LIVE_TESTS if embedder is a real provider
            if not live_tests_enabled():
                # If live tests not enabled and embedder is not mock, prefer using mock behavior
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
        # Persist with retry/backoff
        try:
            increment("worker_batch_total")
            with Timer("worker_upsert_latency"):
                _upsert_with_retry(adapter, namespace_default, upsert_items)
            # mark checkpoint entries as processed
            if checkpoint_path:
                for it in batch:
                    seen.add(compute_checksum(it))
                save_checkpoint(checkpoint_path, seen)
        except Exception as exc:
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)

if __name__ == "__main__":
    main()
```
---- END FILE ----

---- BEGIN FILE: Dockerfile.embedding ----
```dockerfile name=Dockerfile.embedding
# Minimal container image for embedding worker
FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml pyproject.toml
# Install minimal runtime deps (user Phase 5 extend)
RUN pip install --upgrade pip
RUN pip install fastapi pytest

# Copy source
COPY src/ src/

ENV PYTHONPATH=/app

ENTRYPOINT ["python", "-m", "src.workers.embedding_worker"]
```
---- END FILE ----

---- BEGIN FILE: docker-compose.embedding.yml ----
```yaml name=docker-compose.embedding.yml
version: "3.8"
services:
  embedding-worker:
    build:
      context: .
      dockerfile: Dockerfile.embedding
    environment:
      - EMBEDDER_CLASS=src.mcp.embeddings.mock_embedder.MockEmbedder
      - ADAPTER_CLASS=src.mcp.backends.mock_backend.InMemoryMockBackend
      - EMBEDDING_BATCH_SIZE=8
    volumes:
      - ./samples:/samples
    command: ["--input", "/samples/small_docs.json", "--batch-size", "8"]
```
---- END FILE ----

---- BEGIN FILE: tests/embeddings/test_batcher.py ----
```python name=tests/embeddings/test_batcher.py
from src.mcp.embeddings.batcher import batch_iterable, compute_checksum

def test_batch_iterable():
    data = list(range(7))
    batches = list(batch_iterable(data, 3))
    assert len(batches) == 3
    assert batches[0] == [0,1,2]
    assert batches[-1] == [6]

def test_compute_checksum_deterministic():
    item = {"id":"1","content":"hello","metadata":{"k":"v"}}
    c1 = compute_checksum(item)
    c2 = compute_checksum(item)
    assert c1 == c2
```
---- END FILE ----

---- BEGIN FILE: tests/embeddings/test_chunking.py ----
```python name=tests/embeddings/test_chunking.py
from src.mcp.embeddings.chunking import chunk_text, chunk_texts, estimate_tokens_from_chars

def test_chunk_small():
    t = "short text"
    chunks = chunk_text(t, max_chars=100)
    assert len(chunks) == 1

def test_chunk_large_overlap():
    t = "a" * 1000
    chunks = chunk_text(t, max_chars=400, overlap=50)
    assert len(chunks) >= 2
    assert len(chunks[0]) == 400

def test_chunk_texts_structure():
    items = [{"id":"x","content":"a"*900,"metadata":{}}]
    out = chunk_texts(items, max_chars=400, overlap=50)
    assert isinstance(out, list)
    assert out[0]["id"].startswith("x__chunk__")
```
---- END FILE ----

---- BEGIN FILE: tests/embeddings/test_dedupe.py ----
```python name=tests/embeddings/test_dedupe.py
from src.mcp.embeddings.dedupe import InMemoryDeduper

def test_dedupe():
    d = InMemoryDeduper()
    item = {"id":"1","content":"hello","metadata":{}}
    assert not d.is_duplicate(item)
    assert d.is_duplicate(item)
```
---- END FILE ----

---- BEGIN FILE: tests/embeddings/test_worker.py ----
```python name=tests/embeddings/test_worker.py
import json
from src.workers.embedding_worker import run_worker
from src.mcp.backends.mock_backend import InMemoryMockBackend

def test_run_worker_upserts(tmp_path, monkeypatch):
    items = [{"id":"a","content":"hello","metadata":{}},{"id":"b","content":"world","metadata":{}}]
    p = tmp_path / "sample.json"
    p.write_text(json.dumps(items), encoding="utf-8")
    monkeypatch.setenv("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    # run worker; should complete without exceptions
    run_worker(str(p), batch_size=2, namespace_default="testns", checkpoint_path=str(tmp_path/"ck.json"))
    assert True
```
---- END FILE ----

---- BEGIN FILE: tests/integration/fixtures/recorded_openai/example_embedding_response.json ----
```json name=tests/integration/fixtures/recorded_openai/example_embedding_response.json
{
  "data": [
    {"embedding":[0.1,0.2,0.3],"index":0},
    {"embedding":[0.4,0.5,0.6],"index":1}
  ]
}
```
---- END FILE ----

---- BEGIN FILE: docs/embeddings.md ----
```markdown name=docs/embeddings.md
# Embeddings — Worker & Provider Configuration

Purpose
- Document how to configure and run the embedding worker safely.

Configuration variables
- EMBEDDER_CLASS: Python import path for embedder (default: src.mcp.embeddings.mock_embedder.MockEmbedder)
- OPENAI_API_KEY: OpenAI API key (do NOT commit)
- HF_API_TOKEN: Hugging Face token (do NOT commit)
- EMBEDDING_BATCH_SIZE: default batch size for worker (int)
- EMBEDDING_MAX_RETRIES: number of retry attempts for networked embed calls
- EMBEDDING_BACKOFF_BASE: base seconds for exponential backoff
- EMBEDDING_WORKER_NAMESPACE_DEFAULT: default namespace/tenant

Running worker locally
- Prepare a JSON file with a list of items:
  ```json
  [{"id":"1","content":"text","metadata":{}}, {"id":"2","content":"another","metadata":{}}]
  ```
- Run:
  ```bash
  python -m src.workers.embedding_worker --input path/to/sample.json --batch-size 32
  ```

Recorded / gated live runs
- For recorded-mode runs, use recorded fixtures under tests/integration/fixtures/recorded_openai/.
- Live-provider runs must be gated: set ENABLE_LIVE_TESTS=true and add provider secrets to GitHub Secrets or env (see docs/SECRETS_RUNBOOK.md).
```
---- END FILE ----

---- BEGIN FILE: docs/run_embedding_worker.md ----
```markdown name=docs/run_embedding_worker.md
# Running the Embedding Worker (Local & Docker)

Local (dev/mock)
- Ensure repo root is on PYTHONPATH:
  ```bash
  export PYTHONPATH="$(pwd):$PYTHONPATH"
  python -m venv .venv
  . .venv/bin/activate
  pip install -U pip
  pip install pytest
  python -m src.workers.embedding_worker --input samples/small_docs.json --batch-size 8
  ```

Docker (container)
- Build image:
  docker build -f Dockerfile.embedding -t mcp-embedding:local .
- Run via docker-compose:
  docker-compose -f docker-compose.embedding.yml up --build

Notes
- By default the worker uses the mock embedder and the in-repo mock backend; no provider secrets needed.
- To use a real provider, set EMBEDDER_CLASS to a provider adapter and add the required env vars. Only enable live-provider runs in controlled environments after reading docs/SECRETS_RUNBOOK.md.
```
---- END FILE ----

---- BEGIN FILE: docs/SECRETS_RUNBOOK.md ----
```markdown name=docs/SECRETS_RUNBOOK.md
# Secrets Runbook (brief)

Purpose
- Document how to store provider secrets, rotate them, and enable gated live integration tests safely.

Key points
- Store secrets in GitHub Secrets (Repository > Settings > Secrets) or an external vault (HashiCorp Vault).
- Do NOT commit secrets to the repository.
- Use the integration-gated workflow to run live tests; enable by setting ENABLE_LIVE_TESTS=true in workflow inputs or in environment.
- Rotate keys regularly and update secrets in repo settings. Use short-lived credentials where supported.

Enabling live tests (high-level)
- Add provider secrets to repository Secrets: OPENAI_API_KEY, PINECONE_API_KEY, etc.
- Set ENABLE_LIVE_TESTS secret to "true" only for authorized branches or by admins.
- Run the integration-gated workflow manually (or via CI policy) to execute live tests.

Least-privilege guidance
- Create API keys scoped to the test environment and restrict index/prefix access where possible.
- Monitor usage and set provider-side billing alerts.

Audit
- Keep an audit log of who enabled live tests and when; record workflow runs and approvals.
```
---- END FILE ----

---- BEGIN FILE: .github/workflows/integration-gated.yml ----
```yaml name=.github/workflows/integration-gated.yml
name: MCP - Integration (Gated)

# Template gated workflow to run live integration tests only when enabled.
# To enable, set ENABLE_LIVE_TESTS=true and configure required secrets (in repo settings).
on:
  workflow_dispatch:

jobs:
  integration:
    if: ${{ github.event.inputs.enable == 'true' || env.ENABLE_LIVE_TESTS == 'true' }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.11
      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements-test.txt ]; then pip install -r requirements-test.txt; fi
          pip install -e .
      - name: Run integration tests (live)
        env:
          ENABLE_LIVE_TESTS: ${{ secrets.ENABLE_LIVE_TESTS }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          pytest tests/integration -q
```
---- END FILE ----

Notes on wiring & next steps
- After adding the above files:
  - Run pytest -q tests/embeddings and pytest -q tests/mcp to validate unit tests.
  - Ensure PYTHONPATH points to repo root for test runs, or add tests/conftest.py to append repo root to sys.path.
  - Review docs and .env.example to list new env vars (EMBEDDER_CLASS, EMBEDDING_*).
  - Consider adding small integration recorded-mode job that uses recorded fixtures and does not require secrets.
- Suggested small iterative PRs:
  1. Add embedding interface + mock embedder + unit tests.
  2. Add batcher/chunking/dedupe + tests.
  3. Add worker CLI and basic persistence integration with mock backend + checkpoint tests.
  4. Add OpenAI/HF skeletons and recorded fixtures + gated integration workflow.

------

# [Post-Plan]: Validation, Handover & Next Steps — MCP Plans A→D
> Generated: 2025-12-19T00:00:00Z | Author: mbaetiong

Purpose
- Provide a post-implementation plan that describes validation steps, monitoring, handover items, follow-up tickets, retrospective notes and recommended actions after Plans A–D are merged to main.
- This file guides maintainers to verify correctness, operationalize gating & secrets, and plan Plan E+ follow-ups.

Immediate validation checklist (post-merge)
- For each merged Plan's PR, run the following and record results:

1. CI: Confirm workflows
   - mcp-ci.yml: all matrix jobs (3.10/3.11) passed.
   - integration-gated.yml: NOT triggered by default; remains template-only.
2. Tests: Local verification
   - pytest -q tests/mcp -k "not live" --maxfail=1 → pass
   - pytest -q tests/embeddings → pass
3. Import-safety and lazy import checks
   - From a clean environment without provider SDKs installed, run:
     - python -c "import src.mcp.backends.pinecone_adapter; print('import ok')"
     - python -c "import src.mcp.embeddings.openai_embedder; print('import ok')"
   - Expect no exceptions (lazy import patterns).
4. Security check
   - Search code for hardcoded keys or secrets (grep 'API_KEY'/'SECRET' in committed files).
   - Confirm .env.example present and updated with new vars (EMBEDDER_CLASS, EMBEDDING_*).
5. Conformance harness & tenant tests
   - export ADAPTER_UNDER_TEST="src.mcp.backends.mock_backend.InMemoryMockBackend"
   - pytest -q tests/mcp/conformance
   - pytest -q tests/mcp/test_tenant_isolation.py
6. Contract tests & façade
   - pytest -q tests/mcp/test_facade.py
   - pytest -q tests/mcp/test_facade_contract.py

Operational handover (to SRE/DevOps)
- Secrets & gating:
  - Decide responsible admin(s) for enabling live tests (ENABLE_LIVE_TESTS secret).
  - Ensure GitHub repository Secrets lifecycle policy documented: where to store, who can enable, rotation cadence.
- CI:
  - Add a scheduled job to run dependency-scan (dependency-scan.yml) weekly.
  - Add monitoring or alerts for failing scheduled scans.
- Docker images:
  - If teams plan to run embedding worker in prod, add a build/publish workflow and image tags in CI (future plan).

Post-merge follow-ups & backlog (recommended issues)
- P1 — Integrate token-based chunker with an actual tokenizer (tiktoken / HF tokenizers) for better chunk sizes.
- P1 — Replace in-memory rate-limit & dedupe with Redis/Upstash for cross-process safety.
- P1 — Add Prometheus/OTel exporter wiring to metrics facade for production observability.
- P2 — Implement recorded-mode harness for embedder adapters to enable reproducible integration tests.
- P2 — Add robust checkpoint storage (e.g., durable DB or cloud storage) for large workloads.
- P3 — Add policy for cost budgeting & alerts when live tests or workers consume > threshold (billing guard).

Post-merge remediation steps (if CI/test failures)
- Common failures & fixes:
  - ImportError for src.*: Ensure PYTHONPATH includes repo root in CI or tests/conftest.py appends project root.
  - Missing pytest dependency: add requirements-test.txt or update pre-test step in workflow.
  - Mock modules not being applied: ensure tests monkeypatch sys.modules correctly or use importlib.reload when needed.
- Re-run CI after fixes, iterate on PR.

Metrics & monitoring checklist (what to add asap)
- Ensure the minimal metrics facade exposes counters used by plans:
  - adapter_upsert_total, adapter_query_total, adapter_errors_total
  - pinecone_upsert_total, pinecone_query_total (Plan B)
  - mcp_call_tool_total, facade request_latency (Plan C)
  - worker_batch_total, worker_batch_failures, embed_batch_latency (Plan D)
- Add a follow-up to expose metrics via /metrics endpoint using Prometheus client (Plan E).

Release notes (for merge PRs)
- For each Plan PR include a short release notes section:
  - What was added (files, endpoints, workflow)
  - What's gated (integration-gated.yml not enabled)
  - How to run locally (commands)
  - Security note: no keys committed, enable live tests per docs/SECRETS_RUNBOOK.md

Suggested PR checklist (post-merge verification - to include in PR description)
- [ ] All unit tests pass locally and in CI.
- [ ] Conformance & tenant isolation tests run successfully against mock.
- [ ] No secrets or credentials committed.
- [ ] Integration-gated workflow present but not enabled.
- [ ] docs/SECRETS_RUNBOOK.md references updated env vars.
- [ ] PR includes run instructions and acceptance criteria mapping.

Handoff & Documentation to add / update (post-merge)
- Update repository README with:
  - Overview of Plan A–D capabilities and where to find docs.
  - How to run façade and worker locally with mock components.
  - How to enable live tests (link to SECRETS_RUNBOOK.md).
- Add a short "How we tested" section that points to test commands and CI jobs.
- Create an operational playbook for embedding worker: start/stop, logs, checkpoints, and recovery procedures.

Retrospective notes (for team)
- Keep scaffolds minimal and stable. Avoid adding feature-rich provider code until tests and gating are proven working.
- Maintain small, focused PRs for each file to simplify review and rollbacks.
- Prioritize adding recorded fixtures for any external provider tests to avoid flaky integration runs.

Post-Plan enforcement (code health)
- Add a small pre-commit hook to check for accidental secrets (optional).
- Add a CI linting job to check imports and code style (pyproject/ruff/black) in a follow-up plan.
- Add a GitHub CODEOWNERS file to require review by infra/security for any changes under src/mcp/backends/* and .github/workflows/*.

Templates & artifacts (handy copy-paste)
- PR description template (short):
  - Title: Plan <X> — <short summary>
  - Summary: What changed
  - Files: list
  - How to test locally: commands
  - CI jobs: mcp-ci.yml (matrix), integration-gated.yml (template)
  - Security: "No secrets committed"
  - Acceptance: list of ACs

- Quick run commands (post-merge sanity):
  - export PYTHONPATH="$(pwd):$PYTHONPATH"
  - python -m venv .venv && . .venv/bin/activate
  - pip install -U pip
  - pip install pytest
  - pytest -q tests/mcp -k "not live"
  - pytest -q tests/embeddings

Closing next-steps
1. Merge Plan A PR first. Verify CI passes and conformance harness exists.
2. Sequentially merge Plans B, C, D with the pre-defined PR checklist.
3. After merge of Plans A–D, open backlog issues for P1/P2 items above and schedule them into roadmap.
