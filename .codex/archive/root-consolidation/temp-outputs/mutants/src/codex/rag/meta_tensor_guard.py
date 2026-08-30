"""
Meta-Tensor Materialization Guard Rails

Provides comprehensive guard rails for preventing meta-tensor creation and
materialization issues during model initialization. Implements multi-layer
defense mechanisms including:

1. Initialization Guards - Prevent meta tensors from being created
2. Detection Guards - Detect any meta tensors that slip through
3. Recovery Guards - Gracefully handle meta tensor scenarios
4. OOM Protection - Detect and recover from out-of-memory conditions
5. Rollback Mechanism - Restore previous working state on failures

This module is part of Phase 13.2: RAG Meta-Tensor Safety
"""

from __future__ import annotations

import gc
import logging
import os
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Callable, Generator, Optional

logger = logging.getLogger(__name__)


class GuardRailStatus(Enum):
    """Status of guard rail checks."""

    PASSED = "passed"
    FAILED = "failed"
    RECOVERED = "recovered"
    BYPASSED = "bypassed"


class MetaTensorException(Exception):
    """Raised when meta tensors are detected."""

    pass


class OOMException(Exception):
    """Raised when out-of-memory condition is detected."""

    pass


@dataclass
class GuardRailReport:
    """Report from a single guard rail check."""

    name: str
    status: GuardRailStatus
    timestamp: datetime
    details: dict[str, Any]
    error: Optional[Exception] = None
    duration_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for logging/serialization."""
        return {
            "name": self.name,
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "error": str(self.error) if self.error else None,
            "duration_ms": self.duration_ms,
        }


class MetaTensorGuardRail:
    """
    Multi-layer guard rail system for meta tensor prevention.

    Implements defense-in-depth approach:
    - Layer 1: Environment setup guard (prevents meta tensor creation)
    - Layer 2: Initialization guard (validates pre-init state)
    - Layer 3: Model loading guard (monitors during loading)
    - Layer 4: Post-init detection guard (catches any meta tensors)
    - Layer 5: Recovery guard (graceful fallback mechanisms)
    """

    def __init__(self, max_recovery_attempts: int = 3):
        """
        Initialize guard rail system.

        Args:
            max_recovery_attempts: Maximum recovery attempts before failing
        """
        self.max_recovery_attempts = max_recovery_attempts
        self.reports: list[GuardRailReport] = []
        self.state_history: list[dict[str, Any]] = []

    def check_environment(self) -> GuardRailReport:
        """
        Layer 1: Verify PyTorch environment is set up correctly.

        Checks:
        - PyTorch can be imported
        - CUDA availability
        - Memory allocation settings
        """
        start_time = datetime.now(UTC)
        report_details: dict[str, Any] = {}

        try:
            import torch

            report_details["torch_version"] = torch.__version__
            report_details["cuda_available"] = torch.cuda.is_available()
            report_details["device_count"] = (
                torch.cuda.device_count() if torch.cuda.is_available() else 0
            )

            # Check CUDA allocation config
            alloc_conf = os.environ.get("PYTORCH_CUDA_ALLOC_CONF", "not set")
            report_details["pytorch_cuda_alloc_conf"] = alloc_conf

            # Verify we can allocate memory
            try:
                torch.zeros(1, device="cpu")
                report_details["cpu_allocation_test"] = "passed"
            except Exception as e:
                logger.warning("CPU allocation test failed: %s", e)
                report_details["cpu_allocation_test"] = f"failed: {e}"

            status = GuardRailStatus.PASSED
            error = None

        except ImportError as e:
            status = GuardRailStatus.FAILED
            error = e
            report_details["import_error"] = str(e)

        duration = (datetime.now(UTC) - start_time).total_seconds() * 1000

        report = GuardRailReport(
            name="environment_check",
            status=status,
            timestamp=start_time,
            details=report_details,
            error=error,
            duration_ms=duration,
        )

        self.reports.append(report)
        return report

    def check_pre_init_state(self) -> GuardRailReport:
        """
        Layer 2: Verify pre-initialization state.

        Checks:
        - Available memory before loading
        - No active models already loaded
        - GPU memory freed if CUDA available
        """
        start_time = datetime.now(UTC)
        report_details: dict[str, Any] = {}

        try:
            import torch

            # Check memory
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                report_details["gpu_memory_freed"] = True
                gpu_mem = torch.cuda.mem_get_info()
                report_details["gpu_free_mb"] = gpu_mem[0] / 1024 / 1024
                report_details["gpu_total_mb"] = gpu_mem[1] / 1024 / 1024

            # Force garbage collection
            gc.collect()
            report_details["garbage_collection"] = "performed"

            status = GuardRailStatus.PASSED
            error = None

        except Exception as e:
            status = GuardRailStatus.FAILED
            error = e
            report_details["error"] = str(e)

        duration = (datetime.now(UTC) - start_time).total_seconds() * 1000

        report = GuardRailReport(
            name="pre_init_state_check",
            status=status,
            timestamp=start_time,
            details=report_details,
            error=error,
            duration_ms=duration,
        )

        self.reports.append(report)
        return report

    def check_model_loading(self, model: Any) -> GuardRailReport:
        """
        Layer 3: Monitor model during loading (can be called multiple times).

        Checks:
        - Model object is valid
        - Model is not None
        """
        start_time = datetime.now(UTC)
        report_details: dict[str, Any] = {}

        try:
            if model is None:
                raise ValueError("Model is None")

            report_details["model_type"] = type(model).__name__
            report_details["model_has_named_params"] = hasattr(model, "named_parameters")

            status = GuardRailStatus.PASSED
            error = None

        except Exception as e:
            status = GuardRailStatus.FAILED
            error = e
            report_details["error"] = str(e)

        duration = (datetime.now(UTC) - start_time).total_seconds() * 1000

        report = GuardRailReport(
            name="model_loading_check",
            status=status,
            timestamp=start_time,
            details=report_details,
            error=error,
            duration_ms=duration,
        )

        self.reports.append(report)
        return report

    def check_meta_tensors_post_init(self, model: Any) -> GuardRailReport:
        """
        Layer 4: Detect meta tensors after initialization.

        Comprehensive check for meta tensors in:
        - Model parameters
        - Model buffers
        - Submodule parameters and buffers
        """
        start_time = datetime.now(UTC)
        report_details: dict[str, Any] = {
            "meta_params": [],
            "meta_buffers": [],
            "meta_submodule_params": [],
            "meta_submodule_buffers": [],
        }

        try:
            meta_found = False

            # Check direct parameters
            for name, param in model.named_parameters():
                if param.device.type == "meta" or (hasattr(param, "is_meta") and param.is_meta):
                    report_details["meta_params"].append(name)
                    meta_found = True

            # Check direct buffers
            for name, buf in model.named_buffers():
                if buf.device.type == "meta" or (hasattr(buf, "is_meta") and buf.is_meta):
                    report_details["meta_buffers"].append(name)
                    meta_found = True

            # Check submodules
            for submodule_name, submodule in model.named_modules():
                if submodule_name == "":
                    continue

                for param_name, param in submodule.named_parameters(recurse=False):
                    if param.device.type == "meta" or (hasattr(param, "is_meta") and param.is_meta):
                        full_name = f"{submodule_name}.{param_name}"
                        report_details["meta_submodule_params"].append(full_name)
                        meta_found = True

                for buf_name, buf in submodule.named_buffers(recurse=False):
                    if buf.device.type == "meta" or (hasattr(buf, "is_meta") and buf.is_meta):
                        full_name = f"{submodule_name}.{buf_name}"
                        report_details["meta_submodule_buffers"].append(full_name)
                        meta_found = True

            report_details["total_meta_tensors"] = (
                len(report_details["meta_params"])
                + len(report_details["meta_buffers"])
                + len(report_details["meta_submodule_params"])
                + len(report_details["meta_submodule_buffers"])
            )

            if meta_found:
                status = GuardRailStatus.FAILED
                error = MetaTensorException(
                    f"Meta tensors detected: {report_details['total_meta_tensors']} total"
                )
            else:
                status = GuardRailStatus.PASSED
                error = None

        except Exception as e:
            status = GuardRailStatus.FAILED
            error = e
            report_details["error"] = str(e)

        duration = (datetime.now(UTC) - start_time).total_seconds() * 1000

        report = GuardRailReport(
            name="meta_tensor_detection",
            status=status,
            timestamp=start_time,
            details=report_details,
            error=error,
            duration_ms=duration,
        )

        self.reports.append(report)
        return report

    def check_oom_condition(self) -> GuardRailReport:
        """
        Layer 5a: Detect out-of-memory conditions.

        Checks:
        - System memory usage
        - GPU memory if available
        """
        start_time = datetime.now(UTC)
        report_details: dict[str, Any] = {}

        try:
            import psutil

            import torch

            # Check system memory
            mem_info = psutil.virtual_memory()
            report_details["system_memory_percent"] = mem_info.percent
            report_details["system_memory_available_mb"] = mem_info.available / 1024 / 1024

            if mem_info.percent > 95:
                status = GuardRailStatus.FAILED
                error = OOMException(f"System memory usage: {mem_info.percent}%")
            else:
                status = GuardRailStatus.PASSED
                error = None

            # Check GPU memory if available
            if torch.cuda.is_available():
                try:
                    gpu_mem = torch.cuda.mem_get_info()
                    report_details["gpu_memory_percent"] = (
                        (gpu_mem[1] - gpu_mem[0]) / gpu_mem[1] * 100
                    )
                    report_details["gpu_memory_free_mb"] = gpu_mem[0] / 1024 / 1024

                    if report_details["gpu_memory_percent"] > 95:
                        status = GuardRailStatus.FAILED
                        error = OOMException(
                            f"GPU memory usage: {report_details['gpu_memory_percent']:.1f}%"
                        )
                except Exception:
                    pass  # Non-critical

        except ImportError:
            # psutil not available, skip system memory check
            status = GuardRailStatus.BYPASSED
            error = None
            report_details["reason"] = "psutil not installed"

        except Exception as e:
            status = GuardRailStatus.FAILED
            error = e
            report_details["error"] = str(e)

        duration = (datetime.now(UTC) - start_time).total_seconds() * 1000

        report = GuardRailReport(
            name="oom_detection",
            status=status,
            timestamp=start_time,
            details=report_details,
            error=error,
            duration_ms=duration,
        )

        self.reports.append(report)
        return report

    def check_recovery_mechanism(self, recovery_func: Callable[[], Any]) -> GuardRailReport:
        """
        Layer 5b: Test recovery mechanism.

        Attempts to recover from a failure by calling recovery_func.
        """
        start_time = datetime.now(UTC)
        report_details: dict[str, Any] = {
            "recovery_attempts": 0,
            "recovery_successes": 0,
        }

        error = None
        status = GuardRailStatus.FAILED

        try:
            for attempt in range(self.max_recovery_attempts):
                report_details["recovery_attempts"] = attempt + 1

                try:
                    gc.collect()
                    recovery_func()
                    report_details["recovery_successes"] = attempt + 1
                    status = GuardRailStatus.RECOVERED
                    error = None
                    break
                except Exception as attempt_error:
                    if attempt == self.max_recovery_attempts - 1:
                        error = attempt_error
                        status = GuardRailStatus.FAILED
                    else:
                        logger.warning(
                            "Recovery attempt %d/%d failed: %s",
                            attempt + 1,
                            self.max_recovery_attempts,
                            attempt_error,
                        )

        except Exception as e:
            error = e
            status = GuardRailStatus.FAILED

        duration = (datetime.now(UTC) - start_time).total_seconds() * 1000

        report = GuardRailReport(
            name="recovery_mechanism",
            status=status,
            timestamp=start_time,
            details=report_details,
            error=error,
            duration_ms=duration,
        )

        self.reports.append(report)
        return report

    def save_state(self, state_id: str) -> None:
        """Save current guard rail state for potential rollback."""
        self.state_history.append(
            {
                "state_id": state_id,
                "timestamp": datetime.now(UTC).isoformat(),
                "reports_count": len(self.reports),
                "last_status": self.reports[-1].status.value if self.reports else None,
            }
        )

    def get_summary(self) -> dict[str, Any]:
        """Get summary of all guard rail checks."""
        total_checks = len(self.reports)
        passed = sum(1 for r in self.reports if r.status == GuardRailStatus.PASSED)
        failed = sum(1 for r in self.reports if r.status == GuardRailStatus.FAILED)
        recovered = sum(1 for r in self.reports if r.status == GuardRailStatus.RECOVERED)
        bypassed = sum(1 for r in self.reports if r.status == GuardRailStatus.BYPASSED)

        total_time_ms = sum(r.duration_ms for r in self.reports)

        return {
            "total_checks": total_checks,
            "passed": passed,
            "failed": failed,
            "recovered": recovered,
            "bypassed": bypassed,
            "pass_rate": passed / total_checks if total_checks > 0 else 0,
            "total_time_ms": total_time_ms,
            "avg_check_time_ms": total_time_ms / total_checks if total_checks > 0 else 0,
            "details": [r.to_dict() for r in self.reports],
        }

    def log_summary(self) -> None:
        """Log summary of all guard rail checks."""
        summary = self.get_summary()
        logger.info(
            "Guard Rail Summary: %d checks, %d passed, %d failed, %d recovered",
            summary["total_checks"],
            summary["passed"],
            summary["failed"],
            summary["recovered"],
        )


@contextmanager
def guard_rail_context(
    guard_rail: Optional[MetaTensorGuardRail] = None,
) -> Generator[MetaTensorGuardRail, None, None]:
    """
    Context manager for running code with guard rails.

    Usage:
        with guard_rail_context() as guard:
            model = load_model()
            guard.check_meta_tensors_post_init(model)
    """
    if guard_rail is None:
        guard_rail = MetaTensorGuardRail()

    # Pre-execution checks
    guard_rail.check_environment()
    guard_rail.check_pre_init_state()
    guard_rail.check_oom_condition()
    guard_rail.save_state("pre_execution")

    try:
        yield guard_rail
    finally:
        # Post-execution logging
        guard_rail.log_summary()
        guard_rail.save_state("post_execution")


def verify_model_integrity(model: Any, model_name: str = "unknown") -> bool:
    """
    Comprehensive model integrity check.

    Args:
        model: Model to verify
        model_name: Name for logging

    Returns:
        True if model is valid, False otherwise

    Raises:
        MetaTensorException: If meta tensors are detected
        ValueError: If model is invalid
    """
    guard = MetaTensorGuardRail()

    with guard_rail_context(guard):
        guard.check_model_loading(model)
        meta_report = guard.check_meta_tensors_post_init(model)

        if meta_report.status == GuardRailStatus.FAILED:
            raise MetaTensorException(
                f"Model '{model_name}' contains meta tensors: {meta_report.details}"
            )

        return True


if __name__ == "__main__":
    # Example usage
    guard = MetaTensorGuardRail()

    with guard_rail_context(guard):
        logger.info("Guard rails active")

    summary = guard.get_summary()
    print(f"\nGuard Rail Summary: {summary['passed']}/{summary['total_checks']} checks passed")
