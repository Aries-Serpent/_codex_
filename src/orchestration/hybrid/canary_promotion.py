"""
Phase 6: Canary Promotion

Graduated activation of quantum-hybrid solvers: 1% → 5% → 25% → 100%.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class CanaryStage(Enum):
    """Canary deployment stages"""

    STAGE_0_SHADOW = "stage_0_shadow"  # Phase 5
    STAGE_1_CANARY_1PCT = "stage_1_canary_1pct"
    STAGE_2_CANARY_5PCT = "stage_2_canary_5pct"
    STAGE_3_CANARY_25PCT = "stage_3_canary_25pct"
    STAGE_4_FULL_ROLLOUT = "stage_4_full_rollout"


@dataclass
class CanaryGateEvaluation:
    """Evaluation of readiness for next canary stage"""

    gate_name: str
    stage: CanaryStage
    sla_compliant: bool
    cohort_accuracy: float  # >99% required
    volume_threshold_met: bool
    duration_threshold_met: bool
    ready_for_next_stage: bool
    evidence: dict[str, Any] = field(default_factory=dict)
    recommendation: str = ""


@dataclass
class CanaryPromotionStatus:
    """Current canary promotion status"""

    promotion_id: str
    current_stage: CanaryStage
    canary_percentage: float  # 0, 1, 5, 25, 100
    decisions_in_cohort: int
    decisions_routed_to_hybrid: int
    hybrid_success_rate: float
    classical_fallback_rate: float
    gate_evaluations: list[CanaryGateEvaluation]
    next_stage_ready: bool
    next_stage_recommendation: str


class CanaryPromoter:
    """Manages graduated canary promotion from 1% to 100%"""

    def __init__(self):
        self._current_stage = CanaryStage.STAGE_0_SHADOW
        self._stage_history: list[CanaryPromotionStatus] = []
        self._stage_config = {
            CanaryStage.STAGE_1_CANARY_1PCT: {
                "percentage": 0.01,
                "min_samples": 100,
                "min_duration_hours": 24,
                "sla_requirement": 0.99,
                "description": "1% of low-risk cohort",
            },
            CanaryStage.STAGE_2_CANARY_5PCT: {
                "percentage": 0.05,
                "min_samples": 500,
                "min_duration_hours": 48,
                "sla_requirement": 0.99,
                "description": "5% of low-risk cohort",
            },
            CanaryStage.STAGE_3_CANARY_25PCT: {
                "percentage": 0.25,
                "min_samples": 2500,
                "min_duration_hours": 72,
                "sla_requirement": 0.99,
                "description": "25% of low+medium-risk cohorts",
            },
            CanaryStage.STAGE_4_FULL_ROLLOUT: {
                "percentage": 1.0,
                "min_samples": 10000,
                "min_duration_hours": 168,  # 1 week
                "sla_requirement": 0.99,
                "description": "100% - all decisions use hybrid when appropriate",
            },
        }

    def get_current_stage(self) -> CanaryStage:
        """Get current canary stage"""
        return self._current_stage

    def evaluate_stage_readiness(
        self,
        stage: CanaryStage,
        sla_compliant: bool,
        cohort_accuracy: float,
        num_samples: int,
        hours_elapsed: float,
        metadata: dict[str, Any] | None = None,
    ) -> CanaryGateEvaluation:
        """Evaluate readiness to advance to next canary stage"""

        config = self._stage_config.get(stage)
        if not config:
            logger.error(f"Unknown stage: {stage}")
            return CanaryGateEvaluation(
                gate_name=f"Unknown stage {stage}",
                stage=stage,
                sla_compliant=False,
                cohort_accuracy=0.0,
                volume_threshold_met=False,
                duration_threshold_met=False,
                ready_for_next_stage=False,
                recommendation="Invalid stage",
            )

        # Check gate criteria
        volume_met = num_samples >= config["min_samples"]
        duration_met = hours_elapsed >= config["min_duration_hours"]
        accuracy_met = cohort_accuracy >= 0.99
        sla_met = sla_compliant and config["sla_requirement"] <= 1.0

        ready = volume_met and duration_met and accuracy_met and sla_met

        evidence = {
            "stage": stage.value,
            "sla_compliant": sla_compliant,
            "cohort_accuracy": cohort_accuracy,
            "num_samples": num_samples,
            "hours_elapsed": hours_elapsed,
            "config": config,
            **(metadata or {}),
        }

        gate_eval = CanaryGateEvaluation(
            gate_name=f"Canary {config['description']} Gate",
            stage=stage,
            sla_compliant=sla_met,
            cohort_accuracy=cohort_accuracy,
            volume_threshold_met=volume_met,
            duration_threshold_met=duration_met,
            ready_for_next_stage=ready,
            evidence=evidence,
        )

        # Set recommendation
        if not sla_met:
            gate_eval.recommendation = (
                f"❌ SLA not compliant. Keep {config['percentage']*100:.0f}% stage."
            )
        elif not accuracy_met:
            gate_eval.recommendation = (
                f"⚠️  Accuracy {cohort_accuracy*100:.1f}% < 99% threshold. "
                "Investigate hybrid results."
            )
        elif not volume_met:
            gate_eval.recommendation = (
                f"⏳ Insufficient volume ({num_samples}/{config['min_samples']}). "
                "Wait for more data."
            )
        elif not duration_met:
            gate_eval.recommendation = (
                f"⏳ Insufficient duration ({hours_elapsed:.1f}/{config['min_duration_hours']} hours). "
                "Monitor longer."
            )
        elif ready:
            next_pct = (
                config["percentage"] * 100
                if stage != CanaryStage.STAGE_4_FULL_ROLLOUT
                else 100
            )
            gate_eval.recommendation = (
                f"✅ READY TO PROMOTE: Advance to "
                f"{next_pct:.0f}% canary stage"
            )

        logger.info(
            f"Gate evaluation for {stage.value}: "
            f"{'✅ PASS' if ready else '❌ BLOCKED'} | "
            f"SLA={sla_met}, Accuracy={accuracy_met}, "
            f"Volume={volume_met}, Duration={duration_met}"
        )

        return gate_eval

    def promote_to_next_stage(
        self,
        gate_eval: CanaryGateEvaluation,
    ) -> CanaryPromotionStatus | None:
        """Attempt promotion to next canary stage"""

        if not gate_eval.ready_for_next_stage:
            logger.warning(
                f"Cannot promote from {self._current_stage.value}: "
                f"Gate evaluation not ready"
            )
            return None

        # Determine next stage
        stage_progression = [
            CanaryStage.STAGE_1_CANARY_1PCT,
            CanaryStage.STAGE_2_CANARY_5PCT,
            CanaryStage.STAGE_3_CANARY_25PCT,
            CanaryStage.STAGE_4_FULL_ROLLOUT,
        ]

        try:
            current_idx = stage_progression.index(self._current_stage)
            next_stage = stage_progression[current_idx + 1]
        except (ValueError, IndexError):
            logger.error(f"Cannot determine next stage from {self._current_stage}")
            return None

        self._current_stage = next_stage
        config = self._stage_config[next_stage]

        status = CanaryPromotionStatus(
            promotion_id=f"promotion_{len(self._stage_history)}",
            current_stage=next_stage,
            canary_percentage=config["percentage"],
            decisions_in_cohort=gate_eval.evidence.get("num_samples", 0),
            decisions_routed_to_hybrid=int(
                gate_eval.evidence.get("num_samples", 0)
                * config["percentage"]
            ),
            hybrid_success_rate=gate_eval.cohort_accuracy,
            classical_fallback_rate=1.0 - gate_eval.cohort_accuracy,
            gate_evaluations=[gate_eval],
            next_stage_ready=False,
            next_stage_recommendation=gate_eval.recommendation,
        )

        self._stage_history.append(status)
        logger.info(
            f"✅ PROMOTED to {next_stage.value} "
            f"({config['percentage']*100:.0f}% canary)"
        )

        return status

    def get_promotion_status(self) -> CanaryPromotionStatus | None:
        """Get current promotion status"""
        return self._stage_history[-1] if self._stage_history else None

    def get_promotion_history(self) -> list[CanaryPromotionStatus]:
        """Get full promotion history"""
        return self._stage_history.copy()

    def is_production_ready(self) -> bool:
        """Check if quantum-hybrid is production-ready (100% stage)"""
        return self._current_stage == CanaryStage.STAGE_4_FULL_ROLLOUT
