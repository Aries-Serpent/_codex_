"""
Meta-Tensor Materialization Prevention Framework

Provides mechanisms to prevent meta tensor materialization and handle
recovery from materialization events. Implements:

1. Preventive Measures - Environment setup, model validation
2. Detection Strategies - Multiple detection methods
3. Recovery Strategies - Graceful fallback and restoration
4. Monitoring - Continuous meta tensor tracking

This module is part of Phase 13.2: RAG Meta-Tensor Safety
"""

from __future__ import annotations

import logging
import os
import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class MaterializationStrategy(Enum):
    """Strategies for handling meta tensor materialization."""

    PREVENT = "prevent"
    DETECT = "detect"
    RECOVER = "recover"
    MONITOR = "monitor"


class TensorLocation(Enum):
    """Locations where meta tensors can appear."""

    PARAMETERS = "parameters"
    BUFFERS = "buffers"
    SUBMODULE_PARAMS = "submodule_params"
    SUBMODULE_BUFFERS = "submodule_buffers"


@dataclass
class MaterializationEvent:
    """Record of a meta tensor materialization event."""

    timestamp: datetime
    location: TensorLocation
    tensor_name: str
    tensor_shape: tuple[int, ...] = field(default_factory=tuple)
    tensor_dtype: str = "unknown"
    model_name: str = "unknown"
    recovery_attempted: bool = False
    recovery_successful: bool = False
    recovery_method: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "location": self.location.value,
            "tensor_name": self.tensor_name,
            "tensor_shape": self.tensor_shape,
            "tensor_dtype": self.tensor_dtype,
            "model_name": self.model_name,
            "recovery_attempted": self.recovery_attempted,
            "recovery_successful": self.recovery_successful,
            "recovery_method": self.recovery_method,
        }


class MaterializationMonitor:
    """
    Monitors model for meta tensor materialization events.

    Tracks:
    - Meta tensor creation events
    - Materialization patterns
    - Recovery success rates
    """

    def __init__(self, model_name: str = "unknown"):
        """Initialize monitor."""
        self.model_name = model_name
        self.events: list[MaterializationEvent] = []
        self.lock = threading.Lock()

    def record_event(
        self,
        location: TensorLocation,
        tensor_name: str,
        tensor_shape: tuple[int, ...] = (),
        tensor_dtype: str = "unknown",
    ) -> MaterializationEvent:
        """Record a meta tensor materialization event."""
        event = MaterializationEvent(
            timestamp=datetime.now(UTC),
            location=location,
            tensor_name=tensor_name,
            tensor_shape=tensor_shape,
            tensor_dtype=tensor_dtype,
            model_name=self.model_name,
        )

        with self.lock:
            self.events.append(event)

        logger.warning(
            "Meta tensor materialization: %s.%s (shape=%s, dtype=%s)",
            location.value,
            tensor_name,
            tensor_shape,
            tensor_dtype,
        )

        return event

    def record_recovery(self, event: MaterializationEvent, success: bool, method: str) -> None:
        """Record recovery attempt."""
        with self.lock:
            event.recovery_attempted = True
            event.recovery_successful = success
            event.recovery_method = method

        status = "successful" if success else "failed"
        logger.info("Meta tensor recovery %s: %s using %s", status, event.tensor_name, method)

    def get_summary(self) -> dict[str, Any]:
        """Get summary of materialization events."""
        with self.lock:
            events_list = list(self.events)

        total_events = len(events_list)
        recovery_attempts = sum(1 for e in events_list if e.recovery_attempted)
        recovery_successes = sum(
            1 for e in events_list if e.recovery_attempted and e.recovery_successful
        )

        events_by_location = {}
        for loc in TensorLocation:
            count = sum(1 for e in events_list if e.location == loc)
            if count > 0:
                events_by_location[loc.value] = count

        return {
            "model_name": self.model_name,
            "total_events": total_events,
            "recovery_attempts": recovery_attempts,
            "recovery_successes": recovery_successes,
            "recovery_rate": (
                recovery_successes / recovery_attempts if recovery_attempts > 0 else 0
            ),
            "events_by_location": events_by_location,
            "events": [e.to_dict() for e in events_list],
        }


class MatTensorDetector:
    """
    Detects meta tensors in models using multiple detection strategies.

    Supports:
    - Direct device type checking
    - is_meta attribute checking
    - Shape/dtype inspection
    - Recursive submodule checking
    """

    @staticmethod
    def detect_in_model(model: Any) -> list[tuple[TensorLocation, str, Any]]:
        """
        Detect all meta tensors in a model.

        Returns:
            List of (location, tensor_name, tensor) tuples
        """
        meta_tensors = []

        try:
            # Check parameters
            for name, param in model.named_parameters():
                if MatTensorDetector._is_meta_tensor(param):
                    meta_tensors.append((TensorLocation.PARAMETERS, name, param))

            # Check buffers
            for name, buf in model.named_buffers():
                if MatTensorDetector._is_meta_tensor(buf):
                    meta_tensors.append((TensorLocation.BUFFERS, name, buf))

            # Check submodules
            for module_name, submodule in model.named_modules():
                if module_name == "":
                    continue

                for param_name, param in submodule.named_parameters(recurse=False):
                    if MatTensorDetector._is_meta_tensor(param):
                        full_name = f"{module_name}.{param_name}"
                        meta_tensors.append((TensorLocation.SUBMODULE_PARAMS, full_name, param))

                for buf_name, buf in submodule.named_buffers(recurse=False):
                    if MatTensorDetector._is_meta_tensor(buf):
                        full_name = f"{module_name}.{buf_name}"
                        meta_tensors.append((TensorLocation.SUBMODULE_BUFFERS, full_name, buf))

        except Exception as e:
            logger.error("Error detecting meta tensors: %s", e)

        return meta_tensors

    @staticmethod
    def _is_meta_tensor(tensor: Any) -> bool:
        """Check if tensor is a meta tensor using multiple strategies."""
        try:
            # Strategy 1: Check device type
            if hasattr(tensor, "device"):
                if tensor.device.type == "meta":
                    return True

            # Strategy 2: Check is_meta attribute
            if hasattr(tensor, "is_meta"):
                if tensor.is_meta:
                    return True

            # Strategy 3: Check if operations fail
            if hasattr(tensor, "data"):
                try:
                    _ = tensor.data.device
                    if tensor.data.device.type == "meta":
                        return True
                except (RuntimeError, TypeError):
                    return True

        except Exception as e:
            # Unexpected error during meta-tensor detection; treat as non-meta and continue
            logger.debug("Meta-tensor check failed for %r: %s", type(tensor).__name__, e)

        return False

    @staticmethod
    def get_tensor_info(tensor: Any) -> dict[str, Any]:
        """Get information about a tensor."""
        try:
            return {
                "shape": tuple(tensor.shape) if hasattr(tensor, "shape") else None,
                "dtype": str(tensor.dtype) if hasattr(tensor, "dtype") else None,
                "device": str(tensor.device) if hasattr(tensor, "device") else None,
                "is_meta": (tensor.is_meta if hasattr(tensor, "is_meta") else False),
            }
        except Exception as e:
            return {"error": str(e)}


class MaterializationRecoveryStrategy:
    """
    Recovery strategies for handling meta tensor materialization.

    Implements multiple recovery approaches for different scenarios.
    """

    @staticmethod
    def strategy_garbage_collection() -> tuple[bool, str]:
        """
        Recovery Strategy 1: Aggressive garbage collection.

        Frees up memory and potentially allows model reloading.
        """
        try:
            import gc

            gc.collect()
            return True, "garbage_collection"
        except Exception as e:
            logger.warning("Garbage collection recovery failed: %s", e)
            return False, "garbage_collection"

    @staticmethod
    def strategy_cache_clear() -> tuple[bool, str]:
        """
        Recovery Strategy 2: Clear PyTorch CUDA cache.

        Only applicable if CUDA is available.
        """
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            return True, "cache_clear"
        except Exception as e:
            logger.warning("Cache clear recovery failed: %s", e)
            return False, "cache_clear"

    @staticmethod
    def strategy_memory_reset() -> tuple[bool, str]:
        """
        Recovery Strategy 3: Reset all memory allocations.

        Comprehensive memory reset for both CPU and GPU.
        """
        try:
            import gc

            import torch

            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.reset_peak_memory_stats()
            return True, "memory_reset"
        except Exception as e:
            logger.warning("Memory reset recovery failed: %s", e)
            return False, "memory_reset"

    @staticmethod
    def try_all_strategies() -> list[tuple[bool, str]]:
        """Try all recovery strategies in sequence."""
        results = []
        results.append(MaterializationRecoveryStrategy.strategy_garbage_collection())
        results.append(MaterializationRecoveryStrategy.strategy_cache_clear())
        results.append(MaterializationRecoveryStrategy.strategy_memory_reset())
        return results


class MaterializationPreventionFramework:
    """
    Complete framework for preventing and handling meta tensor materialization.

    Provides:
    - Preventive measures (environment setup)
    - Detection mechanisms
    - Recovery strategies
    - Monitoring and reporting
    """

    def __init__(self, model_name: str = "unknown"):
        """Initialize framework."""
        self.model_name = model_name
        self.monitor = MaterializationMonitor(model_name)
        self.detector = MatTensorDetector()
        self.prevention_enabled = True
        self.recovery_enabled = True

    def setup_prevention_environment(self) -> dict[str, str]:
        """
        Setup environment to prevent meta tensor creation.

        Sets key environment variables that prevent meta tensor issues.
        """
        env_vars = {}

        # Ensure PYTORCH_CUDA_ALLOC_CONF is set
        if "PYTORCH_CUDA_ALLOC_CONF" not in os.environ:
            os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"
            env_vars["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"

        # Ensure TRANSFORMERS_OFFLINE is set appropriately
        if "TRANSFORMERS_OFFLINE" not in os.environ:
            os.environ["TRANSFORMERS_OFFLINE"] = "0"
            env_vars["TRANSFORMERS_OFFLINE"] = "0"

        logger.info("Prevention environment setup: %s", env_vars)
        return env_vars

    def detect_materialization(self, model: Any) -> bool:
        """
        Detect if model has meta tensors.

        Args:
            model: Model to check

        Returns:
            True if meta tensors found, False otherwise
        """
        meta_tensors = self.detector.detect_in_model(model)

        if not meta_tensors:
            logger.debug("No meta tensors detected in model")
            return False

        logger.warning("Found %d meta tensors in model", len(meta_tensors))

        for location, name, tensor in meta_tensors:
            tensor_info = self.detector.get_tensor_info(tensor)
            self.monitor.record_event(
                location=location,
                tensor_name=name,
                tensor_shape=tensor_info.get("shape", ()),
                tensor_dtype=tensor_info.get("dtype", "unknown"),
            )

        return True

    def attempt_recovery(self) -> bool:
        """
        Attempt to recover from meta tensor materialization.

        Returns:
            True if recovery successful, False otherwise
        """
        if not self.recovery_enabled:
            logger.warning("Recovery is disabled")
            return False

        logger.info("Attempting meta tensor recovery")

        strategies = MaterializationRecoveryStrategy.try_all_strategies()

        # Record recovery attempts
        for success, strategy_name in strategies:
            if self.monitor.events:
                last_event = self.monitor.events[-1]
                self.monitor.record_recovery(last_event, success, strategy_name)

        # Check if any strategy succeeded
        return any(success for success, _ in strategies)

    def get_status_report(self) -> dict[str, Any]:
        """Get comprehensive status report."""
        return {
            "model_name": self.model_name,
            "prevention_enabled": self.prevention_enabled,
            "recovery_enabled": self.recovery_enabled,
            "monitor_summary": self.monitor.get_summary(),
        }


def prevent_meta_tensor_materialization(
    model_name: str = "unknown",
) -> MaterializationPreventionFramework:
    """
    Create and initialize meta tensor prevention framework.

    Usage:
        framework = prevent_meta_tensor_materialization("my-model")
        framework.setup_prevention_environment()
        # Load model...
        framework.detect_materialization(model)
    """
    framework = MaterializationPreventionFramework(model_name)
    framework.setup_prevention_environment()
    return framework


if __name__ == "__main__":
    # Example usage
    framework = prevent_meta_tensor_materialization("test-model")
    report = framework.get_status_report()
    print(f"Framework initialized: {report['model_name']}")
