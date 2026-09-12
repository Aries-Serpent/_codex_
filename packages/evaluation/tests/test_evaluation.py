from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from codex_evaluation import (
    CodexMetricAdapter,
    EvaluationBatch,
    EvaluationError,
    EvaluationRunner,
    MetricRegistrationError,
    MetricRegistry,
)


def test_runner_produces_immutable_report() -> None:
    batch = EvaluationBatch(["yes", "no"], ["yes", "yes"], {"split": "test"})
    runner = EvaluationRunner({"accuracy": lambda predictions, references: 0.5})

    report = runner.evaluate(batch)

    assert report.sample_count == 2
    assert dict(report.metrics) == {"accuracy": 0.5}
    assert dict(report.metadata) == {"split": "test"}
    with pytest.raises(TypeError):
        report.metrics["accuracy"] = 1.0  # type: ignore[index]


def test_batch_rejects_unaligned_inputs() -> None:
    with pytest.raises(ValueError, match="same length"):
        EvaluationBatch([1], [])


def test_runner_rejects_non_finite_metric() -> None:
    runner = EvaluationRunner({"loss": lambda predictions, references: float("nan")})
    with pytest.raises(EvaluationError, match="non-finite"):
        runner.evaluate(EvaluationBatch([], []))


def test_registry_conflicts_are_explicit() -> None:
    registry = MetricRegistry()
    registry.register("score", lambda predictions, references: 1.0)
    with pytest.raises(MetricRegistrationError, match="already registered"):
        registry.register("score", lambda predictions, references: 0.0)
    assert list(registry) == ["score"]


def test_codex_adapter_is_lazy_and_injectable() -> None:
    loads: list[str] = []

    def loader(name: str):
        loads.append(name)
        return lambda predictions, references: 0.75

    metric = CodexMetricAdapter("accuracy", loader=loader)
    assert loads == []
    assert metric([1], [1]) == 0.75
    assert metric([0], [1]) == 0.75
    assert loads == ["accuracy"]


def test_import_does_not_load_heavy_dependencies() -> None:
    package_src = Path(__file__).parents[1] / "src"
    script = """
import json, sys
import codex_evaluation
print(json.dumps(sorted(name for name in ("torch", "transformers", "datasets", "peft")
                        if name in sys.modules)))
"""
    env = {**os.environ, "PYTHONPATH": str(package_src)}
    result = subprocess.run(
        [sys.executable, "-c", script],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    assert json.loads(result.stdout) == []
