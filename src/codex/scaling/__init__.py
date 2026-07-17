"""
Enterprise scaling framework for multi-tenant resource isolation,
geographic failover, dynamic load balancing, and auto-scaling.

Phase 4E Planset 010 - Enterprise Scaling Framework

Modules:
  - multi_tenant_manager: Core multi-tenant isolation, RBAC, resource quotas
  - failover_manager: Geographic failover with sub-second detection
  - load_balancer: Dynamic load balancing with consistent hashing
  - auto_scaler: Auto-scaling with intelligent trigger logic
  - cost_allocator: Cost tracking and optimization recommendations
"""

from .auto_scaler import (
    AutoScaler,
    ScalingAction,
    ScalingEvent,
    ScalingTrigger,
)
from .cost_allocator import (
    CostAllocationConfig,
    CostAllocator,
    CostReport,
    InstancePricing,
    InstanceType,
    TenantCost,
)
from .failover_manager import (
    FailoverEvent,
    FailoverManager,
    HealthCheckProbe,
    HealthStatus,
    RegionConfig,
)
from .load_balancer import (
    BackendNode,
    BackendState,
    ConsistentHashRing,
    LoadBalancer,
    LoadBalancerConfig,
)
from .multi_tenant_manager import (
    AccessLevel,
    AuditEventType,
    AuditLog,
    RBACPolicy,
    ResourceQuota,
    TenantConfig,
    TenantManager,
    TenantNamespace,
)

__all__ = [
    "TenantManager",
    "TenantConfig",
    "TenantNamespace",
    "RBACPolicy",
    "ResourceQuota",
    "AuditLog",
    "AccessLevel",
    "AuditEventType",
    "FailoverManager",
    "HealthCheckProbe",
    "RegionConfig",
    "FailoverEvent",
    "HealthStatus",
    "LoadBalancer",
    "LoadBalancerConfig",
    "ConsistentHashRing",
    "BackendNode",
    "BackendState",
    "AutoScaler",
    "ScalingTrigger",
    "ScalingEvent",
    "ScalingAction",
    "CostAllocator",
    "CostAllocationConfig",
    "TenantCost",
    "CostReport",
    "InstancePricing",
    "InstanceType",
]
