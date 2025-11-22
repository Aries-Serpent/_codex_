from codex_ml.training.unified_training import distributed_context


def test_distributed_context_env(monkeypatch):
    monkeypatch.setenv("WORLD_SIZE", "4")
    monkeypatch.setenv("RANK", "2")
    monkeypatch.setenv("LOCAL_RANK", "1")

    info = distributed_context()

    assert info["world_size"] == 4
    assert info["rank"] == 2
    assert info["local_rank"] == 1
