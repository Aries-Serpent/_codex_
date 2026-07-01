#             assert ", "Condition must be true"
#             assert ", "Condition must be true"
#             assert ", "Condition must be true"


class TestCreateReproducibilityManifest:
    """Test reproducibility manifest creation"""

    def test_create_reproducibility_manifest_returns_dict(self):
        """Verify create_reproducibility_manifest returns dict"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = create_reproducibility_manifest(seed=42, output_dir=tmpdir)

            assert isinstance(manifest, dict), "Should return manifest dict"

    def test_manifest_contains_seed(self):
        """Verify manifest contains seed information"""
        with tempfile.TemporaryDirectory() as tmpdir: # pragma: allowlist secret
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

            assert "python_version" in env, "Condition must be true"
            assert "platform" in env, "Condition must be true"

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
            assert manifest["dataset_hash"] == "abc123def456", "Data must not be empty"

    def test_manifest_has_timestamp(self):
        """Verify manifest includes timestamp"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = create_reproducibility_manifest(seed=42, output_dir=tmpdir)

            assert "created_at" in manifest, "Should include timestamp"
            # Timestamp should be ISO format
            assert "T" in manifest["created_at"], "Condition must be true"

    def test_manifest_has_hash(self):
        """Verify manifest includes manifest hash"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = create_reproducibility_manifest(seed=42, output_dir=tmpdir)

            assert "manifest_hash" in manifest, "Should include manifest hash"
            assert len(manifest["manifest_hash"]) == 16, "Hash should be 16 chars"

    def test_manifest_file_created(self):
        """Verify manifest JSON file is created"""
        with tempfile.TemporaryDirectory() as tmpdir:
            create_reproducibility_manifest(seed=42, output_dir=tmpdir)

            manifest_path = Path(tmpdir) / "reproducibility_manifest.json"
            assert manifest_path.exists(), "Manifest file should be created"

            # Verify it's valid JSON
            with open(manifest_path) as f:
                loaded_manifest = json.load(f)

            assert loaded_manifest["seed"] == 42, "Condition must be true"


class TestReproducibilityManager:
    """Test ReproducibilityManager class"""

    def test_manager_initialization(self):
        """Verify ReproducibilityManager can be initialized"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ReproducibilityManager(seed=42, output_dir=tmpdir)

            assert manager.seed == 42, "seed is not valid"
            assert manager.output_dir == Path(tmpdir), "output_dir is not valid"

    def test_manager_setup(self):
        """Verify manager setup() enables deterministic training"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ReproducibilityManager(seed=42, output_dir=tmpdir)

            status = manager.setup()

            assert isinstance(status, dict), "setup() should return status dict"
            assert "python_random" in status, "Condition must be true"

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
            assert manifest["seed"] == 42, "Condition must be true"
            assert manifest["config"]["lr"] == 1e-4, "Condition must be true"
            assert manifest["dataset_hash"] == "test123", "Data must not be empty"

    def test_manager_get_manifest(self):
        """Verify manager get_manifest() returns manifest after finalize"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ReproducibilityManager(seed=42, output_dir=tmpdir)

            # Before finalize, should return None
            assert manager.get_manifest() is None, "Condition must be true"

            # After finalize, should return manifest
            manager.finalize()
            manifest = manager.get_manifest()

            assert manifest is not None, "manifest must be initialized"
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
            assert manifest["seed"] == 42, "Condition must be true"
            assert "seeding_status" in manifest, "Condition must be true"
            assert "environment" in manifest, "Condition must be true"
            assert "config" in manifest, "Condition must be true"
            assert "dataset_hash" in manifest, "Data must not be empty"


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
