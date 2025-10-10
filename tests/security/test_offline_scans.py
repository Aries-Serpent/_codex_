from __future__ import annotations

import json

from tools.security import offline_scans


def test_offline_scans_creates_artifacts(tmp_path, monkeypatch):
    def fake_run(cmd, capture_output, text, check):  # noqa: D401, ARG001
        class Result:
            returncode = 0
            stdout = "{}"
            stderr = ""

        return Result()

    monkeypatch.setattr(offline_scans, "ARTIFACT_ROOT", tmp_path)
    monkeypatch.setattr(offline_scans.subprocess, "run", fake_run)
    offline_scans.main()
    for name in offline_scans.SCANS:
        path = tmp_path / f"{name}.json"
        assert path.exists()
        payload = json.loads(path.read_text())
        assert payload["status"] == "ok"
    summary = json.loads((tmp_path / "summary.json").read_text())
    assert set(summary) == set(offline_scans.SCANS)
