import time


def test_rotation(tmp_path, monkeypatch):
    from codex_ml.utils import error_log

    monkeypatch.setattr(time, "time", lambda: 0)
    p = tmp_path / "log.txt"
    error_log.log("x", path=p)
    monkeypatch.setattr(time, "time", lambda: 10**9)
    error_log.log("y", path=p)
    assert p.exists()

