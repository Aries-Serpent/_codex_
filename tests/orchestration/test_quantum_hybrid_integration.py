"""
Integration Tests for Phase 5-6 Quantum-Hybrid Orchestration

Tests for cross-module interactions and end-to-end workflows.
"""

import pytest
from orchestration.hybrid.decision_domains import (
    DecisionDomain,
    DecisionDomainMapper,
    RiskLevel,
)
from orchestration.hybrid.shadow_mode import (
    ShadowExecutor,
    SolverResult,
    ExecutionStatus,
)
from orchestration.hybrid.promotion_gates import PromotionGates, GateStatus
from orchestration.hybrid.cohort_routing import CohortRouter, CohortRisk
from orchestration.hybrid.sla_monitor import SLAMonitor, SLAMetric, ComplianceStatus
from orchestration.hybrid.canary_promotion import CanaryPromoter, CanaryStage


class TestPhase5Phase6Integration:
    """Integration tests across Phase 5 and Phase 6 modules"""

    def test_domain_mapping_to_shadow_execution(self):
        """Test domain mapping feeds into shadow execution"""
        mapper = DecisionDomainMapper()
        compat = mapper.register_domain(
            domain_id="test_domain",
            domain=DecisionDomain.RESOURCE_ALLOCATION,
            classical_solver="solver1",
            hybrid_solver="solver2",
        )

        assert compat.domain_id == "test_domain"
        mapping = mapper.generate_mapping()
        assert mapping.total_domains == 1

    def test_shadow_execution_with_improvement_threshold(self):
        """Test shadow execution meets improvement threshold for promotion"""
        executor = ShadowExecutor()

        def classical_solver(seed=None):
            return SolverResult(
                solver_name="classical",
                status=ExecutionStatus.COMPLETED,
                quality=1.0,
                latency_ms=100.0,
                constraints_satisfied=True,
            )

        def hybrid_solver(seed=None):
            return SolverResult(
                solver_name="hybrid",
                status=ExecutionStatus.COMPLETED,
                quality=1.07,  # 7% improvement
                latency_ms=120.0,
                constraints_satisfied=True,
            )

        comparison = executor.execute_parallel(
            decision_id="test_1",
            classical_solver=classical_solver,
            hybrid_solver=hybrid_solver,
            solver_params={},
        )

        # 7% improvement meets the 5% threshold for Phase 5 gates
        assert comparison.improvement_pct >= 5.0

    def test_shadow_execution_to_promotion_gates(self):
        """Test shadow execution results feed into promotion gates"""
        gates = PromotionGates()
        
        # Simulate shadow execution results
        report = gates.evaluate_shadow_gates(
            avg_improvement_pct=8.0,
            determinism_drift_pct=0.08,
            latency_ratio=1.5,
            num_samples=60,
        )

        # All gates should pass
        assert report.all_passed is True
        assert report.ready_for_promotion is True

    def test_cohort_routing_low_risk_domains(self):
        """Test cohort routing identifies low-risk domains"""
        router = CohortRouter()

        # Low-risk decision
        classification = router.classify_decision(
            decision_id="dec_1",
            risk_indicators={"financial_impact": 0.1, "user_impact": 0.1},
        )

        assert classification.cohort == CohortRisk.LOW

    def test_cohort_routing_high_risk_domains(self):
        """Test cohort routing identifies high-risk domains"""
        router = CohortRouter()

        # High-risk decision
        classification = router.classify_decision(
            decision_id="dec_2",
            risk_indicators={"financial_impact": 0.9, "user_impact": 0.9},
        )

        assert classification.cohort == CohortRisk.HIGH

    def test_sla_monitoring_with_canary_stages(self):
        """Test SLA monitoring tracks metrics for different canary stages"""
        monitor = SLAMonitor()

        # Record metrics for 1% canary
        monitor.record_measurement(SLAMetric.SUCCESS_RATE, 0.995)
        monitor.record_measurement(SLAMetric.LATENCY, 2500.0)
        monitor.record_measurement(SLAMetric.CORRECTNESS, 0.9995)
        report = monitor.evaluate_compliance(canary_percentage=0.01)

        assert report.canary_percentage == 0.01

    def test_end_to_end_phase5_workflow(self):
        """Test complete Phase 5 workflow"""
        # 1. Domain mapping
        mapper = DecisionDomainMapper()
        mapper.register_domain(
            domain_id="resource_opt",
            domain=DecisionDomain.RESOURCE_ALLOCATION,
            classical_solver="solver_a",
            hybrid_solver="solver_b",
        )
        mapping = mapper.generate_mapping()
        assert mapping.compatible_domains > 0

        # 2. Shadow execution
        executor = ShadowExecutor()

        def classical(seed=None):
            return SolverResult(
                solver_name="classical",
                status=ExecutionStatus.COMPLETED,
                quality=1.0,
                latency_ms=100.0,
                constraints_satisfied=True,
            )

        def hybrid(seed=None):
            return SolverResult(
                solver_name="hybrid",
                status=ExecutionStatus.COMPLETED,
                quality=1.08,
                latency_ms=120.0,
                constraints_satisfied=True,
            )

        for i in range(10):
            executor.execute_parallel(
                decision_id=f"test_{i}",
                classical_solver=classical,
                hybrid_solver=hybrid,
                solver_params={},
            )

        stats = executor.get_statistics()
        assert stats["successful_executions"] == 10

        # 3. Promotion gates
        gates = PromotionGates()
        report = gates.evaluate_shadow_gates(
            avg_improvement_pct=8.0,
            determinism_drift_pct=0.05,
            latency_ratio=1.2,
            num_samples=60,
        )
        assert report.ready_for_promotion is True

    def test_end_to_end_phase6_workflow(self):
        """Test complete Phase 6 canary promotion workflow"""
        # 1. Cohort routing
        router = CohortRouter()
        router.classify_decision("dec_1", {"financial_impact": 0.1})
        router.classify_decision("dec_2", {"financial_impact": 0.5})
        router.classify_decision("dec_3", {"financial_impact": 0.9})
        routes = router.generate_routes()
        assert routes.total_decisions == 3

        # 2. SLA monitoring setup
        monitor = SLAMonitor()

        # 3. Canary progression
        promoter = CanaryPromoter()
        promoter._current_stage = CanaryStage.STAGE_1_CANARY_1PCT

        gate_eval = promoter.evaluate_stage_readiness(
            stage=CanaryStage.STAGE_2_CANARY_5PCT,
            sla_compliant=True,
            cohort_accuracy=0.995,
            num_samples=600,
            hours_elapsed=60,
        )
        status = promoter.promote_to_next_stage(gate_eval)
        assert status is not None
        assert promoter.get_current_stage() == CanaryStage.STAGE_2_CANARY_5PCT

    def test_multiple_domain_mapping_and_routing(self):
        """Test multiple domains mapped and routed to different cohorts"""
        mapper = DecisionDomainMapper()
        router = CohortRouter()

        # Map multiple domains
        for i in range(5):
            mapper.register_domain(
                domain_id=f"domain_{i}",
                domain=DecisionDomain.RESOURCE_ALLOCATION if i % 2 == 0
                else DecisionDomain.SCHEDULING,
                classical_solver="solver_c",
                hybrid_solver="solver_h",
            )

        # Route different decisions
        for i in range(10):
            router.classify_decision(
                decision_id=f"dec_{i}",
                risk_indicators={"financial_impact": i / 10},
            )

        mapping = mapper.generate_mapping()
        routes = router.generate_routes()
        
        assert mapping.total_domains == 5
        assert routes.total_decisions == 10

    def test_shadow_execution_determinism_verification(self):
        """Test determinism verification in shadow execution"""
        executor = ShadowExecutor()

        def deterministic_solver(seed=None):
            # Return consistent result based on seed
            return SolverResult(
                solver_name="deterministic",
                status=ExecutionStatus.COMPLETED,
                quality=1.0 if seed == 42 else 0.5,
                latency_ms=100.0,
                constraints_satisfied=True,
            )

        # Run with same seed multiple times
        for _ in range(3):
            comparison = executor.execute_parallel(
                decision_id="test_det",
                classical_solver=deterministic_solver,
                hybrid_solver=deterministic_solver,
                solver_params={},
                seed=42,
            )
            assert comparison.deterministic is True

    def test_gate_progression_requirements(self):
        """Test that gates properly enforce requirements at each level"""
        gates = PromotionGates()

        # Test Gate 1: improvement - fail due to low improvement
        report1 = gates.evaluate_shadow_gates(
            avg_improvement_pct=3.0,  # Below 5% threshold
            determinism_drift_pct=0.05,
            latency_ratio=1.5,
            num_samples=60,
        )
        assert report1.ready_for_promotion is False  # Low improvement

        # Test with sufficient improvement
        report2 = gates.evaluate_shadow_gates(
            avg_improvement_pct=6.0,
            determinism_drift_pct=0.05,
            latency_ratio=1.5,
            num_samples=60,
        )
        assert report2.ready_for_promotion is True

        # Test with insufficient samples (< 50)
        report3 = gates.evaluate_shadow_gates(
            avg_improvement_pct=6.0,
            determinism_drift_pct=0.05,
            latency_ratio=1.5,
            num_samples=30,  # Below 50 minimum
        )
        assert report3.ready_for_promotion is False

    def test_cohort_risk_boundary_cases(self):
        """Test cohort classification at risk boundaries"""
        router = CohortRouter()

        # Test boundary: 0.33 (low/medium threshold)
        low_boundary = router.classify_decision(
            "dec_1", {"financial_impact": 0.32}
        )
        assert low_boundary.cohort == CohortRisk.LOW

        mid_boundary = router.classify_decision(
            "dec_2", {"financial_impact": 0.34}
        )
        assert mid_boundary.cohort == CohortRisk.MEDIUM

        # Test boundary: 0.67 (medium/high threshold)
        med_boundary = router.classify_decision(
            "dec_3", {"financial_impact": 0.66}
        )
        assert med_boundary.cohort == CohortRisk.MEDIUM

        high_boundary = router.classify_decision(
            "dec_4", {"financial_impact": 0.68}
        )
        assert high_boundary.cohort == CohortRisk.HIGH

    def test_sla_compliance_escalation(self):
        """Test SLA compliance escalation from compliant to breach"""
        monitor = SLAMonitor()

        # Start compliant
        monitor.record_measurement(SLAMetric.SUCCESS_RATE, 0.995)
        monitor.record_measurement(SLAMetric.LATENCY, 2500.0)
        report1 = monitor.evaluate_compliance(canary_percentage=0.01)
        assert report1.compliance_status == ComplianceStatus.COMPLIANT

        # Record degraded metrics (approaching breach)
        monitor.record_measurement(SLAMetric.SUCCESS_RATE, 0.991)
        report2 = monitor.evaluate_compliance(canary_percentage=0.01)
        # Should be approaching or breached
        assert report2.compliance_status in [
            ComplianceStatus.APPROACHING_BREACH,
            ComplianceStatus.BREACHED,
        ]

    def test_canary_stage_progression_requirements(self):
        """Test that each canary stage has proper volume/duration requirements"""
        promoter = CanaryPromoter()

        # Stage 1: min 100 samples, 24 hours
        gate1_fail = promoter.evaluate_stage_readiness(
            stage=CanaryStage.STAGE_1_CANARY_1PCT,
            sla_compliant=True,
            cohort_accuracy=0.995,
            num_samples=50,  # Below minimum
            hours_elapsed=30,
        )
        assert gate1_fail.ready_for_next_stage is False

        gate1_pass = promoter.evaluate_stage_readiness(
            stage=CanaryStage.STAGE_1_CANARY_1PCT,
            sla_compliant=True,
            cohort_accuracy=0.995,
            num_samples=100,
            hours_elapsed=24,
        )
        assert gate1_pass.ready_for_next_stage is True

        # Stage 2: min 500 samples, 48 hours
        gate2_fail = promoter.evaluate_stage_readiness(
            stage=CanaryStage.STAGE_2_CANARY_5PCT,
            sla_compliant=True,
            cohort_accuracy=0.995,
            num_samples=500,
            hours_elapsed=30,  # Below minimum
        )
        assert gate2_fail.ready_for_next_stage is False

        gate2_pass = promoter.evaluate_stage_readiness(
            stage=CanaryStage.STAGE_2_CANARY_5PCT,
            sla_compliant=True,
            cohort_accuracy=0.995,
            num_samples=500,
            hours_elapsed=48,
        )
        assert gate2_pass.ready_for_next_stage is True

    def test_integrated_accuracy_and_sla_requirements(self):
        """Test that both accuracy and SLA requirements must be met"""
        promoter = CanaryPromoter()

        # Test: good SLA but low accuracy
        gate_eval = promoter.evaluate_stage_readiness(
            stage=CanaryStage.STAGE_1_CANARY_1PCT,
            sla_compliant=True,
            cohort_accuracy=0.98,  # Below 99% threshold
            num_samples=100,
            hours_elapsed=24,
        )
        assert gate_eval.ready_for_next_stage is False

        # Test: good accuracy but poor SLA
        gate_eval2 = promoter.evaluate_stage_readiness(
            stage=CanaryStage.STAGE_1_CANARY_1PCT,
            sla_compliant=False,
            cohort_accuracy=0.995,
            num_samples=100,
            hours_elapsed=24,
        )
        assert gate_eval2.ready_for_next_stage is False

        # Test: both good
        gate_eval3 = promoter.evaluate_stage_readiness(
            stage=CanaryStage.STAGE_1_CANARY_1PCT,
            sla_compliant=True,
            cohort_accuracy=0.995,
            num_samples=100,
            hours_elapsed=24,
        )
        assert gate_eval3.ready_for_next_stage is True

    def test_domain_compatibility_scoring(self):
        """Test domain compatibility scoring for different risk levels"""
        mapper = DecisionDomainMapper()

        low_risk = mapper.register_domain(
            "low", DecisionDomain.RESOURCE_ALLOCATION, "s", "h", RiskLevel.LOW
        )
        med_risk = mapper.register_domain(
            "med", DecisionDomain.SCHEDULING, "s", "h", RiskLevel.MEDIUM
        )
        high_risk = mapper.register_domain(
            "high", DecisionDomain.GRAPH_OPTIMIZATION, "s", "h", RiskLevel.HIGH
        )

        # Low risk should have highest compatibility
        assert low_risk.compatibility_score > med_risk.compatibility_score
        assert med_risk.compatibility_score > high_risk.compatibility_score

    def test_shadow_execution_constraint_satisfaction(self):
        """Test shadow execution tracking constraint satisfaction"""
        executor = ShadowExecutor()

        def feasible_solver(seed=None):
            return SolverResult(
                solver_name="feasible",
                status=ExecutionStatus.COMPLETED,
                quality=1.0,
                latency_ms=100.0,
                constraints_satisfied=True,
            )

        def infeasible_solver(seed=None):
            return SolverResult(
                solver_name="infeasible",
                status=ExecutionStatus.COMPLETED,
                quality=1.0,
                latency_ms=100.0,
                constraints_satisfied=False,
            )

        # Both feasible
        comparison1 = executor.execute_parallel(
            decision_id="test_1",
            classical_solver=feasible_solver,
            hybrid_solver=feasible_solver,
            solver_params={},
        )
        assert comparison1.both_feasible is True

        # One infeasible
        comparison2 = executor.execute_parallel(
            decision_id="test_2",
            classical_solver=feasible_solver,
            hybrid_solver=infeasible_solver,
            solver_params={},
        )
        assert comparison2.both_feasible is False
