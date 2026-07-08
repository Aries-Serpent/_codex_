"""
Test Mlflow Init

Test module for mlflow init.
"""

from __future__ import annotations

import types

import pytest

from codex_ml.tracking import mlflow_utils


class _DummyRun:
    def __init__(self) -> None:
        self.info = types.SimpleNamespace(run_id="run-1")
        self.data = types.SimpleNamespace(tags={})


class _DummyMlflow:
    def __init__(self) -> None:
        self._active = None

    def start_run(self, run_name=None, **kwargs):
        self._active = _DummyRun()
        return self._active

    def set_tag(self, key: str, value: str) -> None:
        if self._active is None:
            raise RuntimeError("no active run")
        self._active.data.tags[key] = value

    def active_run(self):
        return self._active

    def get_run(self, run_id: str):
        assert self._active is not None, "_active must be initialized"
        assert run_id == self._active.info.run_id, "run_id is not valid"
        return self._active

    def end_run(self):
        self._active = None


@pytest.fixture
def dummy_mlflow(monkeypatch):
    fake = _DummyMlflow()
    monkeypatch.setattr(mlflow_utils, "_mlf", fake, raising=False)
    monkeypatch.setattr(mlflow_utils, "_HAS_MLFLOW", True, raising=False)
    monkeypatch.setattr(mlflow_utils, "_ensure_mlflow_available", lambda: None)
    monkeypatch.setattr(mlflow_utils, "current_commit_hash", lambda: "deadbeefcafebabe")
    return fake


def test_init_run_sets_tags(dummy_mlflow):
    run = mlflow_utils.init_run(run_name="test", config={"alpha": 1})
    assert run is dummy_mlflow.active_run(), "run is not valid"
    tags = dummy_mlflow.active_run().data.tags
    assert tags["git_commit"] == "deadbee", "Condition must be true"
    assert "config_hash" in tags, "Condition must be true"

    dummy_mlflow.end_run()
