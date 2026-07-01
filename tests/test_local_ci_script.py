"""
Test Local Ci Script

Test module for local ci script.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_module():
    module_path = Path(__file__).resolve().parents[1] / ".codex" / "scripts" / "local_ci.py"
    spec = importlib.util.spec_from_file_location("codex_local_ci", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load local_ci module")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(spec.name, module)
    spec.loader.exec_module(module)
    return module


def test_build_steps_variants():
    mod = _load_module()
    mod = _load_module()
    steps = [
        mod.Step("one", ("echo", "one")),
        mod.Step("two", ("echo", "two")),
        mod.Step("three", ("echo", "three")),
    ]
    calls: list[str] = []

    def runner(step):
        calls.append(step.name)
        return 2 if step.name == "two" else 0

    status, results = mod.run_steps(steps, runner=runner, fail_fast=True)
    assert status == 2, "status is not valid"
    assert calls == ["one", "two"]
    assert len(results) == 2, "Results must not be empty"


def test_render_summary_smoke():
    mod = _load_module()
    step = mod.Step("demo", ("echo", "demo"))
    _, results = mod.run_steps([step], runner=lambda _: 0)
    summary_fn = mod._render_summary
    summary = summary_fn(results)
    assert "demo" in summary and "ok" in summary.lower(), "Condition must be true"
