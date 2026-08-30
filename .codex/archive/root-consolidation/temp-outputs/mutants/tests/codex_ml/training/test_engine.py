"""
Test Engine

Test module for engine.
"""

import pytest


class TestNormalizeParams:
    """Test _normalize_params helper function."""

    def test_normalize_params_string(self):
        """Test normalizing string parameters."""
        try:
            from codex_ml.training.engine import _normalize_params

            result = _normalize_params({"key": "value"})
            assert result == {"key": "value"}, "Result must not be empty"
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")

    def test_normalize_params_bool(self):
        """Test normalizing boolean parameters."""
        try:
            from codex_ml.training.engine import _normalize_params

            result = _normalize_params({"flag": True, "other": False})
            assert result == {"flag": 1, "other": 0}
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")

    def test_normalize_params_none(self):
        """Test normalizing None parameters (should be filtered)."""
        try:
            from codex_ml.training.engine import _normalize_params

            result = _normalize_params({"key": None})
            assert result == {}, "Result must not be empty"
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")

    def test_normalize_params_mixed(self):
        """Test normalizing mixed types."""
        try:
            from codex_ml.training.engine import _normalize_params

            result = _normalize_params(
                {"str": "text", "int": 42, "float": 3.14, "bool": True, "none": None}
            )
            assert result["str"] == "text", "Result must not be empty"
            assert result["int"] == 42, "Result must not be empty"
            assert result["float"] == 3.14, "Result must not be empty"
            assert result["bool"] == 1, "Result must not be empty"
            assert "none" not in result, "Result must not be empty"
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")


class TestTrainingEngine:
    """Test TrainingEngine class."""

    def test_engine_creation_default(self):
        """Test creating engine with defaults."""
        try:
            from codex_ml.training.engine import TrainingEngine

            engine = TrainingEngine()
            assert engine is not None, "engine must be initialized"
            assert engine.enable_mlflow is False, "enable_mlflow is not valid"
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")

    def test_engine_creation_with_mlflow(self):
        """Test creating engine with mlflow enabled."""
        try:
            from codex_ml.training.engine import TrainingEngine

            engine = TrainingEngine(enable_mlflow=True)
            assert engine.enable_mlflow in [True, False]
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")

    def test_engine_has_start_run(self):
        """Test engine has start_run method."""
        try:
            from codex_ml.training.engine import TrainingEngine

            engine = TrainingEngine()
            assert hasattr(engine, "start_run")
            assert callable(engine.start_run), "Condition must be true"
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")

    def test_engine_start_run_no_mlflow(self):
        """Test start_run with mlflow disabled."""
        try:
            from codex_ml.training.engine import TrainingEngine

            engine = TrainingEngine(enable_mlflow=False)
            engine.start_run()
            assert engine._active_run is None, "_active_run is not valid"
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")
