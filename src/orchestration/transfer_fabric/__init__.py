"""Transfer Fabric for secure multi-sandbox data movement.

Implements 5-plane architecture: Policy, Control, Tunnel, Data, Observability.
"""

from .data_plane import (
    DataPlane,
    TransferResult,
)
from .observability_plane import (
    ObservabilityPlane,
    ObservabilityReport,
)
from .policy_plane import (
    PolicyConfig,
    PolicyPlane,
    Route,
    TrustBoundary,
)
from .preflight_checks import (
    PreflightCheck,
    PreflightResult,
    PreflightValidator,
)
from .rollback_controls import (
    Checkpoint,
    RollbackManager,
    RollbackResult,
)
from .transfer_aware_scheduler import (
    TransferAwareSchedulerV2,
)
from .tunnel_lifecycle import (
    Tunnel,
    TunnelLifecycle,
    TunnelState,
)

__all__ = [
    "PolicyConfig",
    "Route",
    "TrustBoundary",
    "PolicyPlane",
    "Tunnel",
    "TunnelState",
    "TunnelLifecycle",
    "PreflightCheck",
    "PreflightResult",
    "PreflightValidator",
    "TransferResult",
    "DataPlane",
    "ObservabilityReport",
    "ObservabilityPlane",
    "RollbackResult",
    "Checkpoint",
    "RollbackManager",
    "TransferAwareSchedulerV2",
]
