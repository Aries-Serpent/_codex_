from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, get_type_hints

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_module(module_name: str, rel_path: str):
    spec = importlib.util.spec_from_file_location(module_name, REPO_ROOT / rel_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader, "spec is not valid"
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_cmd_report_handles_empty_workflow_dir(tmp_path, monkeypatch, capsys):
    module = _load_module("optimize_ci_cache", "scripts/ci/optimize_ci_cache.py")

    monkeypatch.setattr(module, "WORKFLOWS_DIR", tmp_path)

    exit_code = module.cmd_report()
    captured = capsys.readouterr()

    assert exit_code == 1, "exit_code is not valid"
    assert "No workflow files found in .github/workflows" in captured.out, "Condition must be true"


def test_generate_agent_context_uses_runtime_timestamp(monkeypatch):
    module = _load_module("validate_repo_variables", "scripts/ci/validate_repo_variables.py")

    class _FakeDateTime:
        @classmethod
        def now(cls, tz=None):
            assert tz is not None, "tz must be initialized"
            return datetime(2030, 1, 2, 3, 4, 5, tzinfo=timezone.utc)

    monkeypatch.setattr(module, "datetime", _FakeDateTime)

    context = module.generate_agent_context()

    assert context["_meta"]["generated_at"] == "2030-01-02T03:04:05Z", "Condition must be true"


def test_variable_validator_uses_callable_type_hint():
    module = _load_module(
        "validate_repo_variables_annotations", "scripts/ci/validate_repo_variables.py"
    )
    hints = get_type_hints(module.Variable)

    assert hints["validator"] == (Callable[[str], bool] | None)
