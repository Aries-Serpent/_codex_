from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from codex_evaluation import (
    EvaluateMetricAdapter,
    HuggingFaceDatasetAdapter,
)


def test_dataset_adapter_is_lazy_and_injectable() -> None:
    calls: list[tuple[object, ...]] = []

    def loader(path, *, split, revision):
        calls.append((path, split, revision))
        return [
            {"prediction": "yes", "reference": "yes"},
            {"prediction": "no", "reference": "yes"},
        ]

    adapter = HuggingFaceDatasetAdapter(loader=loader)
    assert calls == []

    batch = adapter.load("owner/data", split="validation", revision="fixed")

    assert calls == [("owner/data", "validation", "fixed")]
    assert batch.predictions == ("yes", "no")
    assert batch.references == ("yes", "yes")
    assert dict(batch.metadata) == {"dataset": "owner/data", "split": "validation"}


def test_framework_adapter_is_lazy_and_has_scalar_parity() -> None:
    loads: list[str] = []

    class Accuracy:
        def compute(self, *, predictions, references):
            return {
                "accuracy": sum(left == right for left, right in zip(predictions, references))
                / len(predictions)
            }

    adapter = EvaluateMetricAdapter(
        "accuracy",
        loader=lambda name: loads.append(name) or Accuracy(),
    )
    assert loads == []
    assert adapter(["yes", "no"], ["yes", "yes"]) == 0.5
    assert adapter(["yes"], ["yes"]) == 1.0
    assert loads == ["accuracy"]


def test_optional_adapters_report_actionable_missing_dependency() -> None:
    package_src = Path(__file__).parents[1] / "src"
    script = """
import builtins
from codex_evaluation import EvaluateMetricAdapter, HuggingFaceDatasetAdapter

real_import = builtins.__import__
def blocked(name, *args, **kwargs):
    if name in {"datasets", "evaluate"}:
        raise ImportError(name)
    return real_import(name, *args, **kwargs)
builtins.__import__ = blocked

for operation, extra in (
    (lambda: HuggingFaceDatasetAdapter().load("owner/data"), "hf"),
    (lambda: EvaluateMetricAdapter("accuracy")([], []), "framework"),
):
    try:
        operation()
    except ImportError as error:
        assert extra in str(error)
    else:
        raise AssertionError(f"{extra} adapter did not fail")
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(package_src)},
    )
    assert result.returncode == 0, result.stderr


def test_base_import_still_does_not_load_optional_dependencies() -> None:
    package_src = Path(__file__).parents[1] / "src"
    script = """
import json, sys
import codex_evaluation
print(json.dumps(sorted(name for name in
    ("torch", "transformers", "datasets", "evaluate", "codex_ml")
    if name in sys.modules)))
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(package_src)},
    )
    assert json.loads(result.stdout) == []
