import importlib
from pathlib import Path


def test_repo_root_detection(monkeypatch):
    monkeypatch.setenv("REPO_IMPROVEMENT_DRY_RUN", "1")
    monkeypatch.delenv("CODEX_AUTO_RUN", raising=False)
    mod = importlib.reload(
        importlib.import_module("scripts.deep_research_task_process")
    )
    repo_root = Path(mod.REPO_ROOT)
    assert (repo_root / ".pre-commit-config.yaml").exists()
    assert (repo_root / "src" / "codex" / "logging").exists()
    assert (repo_root / ".git").exists()


def test_single_execution_guard(monkeypatch):
    monkeypatch.setenv("REPO_IMPROVEMENT_DRY_RUN", "1")
    monkeypatch.delenv("CODEX_AUTO_RUN", raising=False)
    mod = importlib.reload(
        importlib.import_module("scripts.deep_research_task_process")
    )

    calls = {"count": 0}

    def fake_run_all():
        calls["count"] += 1
        return 0

    monkeypatch.setattr(mod, "run_all", fake_run_all)

    mod._maybe_auto_run_on_import()
    assert calls["count"] == 0

    monkeypatch.setenv("CODEX_AUTO_RUN", "1")
    mod._maybe_auto_run_on_import()
    assert calls["count"] == 1

    mod._maybe_auto_run_on_import()
    assert calls["count"] == 1
