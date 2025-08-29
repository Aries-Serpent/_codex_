from __future__ import annotations

import importlib
import os
import threading
import time


def test_log_error_records(tmp_path, monkeypatch):
    mod = importlib.import_module("codex_ml.utils.error_log")
    monkeypatch.setattr(mod, "ERROR_PATH", tmp_path / "err.ndjson")
    mod.log_error("s", "e", "c")
    data = (tmp_path / "err.ndjson").read_text(encoding="utf-8").strip()
    assert "\"s\"" in data


def test_log_rotation_and_concurrency(tmp_path, monkeypatch):
    mod = importlib.import_module("codex_ml.utils.error_log")
    log = tmp_path / "log.txt"
    log.write_text("old", encoding="utf-8")
    old = time.time() - mod.ROTATE_AFTER - 1
    os.utime(log, (old, old))
    threads = [threading.Thread(target=lambda: mod.log("x\n", log)) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    rotated = list(tmp_path.glob("log.txt.*"))
    assert rotated and log.read_text(encoding="utf-8").count("x") == 5
