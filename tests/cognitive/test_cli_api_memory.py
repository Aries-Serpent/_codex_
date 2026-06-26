"""
Tests for cli_api_server memory endpoints (Sprint 11 / Phase 5).

Covers:
- SQLiteMemory.retrieve() access_count increment
- POST /api/memory/consolidate endpoint
- GET /api/memory/state endpoint
- GET /api/memory/search endpoint
- memory-sync-agent and telemetry-classifier-agent registry readiness
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

fastapi = pytest.importorskip("fastapi")
pytest.importorskip("fastapi.testclient")
httpx = pytest.importorskip("httpx")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@pytest.fixture()
def server_app(tmp_path: Path):
    """
    Import cli_api_server with a patched DB path so we get an isolated DB
    for each test without touching the real ~/.codex/cli_history.db.
    """
    db_path = str(tmp_path / "cli_history.db")
    master_key = "test-master-key-sprint11"

    env_overrides = {
        "CODEX_DB_PATH": db_path,
        "CODEX_MASTER_KEY": master_key,
        "CODEX_BACKUP_KEY": "",
        "CODEX_MEMORY_CAPACITY": "100",
        "CODEX_STM_HOT_THRESHOLD": "3",
        "CODEX_HOT_ENTRIES_LIMIT": "50",
    }

    # Re-import the module with patched environment so _DB_PATH is correct.
    import importlib
    import sys

    with patch.dict(os.environ, env_overrides):
        # Remove cached module so env vars are picked up fresh
        for mod_key in list(sys.modules.keys()):
            if "cli_api_server" in mod_key:
                del sys.modules[mod_key]

        import cognitive_app.src.server.cli_api_server as srv

        importlib.reload(srv)

        yield srv, master_key, db_path


@pytest.fixture()
def client(server_app):
    from fastapi.testclient import TestClient

    srv, master_key, _db_path = server_app
    return TestClient(srv.app), master_key, srv


# ---------------------------------------------------------------------------
# SQLiteMemory unit tests
# ---------------------------------------------------------------------------


class TestSQLiteMemoryRetrieve:
    """Unit tests for SQLiteMemory — specifically the access_count increment."""

    def test_retrieve_increments_access_count(self, server_app):
        """retrieve() must increment access_count each time it is called."""
        srv, _key, _db_path = server_app
        mem = srv.SQLiteMemory()

        # Store an entry
        mem.store("k1", {"val": 42})

        # Retrieve once
        result = mem.retrieve("k1")
        assert result == {"val": 42}, "Result must not be empty"

        # Check DB: access_count should be 1
        row = srv._db.execute(
            "SELECT access_count FROM stm_entries WHERE key = ?", ("k1",)
        ).fetchone()
        assert row is not None, "row must be initialized"
        assert row["access_count"] == 1, "Count must be greater than zero"

    def test_retrieve_increments_on_each_call(self, server_app):
        """access_count must accumulate across multiple retrieve() calls."""
        srv, _key, _db_path = server_app
        mem = srv.SQLiteMemory()
        mem.store("k2", "hello")

        for _ in range(5):
            mem.retrieve("k2")

        row = srv._db.execute(
            "SELECT access_count FROM stm_entries WHERE key = ?", ("k2",)
        ).fetchone()
        assert row["access_count"] == 5, "Count must be greater than zero"

    def test_retrieve_missing_key_returns_none(self, server_app):
        """retrieve() on a non-existent key must return None without error."""
        srv, _key, _db_path = server_app
        mem = srv.SQLiteMemory()
        assert mem.retrieve("no_such_key") is None, "Condition must be true"

    def test_retrieve_does_not_increment_for_missing_key(self, server_app):
        """No DB write should occur when the key does not exist."""
        srv, _key, _db_path = server_app
        mem = srv.SQLiteMemory()
        mem.retrieve("ghost")
        count = srv._db.execute("SELECT COUNT(*) FROM stm_entries").fetchone()[0]
        assert count == 0, "Count must be greater than zero"

    def test_search_executes_under_db_lock(self, server_app, monkeypatch):
        """search() must acquire the shared DB lock before querying."""
        srv, _key, _db_path = server_app

        class _RecordingLock:
            entered = False
            exited = False

            def __enter__(self):
                self.entered = True
                return self

            def __exit__(self, exc_type, exc, tb):
                self.exited = True
                return False

        class _FakeDB:
            params = None

            def execute(self, _sql, params):
                self.params = params

                class _Cursor:
                    @staticmethod
                    def fetchall():
                        return [{"key": "k1", "value": '{"value": 1}'}]

                return _Cursor()

        lock = _RecordingLock()
        fake_db = _FakeDB()
        monkeypatch.setattr(srv, "_db_lock", lock)
        monkeypatch.setattr(srv, "_db", fake_db)

        result = srv.SQLiteMemory().search({"text": "value"}, limit=3)

        assert lock.entered is True, "entered is not valid"
        assert lock.exited is True, "exited is not valid"
        assert fake_db.params == ("%value%", 3)
        assert result == [("k1", {"value": 1})]


# ---------------------------------------------------------------------------
# POST /api/memory/consolidate endpoint tests
# ---------------------------------------------------------------------------


class TestMemoryConsolidateEndpoint:
    """Tests for the Sprint 11 POST /api/memory/consolidate endpoint."""

    def _auth_headers(self, key: str) -> dict:
        return {"Authorization": f"Bearer {key}"}

    def test_consolidate_requires_auth(self, client):
        tc, _master_key, _srv = client
        resp = tc.post("/api/memory/consolidate")
        assert resp.status_code == 401, "status_code is not valid"

    def test_consolidate_empty_db_returns_zeros(self, client):
        """Consolidate on an empty DB must return 0s without error."""
        tc, master_key, _srv = client
        resp = tc.post(
            "/api/memory/consolidate",
            headers=self._auth_headers(master_key),
        )
        assert resp.status_code == 200, "status_code is not valid"
        body = resp.json()
        assert body["consolidated"] == 0, "Condition must be true"
        assert body["pruned"] == 0, "Condition must be true"
        assert "error" not in body, "Error should be raised or set"

    def test_consolidate_promotes_hot_entries(self, client):
        """Hot STM entries (access_count >= threshold) must be promoted to LTM."""
        tc, master_key, srv = client
        mem = srv.SQLiteMemory()

        # Store entries and simulate hot access
        mem.store("hot1", {"data": "hot1"})
        mem.store("hot2", {"data": "hot2"})
        mem.store("cold", {"data": "cold"})

        # Make hot1 and hot2 hot (access_count >= 3)
        for _ in range(3):
            mem.retrieve("hot1")
            mem.retrieve("hot2")
        # cold stays at 0

        resp = tc.post(
            "/api/memory/consolidate",
            headers=self._auth_headers(master_key),
        )
        assert resp.status_code == 200, "status_code is not valid"
        body = resp.json()
        assert body["consolidated"] == 2, "Condition must be true"
        assert "error" not in body, "Error should be raised or set"

        # hot1 and hot2 must have been removed from STM
        remaining_stm = srv._db.execute("SELECT key FROM stm_entries").fetchall()
        remaining_keys = {r["key"] for r in remaining_stm}
        assert "hot1" not in remaining_keys, "Condition must be true"
        assert "hot2" not in remaining_keys, "Condition must be true"
        assert "cold" in remaining_keys, "Condition must be true"

        # hot1 and hot2 must be in LTM
        ltm_keys = {r["key"] for r in srv._db.execute("SELECT key FROM ltm_entries").fetchall()}
        assert "hot1" in ltm_keys, "Condition must be true"
        assert "hot2" in ltm_keys, "Condition must be true"

    def test_consolidate_confidence_calculation(self, client):
        """confidence = min(1.0, access_count / 10) must be written to LTM."""
        tc, master_key, srv = client
        mem = srv.SQLiteMemory()
        mem.store("conf_test", {"x": 1})

        # 5 retrievals → confidence = 0.5
        for _ in range(5):
            mem.retrieve("conf_test")

        tc.post(
            "/api/memory/consolidate",
            headers=self._auth_headers(master_key),
        )

        ltm_row = srv._db.execute(
            "SELECT confidence FROM ltm_entries WHERE key = ?", ("conf_test",)
        ).fetchone()
        assert ltm_row is not None, "ltm_row must be initialized"
        assert abs(ltm_row["confidence"] - 0.5) < 0.01, "Condition must be true"

    def test_consolidate_returns_counts(self, client):
        """Response must include stm_count and ltm_count."""
        tc, master_key, srv = client
        mem = srv.SQLiteMemory()
        mem.store("item_a", "a")
        for _ in range(3):
            mem.retrieve("item_a")

        resp = tc.post(
            "/api/memory/consolidate",
            headers=self._auth_headers(master_key),
        )
        body = resp.json()
        assert "stm_count" in body, "Count must be greater than zero"
        assert "ltm_count" in body, "Count must be greater than zero"
        assert "timestamp" in body, "Condition must be true"
        assert body["ltm_count"] >= 1, "Value must be greater than zero"

    def test_consolidate_wrong_token_rejected(self, client):
        """A wrong bearer token must receive 401."""
        tc, _master_key, _srv = client
        resp = tc.post(
            "/api/memory/consolidate",
            headers=self._auth_headers("wrong-token"),
        )
        assert resp.status_code == 401, "status_code is not valid"


# ---------------------------------------------------------------------------
# GET /api/memory/state (existing endpoint — verify access_count is surfaced)
# ---------------------------------------------------------------------------


class TestMemoryStateEndpoint:
    def _auth_headers(self, key: str) -> dict:
        return {"Authorization": f"Bearer {key}"}

    def test_state_requires_auth(self, client):
        tc, _key, _srv = client
        resp = tc.get("/api/memory/state")
        assert resp.status_code == 401, "status_code is not valid"

    def test_state_returns_counts(self, client):
        tc, master_key, srv = client
        mem = srv.SQLiteMemory()
        mem.store("s1", 1)
        mem.store("s2", 2)

        resp = tc.get(
            "/api/memory/state",
            headers=self._auth_headers(master_key),
        )
        assert resp.status_code == 200, "status_code is not valid"
        body = resp.json()
        assert body["stm_count"] >= 2, "Value must be greater than zero"
        assert "ltm_count" in body, "Count must be greater than zero"
        assert "capacity" in body, "Condition must be true"
        assert "compression_rate" in body, "Condition must be true"

    def test_cache_hit_rate_zero_when_no_retrievals(self, client):
        """cache_hit_rate must be 0.0 when no entries have been retrieved (access_count=0)."""
        tc, master_key, srv = client
        mem = srv.SQLiteMemory()
        mem.store("cold1", "x")
        mem.store("cold2", "y")

        resp = tc.get(
            "/api/memory/state",
            headers=self._auth_headers(master_key),
        )
        assert resp.status_code == 200, "status_code is not valid"
        body = resp.json()
        assert body["stm_count"] == 2, "Count must be greater than zero"
        assert body["cache_hit_rate"] == 0.0, "Condition must be true"

    def test_cache_hit_rate_increases_after_retrieve(self, client):
        """cache_hit_rate must reflect warm entries (access_count >= 1)."""
        tc, master_key, srv = client
        mem = srv.SQLiteMemory()
        mem.store("warm", "w")
        mem.store("cold", "c")

        # Retrieve one entry — makes it warm
        mem.retrieve("warm")

        resp = tc.get(
            "/api/memory/state",
            headers=self._auth_headers(master_key),
        )
        assert resp.status_code == 200, "status_code is not valid"
        body = resp.json()
        # 1 of 2 entries is warm → rate must be exactly 0.5
        assert body["stm_count"] == 2, "Count must be greater than zero"
        assert body["cache_hit_rate"] == 0.5, "Condition must be true"

    def test_cache_hit_rate_is_one_when_all_warm(self, client):
        """cache_hit_rate == 1.0 when every STM entry has been retrieved at least once."""
        tc, master_key, srv = client
        mem = srv.SQLiteMemory()
        mem.store("e1", 1)
        mem.store("e2", 2)
        mem.retrieve("e1")
        mem.retrieve("e2")

        resp = tc.get(
            "/api/memory/state",
            headers=self._auth_headers(master_key),
        )
        assert resp.status_code == 200, "status_code is not valid"
        body = resp.json()
        assert body["cache_hit_rate"] == 1.0, "Condition must be true"


# ---------------------------------------------------------------------------
# Agent registry promotion checks (memory-sync-agent & telemetry-classifier)
# ---------------------------------------------------------------------------


class TestAgentRegistryReadiness:
    """Verify AGENT_REGISTRY.yaml is updated to production + has_tests: true."""

    @pytest.fixture(autouse=True)
    def registry_path(self):
        repo_root = Path(__file__).resolve().parents[2]
        self._registry = repo_root / ".github" / "agents" / "AGENT_REGISTRY.yaml"

    def _load_agents(self) -> list[dict[str, Any]]:
        """Parse AGENT_REGISTRY.yaml with PyYAML and return the list of agent dicts."""
        yaml = pytest.importorskip("yaml")
        data = yaml.safe_load(self._registry.read_text())
        # The registry is a mapping whose values may include lists of agent dicts.
        # Walk the top-level values to find a list containing dicts with an 'id' key.
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for v in data.values():
                if isinstance(v, list) and v and isinstance(v[0], dict) and "id" in v[0]:
                    return v
        return []

    def _get_agent(self, agent_id: str) -> dict[str, Any]:
        for agent in self._load_agents():
            if isinstance(agent, dict) and agent.get("id") == agent_id:
                return agent
        return {}

    def test_memory_sync_agent_is_production(self):
        agent = self._get_agent("memory-sync-agent")
        assert (agent.get("maturity") == "production", "Condition must be true"
        ), f"memory-sync-agent maturity should be 'production', got {agent.get('maturity')!r}"

    def test_memory_sync_agent_has_tests(self):
        agent = self._get_agent("memory-sync-agent")
        assert (agent.get("has_tests") is True, "Condition must be true"
        ), f"memory-sync-agent has_tests should be True, got {agent.get('has_tests')!r}"

    def test_telemetry_classifier_agent_is_production(self):
        agent = self._get_agent("telemetry-classifier-agent")
        assert (agent.get("maturity") == "production", "Condition must be true"
        ), f"telemetry-classifier-agent maturity should be 'production', got {agent.get('maturity')!r}"

    def test_telemetry_classifier_agent_has_tests(self):
        agent = self._get_agent("telemetry-classifier-agent")
        assert (agent.get("has_tests") is True, "Condition must be true"
        ), f"telemetry-classifier-agent has_tests should be True, got {agent.get('has_tests')!r}"


# ---------------------------------------------------------------------------
# .env.example check
# ---------------------------------------------------------------------------


class TestEnvExample:
    def test_codex_cli_api_url_in_env_example(self):
        env_example = Path(__file__).resolve().parents[2] / "cognitive_app" / ".env.example"
        content = env_example.read_text()
        assert ("CODEX_CLI_API_URL" in content, "Content must not be empty"
        ), "CODEX_CLI_API_URL must be documented in cognitive_app/.env.example"
