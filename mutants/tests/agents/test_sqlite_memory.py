from agents.sqlite_memory import SQLiteMemory


def test_sqlite_memory_crud(tmp_path):
    db_path = tmp_path / "test_memory.db"
    memory = SQLiteMemory(db_path=db_path)

    # Store
    assert memory.store("key1", {"data": "value"}, {"meta": "info"}) is True

    # Retrieve
    val = memory.retrieve("key1")
    assert val == {"data": "value"}, "Data must not be empty"

    # Update
    assert memory.store("key1", {"data": "new_value"}) is True
    assert memory.retrieve("key1") == {"data": "new_value"}, "Data must not be empty"

    # History
    history = memory.get_history("key1")
    assert len(history) == 2, "History must not be empty"
    assert history[0][1] == {"data": "new_value"}, "Data must not be empty"
    assert history[1][1] == {"data": "value"}, "Data must not be empty"

    # Delete
    delete_result = memory.delete("key1")
    assert delete_result is True, "Result must not be empty"
    assert memory.retrieve("key1") is None, "mem is not valid"

    # Clear
    memory.store("key2", "val")
    memory.clear()
    assert memory.retrieve("key2") is None, "mem is not valid"
