"""
Tests for WP-G: Reproducibility Hardening

Validates that:
1. enable_deterministic_training() sets all seeds correctly
2. save_env_snapshot() captures environment information
3. create_reproducibility_manifest() produces complete manifest
4. ReproducibilityManager provides unified interface
5. Two runs with same seed produce deterministic results
"""

import json
import os
import random
import tempfile
from pathlib import Path

import pytest

# Import the module under test
from src.codex_ml.utils.reproducibility_hardening import (
    ReproducibilityManager,
    create_reproducibility_manifest,
    enable_deterministic_training,
    save_env_snapshot,
)


class TestEnableDeterministicTraining:
    """Test deterministic training enablement"""

    def test_enable_deterministic_training_returns_status(self):
        """Verify enable_deterministic_training returns status dict"""
        status = enable_deterministic_training(seed=42)

        assert isinstance(status, dict), "Should return status dict"
        assert "python_random" in status, "Should include python_random status"
        assert "python_hash_seed" in status, "Should include python_hash_seed status"

    def test_python_random_seeded(self):
        """Verify Python random is seeded"""
        # Set seed and generate numbers
        enable_deterministic_training(seed=42)
        numbers1 = [random.random() for _ in range(10)]

        # Reset and regenerate
        enable_deterministic_training(seed=42)
        numbers2 = [random.random() for _ in range(10)]

        assert numbers1 == numbers2, "Python random should produce same sequence with same seed"

    def test_python_hash_seed_set(self):
        """Verify PYTHONHASHSEED is set"""
        enable_deterministic_training(seed=42)

        assert "PYTHONHASHSEED" in os.environ, "PYTHONHASHSEED should be set"
        assert os.environ["PYTHONHASHSEED"] == "42", "PYTHONHASHSEED should equal seed"

    @pytest.mark.skipif(
        not pytest.importorskip("numpy", reason="NumPy not available"), reason="Requires NumPy"
    )
    def test_numpy_seeded(self):
        """Verify NumPy is seeded (if available)"""
        import numpy as np

        status = enable_deterministic_training(seed=42)

        # NumPy status should be True (seeded) or None (not available)
        assert status["numpy"] in [True, None], "NumPy should be seeded if available"

        if status["numpy"]:
            # Generate random numbers
            numbers1 = np.random.rand(10).tolist()

            # Reset and regenerate
            enable_deterministic_training(seed=42)
            numbers2 = np.random.rand(10).tolist()

            assert numbers1 == numbers2, "NumPy should produce same sequence with same seed"

    @pytest.mark.skipif(
        not pytest.importorskip("torch", reason="PyTorch not available"), reason="Requires PyTorch"
    )
    def test_torch_seeded(self):
        """Verify PyTorch is seeded (if available)"""
        import torch

        status = enable_deterministic_training(seed=42)

        assert status["torch"] in [True, None], "PyTorch should be seeded if available"

        if status["torch"]:
            # Generate random tensor
            tensor1 = torch.rand(10).tolist()

            # Reset and regenerate
            enable_deterministic_training(seed=42)
            tensor2 = torch.rand(10).tolist()

            assert tensor1 == tensor2, "PyTorch should produce same sequence with same seed"

    def test_strict_mode_enables_deterministic_algorithms(self):
        """Verify strict mode enables deterministic algorithms"""
        pytest.importorskip("torch")

        status = enable_deterministic_training(seed=42, strict=True)

        # In strict mode, should attempt to enable deterministic algorithms
        # Status might be True or False depending on PyTorch version/ops support
        assert "torch_deterministic_algorithms" in status

    def test_non_strict_mode_skips_deterministic_algorithms(self):
        """Verify non-strict mode doesn't enable deterministic algorithms"""
        pytest.importorskip("torch")

        status = enable_deterministic_training(seed=42, strict=False)

        # In non-strict mode, should not enable deterministic algorithms
        assert status["torch_deterministic_algorithms"] is None


class TestSaveEnvSnapshot:
    """Test environment snapshot capture"""

    def test_save_env_snapshot_creates_file(self):
        """Verify save_env_snapshot creates output file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "env_snapshot.txt"

            snapshot = save_env_snapshot(output_path)

            assert output_path.exists(), "Snapshot file should be created"
            assert output_path.is_file(), "Should create a file"

    def test_save_env_snapshot_returns_dict(self):
        """Verify save_env_snapshot returns snapshot dict"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "env_snapshot.txt"

            snapshot = save_env_snapshot(output_path)

            assert isinstance(snapshot, dict), "Should return dict"
            assert "python_version" in snapshot, "Should include Python version"
            assert "platform" in snapshot, "Should include platform info"

    def test_snapshot_contains_python_info(self):
        """Verify snapshot contains Python information"""
        with tempfile.TemporaryDirectory() as tmpdir:
            snapshot = save_env_snapshot(Path(tmpdir) / "env_snapshot.txt")

            assert "python_version" in snapshot
            assert "python_executable" in snapshot
            assert "python_version_info" in snapshot

            version_info = snapshot["python_version_info"]
            assert "major" in version_info
            assert "minor" in version_info
            assert "micro" in version_info

    def test_snapshot_contains_platform_info(self):
        """Verify snapshot contains platform information"""
        with tempfile.TemporaryDirectory() as tmpdir:
            snapshot = save_env_snapshot(Path(tmpdir) / "env_snapshot.txt")

            assert "platform" in snapshot
            platform_info = snapshot["platform"]

            assert "system" in platform_info
            assert "machine" in platform_info

    def test_snapshot_includes_pip_freeze(self):
        """Verify snapshot includes pip freeze by default"""
        with tempfile.TemporaryDirectory() as tmpdir:
            snapshot = save_env_snapshot(Path(tmpdir) / "env_snapshot.txt")

            assert "pip_freeze" in snapshot
            # pip_freeze should be a list or None
            assert snapshot["pip_freeze"] is None or isinstance(snapshot["pip_freeze"], list)

    def test_snapshot_skips_pip_freeze_when_disabled(self):
        """Verify snapshot skips pip freeze when disabled"""
        with tempfile.TemporaryDirectory() as tmpdir:
            snapshot = save_env_snapshot(
                Path(tmpdir) / "env_snapshot.txt", include_pip_freeze=False
            )

            assert snapshot["pip_freeze"] is None, "Should skip pip freeze when disabled"

    def test_snapshot_creates_json_file(self):
        """Verify snapshot creates JSON version"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "env_snapshot.txt"
            json_path = output_path.with_suffix(".json")

            save_env_snapshot(output_path)

            assert json_path.exists(), "JSON version should be created"

            with open(json_path) as f:
                json_data = json.load(f)

            assert isinstance(json_data, dict), "JSON should contain dict"
            assert "python_version" in json_data

    def test_snapshot_file_readable(self):
        """Verify snapshot file is human-readable"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "env_snapshot.txt"

            save_env_snapshot(output_path)

            content = output_path.read_text()

            # Should contain expected sections
            assert "# Environment Snapshot" in content
            assert "## Python Information" in content
            assert "## Platform Information" in content


class TestCreateReproducibilityManifest:
    """Test reproducibility manifest creation"""

    def test_create_reproducibility_manifest_returns_dict(self):
        """Verify create_reproducibility_manifest returns dict"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = create_reproducibility_manifest(seed=42, output_dir=tmpdir)

            assert isinstance(manifest, dict), "Should return manifest dict"

    def test_manifest_contains_seed(self):
        """Verify manifest contains seed information"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = create_reproducibility_manifest(seed=42, output_dir=tmpdir)

            assert "seed" in manifest, "Should include seed"
            assert manifest["seed"] == 42, "Should record correct seed"

    def test_manifest_contains_seeding_status(self):
        """Verify manifest contains seeding status"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = create_reproducibility_manifest(seed=42, output_dir=tmpdir)

            assert "seeding_status" in manifest, "Should include seeding status"
            assert isinstance(manifest["seeding_status"], dict)

    def test_manifest_contains_environment_info(self):
        """Verify manifest contains environment information"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = create_reproducibility_manifest(seed=42, output_dir=tmpdir)

            assert "environment" in manifest, "Should include environment info"
            env = manifest["environment"]

            assert "python_version" in env
            assert "platform" in env

    def test_manifest_includes_config(self):
        """Verify manifest includes config when provided"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_config = {"learning_rate": 1e-4, "batch_size": 32}

            manifest = create_reproducibility_manifest(
                seed=42, output_dir=tmpdir, config=test_config
            )

            assert "config" in manifest, "Should include config"
            assert manifest["config"] == test_config, "Should record correct config"

    def test_manifest_includes_dataset_hash(self):
        """Verify manifest includes dataset hash when provided"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = create_reproducibility_manifest(
                seed=42, output_dir=tmpdir, dataset_hash="abc123def456"
            )

            assert "dataset_hash" in manifest, "Should include dataset hash"
            assert manifest["dataset_hash"] == "abc123def456"

    def test_manifest_has_timestamp(self):
        """Verify manifest includes timestamp"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = create_reproducibility_manifest(seed=42, output_dir=tmpdir)

            assert "created_at" in manifest, "Should include timestamp"
            # Timestamp should be ISO format
            assert "T" in manifest["created_at"]

    def test_manifest_has_hash(self):
        """Verify manifest includes manifest hash"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = create_reproducibility_manifest(seed=42, output_dir=tmpdir)

            assert "manifest_hash" in manifest, "Should include manifest hash"
            assert len(manifest["manifest_hash"]) == 16, "Hash should be 16 chars"

    def test_manifest_file_created(self):
        """Verify manifest JSON file is created"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = create_reproducibility_manifest(seed=42, output_dir=tmpdir)

            manifest_path = Path(tmpdir) / "reproducibility_manifest.json"
            assert manifest_path.exists(), "Manifest file should be created"

            # Verify it's valid JSON
            with open(manifest_path) as f:
                loaded_manifest = json.load(f)

            assert loaded_manifest["seed"] == 42


class TestReproducibilityManager:
    """Test ReproducibilityManager class"""

    def test_manager_initialization(self):
        """Verify ReproducibilityManager can be initialized"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ReproducibilityManager(seed=42, output_dir=tmpdir)

            assert manager.seed == 42
            assert manager.output_dir == Path(tmpdir)

    def test_manager_setup(self):
        """Verify manager setup() enables deterministic training"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ReproducibilityManager(seed=42, output_dir=tmpdir)

            status = manager.setup()

            assert isinstance(status, dict), "setup() should return status dict"
            assert "python_random" in status

    def test_manager_capture_environment(self):
        """Verify manager capture_environment() saves snapshot"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ReproducibilityManager(seed=42, output_dir=tmpdir)

            snapshot = manager.capture_environment()

            assert isinstance(snapshot, dict), "Should return snapshot dict"

            # Verify file was created
            snapshot_path = Path(tmpdir) / "env_snapshot.txt"
            assert snapshot_path.exists(), "Snapshot file should be created"

    def test_manager_finalize(self):
        """Verify manager finalize() creates manifest"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ReproducibilityManager(seed=42, output_dir=tmpdir)
            manager.setup()

            manifest = manager.finalize(config={"lr": 1e-4}, dataset_hash="test123")

            assert isinstance(manifest, dict), "finalize() should return manifest"
            assert manifest["seed"] == 42
            assert manifest["config"]["lr"] == 1e-4
            assert manifest["dataset_hash"] == "test123"

    def test_manager_get_manifest(self):
        """Verify manager get_manifest() returns manifest after finalize"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ReproducibilityManager(seed=42, output_dir=tmpdir)

            # Before finalize, should return None
            assert manager.get_manifest() is None

            # After finalize, should return manifest
            manager.finalize()
            manifest = manager.get_manifest()

            assert manifest is not None
            assert isinstance(manifest, dict)

    def test_manager_full_workflow(self):
        """Test complete workflow with manager"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize manager
            manager = ReproducibilityManager(seed=42, output_dir=tmpdir)

            # Setup deterministic training
            manager.setup(strict=False)

            # Capture environment
            manager.capture_environment()

            # Finalize with config and dataset
            manifest = manager.finalize(config={"epochs": 10, "lr": 1e-4}, dataset_hash="abc123")

            # Verify all artifacts created
            assert Path(tmpdir, "env_snapshot.txt").exists()
            assert Path(tmpdir, "env_snapshot.json").exists()
            assert Path(tmpdir, "reproducibility_manifest.json").exists()

            # Verify manifest completeness
            assert manifest["seed"] == 42
            assert "seeding_status" in manifest
            assert "environment" in manifest
            assert "config" in manifest
            assert "dataset_hash" in manifest


class TestSeedConsistency:
    """Test that seeds produce consistent results"""

    def test_two_runs_same_seed_produce_same_random_numbers(self):
        """Verify two runs with same seed produce identical random numbers"""
        # Run 1
        enable_deterministic_training(seed=42)
        run1_numbers = [random.random() for _ in range(100)]

        # Run 2
        enable_deterministic_training(seed=42)
        run2_numbers = [random.random() for _ in range(100)]

        assert run1_numbers == run2_numbers, "Same seed should produce identical sequences"

    def test_different_seeds_produce_different_numbers(self):
        """Verify different seeds produce different random numbers"""
        # Seed 42
        enable_deterministic_training(seed=42)
        numbers_42 = [random.random() for _ in range(10)]

        # Seed 123
        enable_deterministic_training(seed=123)
        numbers_123 = [random.random() for _ in range(10)]

        assert numbers_42 != numbers_123, "Different seeds should produce different sequences"

    @pytest.mark.skipif(
        not pytest.importorskip("torch", reason="PyTorch not available"), reason="Requires PyTorch"
    )
    def test_torch_deterministic_with_same_seed(self):
        """Verify PyTorch operations are deterministic with same seed"""
        import torch

        # Run 1
        enable_deterministic_training(seed=42)
        x = torch.randn(100, 100)
        y = torch.randn(100, 100)
        result1 = (x @ y).sum().item()

        # Run 2
        enable_deterministic_training(seed=42)
        x = torch.randn(100, 100)
        y = torch.randn(100, 100)
        result2 = (x @ y).sum().item()

        # Results should be identical (or very close due to floating point)
        assert abs(result1 - result2) < 1e-5, "Same seed should produce deterministic PyTorch ops"


# Fixtures
@pytest.fixture
def temp_output_dir():
    """Provide temporary output directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_config():
    """Provide sample configuration for testing"""
    return {
        "learning_rate": 1e-4,
        "batch_size": 32,
        "epochs": 10,
        "optimizer": "adamw",
    }
