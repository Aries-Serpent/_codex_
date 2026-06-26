"""
Tests for ABTestFramework class.

Tests deterministic assignment, variant distribution, statistical analysis,
and experiment tracking functionality.
"""

import sqlite3
import tempfile
from pathlib import Path

import pytest

from cognitive_brain.models.quantum_metrics import QuantumMetricRepository
from cognitive_brain.quantum.ab_testing import (
    EXP_1_CONFIG,
    EXP_2_CONFIG,
    EXP_3_CONFIG,
    ABTestFramework,
    ExperimentConfig,
    Variant,
)


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    conn = sqlite3.connect(db_path)
    conn.executescript("""
        CREATE TABLE quantum_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            feature VARCHAR(50) NOT NULL,
            metric_name VARCHAR(100) NOT NULL,
            metric_value FLOAT NOT NULL,
            agent_id VARCHAR(100),
            metadata TEXT DEFAULT '{}',
            UNIQUE(timestamp, feature, metric_name)
        );
    """)
    conn.close()

    yield db_path
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def repo(temp_db):
    """Create repository."""
    return QuantumMetricRepository(db_path=temp_db)


@pytest.fixture
def framework(repo):
    """Create A/B testing framework."""
    return ABTestFramework(repository=repo)


class TestExperimentConfig:
    """Test ExperimentConfig dataclass."""

    def test_create_valid_config(self):
        """Test creating valid experiment config."""
        config = ExperimentConfig(
            experiment_id="TEST-1",
            name="Test Experiment",
            feature="superposition",
            sample_size=100,
            control_description="Control",
            treatment_description="Treatment",
            success_metric="accuracy",
        )

        assert config.experiment_id == "TEST-1", "experiment_id is not valid"
        assert config.sample_size == 100, "sample_size is not valid"

    def test_invalid_sample_size(self):
        """Test that small sample size raises error."""
        with pytest.raises(ValueError, match="sample_size must be at least 10"):
            ExperimentConfig(
                experiment_id="TEST-1",
                name="Test",
                feature="superposition",
                sample_size=5,
                control_description="C",
                treatment_description="T",
                success_metric="m",
            )


class TestExperimentManagement:
    """Test experiment creation and retrieval."""

    def test_create_experiment(self, framework):
        """Test creating an experiment."""
        config = ExperimentConfig(
            experiment_id="EXP-TEST",
            name="Test",
            feature="superposition",
            sample_size=100,
            control_description="C",
            treatment_description="T",
            success_metric="accuracy",
        )

        framework.create_experiment(config)

        retrieved = framework.get_experiment("EXP-TEST")
        assert retrieved is not None, "retrieved must be initialized"
        assert retrieved.experiment_id == "EXP-TEST", "experiment_id is not valid"

    def test_create_duplicate_experiment(self, framework):
        """Test that duplicate experiment raises error."""
        config = ExperimentConfig(
            experiment_id="EXP-TEST",
            name="Test",
            feature="superposition",
            sample_size=100,
            control_description="C",
            treatment_description="T",
            success_metric="m",
        )

        framework.create_experiment(config)

        with pytest.raises(ValueError, match="already exists"):
            framework.create_experiment(config)

    def test_get_nonexistent_experiment(self, framework):
        """Test getting non-existent experiment returns None."""
        result = framework.get_experiment("NONEXISTENT")
        assert result is None, "Result must not be empty"


class TestVariantAssignment:
    """Test deterministic variant assignment."""

    def test_deterministic_assignment(self, framework):
        """Test that same user always gets same variant."""
        config = ExperimentConfig(
            experiment_id="EXP-TEST",
            name="Test",
            feature="superposition",
            sample_size=100,
            control_description="C",
            treatment_description="T",
            success_metric="m",
        )
        framework.create_experiment(config)

        # Assign same user multiple times
        variant1 = framework.assign_variant("EXP-TEST", "user-123")
        variant2 = framework.assign_variant("EXP-TEST", "user-123")
        variant3 = framework.assign_variant("EXP-TEST", "user-123")

        assert variant1 == variant2 == variant3, "variant1 is not valid"

    def test_different_users_different_variants(self, framework):
        """Test that different users can get different variants."""
        config = ExperimentConfig(
            experiment_id="EXP-TEST",
            name="Test",
            feature="superposition",
            sample_size=100,
            control_description="C",
            treatment_description="T",
            success_metric="m",
        )
        framework.create_experiment(config)

        variants = set()
        for i in range(10):
            variant = framework.assign_variant("EXP-TEST", f"user-{i}")
            variants.add(variant)

        # Should have both variants
        assert len(variants) == 2, "Variants must not be empty"

    def test_assign_to_nonexistent_experiment(self, framework):
        """Test assigning to non-existent experiment raises error."""
        with pytest.raises(ValueError, match="not found"):
            framework.assign_variant("NONEXISTENT", "user-123")

    def test_get_existing_assignment(self, framework):
        """Test retrieving existing assignment."""
        config = ExperimentConfig(
            experiment_id="EXP-TEST",
            name="Test",
            feature="superposition",
            sample_size=100,
            control_description="C",
            treatment_description="T",
            success_metric="m",
        )
        framework.create_experiment(config)

        variant = framework.assign_variant("EXP-TEST", "user-123")
        retrieved = framework.get_assignment("EXP-TEST", "user-123")

        assert retrieved == variant, "retrieved is not valid"


class TestVariantDistribution:
    """Test 50/50 variant distribution."""

    def test_distribution_over_1000_users(self, framework):
        """Test that distribution is approximately 50/50 over 1000 users."""
        config = ExperimentConfig(
            experiment_id="EXP-TEST",
            name="Test",
            feature="superposition",
            sample_size=1000,
            control_description="C",
            treatment_description="T",
            success_metric="m",
        )
        framework.create_experiment(config)

        distribution = framework.get_variant_distribution("EXP-TEST", n_samples=1000)

        control_count = distribution[Variant.CONTROL]
        treatment_count = distribution[Variant.TREATMENT]

        # Should be approximately 50/50 (allow 40-60% range)
        assert 400 <= control_count <= 600, "Count must be greater than zero"
        assert 400 <= treatment_count <= 600, "Count must be greater than zero"
        assert control_count + treatment_count == 1000, "Count must be greater than zero"

    def test_distribution_over_100_users(self, framework):
        """Test distribution over smaller sample."""
        config = ExperimentConfig(
            experiment_id="EXP-TEST",
            name="Test",
            feature="superposition",
            sample_size=100,
            control_description="C",
            treatment_description="T",
            success_metric="m",
        )
        framework.create_experiment(config)

        distribution = framework.get_variant_distribution("EXP-TEST", n_samples=100)

        assert distribution[Variant.CONTROL] + distribution[Variant.TREATMENT] == 100, "Condition must be true"


class TestMetricRecording:
    """Test metric recording for experiments."""

    def test_record_metric(self, framework):
        """Test recording a metric."""
        config = ExperimentConfig(
            experiment_id="EXP-TEST",
            name="Test",
            feature="superposition",
            sample_size=100,
            control_description="C",
            treatment_description="T",
            success_metric="accuracy",
        )
        framework.create_experiment(config)

        metric = framework.record_metric("EXP-TEST", "user-123", 0.95)

        assert metric.id is not None, "id must be initialized"
        assert metric.feature == "superposition", "feature is not valid"
        assert metric.metric_name == "accuracy", "metric_name is not valid"
        assert metric.metric_value == 0.95, "Value must be initialized"
        assert metric.metadata["experiment_id"] == "EXP-TEST", "Data must not be empty"
        assert metric.metadata["user_id"] == "user-123", "Data must not be empty"

    def test_record_metric_assigns_variant(self, framework):
        """Test that recording metric auto-assigns variant."""
        config = ExperimentConfig(
            experiment_id="EXP-TEST",
            name="Test",
            feature="superposition",
            sample_size=100,
            control_description="C",
            treatment_description="T",
            success_metric="m",
        )
        framework.create_experiment(config)

        # User not yet assigned
        assert framework.get_assignment("EXP-TEST", "user-new") is None

        # Recording metric should assign
        framework.record_metric("EXP-TEST", "user-new", 0.9)

        # Now should be assigned
        assert framework.get_assignment("EXP-TEST", "user-new") is not None


class TestStatisticalAnalysis:
    """Test statistical significance calculations."""

    def test_analyze_with_significant_difference(self, framework):
        """Test analysis with statistically significant difference."""
        config = ExperimentConfig(
            experiment_id="EXP-TEST",
            name="Test",
            feature="superposition",
            sample_size=100,
            control_description="C",
            treatment_description="T",
            success_metric="accuracy",
        )
        framework.create_experiment(config)

        # Record control metrics (lower values)
        for i in range(30):
            user_id = f"control-user-{i}"
            framework.assign_variant("EXP-TEST", user_id)
            # Force control assignment for testing
            framework._assignments[("EXP-TEST", user_id)] = Variant.CONTROL
            framework.record_metric("EXP-TEST", user_id, 0.80 + (i % 10) * 0.01)

        # Record treatment metrics (higher values)
        for i in range(30):
            user_id = f"treatment-user-{i}"
            framework.assign_variant("EXP-TEST", user_id)
            # Force treatment assignment for testing
            framework._assignments[("EXP-TEST", user_id)] = Variant.TREATMENT
            framework.record_metric("EXP-TEST", user_id, 0.90 + (i % 10) * 0.01)

        result = framework.analyze_experiment("EXP-TEST")

        assert result.control_n == 30, "Result must not be empty"
        assert result.treatment_n == 30, "Result must not be empty"
        assert result.treatment_mean > result.control_mean, "treatment_mean must be greater than zero"
        assert result.p_value < 0.05, "Result must not be empty"
        assert result.is_significant, "Result must not be empty"

    def test_analyze_insufficient_data(self, framework):
        """Test that analysis with insufficient data raises error."""
        config = ExperimentConfig(
            experiment_id="EXP-TEST",
            name="Test",
            feature="superposition",
            sample_size=100,
            control_description="C",
            treatment_description="T",
            success_metric="m",
        )
        framework.create_experiment(config)

        # Record only 1 metric
        framework.record_metric("EXP-TEST", "user-1", 0.9)

        with pytest.raises(ValueError, match="Insufficient data"):
            framework.analyze_experiment("EXP-TEST")

    def test_experiment_result_to_dict(self, framework):
        """Test converting ExperimentResult to dict."""
        config = ExperimentConfig(
            experiment_id="EXP-TEST",
            name="Test",
            feature="superposition",
            sample_size=100,
            control_description="C",
            treatment_description="T",
            success_metric="m",
        )
        framework.create_experiment(config)

        # Create minimal dataset
        for i in range(10):
            user_id = f"user-{i}"
            _ = framework.assign_variant("EXP-TEST", user_id)  # Assignment needed for test setup
            framework.record_metric("EXP-TEST", user_id, 0.85 + i * 0.01)

        result = framework.analyze_experiment("EXP-TEST")
        result_dict = result.to_dict()

        assert "experiment_id" in result_dict, "Result must not be empty"
        assert "p_value" in result_dict, "Result must not be empty"
        assert "is_significant" in result_dict, "Result must not be empty"


class TestPredefinedExperiments:
    """Test predefined experiment configurations."""

    def test_exp1_config(self):
        """Test EXP-1 configuration."""
        assert EXP_1_CONFIG.experiment_id == "EXP-1", "experiment_id is not valid"
        assert EXP_1_CONFIG.feature == "superposition", "feature is not valid"
        assert EXP_1_CONFIG.sample_size == 100, "sample_size is not valid"

    def test_exp2_config(self):
        """Test EXP-2 configuration."""
        assert EXP_2_CONFIG.experiment_id == "EXP-2", "experiment_id is not valid"
        assert EXP_2_CONFIG.feature == "entanglement", "feature is not valid"
        assert EXP_2_CONFIG.sample_size == 500, "sample_size is not valid"

    def test_exp3_config(self):
        """Test EXP-3 configuration."""
        assert EXP_3_CONFIG.experiment_id == "EXP-3", "experiment_id is not valid"
        assert EXP_3_CONFIG.feature == "uncertainty", "feature is not valid"
        assert EXP_3_CONFIG.sample_size == 50, "sample_size is not valid"


class TestIntegration:
    """Integration tests for full experiment workflow."""

    def test_full_experiment_workflow(self, framework):
        """Test complete experiment workflow."""
        # 1. Create experiment
        framework.create_experiment(EXP_1_CONFIG)

        # 2. Assign users and record metrics
        for i in range(50):
            user_id = f"user-{i}"
            variant = framework.assign_variant("EXP-1", user_id)

            # Simulate metrics (control slightly lower)
            if variant == Variant.CONTROL:
                metric_value = 0.85 + (i % 10) * 0.01
            else:
                metric_value = 0.90 + (i % 10) * 0.01

            framework.record_metric("EXP-1", user_id, metric_value)

        # 3. Analyze results
        result = framework.analyze_experiment("EXP-1")

        # 4. Verify results
        assert result.experiment_id == "EXP-1", "Result must not be empty"
        assert result.control_n + result.treatment_n == 50, "Result must not be empty"
        assert result.p_value is not None, "p_value must be initialized"
        assert result.confidence_interval is not None, "confidence_interval must be initialized"
