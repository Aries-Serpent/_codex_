"""Tunnel Lifecycle: Secure channel setup, monitoring, and teardown.

Manages tunnel state transitions, health checks, and graceful cleanup.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class TunnelState(Enum):
    """Possible states for a tunnel."""

    CREATE = "create"
    ACTIVE = "active"
    MONITOR = "monitor"
    TEARDOWN = "teardown"


class TunnelError(Exception):
    """Raised when tunnel operations fail."""

    pass


@dataclass
class Tunnel:
    """Represents a secure transfer tunnel."""

    tunnel_id: str = field(default_factory=lambda: str(uuid4()))
    source_sandbox: str = ""
    destination_sandbox: str = ""
    state: TunnelState = TunnelState.CREATE
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    last_heartbeat: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    bytes_transferred: int = 0
    latency_ms: float = 0.0
    is_healthy: bool = True
    error_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tunnel_id": self.tunnel_id,
            "source_sandbox": self.source_sandbox,
            "destination_sandbox": self.destination_sandbox,
            "state": self.state.value,
            "created_at": self.created_at,
            "last_heartbeat": self.last_heartbeat,
            "bytes_transferred": self.bytes_transferred,
            "latency_ms": self.latency_ms,
            "is_healthy": self.is_healthy,
            "error_count": self.error_count,
        }


class TunnelLifecycle:
    """Manages tunnel lifecycle: creation, monitoring, teardown."""

    def __init__(self):
        """Initialize tunnel lifecycle manager."""
        self.tunnels: Dict[str, Tunnel] = {}
        self.tunnel_index: Dict[tuple, str] = {}

    def create_tunnel(
        self, source_sandbox: str, destination_sandbox: str
    ) -> Tunnel:
        """Create a new secure channel tunnel."""
        tunnel = Tunnel(
            source_sandbox=source_sandbox,
            destination_sandbox=destination_sandbox,
            state=TunnelState.CREATE,
        )
        self.tunnels[tunnel.tunnel_id] = tunnel
        self.tunnel_index[(source_sandbox, destination_sandbox)] = tunnel.tunnel_id
        logger.info(f"Tunnel created: {tunnel.tunnel_id}")
        return tunnel

    def activate_tunnel(self, tunnel_id: str) -> Tunnel:
        """Activate a tunnel for data transfer."""
        tunnel = self._get_tunnel(tunnel_id)
        if tunnel.state != TunnelState.CREATE:
            raise TunnelError(f"Cannot activate tunnel in {tunnel.state.value} state")

        tunnel.state = TunnelState.ACTIVE
        tunnel.last_heartbeat = datetime.now(timezone.utc).isoformat()
        logger.info(f"Tunnel activated: {tunnel_id}")
        return tunnel

    def record_heartbeat(self, tunnel_id: str, latency_ms: float = 0.0) -> None:
        """Record tunnel health check heartbeat."""
        tunnel = self._get_tunnel(tunnel_id)
        tunnel.last_heartbeat = datetime.now(timezone.utc).isoformat()
        tunnel.latency_ms = latency_ms
        tunnel.is_healthy = True
        logger.debug(f"Heartbeat recorded: {tunnel_id}, latency: {latency_ms}ms")

    def record_error(self, tunnel_id: str) -> None:
        """Record transfer error on tunnel."""
        tunnel = self._get_tunnel(tunnel_id)
        tunnel.error_count += 1

        if tunnel.error_count >= 3:
            tunnel.is_healthy = False
            logger.warning(f"Tunnel marked unhealthy: {tunnel_id}")

    def record_transfer(self, tunnel_id: str, bytes_count: int) -> None:
        """Record bytes transferred through tunnel."""
        tunnel = self._get_tunnel(tunnel_id)
        tunnel.bytes_transferred += bytes_count

    def mark_for_teardown(self, tunnel_id: str) -> Tunnel:
        """Mark tunnel for graceful teardown."""
        tunnel = self._get_tunnel(tunnel_id)
        tunnel.state = TunnelState.TEARDOWN
        logger.info(f"Tunnel marked for teardown: {tunnel_id}")
        return tunnel

    def teardown_tunnel(self, tunnel_id: str) -> Dict[str, Any]:
        """Perform graceful teardown of tunnel."""
        tunnel = self._get_tunnel(tunnel_id)
        tunnel.state = TunnelState.TEARDOWN

        cleanup_result = {
            "tunnel_id": tunnel_id,
            "bytes_transferred": tunnel.bytes_transferred,
            "total_errors": tunnel.error_count,
            "avg_latency_ms": tunnel.latency_ms,
        }

        del self.tunnels[tunnel_id]
        key = (tunnel.source_sandbox, tunnel.destination_sandbox)
        if key in self.tunnel_index:
            del self.tunnel_index[key]

        logger.info(f"Tunnel teardown complete: {tunnel_id}")
        return cleanup_result

    def get_tunnel(self, tunnel_id: str) -> Optional[Tunnel]:
        """Get tunnel by ID."""
        return self.tunnels.get(tunnel_id)

    def get_tunnel_by_route(
        self, source_sandbox: str, destination_sandbox: str
    ) -> Optional[Tunnel]:
        """Get tunnel by source and destination."""
        tunnel_id = self.tunnel_index.get((source_sandbox, destination_sandbox))
        if tunnel_id:
            return self.tunnels.get(tunnel_id)
        return None

    def get_all_active_tunnels(self) -> list:
        """Get all active tunnels."""
        return [
            t for t in self.tunnels.values() if t.state in (TunnelState.ACTIVE, TunnelState.MONITOR)
        ]

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on all tunnels."""
        active = self.get_all_active_tunnels()
        healthy = sum(1 for t in active if t.is_healthy)

        return {
            "total_tunnels": len(self.tunnels),
            "active_tunnels": len(active),
            "healthy_tunnels": healthy,
            "unhealthy_tunnels": len(active) - healthy,
        }

    def _get_tunnel(self, tunnel_id: str) -> Tunnel:
        """Internal: Get tunnel or raise error."""
        tunnel = self.tunnels.get(tunnel_id)
        if not tunnel:
            raise TunnelError(f"Tunnel not found: {tunnel_id}")
        return tunnel
