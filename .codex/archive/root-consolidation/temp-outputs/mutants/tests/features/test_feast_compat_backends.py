"""Tests for feast_compat production backends (SAR-G02 — S116/W-142).

Covers InMemoryBackend, SQLiteBackend, RedisBackend (mocked),
FeastBackend Protocol conformance, and create_backend() factory.
"""

from __future__ import annotations

import importlib.util
import json
from unittest.mock import MagicMock, patch

import pytest

# ── Import helpers ──────────────────────────────────────────────────────────


def _import_feast():
    return pytest.importorskip(
        "codex_ml.features.feast_compat",
        reason="codex_ml.features.feast_compat not importable",
    )


# ── FeastBackend Protocol ───────────────────────────────────────────────────


class TestFeastBackendProtocol:
    """Protocol conformance tests."""

    def test_in_memory_satisfies_protocol(self):
        mod = _import_feast()
        backend = mod.InMemoryBackend()
        assert isinstance(backend, mod.FeastBackend)

    def test_sqlite_satisfies_protocol(self):
        mod = _import_feast()
        backend = mod.SQLiteBackend(db_path=":memory:")
        assert isinstance(backend, mod.FeastBackend)
        backend.close()

    def test_protocol_methods_raise_not_implemented(self):
        """Direct Protocol instantiation should raise — methods are not callable."""
        mod = _import_feast()
        # Protocol is @runtime_checkable — it cannot be instantiated directly;
        # but all concrete classes must override all methods.
        with pytest.raises(TypeError):
            mod.FeastBackend()  # type: ignore[abstract]


# ── InMemoryBackend ─────────────────────────────────────────────────────────


class TestInMemoryBackend:
    """Unit tests for InMemoryBackend."""

    def setup_method(self):
        mod = _import_feast()
        self.mod = mod
        self.backend = mod.InMemoryBackend()

    def teardown_method(self):
        self.backend.close()

    def test_write_and_read_round_trip(self):
        self.backend.write("view_a", "user:1", {"age": 30, "tier": "gold"})
        result = self.backend.read("view_a", "user:1")
        assert result is not None, "result must be initialized"
        assert result["age"] == 30, "Result must not be empty"
        assert result["tier"] == "gold", "Result must not be empty"
        assert "__written_at" in result, "Result must not be empty"

    def test_read_missing_returns_none(self):
        assert self.backend.read("view_z", "nobody") is None

    def test_overwrite_replaces_value(self):
        self.backend.write("v", "k", {"x": 1})
        self.backend.write("v", "k", {"x": 99})
        assert self.backend.read("v", "k")["x"] == 99

    def test_delete_removes_entry(self):
        self.backend.write("v", "k", {"x": 1})
        self.backend.delete("v", "k")
        assert self.backend.read("v", "k") is None

    def test_delete_nonexistent_is_noop(self):
        self.backend.delete("v", "ghost")  # should not raise

    def test_list_views_returns_written_views(self):
        self.backend.write("view_x", "e1", {"f": 1})
        self.backend.write("view_y", "e2", {"f": 2})
        views = self.backend.list_views()
        assert "view_x" in views, "Condition must be true"
        assert "view_y" in views, "Condition must be true"

    def test_list_views_empty_initially(self):
        assert self.backend.list_views() == [], "Condition must be true"

    def test_thread_safety_concurrent_writes(self):
        """Multiple threads writing to different keys must not clobber each other."""
        import threading

        errors: list[Exception] = []

        def writer(i: int) -> None:
            try:
                self.backend.write("view", f"key:{i}", {"val": i})
            except (IOError, OSError) as exc:
                errors.append(exc)

        threads = [threading.Thread(target=writer, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, "Error should be raised or set"
        for i in range(20):
            r = self.backend.read("view", f"key:{i}")
            assert r is not None, "r must be initialized"
            assert r["val"] == i, "Condition must be true"


# ── SQLiteBackend ───────────────────────────────────────────────────────────


class TestSQLiteBackend:
    """Unit tests for SQLiteBackend."""

    def setup_method(self):
        mod = _import_feast()
        self.mod = mod
        self.backend = mod.SQLiteBackend(db_path=":memory:")

    def teardown_method(self):
        self.backend.close()

    def test_write_and_read_round_trip(self):
        self.backend.write("profile", "u:1", {"plan": "pro", "credits": 500})
        r = self.backend.read("profile", "u:1")
        assert r is not None, "r must be initialized"
        assert r["plan"] == "pro", "Condition must be true"
        assert r["credits"] == 500, "Condition must be true"

    def test_read_missing_returns_none(self):
        assert self.backend.read("nope", "nobody") is None

    def test_upsert_replaces_existing(self):
        self.backend.write("v", "k", {"score": 1})
        self.backend.write("v", "k", {"score": 2})
        assert self.backend.read("v", "k")["score"] == 2

    def test_delete_removes_entry(self):
        self.backend.write("v", "k", {"x": 1})
        self.backend.delete("v", "k")
        assert self.backend.read("v", "k") is None

    def test_delete_nonexistent_is_noop(self):
        self.backend.delete("v", "ghost")

    def test_list_views_distinct(self):
        self.backend.write("a", "e1", {})
        self.backend.write("a", "e2", {})
        self.backend.write("b", "e1", {})
        views = self.backend.list_views()
        assert sorted(views) == ["a", "b"]

    def test_persistent_db_file(self, tmp_path):
        db_path = tmp_path / "test.db"
        mod = _import_feast()
        b = mod.SQLiteBackend(db_path=db_path)
        b.write("v", "k", {"n": 42})
        b.close()
        assert db_path.exists(), "Condition must be true"

        # Re-open and verify data persisted
        b2 = mod.SQLiteBackend(db_path=db_path)
        assert b2.read("v", "k")["n"] == 42
        b2.close()

    def test_thread_safety(self):
        import threading

        errors: list[Exception] = []

        def writer(i: int) -> None:
            try:
                self.backend.write("view", f"key:{i}", {"val": i})
            except (IOError, OSError) as exc:
                errors.append(exc)

        threads = [threading.Thread(target=writer, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert not errors, "Error should be raised or set"


# ── RedisBackend (mocked) ───────────────────────────────────────────────────


@pytest.fixture
def mock_redis_backend():
    """Pytest fixture: returns (backend, mock_redis) with a mocked Redis client."""
    mod = _import_feast()
    mock_redis = MagicMock()
    mock_redis.get.return_value = None
    # scan() returns (cursor, keys); cursor=0 means iteration complete.
    mock_redis.scan.return_value = (0, [])

    with patch.dict(
        "sys.modules", {"redis": MagicMock(from_url=MagicMock(return_value=mock_redis))}
    ):
        backend = mod.RedisBackend(url="redis://localhost:6379/0")
    backend._redis = mock_redis
    return backend, mock_redis, mod


class TestRedisBackend:
    """Unit tests for RedisBackend using a mocked Redis client."""

    def test_write_calls_redis_set(self, mock_redis_backend):
        backend, mock_redis, _ = mock_redis_backend
        backend.write("view", "key:1", {"x": 10})
        assert mock_redis.set.called or mock_redis.setex.called, "Condition must be true"

    def test_write_with_ttl_calls_setex(self):
        mod = _import_feast()
        mock_redis = MagicMock()
        mock_redis.scan.return_value = (0, [])
        with patch.dict(
            "sys.modules", {"redis": MagicMock(from_url=MagicMock(return_value=mock_redis))}
        ):
            backend = mod.RedisBackend(url="redis://localhost:6379/0", ttl=60)
        backend._redis = mock_redis
        backend.write("view", "key:1", {"x": 10})
        mock_redis.setex.assert_called_once()
        assert mock_redis.setex.call_args[0][1] == 60, "Condition must be true"

    def test_read_missing_returns_none(self, mock_redis_backend):
        backend, mock_redis, _ = mock_redis_backend
        mock_redis.get.return_value = None
        assert backend.read("view", "missing") is None

    def test_read_returns_deserialized_data(self, mock_redis_backend):
        backend, mock_redis, _ = mock_redis_backend
        payload = json.dumps({"age": 30, "__written_at": "2026-03-07T00:00:00Z"})
        mock_redis.get.return_value = payload
        result = backend.read("view", "key:1")
        assert result["age"] == 30, "Result must not be empty"

    def test_delete_calls_redis_delete(self, mock_redis_backend):
        backend, mock_redis, _ = mock_redis_backend
        backend.delete("view", "key:1")
        mock_redis.delete.assert_called_once()

    def test_list_views_parses_keys(self, mock_redis_backend):
        backend, mock_redis, _ = mock_redis_backend
        # Keys format: {view_name}:{entity_key}. rsplit(":", 1) extracts view_name.
        # SCAN returns (cursor=0, keys) — cursor=0 means scan complete.
        mock_redis.scan.return_value = (0, ["profile:1", "profile:2", "orders:1"])
        views = backend.list_views()
        assert "profile" in views, "Condition must be true"
        assert "orders" in views, "Condition must be true"

    def test_close_calls_redis_close(self, mock_redis_backend):
        backend, mock_redis, _ = mock_redis_backend
        backend.close()
        mock_redis.close.assert_called_once()

    def test_missing_redis_package_raises_import_error(self):
        mod = _import_feast()
        import sys

        real_redis = sys.modules.pop("redis", None)
        try:
            with pytest.raises(ImportError, match="RedisBackend requires"):
                mod.RedisBackend()
        finally:
            if real_redis is not None:
                sys.modules["redis"] = real_redis


# ── create_backend() factory ────────────────────────────────────────────────


class TestCreateBackend:
    """Tests for the create_backend() factory function."""

    def test_memory_backend(self):
        mod = _import_feast()
        b = mod.create_backend("memory")
        assert isinstance(b, mod.InMemoryBackend)

    def test_sqlite_backend_default_memory(self):
        mod = _import_feast()
        b = mod.create_backend("sqlite")
        assert isinstance(b, mod.SQLiteBackend)
        b.close()

    def test_sqlite_backend_custom_path(self, tmp_path):
        mod = _import_feast()
        b = mod.create_backend("sqlite", db_path=tmp_path / "feat.db")
        assert isinstance(b, mod.SQLiteBackend)
        b.close()

    def test_unknown_backend_raises_value_error(self):
        mod = _import_feast()
        with pytest.raises(ValueError, match="cassandra"):
            mod.create_backend("cassandra")

    def test_all_supported_types_in_error_message(self):
        mod = _import_feast()
        with pytest.raises(ValueError) as exc_info:
            mod.create_backend("bad")
        msg = str(exc_info.value)
        assert "memory" in msg, "Condition must be true"
        assert "sqlite" in msg, "Condition must be true"
        assert "redis" in msg, "Condition must be true"
        assert "duckdb" in msg, "Condition must be true"

    def test_duckdb_backend(self):
        if importlib.util.find_spec("duckdb") is None:
            pytest.skip("duckdb not installed")
        mod = _import_feast()
        b = mod.create_backend("duckdb")
        assert isinstance(b, mod.DuckDBBackend)
        b.close()

    def test_duckdb_backend_custom_path(self, tmp_path):
        if importlib.util.find_spec("duckdb") is None:
            pytest.skip("duckdb not installed")
        mod = _import_feast()
        db_path = tmp_path / "offline.duckdb"
        b = mod.create_backend("duckdb", db_path=db_path)
        assert isinstance(b, mod.DuckDBBackend)
        b.close()


def _import_duckdb():
    """Skip the test if duckdb is not installed."""
    if importlib.util.find_spec("duckdb") is None:
        pytest.skip("duckdb or feast_compat not importable")

    return pytest.importorskip(
        "codex_ml.features.feast_compat",
        reason="duckdb or feast_compat not importable",
    )


# ── DuckDB Backend ──────────────────────────────────────────────────────────


class TestDuckDBBackend:
    """Tests for DuckDBBackend — offline materialization via DuckDB + Arrow."""

    def test_write_and_read(self):
        mod = _import_duckdb()
        b = mod.DuckDBBackend()
        b.write("views", "k1", {"x": 1, "y": "hello"})
        result = b.read("views", "k1")
        assert result is not None, "result must be initialized"
        assert result["x"] == 1, "Result must not be empty"
        assert result["y"] == "hello", "Result must not be empty"
        b.close()

    def test_read_missing_returns_none(self):
        mod = _import_duckdb()
        b = mod.DuckDBBackend()
        assert b.read("views", "nonexistent") is None
        b.close()

    def test_upsert_overwrites(self):
        mod = _import_duckdb()
        b = mod.DuckDBBackend()
        b.write("views", "k1", {"x": 1})
        b.write("views", "k1", {"x": 99})
        assert b.read("views", "k1")["x"] == 99
        b.close()

    def test_delete(self):
        mod = _import_duckdb()
        b = mod.DuckDBBackend()
        b.write("views", "k1", {"x": 1})
        b.delete("views", "k1")
        assert b.read("views", "k1") is None
        b.close()

    def test_list_views(self):
        mod = _import_duckdb()
        b = mod.DuckDBBackend()
        b.write("view_a", "k1", {"x": 1})
        b.write("view_b", "k2", {"y": 2})
        views = b.list_views()
        assert "view_a" in views, "Condition must be true"
        assert "view_b" in views, "Condition must be true"
        b.close()

    def test_list_views_empty(self):
        mod = _import_duckdb()
        b = mod.DuckDBBackend()
        assert b.list_views() == [], "Condition must be true"
        b.close()

    def test_row_count(self):
        mod = _import_duckdb()
        b = mod.DuckDBBackend()
        b.write("v", "k1", {"x": 1})
        b.write("v", "k2", {"x": 2})
        assert b.row_count("v") == 2, "Count must be greater than zero"
        b.close()

    def test_row_count_empty_view(self):
        mod = _import_duckdb()
        b = mod.DuckDBBackend()
        assert b.row_count("empty_view") == 0, "Count must be greater than zero"
        b.close()

    def test_satisfies_feast_backend_protocol(self):
        mod = _import_duckdb()
        b = mod.DuckDBBackend()
        assert isinstance(b, mod.FeastBackend)
        b.close()

    def test_materialize_to_parquet(self, tmp_path):
        mod = _import_duckdb()
        b = mod.DuckDBBackend()
        b.write("feats", "u1", {"age": 25, "score": 0.8})
        b.write("feats", "u2", {"age": 40, "score": 0.6})
        out = tmp_path / "feats.parquet"
        result_path = b.materialize_to_parquet("feats", out)
        assert result_path == out, "Result must not be empty"
        assert out.exists(), "Condition must be true"
        import pyarrow.parquet as pq

        table = pq.read_table(str(out))
        assert table.num_rows == 2, "num_rows is not valid"
        b.close()

    def test_materialize_creates_parent_dirs(self, tmp_path):
        mod = _import_duckdb()
        b = mod.DuckDBBackend()
        b.write("feats", "u1", {"val": 1})
        out = tmp_path / "nested" / "dir" / "feats.parquet"
        b.materialize_to_parquet("feats", out)
        assert out.exists(), "Condition must be true"
        b.close()

    def test_thread_safety_concurrent_writes(self):
        import threading

        mod = _import_duckdb()
        b = mod.DuckDBBackend()
        errors: list[Exception] = []

        def write_batch(start: int) -> None:
            for i in range(start, start + 5):
                try:
                    b.write("v", f"key_{i}", {"val": i})
                except (IOError, OSError) as exc:
                    errors.append(exc)

        threads = [threading.Thread(target=write_batch, args=(i * 5,)) for i in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Thread errors: {errors}"
        assert b.row_count("v") == 20, "Count must be greater than zero"
        b.close()

    def test_missing_duckdb_package_raises_import_error(self):
        mod = _import_duckdb()
        with patch.dict("sys.modules", {"duckdb": None}):
            with pytest.raises(ImportError, match="duckdb"):
                mod.DuckDBBackend()

    def test_custom_table_prefix(self):
        mod = _import_duckdb()
        b = mod.DuckDBBackend(table_prefix="_custom_")
        b.write("myview", "k1", {"a": 1})
        views = b.list_views()
        assert "myview" in views, "Condition must be true"
        b.close()

    def test_persistence_across_close_reopen(self, tmp_path):
        mod = _import_duckdb()
        db_path = tmp_path / "persist.duckdb"
        b1 = mod.DuckDBBackend(db_path=db_path)
        b1.write("v", "k1", {"stored": True})
        b1.close()
        b2 = mod.DuckDBBackend(db_path=db_path)
        result = b2.read("v", "k1")
        assert result is not None, "result must be initialized"
        assert result["stored"] is True, "Result must not be empty"
        b2.close()

    def test_materialize_to_arrow_ipc(self, tmp_path):
        """Arrow IPC export produces a valid file readable by pyarrow."""
        pytest.importorskip("pyarrow")
        mod = _import_duckdb()
        b = mod.DuckDBBackend()
        b.write("feats", "u1", {"age": 25, "score": 0.8})
        b.write("feats", "u2", {"age": 40, "score": 0.6})
        out = tmp_path / "feats.arrow"
        result_path = b.materialize_to_arrow_ipc("feats", out)
        assert result_path == out, "Result must not be empty"
        assert out.exists(), "Condition must be true"
        import pyarrow.ipc as pa_ipc

        reader = pa_ipc.open_file(str(out))
        table = reader.read_all()
        assert table.num_rows == 2, "num_rows is not valid"
        b.close()

    def test_materialize_to_arrow_ipc_creates_parent_dirs(self, tmp_path):
        """Arrow IPC export creates missing parent directories."""
        pytest.importorskip("pyarrow")
        mod = _import_duckdb()
        b = mod.DuckDBBackend()
        b.write("feats", "u1", {"val": 99})
        out = tmp_path / "deep" / "nested" / "feats.ipc"
        b.materialize_to_arrow_ipc("feats", out)
        assert out.exists(), "Condition must be true"
        b.close()

    def test_materialize_to_arrow_ipc_no_pyarrow(self, tmp_path, monkeypatch):
        """materialize_to_arrow_ipc raises ImportError when pyarrow is absent."""
        mod = _import_duckdb()
        import sys

        monkeypatch.setitem(sys.modules, "pyarrow", None)
        monkeypatch.setitem(sys.modules, "pyarrow.ipc", None)
        b = mod.DuckDBBackend()
        b.write("feats", "u1", {"val": 1})
        with pytest.raises(ImportError, match="pyarrow"):
            b.materialize_to_arrow_ipc("feats", tmp_path / "out.arrow")
        b.close()
