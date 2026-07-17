"""Policy Plane: Trust boundaries and legal routes for sandbox transfers.

Defines trust boundaries between sandboxes, legal routes, rate limits,
and data classification policies.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PolicyValidationError(Exception):
    """Raised when policy validation fails."""

    pass


@dataclass
class TrustBoundary:
    """Represents a trust boundary between sandboxes."""

    name: str
    source_sandbox: str
    destination_sandbox: str
    classification: str
    is_bidirectional: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "source_sandbox": self.source_sandbox,
            "destination_sandbox": self.destination_sandbox,
            "classification": self.classification,
            "is_bidirectional": self.is_bidirectional,
        }


@dataclass
class Route:
    """Represents a legal transfer route."""

    route_id: str
    source: str
    destination: str
    allowed_data_types: List[str] = field(default_factory=list)
    rate_limit_mbps: int = 100
    max_payload_mb: int = 1000

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "route_id": self.route_id,
            "source": self.source,
            "destination": self.destination,
            "allowed_data_types": self.allowed_data_types,
            "rate_limit_mbps": self.rate_limit_mbps,
            "max_payload_mb": self.max_payload_mb,
        }


@dataclass
class PolicyConfig:
    """Complete policy configuration for transfer fabric."""

    trust_boundaries: Dict[str, TrustBoundary] = field(default_factory=dict)
    routes: List[Route] = field(default_factory=list)
    rate_limits: Dict[str, int] = field(default_factory=dict)
    data_classifications: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "trust_boundaries": {
                k: v.to_dict() for k, v in self.trust_boundaries.items()
            },
            "routes": [r.to_dict() for r in self.routes],
            "rate_limits": self.rate_limits,
            "data_classifications": self.data_classifications,
        }


class PolicyPlane:
    """Manages trust boundaries and legal routes for sandbox transfers."""

    def __init__(self):
        """Initialize policy plane."""
        self.config = PolicyConfig()
        self.route_index: Dict[str, Route] = {}

    def define_trust_boundary(
        self,
        name: str,
        source_sandbox: str,
        destination_sandbox: str,
        classification: str,
        is_bidirectional: bool = False,
    ) -> TrustBoundary:
        """Define a trust boundary between sandboxes."""
        boundary = TrustBoundary(
            name=name,
            source_sandbox=source_sandbox,
            destination_sandbox=destination_sandbox,
            classification=classification,
            is_bidirectional=is_bidirectional,
        )
        self.config.trust_boundaries[name] = boundary
        logger.info(f"Trust boundary defined: {name}")
        return boundary

    def add_route(
        self,
        route_id: str,
        source: str,
        destination: str,
        allowed_data_types: Optional[List[str]] = None,
        rate_limit_mbps: int = 100,
        max_payload_mb: int = 1000,
    ) -> Route:
        """Add a legal transfer route."""
        if allowed_data_types is None:
            allowed_data_types = []

        route = Route(
            route_id=route_id,
            source=source,
            destination=destination,
            allowed_data_types=allowed_data_types,
            rate_limit_mbps=rate_limit_mbps,
            max_payload_mb=max_payload_mb,
        )
        self.config.routes.append(route)
        self.route_index[route_id] = route
        logger.info(f"Route added: {route_id}")
        return route

    def set_rate_limit(self, route_id: str, mbps: int) -> None:
        """Set rate limit for a route."""
        if route_id not in self.route_index:
            raise PolicyValidationError(f"Route not found: {route_id}")

        self.route_index[route_id].rate_limit_mbps = mbps
        self.config.rate_limits[route_id] = mbps
        logger.info(f"Rate limit set for {route_id}: {mbps} Mbps")

    def add_data_classification(self, classification_id: str, policy: str) -> None:
        """Add data classification policy."""
        self.config.data_classifications[classification_id] = policy
        logger.info(f"Data classification added: {classification_id}")

    def is_route_legal(
        self, source: str, destination: str, data_type: str = ""
    ) -> bool:
        """Verify if a transfer route is legal."""
        for route in self.config.routes:
            if route.source == source and route.destination == destination:
                if not route.allowed_data_types or data_type in route.allowed_data_types:
                    return True
        return False

    def validate_trust_boundary(
        self, source: str, destination: str
    ) -> bool:
        """Validate transfer against trust boundaries."""
        for boundary in self.config.trust_boundaries.values():
            if (
                boundary.source_sandbox == source
                and boundary.destination_sandbox == destination
            ):
                return True
            if (
                boundary.is_bidirectional
                and boundary.source_sandbox == destination
                and boundary.destination_sandbox == source
            ):
                return True
        return False

    def get_route(self, route_id: str) -> Optional[Route]:
        """Get route by ID."""
        return self.route_index.get(route_id)

    def get_all_routes(self) -> List[Route]:
        """Get all defined routes."""
        return self.config.routes.copy()

    def validate_payload_size(self, route_id: str, payload_bytes: int) -> bool:
        """Validate if payload exceeds route's max size."""
        route = self.get_route(route_id)
        if not route:
            return False
        return payload_bytes <= route.max_payload_mb * 1024 * 1024

    def get_policy_config(self) -> PolicyConfig:
        """Get complete policy configuration."""
        return self.config
