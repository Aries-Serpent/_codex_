"""Regression tests for optional backend isolation during installed CLI startup."""

from __future__ import annotations

import importlib
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock

import pytest


def test_package_and_lightweight_utilities_do_not_import_ml_backends(tmp_path: Path) -> None:
    """Metadata and atomic file helpers must not initialize training frameworks."""
    source = Path(__file__).resolve().parents[1] / "src"
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(source)
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; import codex_ml; import codex_ml.cli.main; "
            "from codex_ml.utils import safe_write_text; "
            "assert callable(safe_write_text); "
            "assert not any(name in sys.modules for name in "
            "('torch', 'transformers', 'sklearn', 'codex_ml.pipeline', "
            "'codex_ml.symbolic_pipeline', 'codex_ml.cli.codex_cli'))",
        ],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == 0, result.stderr


def test_lazy_utility_exports_preserve_identity() -> None:
    """Legacy utility exports resolve to the canonical implementation objects."""
    utilities = importlib.import_module("codex_ml.utils")
    atomic = importlib.import_module("codex_ml.utils.atomic_io")
    assert utilities.safe_write_text is atomic.safe_write_text
    assert utilities.safe_write_bytes is atomic.safe_write_bytes
    assert utilities.error_log is importlib.import_module("codex_ml.utils.error_log")
    with pytest.raises(AttributeError, match="has no attribute"):
        getattr(utilities, "nonexistent_phase2_utility")


def test_evaluation_wrapper_defers_and_forwards_backend_calls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """CLI evaluation stays patchable while loading its backend only on demand."""
    cli = importlib.import_module("codex_ml.cli.main")
    backend = ModuleType("codex_ml.eval.eval_runner")
    evaluate = Mock(return_value={"evaluated": True})
    monkeypatch.setattr(backend, "evaluate_datasets", evaluate, raising=False)
    monkeypatch.setitem(sys.modules, backend.__name__, backend)

    assert cli.evaluate_datasets(["dataset"], output_dir="results") == {"evaluated": True}
    evaluate.assert_called_once_with(["dataset"], output_dir="results")


def test_inference_alias_preserves_the_legacy_cli() -> None:
    """The historical alias does not probe a nonexistent inference app export."""
    from codex_ml.cli import cli, infer

    assert infer is cli


@pytest.mark.parametrize("content", ["[one, two]", "a scalar", "42"])
def test_training_config_rejects_non_mappings(tmp_path: Path, content: str) -> None:
    """Invalid YAML shapes fail explicitly before training configuration access."""
    from codex_ml.cli import _load_training_config

    config = tmp_path / "training.yaml"
    config.write_text(content)
    with pytest.raises(ValueError, match="must be a mapping"):
        _load_training_config(str(config))
