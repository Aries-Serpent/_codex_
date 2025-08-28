import json, types
from pathlib import Path

SAMPLE = {"runners": [
    {"id": 1, "name": "r1", "status": "online"},
    {"id": 2, "name": "r2", "status": "offline"},
]}

def test_parse_offline(tmp_path, monkeypatch):
    import tools.runner_doctor as rd  # type: ignore

    def fake_req(path, token, method="GET"):
        assert path.startswith("/repos/")
        return SAMPLE

    monkeypatch.setattr(rd, "_req", fake_req)
    out = rd.list_runners("token")
    assert any(r["status"] == "offline" for r in out)
