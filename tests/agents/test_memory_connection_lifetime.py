"""SQLite connections must close without relying on garbage collection."""

import sqlite3
from concurrent.futures import ThreadPoolExecutor
from threading import Event

import pytest
from agents.agent_memory import AgentMemory


def test_memory_operations_close_owned_connections(tmp_path, monkeypatch):
    opened = []
    connect = sqlite3.connect

    def tracked_connect(*args, **kwargs):
        connection = connect(*args, **kwargs)
        opened.append(connection)
        return connection

    with monkeypatch.context() as context:
        context.setattr(sqlite3, "connect", tracked_connect)
        memory = AgentMemory(db_path=tmp_path / "memory.db")
        memory.store_memory({"memory_id": "saved", "content": "value"})
        assert memory.retrieve_content("saved") == "value"
        assert memory.retrieve_memory("saved").content == "value"
        assert memory.retrieve_memory("missing") is None
        assert len(memory.search_memories(category="fact")) == 1
        assert memory.get_memory_stats()["total_memories"] == 1
        memory.clear()
        assert memory.retrieve_memory("saved") is None

    assert len(opened) >= 9
    for connection in opened:
        with pytest.raises(sqlite3.ProgrammingError, match="closed"):
            connection.execute("SELECT 1")


def test_failed_write_rolls_back_and_closes_connection(tmp_path, monkeypatch):
    memory = AgentMemory(db_path=tmp_path / "memory.db")
    connect = sqlite3.connect
    connection = connect(memory.db_path)
    with monkeypatch.context() as context:
        context.setattr(sqlite3, "connect", lambda *args, **kwargs: connection)
        with pytest.raises(sqlite3.IntegrityError):
            memory.store_memory({"memory_id": "invalid", "category": None})

    with pytest.raises(sqlite3.ProgrammingError, match="closed"):
        connection.execute("SELECT 1")
    memory.store_memory({"memory_id": "valid", "content": "committed"})
    assert memory.retrieve_content("valid") == "committed"


def test_shared_memory_serializes_transactions_before_connecting(tmp_path, monkeypatch):
    memory = AgentMemory(db_path=tmp_path / "concurrent.db")
    connect = sqlite3.connect
    first_inserted = Event()
    release_first = Event()
    second_started = Event()
    second_connected = Event()

    class HeldWriteConnection(sqlite3.Connection):
        def execute(self, sql, parameters=()):
            cursor = super().execute(sql, parameters)
            if sql.lstrip().startswith("INSERT") and parameters[0] == "first":
                first_inserted.set()
                assert release_first.wait(5), "First transaction was not released"
            return cursor

    def tracked_connect(*args, **kwargs):
        if second_started.is_set():
            second_connected.set()
        return connect(*args, **kwargs, timeout=0.01, factory=HeldWriteConnection)

    def second_write():
        second_started.set()
        memory.store_memory(memory_id="second", content="value")

    with monkeypatch.context() as context:
        context.setattr(sqlite3, "connect", tracked_connect)
        with ThreadPoolExecutor(max_workers=2) as executor:
            first = executor.submit(memory.store_memory, memory_id="first", content="value")
            try:
                assert first_inserted.wait(5)
                second = executor.submit(second_write)
                assert second_started.wait(5)
                assert not second_connected.wait(0.1)
            finally:
                release_first.set()
            first.result(timeout=5)
            second.result(timeout=5)

    assert memory.get_memory_stats()["total_memories"] == 2
