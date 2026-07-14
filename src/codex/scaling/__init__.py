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

from .multi_tenant_manager import (
    TenantManager,
    TenantConfig,
    TenantNamespace,
    RBACPolicy,
    ResourceQuota,
    AuditLog,
    AccessLevel,
    AuditEventType,
)
from .failover_manager import (
    FailoverManager,
    HealthCheckProbe,
    RegionConfig,
    FailoverEvent,
    HealthStatus,
)
from .load_balancer import (
    LoadBalancer,
    LoadBalancerConfig,
    ConsistentHashRing,
    BackendNode,
    BackendState,
)
from .auto_scaler import (
    AutoScaler,
    ScalingTrigger,
    ScalingEvent,
    ScalingAction,
)
from .cost_allocator import (
    CostAllocator,
    CostAllocationConfig,
    TenantCost,
    CostReport,
    InstancePricing,
    InstanceType,
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
