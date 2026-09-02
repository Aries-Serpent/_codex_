"""
from codex.logging.adapter import LoggerAdapter, NullLogger, get_default_logger
Blue-green deployment and traffic management for inference serving.

This module provides zero-downtime deployment strategies with gradual rollout,
automatic failover, and rollback capabilities.
"""

import logging
import time

from aries_serpent_core.logging.adapter import get_default_logger

logger = logging.getLogger(__name__)
import random  # noqa: E402
from collections.abc import Callable  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from enum import Enum  # noqa: E402
from typing import Any, Optional  # noqa: E402


class DeploymentStrategy(Enum):
    """Deployment strategy types."""

    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    ROLLING = "rolling"


@dataclass
class DeploymentConfig:
    """Configuration for deployment strategy."""

    strategy: DeploymentStrategy = DeploymentStrategy.BLUE_GREEN
    health_check_interval_s: int = 10
    health_check_timeout_s: int = 5
    error_threshold_percent: float = 5.0
    min_healthy_duration_s: int = 60
    rollout_duration_s: int = 300


class TrafficSplitter:
    """
    Manages traffic splitting between blue and green deployments.

    Features:
    - Gradual rollout (0% → 100%)
    - Health-based automatic failover
    - Rollback on error spike
    - Weighted routing

    Example:
        >>> splitter = TrafficSplitter()
        >>> splitter.set_weights(blue=80, green=20)  # 80% to blue, 20% to green
        >>> target = splitter.route_request(request_id)
    """

    def __init__(self) -> None:
        self.blue_weight: float = 100.0
        self.green_weight: float = 0.0
        self.blue_healthy = True
        self.green_healthy = True
        self.blue_errors = 0
        self.green_errors = 0
        self.blue_requests = 0
        self.green_requests = 0

    def set_weights(self, blue: int, green: int):
        """
        set traffic weights for blue and green.

        Args:
            blue: Percentage of traffic to blue (0-100)
            green: Percentage of traffic to green (0-100)
        """
        total = blue + green
        if total == 0:
            raise ValueError("At least one deployment must have non-zero weight")

        self.blue_weight = (blue / total) * 100
        self.green_weight = (green / total) * 100

    def route_request(self, request_id: str) -> str:
        """
        Route request to blue or green deployment.

        Args:
            request_id: Unique request identifier

        Returns:
            "blue" or "green" indicating target deployment
        """
        # Health-based routing
        if not self.blue_healthy and self.green_healthy:
            return "green"
        if not self.green_healthy and self.blue_healthy:
            return "blue"
        if not self.blue_healthy and not self.green_healthy:
            # Both unhealthy, failover to blue
            return "blue"

        # Weighted routing
        rand = random.random() * 100  # nosec B311 — non-cryptographic ML sampling/shuffling
        if rand < self.blue_weight:
            self.blue_requests += 1
            return "blue"
        self.green_requests += 1
        return "green"

    def record_error(self, deployment: str):
        """Record error for deployment."""
        if deployment == "blue":
            self.blue_errors += 1
        else:
            self.green_errors += 1

    def get_error_rate(self, deployment: str) -> float:
        """Get error rate for deployment."""
        if deployment == "blue":
            if self.blue_requests == 0:
                return 0.0
            return (self.blue_errors / self.blue_requests) * 100
        if self.green_requests == 0:
            return 0.0
        return (self.green_errors / self.green_requests) * 100

    def update_health(self, deployment: str, healthy: bool):
        """Update health status for deployment."""
        if deployment == "blue":
            self.blue_healthy = healthy
        else:
            self.green_healthy = healthy

    def reset_stats(self) -> None:
        """Reset error and request counters."""
        self.blue_errors = 0
        self.green_errors = 0
        self.blue_requests = 0
        self.green_requests = 0


class BlueGreenDeployment:
    """
    Blue-green deployment manager with automatic rollout and rollback.

    Features:
    - Gradual traffic shift (0% → 100%)
    - Continuous health monitoring
    - Automatic rollback on failures
    - Configurable rollout duration

    Example:
        >>> deployment = BlueGreenDeployment(config)
        >>> deployment.start_rollout(new_model_version="v2")
        >>> # Monitors health and gradually shifts traffic
        >>> status = deployment.get_status()
    """

    def __init__(
        self,
        config: Optional[DeploymentConfig] = None,
        health_check_fn: Optional[Callable[[str], bool]] = None,
    ):
        self.config = config or DeploymentConfig()
        self.health_check_fn = health_check_fn
        self.splitter = TrafficSplitter()
        self.rollout_start_time: Optional[float] = None
        self.rollout_active = False
        self.rollback_triggered = False
        self.current_blue_version = "v1"
        self.current_green_version: Optional[str] = None

    def start_rollout(self, new_model_version: str):
        """
        Start gradual rollout of new model version.

        Args:
            new_model_version: Version identifier for new model
        """
        self.current_green_version = new_model_version
        self.rollout_start_time = time.time()
        self.rollout_active = True
        self.rollback_triggered = False
        self.splitter.reset_stats()

        get_default_logger().info(
            f"Starting rollout: {self.current_blue_version} → {new_model_version}"
        )

    def update_rollout(self) -> dict[str, Any]:
        """
        Update rollout progress and health checks.

        Returns:
            Status dictionary with progress and health info
        """
        if not self.rollout_active:
            return {"status": "idle", "progress": 0}

        elapsed = time.time() - self.rollout_start_time  # type: ignore[operator]
        progress = min(elapsed / self.config.rollout_duration_s, 1.0)

        # Update traffic weights
        green_weight = int(progress * 100)
        blue_weight = 100 - green_weight
        self.splitter.set_weights(blue=blue_weight, green=green_weight)

        # Health checks
        blue_healthy = self._check_health("blue")
        green_healthy = self._check_health("green")
        self.splitter.update_health("blue", blue_healthy)
        self.splitter.update_health("green", green_healthy)

        # Check error rates
        blue_error_rate = self.splitter.get_error_rate("blue")
        green_error_rate = self.splitter.get_error_rate("green")

        # Rollback logic
        if green_error_rate > self.config.error_threshold_percent:
            self.trigger_rollback("High error rate in green deployment")
            return {
                "status": "rolled_back",
                "progress": progress,
                "reason": "High error rate",
                "green_error_rate": green_error_rate,
            }

        if not green_healthy and self.splitter.green_requests > 10:
            self.trigger_rollback("Green deployment unhealthy")
            return {
                "status": "rolled_back",
                "progress": progress,
                "reason": "Health check failed",
            }

        # Complete rollout
        if progress >= 1.0 and elapsed > self.config.min_healthy_duration_s:
            self.complete_rollout()
            return {
                "status": "completed",
                "progress": 1.0,
                "new_version": self.current_green_version,
            }

        return {
            "status": "in_progress",
            "progress": progress,
            "blue_weight": blue_weight,
            "green_weight": green_weight,
            "blue_healthy": blue_healthy,
            "green_healthy": green_healthy,
            "blue_error_rate": blue_error_rate,
            "green_error_rate": green_error_rate,
        }

    def trigger_rollback(self, reason: str):
        """
        Trigger rollback to blue deployment.

        Args:
            reason: Reason for rollback
        """
        get_default_logger().info(f"Rollback triggered: {reason}")
        self.splitter.set_weights(blue=100, green=0)
        self.rollout_active = False
        self.rollback_triggered = True
        self.current_green_version = None

    def complete_rollout(self) -> None:
        """Complete rollout and promote green to blue."""
        get_default_logger().info(
            f"Rollout complete: {self.current_green_version} promoted to blue"
        )
        self.current_blue_version = self.current_green_version or self.current_blue_version
        self.current_green_version = None
        self.rollout_active = False
        self.splitter.set_weights(blue=100, green=0)

    def _check_health(self, deployment: str) -> bool:
        """Check health of deployment."""
        if self.health_check_fn:
            try:
                return self.health_check_fn(deployment)
            except (ValueError, TypeError, RuntimeError):
                get_default_logger().warning("Exception occurred", exc_info=True)
                return False
        return True

    def get_status(self) -> dict[str, Any]:
        """Get current deployment status."""
        return {
            "blue_version": self.current_blue_version,
            "green_version": self.current_green_version,
            "rollout_active": self.rollout_active,
            "rollback_triggered": self.rollback_triggered,
            "traffic_weights": {
                "blue": self.splitter.blue_weight,
                "green": self.splitter.green_weight,
            },
            "health": {
                "blue": self.splitter.blue_healthy,
                "green": self.splitter.green_healthy,
            },
        }
