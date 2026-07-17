"""
Phase 5: Shadow Mode Quantum-Hybrid Orchestration

Enables advisory-only execution of quantum-hybrid solvers in parallel with
classical solvers. Zero production impact during shadow mode.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class DecisionDomain(Enum):
    """Quantum-hybrid compatible decision domains"""

    RESOURCE_ALLOCATION = "resource_allocation"
    SCHEDULING = "scheduling"
    COMBINATORIAL_OPTIMIZATION = "combinatorial_optimization"
    CONSTRAINT_SATISFACTION = "constraint_satisfaction"
    GRAPH_OPTIMIZATION = "graph_optimization"
    PORTFOLIO_OPTIMIZATION = "portfolio_optimization"


class RiskLevel(Enum):
    """Compatibility risk level for hybrid optimization"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class DomainCompatibility:
    """Compatibility assessment for a decision domain"""

    domain_id: str
    domain: DecisionDomain
    classical_solver: str
    hybrid_solver: str
    compatibility_score: float  # 0.0 to 1.0
    risk_level: RiskLevel
    min_improvement_threshold: float  # Minimum % improvement required
    max_latency_multiplier: float  # Hybrid latency / classical latency
    determinism_threshold: float  # Max allowed variance (0.0 to 1.0)
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DomainMapping:
    """Result of decision domain mapping"""

    mapping_id: str
    domains: dict[str, DomainCompatibility]
    total_domains: int
    compatible_domains: int
    compatibility_pct: float
    created_at: float = field(default_factory=time.time)


class DecisionDomainMapper:
    """Maps classical decisions to quantum-hybrid compatible domains"""

    def __init__(self):
        self._domains: dict[str, DomainCompatibility] = {}
        self._default_thresholds = {
            DecisionDomain.RESOURCE_ALLOCATION: {
                "min_improvement": 0.05,  # 5%
                "max_latency": 2.0,
                "determinism": 0.001,  # 0.1%
            },
            DecisionDomain.SCHEDULING: {
                "min_improvement": 0.05,
                "max_latency": 2.0,
                "determinism": 0.001,
            },
            DecisionDomain.COMBINATORIAL_OPTIMIZATION: {
                "min_improvement": 0.08,  # 8% for complex problems
                "max_latency": 2.5,
                "determinism": 0.005,  # 0.5%
            },
            DecisionDomain.CONSTRAINT_SATISFACTION: {
                "min_improvement": 0.06,
                "max_latency": 2.0,
                "determinism": 0.002,
            },
            DecisionDomain.GRAPH_OPTIMIZATION: {
                "min_improvement": 0.10,  # 10% - harder problems
                "max_latency": 3.0,
                "determinism": 0.005,
            },
            DecisionDomain.PORTFOLIO_OPTIMIZATION: {
                "min_improvement": 0.07,
                "max_latency": 2.0,
                "determinism": 0.001,
            },
        }

    def register_domain(
        self,
        domain_id: str,
        domain: DecisionDomain,
        classical_solver: str,
        hybrid_solver: str,
        risk_level: RiskLevel = RiskLevel.LOW,
        custom_thresholds: Optional[dict[str, float]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> DomainCompatibility:
        """Register a decision domain for hybrid optimization"""
        
        defaults = self._default_thresholds.get(domain, {})
        thresholds = {**defaults, **(custom_thresholds or {})}

        # Risk-based compatibility scoring
        risk_multiplier = {
            RiskLevel.LOW: 1.0,
            RiskLevel.MEDIUM: 0.85,
            RiskLevel.HIGH: 0.70,
        }[risk_level]

        compatibility_score = min(1.0, 0.95 * risk_multiplier)

        compat = DomainCompatibility(
            domain_id=domain_id,
            domain=domain,
            classical_solver=classical_solver,
            hybrid_solver=hybrid_solver,
            compatibility_score=compatibility_score,
            risk_level=risk_level,
            min_improvement_threshold=thresholds.get("min_improvement", 0.05),
            max_latency_multiplier=thresholds.get("max_latency", 2.0),
            determinism_threshold=thresholds.get("determinism", 0.001),
            metadata=metadata or {},
        )

        self._domains[domain_id] = compat
        logger.info(
            f"Registered domain {domain_id} ({domain.value}) "
            f"with compatibility {compatibility_score:.3f}"
        )

        return compat

    def generate_mapping(
        self, include_high_risk: bool = False
    ) -> DomainMapping:
        """Generate domain mapping with compatibility assessments"""
        
        mapping_id = f"mapping_{int(time.time())}"
        total = len(self._domains)
        
        if include_high_risk:
            compatible = total
        else:
            compatible = sum(
                1 for d in self._domains.values()
                if d.risk_level in (RiskLevel.LOW, RiskLevel.MEDIUM)
            )

        mapping = DomainMapping(
            mapping_id=mapping_id,
            domains=self._domains.copy(),
            total_domains=total,
            compatible_domains=compatible,
            compatibility_pct=compatible / total if total > 0 else 0.0,
        )

        logger.info(
            f"Generated domain mapping: {total} total, "
            f"{compatible} compatible ({mapping.compatibility_pct*100:.1f}%)"
        )

        return mapping

    def get_low_risk_domains(self) -> list[DomainCompatibility]:
        """Get low-risk domains suitable for immediate Phase 6 promotion"""
        return [
            d for d in self._domains.values()
            if d.risk_level == RiskLevel.LOW
        ]

    def get_medium_risk_domains(self) -> list[DomainCompatibility]:
        """Get medium-risk domains for Phase 6 staged promotion"""
        return [
            d for d in self._domains.values()
            if d.risk_level == RiskLevel.MEDIUM
        ]
