"""
Test Runner Doctor

Test module for runner doctor.
"""
import pytest
    import tools.runner_doctor as rd  # type: ignore

SAMPLE = {
    "runners": [
        {"id": 1, "name": "r1", "status": "online"},
        {"id": 2, "name": "r2", "status": "offline"},
    ]
}


def test_parse_offline(tmp_path, monkeypatch):

    def fake_req(path, token, method="GET"):
        assert path.startswith("/repos/"), "Condition must be true"
        return SAMPLE

    monkeypatch.setattr(rd, "_req", fake_req)
    out = rd.list_runners("token")
    assert any(r["status"] == "offline" for r in out), "Condition must be true"
