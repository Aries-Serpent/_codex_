"""Basic smoke tests for restore_pipeline module.

These tests verify that the restore_pipeline package can be imported
and basic functionality is available, without requiring heavy dependencies
like CUDA torch or GPU-specific libraries.
"""

from __future__ import annotations

import pytest


class TestRestorePipelineImport:
    """Test that restore_pipeline can be imported successfully."""

    def test_import_restore_pipeline(self) -> None:
        """Verify restore_pipeline module imports without errors."""
        import restore_pipeline

        assert hasattr(restore_pipeline, "__version__")
        assert restore_pipeline.__version__ is not None

    def test_import_submodules(self) -> None:
        """Verify restore_pipeline submodules can be imported."""
        from restore_pipeline import config, io, metrics, pipeline

        assert config is not None
        assert io is not None
        assert metrics is not None
        assert pipeline is not None


class TestRestorePipelineBasics:
    """Test basic restore_pipeline functionality."""

    def test_pipeline_module_has_pipeline_functions(self) -> None:
        """Verify process function exists in pipeline module."""
        from restore_pipeline.pipeline import process

        assert callable(process)

    def test_config_module_has_pipeline_config_class(self) -> None:
        """Verify PipelineConfig class exists in config module."""
        from restore_pipeline.config import PipelineConfig

        assert PipelineConfig is not None

    @pytest.mark.skipif(
        True,
        reason="Full integration tests require GPU/heavy dependencies not present in CPU-only CI",
    )
    def test_full_pipeline_integration(self) -> None:
        """Placeholder for full integration test.

        This test is skipped in CPU-only CI environments where GPU-specific
        libraries are not available.
        """
        pass
