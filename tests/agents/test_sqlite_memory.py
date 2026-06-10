
from agents.sqlite_memory import SQLiteMemory


def test_sqlite_memory_crud(tmp_path):
    db_path = tmp_path / "test_memory.db"
    memory = SQLiteMemory(db_path=db_path)

    # Store
    assert memory.store("key1", {"data": "value"}, {"meta": "info"}) is True

    # Retrieve
    val = memory.retrieve("key1")
    assert val == {"data": "value"}

    # Update
    assert memory.store("key1", {"data": "new_value"}) is True
    assert memory.retrieve("key1") == {"data": "new_value"}

    # History
    history = memory.get_history("key1")
    assert len(history) == 2
    assert history[0][1] == {"data": "new_value"}
    assert history[1][1] == {"data": "value"}

    # Delete
    assert memory.delete("key1") is True
    assert memory.retrieve("key1") is None

    # Clear
    memory.store("key2", "val")
    memory.clear()
    assert memory.retrieve("key2") is None
