"""Focused compatibility checks for Phase 2 standalone-package facades."""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_PACKAGE_SOURCES = [
    _ROOT / "packages" / "evaluation" / "src",
    _ROOT / "packages" / "lora" / "src",
    _ROOT / "packages" / "telemetry" / "src",
]


def _run_python(source: str, *, standalone: bool = True) -> subprocess.CompletedProcess[str]:
    paths = [str(_ROOT / "src")]
    if standalone:
        paths.extend(str(path) for path in _PACKAGE_SOURCES)
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(paths)
    return subprocess.run(
        [sys.executable, "-c", textwrap.dedent(source)],
        cwd=_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )


def test_evaluation_forwards_contracts_without_replacing_legacy_runner() -> None:
    result = _run_python(
        """
        import inspect
        import sys
        import types
        import warnings
        import codex_evaluation

        torch = types.ModuleType("torch")
        torch.utils = types.SimpleNamespace(
            data=types.SimpleNamespace(DataLoader=type("DataLoader", (), {}))
        )
        sys.modules["torch"] = torch

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", DeprecationWarning)
            import codex_ml.evaluation as legacy

        assert legacy.EvaluationBatch is codex_evaluation.EvaluationBatch
        assert legacy.EvaluationReport is codex_evaluation.EvaluationReport
        assert legacy.ScalarEvaluationRunner is codex_evaluation.EvaluationRunner
        assert legacy.EvaluationRunner is not codex_evaluation.EvaluationRunner
        assert "model" in inspect.signature(legacy.EvaluationRunner).parameters
        assert "metrics" in inspect.signature(
            codex_evaluation.EvaluationRunner
        ).parameters
        assert not [item for item in caught if item.category is DeprecationWarning]

        class Model:
            def predict(self, inputs):
                return inputs

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", DeprecationWarning)
            legacy.EvaluationRunner(Model(), [], [], output_dir="/tmp/codex-eval-warning")
            legacy.EvaluationRunner(Model(), [], [], output_dir="/tmp/codex-eval-warning")

        warnings_seen = [item for item in caught if item.category is DeprecationWarning]
        assert len(warnings_seen) == 1
        assert "0.5.0" in str(warnings_seen[0].message)
        """
    )
    assert result.returncode == 0, result.stderr


def test_lora_forwards_types_and_preserves_legacy_apply_signature() -> None:
    result = _run_python(
        """
        import inspect
        import sys
        import warnings

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", DeprecationWarning)
            import codex_ml.peft as legacy

        assert "codex_lora" not in sys.modules
        forwarded_config = legacy.LoraConfig

        import codex_lora
        with warnings.catch_warnings(record=True) as repeated:
            warnings.simplefilter("always", DeprecationWarning)
            import codex_ml.peft.adapters as adapters
            import codex_ml.peft.contracts as contracts
            import codex_ml.peft.service as service

        assert forwarded_config is codex_lora.LoraConfig
        assert contracts.LoraConfig is codex_lora.LoraConfig
        assert adapters.PeftBackend is codex_lora.PeftBackend
        assert service.apply_lora is codex_lora.apply_lora
        assert legacy.load_lora is codex_lora.load_lora
        signature = inspect.signature(legacy.apply_lora)
        assert signature.parameters["cfg"].kind is inspect.Parameter.POSITIONAL_ONLY
        warnings_seen = [item for item in caught if item.category is DeprecationWarning]
        assert len(warnings_seen) == 1
        assert "0.5.0" in str(warnings_seen[0].message)
        assert not [item for item in repeated if item.category is DeprecationWarning]
        """
    )
    assert result.returncode == 0, result.stderr


def test_telemetry_root_delegates_with_legacy_fallback_modules() -> None:
    result = _run_python(
        """
        import warnings
        import codex_ml_telemetry

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", DeprecationWarning)
            import codex_ml.telemetry as legacy
            import codex_ml.telemetry.export as export
            import codex_ml.telemetry.health as health
            import codex_ml.telemetry.metrics as metrics
            import codex_ml.telemetry.server as server

        assert legacy.MetricsRegistry is codex_ml_telemetry.MetricsRegistry
        assert legacy.track_time is metrics.track_time
        assert legacy.start_metrics_server is server.start_metrics_server
        assert metrics._standalone_track_time is codex_ml_telemetry.track_time
        assert (
            server._standalone_start_metrics_server
            is codex_ml_telemetry.start_metrics_server
        )
        assert export.render_prometheus is codex_ml_telemetry.render_prometheus
        assert health.HealthReport is codex_ml_telemetry.HealthReport
        warnings_seen = [item for item in caught if item.category is DeprecationWarning]
        assert len(warnings_seen) == 1
        assert "0.5.0" in str(warnings_seen[0].message)
        """
    )
    assert result.returncode == 0, result.stderr


def test_existing_facades_import_without_standalone_distributions() -> None:
    result = _run_python(
        """
        import importlib.abc
        import sys
        import types
        import warnings

        class BlockStandalone(importlib.abc.MetaPathFinder):
            def find_spec(self, fullname, path=None, target=None):
                if fullname in {"codex_evaluation", "codex_lora", "codex_ml_telemetry"}:
                    raise ModuleNotFoundError(fullname)
                return None

        sys.meta_path.insert(0, BlockStandalone())
        warnings.simplefilter("ignore", DeprecationWarning)

        torch = types.ModuleType("torch")
        torch.utils = types.SimpleNamespace(
            data=types.SimpleNamespace(DataLoader=type("DataLoader", (), {}))
        )
        sys.modules["torch"] = torch

        import codex_ml.evaluation as evaluation
        import codex_ml.peft as peft
        import codex_ml.telemetry as telemetry

        assert callable(evaluation.evaluate_epoch)
        assert callable(peft.apply_lora)
        assert callable(telemetry.track_time)
        """,
        standalone=False,
    )
    assert result.returncode == 0, result.stderr
