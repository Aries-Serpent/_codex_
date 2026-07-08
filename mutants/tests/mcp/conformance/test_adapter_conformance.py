"""
Test Adapter Conformance

Test module for adapter conformance.
"""

# Conformance test scaffold for adapters.
# This file is a lightweight conformance harness that can be parameterized
# to run against any adapter implementation that implements BackendAdapter.
#
# It is safe for CI: by default it expects to be run against the in-repo mock backend.
# Adapter factory lookup helper. Tests should set ADAPTER_UNDER_TEST to the import path
# e.g. "src.mcp.backends.mock_backend.InMemoryMockBackend" or "src.mcp.backends.pinecone_adapter.PineconeAdapter"
import importlib
import os
from collections.abc import Iterable
from typing import Any

import pytest

ADAPTER_PATH = os.environ.get(
    "ADAPTER_UNDER_TEST", "src.mcp.backends.mock_backend.InMemoryMockBackend"
)


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


def sample_items() -> Iterable[dict[str, Any]]:
    return [
        {"id": "conf-a", "embedding": [1.0, 0.0], "content": "a", "metadata": {"tag": "x"}},
        {"id": "conf-b", "embedding": [0.9, 0.1], "content": "b", "metadata": {"tag": "y"}},
    ]


def test_conformance_connect_health(adapter):
    h = adapter.health_check()
    assert isinstance(h, dict)
    assert "status" in h, "Condition must be true"


def test_conformance_upsert_query_delete(adapter):
    ns = "conformance"
    items = list(sample_items())
    adapter.upsert_batch(ns, items)
    res = adapter.query_top_k(ns, [1.0, 0.0], top_k=2)
    assert isinstance(res, list)
    assert len(res) >= 1, "Res must not be empty"
    # delete one
    delete_result = adapter.delete(ns, items[0]["id"])
    assert delete_result in (True, False)
    # health still present
    _ = adapter.health_check()
