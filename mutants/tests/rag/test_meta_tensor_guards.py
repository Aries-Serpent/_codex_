"""
Unit Tests for Meta-Tensor Guard Rails

Tests for all guard rail components:
- Guard rail checks
- Detection mechanisms
- Recovery strategies
- Monitoring and reporting

This module is part of Phase 13.2: RAG Meta-Tensor Safety
"""

from datetime import UTC, datetime

import pytest

from codex.rag.materialization_prevention import (
    MaterializationEvent,
    MaterializationMonitor,
    MaterializationPreventionFramework,
    MaterializationRecoveryStrategy,
    MatTensorDetector,
    TensorLocation,
    prevent_meta_tensor_materialization,
)
from codex.rag.meta_tensor_guard import (
    GuardRailReport,
    GuardRailStatus,
    MetaTensorException,
    MetaTensorGuardRail,
    guard_rail_context,
    verify_model_integrity,
)


class TestGuardRailBasics:
    """Test basic guard rail functionality."""

    def test_guard_rail_initialization(self):
        """Test guard rail initialization."""
        guard = MetaTensorGuardRail(max_recovery_attempts=3)
        assert guard.max_recovery_attempts == 3
        assert len(guard.reports) == 0
        assert len(guard.state_history) == 0

    def test_check_environment_success(self):
        """Test environment check succeeds."""
        guard = MetaTensorGuardRail()
        report = guard.check_environment()

        assert report.name == "environment_check"
        assert report.status == GuardRailStatus.PASSED
        assert report.error is None
        assert "torch_version" in report.details
        assert report.duration_ms >= 0

    def test_check_pre_init_state_success(self):
        """Test pre-init state check succeeds."""
        guard = MetaTensorGuardRail()
        report = guard.check_pre_init_state()

        assert report.name == "pre_init_state_check"
        assert report.status == GuardRailStatus.PASSED
        assert "garbage_collection" in report.details

    def test_check_oom_condition_success(self):
        """Test OOM check succeeds under normal conditions."""
        guard = MetaTensorGuardRail()
        report = guard.check_oom_condition()

        # Should either pass or be bypassed (psutil optional)
        assert report.status in [GuardRailStatus.PASSED, GuardRailStatus.BYPASSED]

    def test_guard_rail_report_summary(self):
        """Test guard rail summary generation."""
        guard = MetaTensorGuardRail()
        guard.check_environment()
        guard.check_pre_init_state()

        summary = guard.get_summary()
        assert summary["total_checks"] == 2
        assert summary["passed"] >= 0
        assert "details" in summary
        assert isinstance(summary["pass_rate"], float)

    def test_guard_rail_state_history(self):
        """Test state history tracking."""
        guard = MetaTensorGuardRail()
        guard.save_state("initial")
        guard.save_state("final")

        assert len(guard.state_history) == 2
        assert guard.state_history[0]["state_id"] == "initial"
        assert guard.state_history[1]["state_id"] == "final"


class TestModelChecking:
    """Test model validation checks."""

    def test_check_model_loading_success(self):
        """Test model loading check with valid model."""
        guard = MetaTensorGuardRail()
        mock_model = Mock()
        mock_model.named_parameters = Mock(return_value=[])

        report = guard.check_model_loading(mock_model)
        assert report.status == GuardRailStatus.PASSED

    def test_check_model_loading_failure_none_model(self):
        """Test model loading check with None model."""
        guard = MetaTensorGuardRail()
        report = guard.check_model_loading(None)

        assert report.status == GuardRailStatus.FAILED
        assert report.error is not None

    def test_check_meta_tensors_no_tensors(self):
        """Test meta tensor check when no meta tensors present."""
        guard = MetaTensorGuardRail()

        # Create mock model with no meta tensors
        mock_model = Mock()
        mock_model.named_parameters = Mock(return_value=[])
        mock_model.named_buffers = Mock(return_value=[])
        mock_model.named_modules = Mock(return_value=[])

        report = guard.check_meta_tensors_post_init(mock_model)
        assert report.status == GuardRailStatus.PASSED
        assert report.details["total_meta_tensors"] == 0

    def test_check_meta_tensors_with_meta_param(self):
        """Test meta tensor check detects meta parameter."""
        guard = MetaTensorGuardRail()

        # Create mock tensor on meta device
        meta_param = Mock()
        meta_param.device.type = "meta"

        mock_model = Mock()
        mock_model.named_parameters = Mock(return_value=[("weight", meta_param)])
        mock_model.named_buffers = Mock(return_value=[])
        mock_model.named_modules = Mock(return_value=[])

        report = guard.check_meta_tensors_post_init(mock_model)
        assert report.status == GuardRailStatus.FAILED
        assert len(report.details["meta_params"]) > 0
        assert isinstance(report.error, MetaTensorException)


class TestRecoveryMechanism:
    """Test recovery mechanisms."""

    def test_recovery_mechanism_success(self):
        """Test successful recovery."""
        guard = MetaTensorGuardRail()

        def success_recovery():
            return True

        report = guard.check_recovery_mechanism(success_recovery)
        assert report.status == GuardRailStatus.RECOVERED
        assert report.details["recovery_successes"] == 1

    def test_recovery_mechanism_failure(self):
        """Test failed recovery."""
        guard = MetaTensorGuardRail()

        def failure_recovery():
            raise RuntimeError("Recovery failed")

        report = guard.check_recovery_mechanism(failure_recovery)
        assert report.status == GuardRailStatus.FAILED
        assert report.error is not None

    def test_recovery_multiple_attempts(self):
        """Test recovery with multiple attempts."""
        guard = MetaTensorGuardRail(max_recovery_attempts=3)

        call_count = 0

        def intermittent_recovery():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RuntimeError("Not yet")
            return True

        report = guard.check_recovery_mechanism(intermittent_recovery)
        assert report.details["recovery_attempts"] == 3


class TestGuardRailContext:
    """Test guard rail context manager."""

    def test_guard_rail_context_manager(self):
        """Test guard rail context manager."""
        with guard_rail_context() as guard:
            assert guard is not None
            assert len(guard.reports) >= 1  # At least environment check

    def test_guard_rail_context_logging(self):
        """Test that context manager logs summary."""
        with guard_rail_context() as guard:
            summary = guard.get_summary()
            assert summary["total_checks"] >= 1


class TestMaterializationMonitor:
    """Test materialization monitoring."""

    def test_monitor_initialization(self):
        """Test monitor initialization."""
        monitor = MaterializationMonitor("test-model")
        assert monitor.model_name == "test-model"
        assert len(monitor.events) == 0

    def test_record_event(self):
        """Test recording materialization event."""
        monitor = MaterializationMonitor("test-model")
        event = monitor.record_event(
            location=TensorLocation.PARAMETERS,
            tensor_name="weight",
            tensor_shape=(10, 20),
            tensor_dtype="float32",
        )

        assert event.tensor_name == "weight"
        assert len(monitor.events) == 1

    def test_record_recovery(self):
        """Test recording recovery attempt."""
        monitor = MaterializationMonitor("test-model")
        event = monitor.record_event(
            location=TensorLocation.PARAMETERS,
            tensor_name="bias",
        )

        monitor.record_recovery(event, success=True, method="gc")
        assert event.recovery_attempted is True
        assert event.recovery_successful is True
        assert event.recovery_method == "gc"

    def test_monitor_summary(self):
        """Test monitor summary generation."""
        monitor = MaterializationMonitor("test-model")
        monitor.record_event(TensorLocation.PARAMETERS, "weight")
        monitor.record_event(TensorLocation.BUFFERS, "bias")

        summary = monitor.get_summary()
        assert summary["total_events"] == 2
        assert summary["model_name"] == "test-model"


class TestMetaTensorDetector:
    """Test meta tensor detection."""

    def test_detector_with_empty_model(self):
        """Test detector with empty model."""
        mock_model = Mock()
        mock_model.named_parameters = Mock(return_value=[])
        mock_model.named_buffers = Mock(return_value=[])
        mock_model.named_modules = Mock(return_value=[])

        result = MatTensorDetector.detect_in_model(mock_model)
        assert len(result) == 0

    def test_detector_identifies_meta_tensor(self):
        """Test detector identifies meta tensor."""
        meta_tensor = Mock()
        meta_tensor.device.type = "meta"

        mock_model = Mock()
        mock_model.named_parameters = Mock(return_value=[("weight", meta_tensor)])
        mock_model.named_buffers = Mock(return_value=[])
        mock_model.named_modules = Mock(return_value=[])

        result = MatTensorDetector.detect_in_model(mock_model)
        assert len(result) == 1
        assert result[0][1] == "weight"

    def test_detector_tensor_info(self):
        """Test getting tensor information."""
        tensor = Mock()
        tensor.shape = (10, 20)
        tensor.dtype = "float32"
        tensor.device = "cpu"
        tensor.is_meta = False

        info = MatTensorDetector.get_tensor_info(tensor)
        assert info["shape"] == (10, 20)
        assert "float32" in info["dtype"]


class TestRecoveryStrategies:
    """Test recovery strategies."""

    def test_garbage_collection_recovery(self):
        """Test garbage collection recovery."""
        success, method = MaterializationRecoveryStrategy.strategy_garbage_collection()
        assert success is True
        assert method == "garbage_collection"

    def test_cache_clear_recovery(self):
        """Test cache clear recovery."""
        success, method = MaterializationRecoveryStrategy.strategy_cache_clear()
        assert success is True
        assert method == "cache_clear"

    def test_memory_reset_recovery(self):
        """Test memory reset recovery."""
        success, method = MaterializationRecoveryStrategy.strategy_memory_reset()
        assert success is True
        assert method == "memory_reset"

    def test_all_strategies(self):
        """Test all recovery strategies."""
        results = MaterializationRecoveryStrategy.try_all_strategies()
        assert len(results) >= 3


class TestMaterializationPreventionFramework:
    """Test materialization prevention framework."""

    def test_framework_initialization(self):
        """Test framework initialization."""
        framework = MaterializationPreventionFramework("test-model")
        assert framework.model_name == "test-model"
        assert framework.prevention_enabled is True
        assert framework.recovery_enabled is True

    def test_framework_setup_prevention_environment(self):
        """Test environment setup."""
        framework = MaterializationPreventionFramework()
        env_vars = framework.setup_prevention_environment()

        # Should have set up some environment variables
        assert isinstance(env_vars, dict)

    def test_framework_detect_materialization_no_meta_tensors(self):
        """Test detection with no meta tensors."""
        framework = MaterializationPreventionFramework()

        mock_model = Mock()
        mock_model.named_parameters = Mock(return_value=[])
        mock_model.named_buffers = Mock(return_value=[])
        mock_model.named_modules = Mock(return_value=[])

        has_meta = framework.detect_materialization(mock_model)
        assert has_meta is False

    def test_framework_attempt_recovery(self):
        """Test recovery attempt."""
        framework = MaterializationPreventionFramework()
        success = framework.attempt_recovery()

        # Recovery should at least be attempted
        assert isinstance(success, bool)

    def test_framework_status_report(self):
        """Test status report generation."""
        framework = MaterializationPreventionFramework("test-model")
        report = framework.get_status_report()

        assert report["model_name"] == "test-model"
        assert "prevention_enabled" in report
        assert "recovery_enabled" in report


class TestPreventionFrameworkIntegration:
    """Test full prevention framework integration."""

    def test_prevent_meta_tensor_materialization(self):
        """Test framework creation and initialization."""
        framework = prevent_meta_tensor_materialization("integration-test")
        assert framework.model_name == "integration-test"


class TestVerifyModelIntegrity:
    """Test model integrity verification."""

    def test_verify_valid_model(self):
        """Test verification of valid model."""
        mock_model = Mock()
        mock_model.named_parameters = Mock(return_value=[])
        mock_model.named_buffers = Mock(return_value=[])
        mock_model.named_modules = Mock(return_value=[])

        result = verify_model_integrity(mock_model, "test-model")
        assert result is True

    def test_verify_model_with_meta_tensors(self):
        """Test verification fails for model with meta tensors."""
        meta_tensor = Mock()
        meta_tensor.device.type = "meta"

        mock_model = Mock()
        mock_model.named_parameters = Mock(return_value=[("weight", meta_tensor)])
        mock_model.named_buffers = Mock(return_value=[])
        mock_model.named_modules = Mock(return_value=[])

        with pytest.raises(MetaTensorException):
            verify_model_integrity(mock_model, "test-model")


class TestGuardRailReport:
    """Test guard rail report generation."""

    def test_report_to_dict(self):
        """Test report serialization."""
        report = GuardRailReport(
            name="test",
            status=GuardRailStatus.PASSED,
            timestamp=datetime.now(UTC),
            details={"key": "value"},
            error=None,
            duration_ms=10.5,
        )

        data = report.to_dict()
        assert data["name"] == "test"
        assert data["status"] == "passed"
        assert "timestamp" in data
        assert data["duration_ms"] == 10.5


class TestMaterializationEvent:
    """Test materialization event tracking."""

    def test_event_to_dict(self):
        """Test event serialization."""
        event = MaterializationEvent(
            timestamp=datetime.now(UTC),
            location=TensorLocation.PARAMETERS,
            tensor_name="weight",
            tensor_shape=(10, 20),
            tensor_dtype="float32",
            model_name="test",
        )

        data = event.to_dict()
        assert data["tensor_name"] == "weight"
        assert data["location"] == "parameters"
        assert data["model_name"] == "test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
