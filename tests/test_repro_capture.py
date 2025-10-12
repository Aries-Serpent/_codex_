from __future__ import annotations

import json
from pathlib import Path

import pytest

from codex_ml.utils.repro import capture_environment


@pytest.mark.infra
def test_capture_environment_writes_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TEST_SECRET_KEY", "value")
    capture_environment(tmp_path)
    pip_freeze = (tmp_path / "pip_freeze.txt").read_text(encoding="utf-8")
    env_vars = json.loads((tmp_path / "env_vars.json").read_text(encoding="utf-8"))
    assert pip_freeze
    assert env_vars["TEST_SECRET_KEY"] == "<redacted>"  # noqa: S105
