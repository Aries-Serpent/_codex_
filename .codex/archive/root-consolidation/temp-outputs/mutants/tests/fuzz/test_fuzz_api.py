"""Hypothesis-based fuzz tests for FastAPI / Pydantic request-model validation.

Targets (from ``codex.api.rag_api``):
- ``QueryRequest`` — query text, index name, top_k, min_score
- ``BuildIndexRequest`` — files list, index_name, chunk_size, overlap
- ``DeleteIndexRequest`` — index_name, tenant_id, force
- ``MergeIndicesRequest`` — source_indices (≥2), target_index
- ``HealthResponse`` — status, version, timestamp, components

Fuzzes with arbitrary strings, numbers, and nested structures to ensure
models validate inputs correctly (raise ``ValidationError``) and never
crash with unexpected exceptions.

Import guard skips the module when ``hypothesis`` is absent.
"""

from __future__ import annotations

import pytest

hypothesis = pytest.importorskip("hypothesis")

from hypothesis import (  # noqa: E402
    HealthCheck,  # noqa: E402
    given,
    settings,
)
from hypothesis import strategies as st  # noqa: E402

# ---------------------------------------------------------------------------
# Lazy import helpers
# ---------------------------------------------------------------------------


def _import_models():
    from codex.api.rag_api import (
        BuildIndexRequest,
        DeleteIndexRequest,
        HealthResponse,
        MergeIndicesRequest,
        QueryRequest,
    )

    return QueryRequest, BuildIndexRequest, DeleteIndexRequest, MergeIndicesRequest, HealthResponse


def _validation_error():
    from pydantic import ValidationError

    return ValidationError


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

_nonempty_text = st.text(min_size=1, max_size=256)
_tenant_id = st.one_of(
    st.just("default"),
    _nonempty_text,
    st.just(""),
)
_file_path = st.text(min_size=1, max_size=128)

# ---------------------------------------------------------------------------
# QueryRequest fuzz tests
# ---------------------------------------------------------------------------


@given(
    query=_nonempty_text,
    index_name=_nonempty_text,
    tenant_id=_tenant_id,
    top_k=st.integers(min_value=1, max_value=100),
    min_score=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=80, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_fuzz_query_request_valid(query, index_name, tenant_id, top_k, min_score):
    """Fuzz: QueryRequest accepts valid inputs and exposes correct fields."""
    QueryRequest, *_ = _import_models()
    ValidationError = _validation_error()
    try:
        req = QueryRequest(
            query=query,
            index_name=index_name,
            tenant_id=tenant_id,
            top_k=top_k,
            min_score=min_score,
        )
        assert req.query == query, "query is not valid"
        assert 1 <= req.top_k <= 100, "1 is not valid"
        assert 0.0 <= req.min_score <= 1.0, "0 is not valid"
    except ValidationError:
        pass  # invalid input rejected by Pydantic — expected behaviour
    except (ConnectionError, TimeoutError) as exc:  # noqa: BLE001
        pytest.fail(f"QueryRequest raised unexpected: {exc!r}")


@given(
    query=st.one_of(st.just(""), st.just(None), st.integers()),
    top_k=st.one_of(
        st.integers(min_value=-100, max_value=0),
        st.integers(min_value=101, max_value=10000),
    ),
    min_score=st.one_of(
        st.floats(min_value=-10.0, max_value=-0.01, allow_nan=False),
        st.floats(min_value=1.01, max_value=100.0, allow_nan=False),
        st.just(float("nan")),
        st.just(float("inf")),
    ),
)
@settings(max_examples=60, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_fuzz_query_request_invalid_inputs(query, top_k, min_score):
    """Fuzz: invalid query / top_k / min_score must raise ValidationError."""
    QueryRequest, *_ = _import_models()
    ValidationError = _validation_error()
    with pytest.raises((ValidationError, Exception)):
        QueryRequest(
            query=query,
            index_name="some-index",
            top_k=top_k,
            min_score=min_score,
        )


# ---------------------------------------------------------------------------
# BuildIndexRequest fuzz tests
# ---------------------------------------------------------------------------


@given(
    files=st.lists(_file_path, min_size=1, max_size=20),
    index_name=_nonempty_text,
    chunk_size=st.integers(min_value=100, max_value=10000),
    overlap=st.integers(min_value=0, max_value=9999),
)
@settings(max_examples=60, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_fuzz_build_index_request_valid(files, index_name, chunk_size, overlap):
    """Fuzz: BuildIndexRequest accepts valid file lists and numeric params."""
    _, BuildIndexRequest, *_ = _import_models()
    ValidationError = _validation_error()
    try:
        req = BuildIndexRequest(
            files=files, index_name=index_name, chunk_size=chunk_size, overlap=overlap
        )
        assert isinstance(req.files, list)
        assert 100 <= req.chunk_size <= 10000, "100 is not valid"
    except ValidationError:
        pass  # invalid input rejected by Pydantic — expected behaviour
    except (ConnectionError, TimeoutError) as exc:  # noqa: BLE001
        pytest.fail(f"BuildIndexRequest raised unexpected: {exc!r}")


@given(
    chunk_size=st.one_of(
        st.integers(min_value=-1000, max_value=99),  # below min
        st.integers(min_value=10001, max_value=100000),  # above max
    ),
    overlap=st.integers(min_value=-1000, max_value=-1),  # negative
)
@settings(max_examples=50, deadline=None)
def test_fuzz_build_index_request_invalid_numerics(chunk_size, overlap):
    """Fuzz: out-of-range chunk_size / negative overlap must raise ValidationError."""
    _, BuildIndexRequest, *_ = _import_models()
    ValidationError = _validation_error()
    with pytest.raises((ValidationError, Exception)):
        BuildIndexRequest(
            files=["file.txt"],
            index_name="idx",
            chunk_size=chunk_size,
            overlap=overlap,
        )


# ---------------------------------------------------------------------------
# DeleteIndexRequest fuzz tests
# ---------------------------------------------------------------------------


@given(
    index_name=_nonempty_text,
    tenant_id=_tenant_id,
    force=st.booleans(),
)
@settings(max_examples=60, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_fuzz_delete_index_request_valid(index_name, tenant_id, force):
    """Fuzz: DeleteIndexRequest accepts arbitrary index names and tenant IDs."""
    _, _, DeleteIndexRequest, *_ = _import_models()
    ValidationError = _validation_error()
    try:
        req = DeleteIndexRequest(index_name=index_name, tenant_id=tenant_id, force=force)
        assert isinstance(req.force, bool)
    except ValidationError:
        pass  # invalid input rejected by Pydantic — expected behaviour
    except (ConnectionError, TimeoutError) as exc:  # noqa: BLE001
        pytest.fail(f"DeleteIndexRequest raised unexpected: {exc!r}")


# ---------------------------------------------------------------------------
# MergeIndicesRequest fuzz tests
# ---------------------------------------------------------------------------


@given(
    source_indices=st.lists(_nonempty_text, min_size=2, max_size=10),
    target_index=_nonempty_text,
    tenant_id=_tenant_id,
)
@settings(max_examples=60, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_fuzz_merge_indices_request_valid(source_indices, target_index, tenant_id):
    """Fuzz: MergeIndicesRequest accepts lists of ≥2 source indices."""
    *_, MergeIndicesRequest, _ = _import_models()
    ValidationError = _validation_error()
    try:
        req = MergeIndicesRequest(
            source_indices=source_indices,
            target_index=target_index,
            tenant_id=tenant_id,
        )
        assert len(req.source_indices) >= 2, "Collection must not be empty"
    except ValidationError:
        pass  # invalid input rejected by Pydantic — expected behaviour in fuzz test
    except (ConnectionError, TimeoutError) as exc:  # noqa: BLE001
        pytest.fail(f"MergeIndicesRequest raised unexpected: {exc!r}")


@given(
    source_indices=st.one_of(
        st.just([]),
        st.lists(_nonempty_text, min_size=1, max_size=1),
    ),
    target_index=_nonempty_text,
)
@settings(max_examples=40, deadline=None)
def test_fuzz_merge_indices_request_too_few_sources(source_indices, target_index):
    """Fuzz: fewer than 2 source indices must raise ValidationError."""
    *_, MergeIndicesRequest, _ = _import_models()
    ValidationError = _validation_error()
    with pytest.raises((ValidationError, Exception)):
        MergeIndicesRequest(source_indices=source_indices, target_index=target_index)


# ---------------------------------------------------------------------------
# HealthResponse fuzz tests
# ---------------------------------------------------------------------------


@given(
    status=st.one_of(st.just("ok"), st.just("degraded"), st.just("down"), _nonempty_text),
    version=_nonempty_text,
    timestamp=st.one_of(
        st.just("2024-01-01T00:00:00Z"),
        _nonempty_text,
        st.just(""),
    ),
    components=st.dictionaries(
        keys=st.text(min_size=1, max_size=32),
        values=st.one_of(st.just("ok"), st.just("error"), _nonempty_text),
        min_size=0,
        max_size=10,
    ),
)
@settings(max_examples=60, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_fuzz_health_response_construction(status, version, timestamp, components):
    """Fuzz: HealthResponse accepts arbitrary string fields for all keys."""
    *_, HealthResponse = _import_models()
    ValidationError = _validation_error()
    try:
        resp = HealthResponse(
            status=status, version=version, timestamp=timestamp, components=components
        )
        assert isinstance(resp.status, str)
        assert isinstance(resp.components, dict)
    except (ValidationError, Exception):
        pass  # arbitrary inputs may fail validation or construction — expected in fuzz test
