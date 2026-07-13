"""
Phase 5-6 Quantum-Hybrid Orchestration Bridge

Bridges classical optimization with quantum-hybrid solvers through shadow mode
(Phase 5) and graduated canary promotion (Phase 6).

Modules:
- decision_domains: Classical-to-hybrid decision mapping
- shadow_mode: Parallel execution (advisory only)
- promotion_gates: KPI-gated phase transitions
- cohort_routing: Risk-based decision cohort classification
- sla_monitor: SLA compliance tracking and fallback
- canary_promotion: 1% → 5% → 25% → 100% rollout
"""

from orchestration.hybrid.canary_promotion import (
    CanaryPromoter,
    CanaryPromotionStatus,
    CanaryStage,
)
from orchestration.hybrid.cohort_routing import CohortRouter, CohortRoutes, CohortRisk
from orchestration.hybrid.decision_domains import (
    DecisionDomain,
    DecisionDomainMapper,
    DomainCompatibility,
    DomainMapping,
    RiskLevel,
)
from orchestration.hybrid.promotion_gates import (
    GateResult,
    PromotionGateReport,
    PromotionGates,
)
from orchestration.hybrid.shadow_mode import (
    ShadowComparison,
    ShadowExecutor,
    SolverResult,
)
from orchestration.hybrid.sla_monitor import SLAMonitor, SLAReport, SLAThreshold

__all__ = [
    # Phase 5: Shadow Mode
    "DecisionDomain",
    "DecisionDomainMapper",
    "DomainCompatibility",
    "DomainMapping",
    "RiskLevel",
    "ShadowExecutor",
    "ShadowComparison",
    "SolverResult",
    "PromotionGates",
    "PromotionGateReport",
    "GateResult",
    # Phase 6: Canary Promotion
    "CohortRouter",
    "CohortRoutes",
    "CohortRisk",
    "SLAMonitor",
    "SLAReport",
    "SLAThreshold",
    "CanaryPromoter",
    "CanaryPromotionStatus",
    "CanaryStage",
]
