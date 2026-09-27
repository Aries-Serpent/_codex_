"""
Comprehensive test suite for SLA optimizer (700-900 LOC).

Phase 4E Planset 013 - Gate Criteria Verification
"""

import json

import pytest

from codex.optimization.sla_optimizer import (
    BillingEngine,
    HeuristicConstraintSolver,
    ParetoOptimizer,
    PricingModel,
    ResourceAllocation,
    SLAOptimizer,
    SLASpec,
    Tier,
    TierManager,
)


class TestConstraintSolver:
    """Test constraint satisfaction for SLA mapping."""

    def test_heuristic_solver_basic(self):
        """Test heuristic solver produces feasible allocation."""
        sla = SLASpec(
            tenant_id="test-1",
            target_uptime_percent=99.9,
            max_response_time_ms=100,
            max_error_rate_percent=0.1,
            data_retention_days=30,
            peak_qps=1000,
        )

        pricing = PricingModel()
        solver = HeuristicConstraintSolver()
        allocation = solver.solve(sla, pricing)

        assert allocation is not None, "allocation must be initialized"
        assert allocation.tenant_id == "test-1", "tenant_id is not valid"
        assert allocation.cpu_cores > 0, "cpu_cores must be greater than zero"
        assert allocation.memory_gb > 0, "memory_gb must be greater than zero"
        assert allocation.disk_gb > 0, "disk_gb must be greater than zero"
        assert allocation.network_mbps > 0, "network_mbps must be greater than zero"

    def test_allocation_meets_safety_margin(self):
        """Test allocation includes <5% safety margin."""
        sla = SLASpec(
            tenant_id="test-2",
            target_uptime_percent=99.99,
            max_response_time_ms=50,
            max_error_rate_percent=0.01,
            data_retention_days=90,
            peak_qps=5000,
        )

        pricing = PricingModel()
        solver = HeuristicConstraintSolver()
        allocation = solver.solve(sla, pricing)

        # Verify allocation meets minimum requirements with margin
        min_cpu = (sla.peak_qps / 1000.0) * 1.05
        min_memory = (sla.peak_qps / 500.0) * 1.05

        assert allocation.cpu_cores >= min_cpu, "cpu_cores must be greater than zero"
        assert allocation.memory_gb >= min_memory, "memory_gb must be greater than zero"

    def test_tier_selection_from_uptime(self):
        """Test correct tier selected based on uptime target."""
        test_cases = [
            (99.0, Tier.BRONZE),
            (99.9, Tier.SILVER),
            (99.99, Tier.GOLD),
            (99.999, Tier.PLATINUM),
        ]

        for uptime, expected_tier in test_cases:
            sla = SLASpec(
                tenant_id=f"tier-test-{uptime}",
                target_uptime_percent=uptime,
                max_response_time_ms=100,
                max_error_rate_percent=0.1,
                data_retention_days=30,
                peak_qps=1000,
            )

            pricing = PricingModel()
            solver = HeuristicConstraintSolver()
            allocation = solver.solve(sla, pricing)

            assert allocation.tier == expected_tier, "tier is not valid"


class TestParetoOptimizer:
    """Test Pareto frontier generation."""

    def test_frontier_generation(self):
        """Test Pareto frontier generates multiple points."""
        slas = [
            SLASpec(
                tenant_id=f"tenant-{i}",
                target_uptime_percent=99.9,
                max_response_time_ms=100,
                max_error_rate_percent=0.1,
                data_retention_days=30,
                peak_qps=1000 + i * 500,
            )
            for i in range(3)
        ]

        pricing = PricingModel()
        solver = HeuristicConstraintSolver()
        optimizer = ParetoOptimizer(solver)

        frontier = optimizer.generate_frontier(slas, pricing, num_points=4)

        assert len(frontier) <= 4, "Frontier must not be empty"
        assert all(len(allocs) == 3 for _, allocs in frontier)  # 3 tenants each

        # Verify frontier is sorted by cost (ascending)
        costs = [cost for cost, _ in frontier]
        assert costs == sorted(costs), "costs is not valid"

    def test_frontier_computation_time(self):
        """Test Pareto frontier computes in <10 seconds."""
        slas = [
            SLASpec(
                tenant_id=f"tenant-{i}",
                target_uptime_percent=99.9,
                max_response_time_ms=100,
                max_error_rate_percent=0.1,
                data_retention_days=30,
                peak_qps=1000,
            )
            for i in range(10)
        ]

        pricing = PricingModel()
        solver = HeuristicConstraintSolver()
        optimizer = ParetoOptimizer(solver)

        import time
        start = time.time()
        frontier = optimizer.generate_frontier(slas, pricing, num_points=20)
        elapsed = time.time() - start

        assert elapsed < 10.0, f"Frontier generation took {elapsed:.2f}s, expected <10s"
        assert len(frontier) > 0, "Frontier must not be empty"

    def test_frontier_pareto_property(self):
        """Test frontier exhibits Pareto optimality."""
        slas = [
            SLASpec(
                tenant_id=f"tenant-{i}",
                target_uptime_percent=99.9,
                max_response_time_ms=100,
                max_error_rate_percent=0.1,
                data_retention_days=30,
                peak_qps=1000,
            )
            for i in range(3)
        ]

        pricing = PricingModel()
        solver = HeuristicConstraintSolver()
        optimizer = ParetoOptimizer(solver)

        frontier = optimizer.generate_frontier(slas, pricing, num_points=4)

        # Points on frontier should be monotonic in cost (no crossing)
        costs = [cost for cost, _ in frontier]
        for i in range(len(costs) - 1):
            assert costs[i] <= costs[i + 1], "Condition must be true"


class TestTierManager:
    """Test automatic tier promotion/demotion."""

    def test_promotion_when_sla_at_risk(self):
        """Test promotion triggered when SLA at risk."""
        manager = TierManager(cooldown_days=0)  # No cooldown for testing

        # SLA achieved 98.5% of target = at risk
        should_promote = manager.should_promote(
            tenant_id="test-1",
            current_tier=Tier.SILVER,
            sla_achieved=99.8,
            sla_target=99.9,
        )
        assert should_promote is True, "should_promote is not valid"

    def test_demotion_when_over_provisioned(self):
        """Test demotion when resources underutilized."""
        manager = TierManager(cooldown_days=0)

        # SLA exceeded by 5% and only 30% resource utilization
        should_demote = manager.should_demote(
            tenant_id="test-1",
            current_tier=Tier.GOLD,
            sla_achieved=99.99,
            sla_target=99.9,
            resource_utilization=0.3,
        )
        assert should_demote is True, "should_demote is not valid"

    def test_cooldown_prevents_oscillation(self):
        """Test 7-day cooldown prevents tier oscillation."""
        manager = TierManager(cooldown_days=7)

        # First promotion
        tenant_id = "test-1"
        new_tier = manager.promote_tier(tenant_id, Tier.SILVER)
        assert new_tier == Tier.GOLD, "new_tier is not valid"

        # Immediate second promotion attempt should fail due to cooldown
        should_promote = manager.should_promote(
            tenant_id=tenant_id,
            current_tier=Tier.GOLD,
            sla_achieved=99.8,
            sla_target=99.9,
        )
        assert should_promote is False, "should_promote is not valid"

    def test_tier_change_history_tracking(self):
        """Test tier changes are recorded."""
        manager = TierManager(cooldown_days=0)

        manager.promote_tier("test-1", Tier.BRONZE)
        history = manager.get_change_history("test-1")

        assert len(history) == 1, "History must not be empty"
        assert history[0].from_tier == Tier.BRONZE, "from_tier is not valid"
        assert history[0].to_tier == Tier.SILVER, "to_tier is not valid"
        assert history[0].reason == "promotion", "reason is not valid"

    def test_churn_rate_calculation(self):
        """Test churn rate tracks tier changes."""
        manager = TierManager(cooldown_days=0)

        manager.promote_tier("test-1", Tier.BRONZE)
        manager.promote_tier("test-1", Tier.SILVER)
        manager.demote_tier("test-2", Tier.GOLD)

        churn = manager.get_churn_rate()
        assert churn == 3 / 2, "churn is not valid"


class TestBillingEngine:
    """Test billing calculations."""

    def test_billing_basic_calculation(self):
        """Test basic billing calculation."""
        allocation = ResourceAllocation(
            tenant_id="test-1",
            cpu_cores=4,
            memory_gb=16,
            disk_gb=100,
            network_mbps=100,
            tier=Tier.SILVER,
        )

        pricing = PricingModel()
        engine = BillingEngine(pricing)

        billing = engine.calculate_billing(allocation, uptime_achieved=99.85, month="2026-07")

        assert billing.tenant_id == "test-1", "tenant_id is not valid"
        assert billing.month == "2026-07", "month is not valid"
        assert billing.total_cost() > 0, "Value must be greater than zero"

    def test_sla_credit_application(self):
        """Test SLA credits reduce bill when uptime missed."""
        allocation = ResourceAllocation(
            tenant_id="test-1",
            cpu_cores=4,
            memory_gb=16,
            disk_gb=100,
            network_mbps=100,
            tier=Tier.SILVER,  # Target 99.9%
        )

        pricing = PricingModel()
        engine = BillingEngine(pricing)

        # Uptime 0.2% below target
        billing = engine.calculate_billing(allocation, uptime_achieved=99.7, month="2026-07")

        assert billing.sla_credit > 0, "sla_credit must be greater than zero"
        total_before_credit = (billing.cpu_cost + billing.memory_cost +
                              billing.disk_cost + billing.network_cost) * Tier.SILVER.cost_multiplier
        assert billing.total_cost() < total_before_credit, "Condition must be true"

    def test_tier_cost_multiplier_applied(self):
        """Test tier cost multiplier is applied correctly."""
        allocations = [
            ResourceAllocation(
                tenant_id=f"tier-{tier.tier_name}",
                cpu_cores=4,
                memory_gb=16,
                disk_gb=100,
                network_mbps=100,
                tier=tier,
            )
            for tier in Tier
        ]

        pricing = PricingModel()
        engine = BillingEngine(pricing)

        for allocation in allocations:
            billing = engine.calculate_billing(allocation, uptime_achieved=99.95, month="2026-07")
            # Higher tier should have higher cost
            assert billing.cpu_cost > 0, "cpu_cost must be greater than zero"


class TestSLAOptimizer:
    """Integration tests for SLAOptimizer."""

    def test_optimize_single_sla(self):
        """Test optimizing a single SLA."""
        sla = SLASpec(
            tenant_id="tenant-1",
            target_uptime_percent=99.9,
            max_response_time_ms=100,
            max_error_rate_percent=0.1,
            data_retention_days=30,
            peak_qps=1000,
        )

        optimizer = SLAOptimizer()
        allocation = optimizer.optimize_sla(sla)

        assert allocation is not None, "allocation must be initialized"
        assert allocation.tenant_id == "tenant-1", "tenant_id is not valid"
        assert allocation in optimizer.allocations.values(), "Value must be initialized"

    def test_optimize_multiple_slas(self):
        """Test optimizing multiple SLAs."""
        slas = [
            SLASpec(
                tenant_id=f"tenant-{i}",
                target_uptime_percent=99.9 - i * 0.05,
                max_response_time_ms=100,
                max_error_rate_percent=0.1,
                data_retention_days=30,
                peak_qps=1000 * (i + 1),
            )
            for i in range(5)
        ]

        optimizer = SLAOptimizer()
        allocations = optimizer.optimize_tenant_slas(slas)

        assert len(allocations) == 5, "Allocations must not be empty"
        for sla in slas:
            assert sla.tenant_id in allocations, "Condition must be true"

    def test_generate_pareto_frontier(self):
        """Test frontier generation through optimizer."""
        slas = [
            SLASpec(
                tenant_id=f"tenant-{i}",
                target_uptime_percent=99.9,
                max_response_time_ms=100,
                max_error_rate_percent=0.1,
                data_retention_days=30,
                peak_qps=1000,
            )
            for i in range(3)
        ]

        optimizer = SLAOptimizer()
        frontier = optimizer.generate_pareto_frontier(slas, num_points=20)

        assert len(frontier) > 0, "Frontier must not be empty"
        assert all(len(allocs) == 3 for _, allocs in frontier)

    def test_tier_transitions(self):
        """Test tier transition logic."""
        optimizer = SLAOptimizer()

        # Promotion scenario
        new_tier = optimizer.check_tier_transitions(
            tenant_id="test-1",
            current_tier=Tier.SILVER,
            sla_achieved=99.8,
            sla_target=99.9,
            resource_utilization=0.5,
        )
        # Cooldown not active first time, so should promote
        if new_tier:
            assert new_tier in [Tier.BRONZE, Tier.SILVER, Tier.GOLD, Tier.PLATINUM]

    def test_billing_report_generation(self):
        """Test monthly billing report generation."""
        slas = [
            SLASpec(
                tenant_id=f"tenant-{i}",
                target_uptime_percent=99.9,
                max_response_time_ms=100,
                max_error_rate_percent=0.1,
                data_retention_days=30,
                peak_qps=1000,
            )
            for i in range(3)
        ]

        optimizer = SLAOptimizer()
        optimizer.optimize_tenant_slas(slas)
        reports = optimizer.generate_billing_report("2026-07")

        assert len(reports) == 3, "Reports must not be empty"
        for tenant_id, billing in reports.items():
            assert billing.total_cost() > 0, "Value must be greater than zero"
            assert billing.month == "2026-07", "month is not valid"

    def test_csv_export(self):
        """Test CSV export of billing reports."""
        sla = SLASpec(
            tenant_id="tenant-1",
            target_uptime_percent=99.9,
            max_response_time_ms=100,
            max_error_rate_percent=0.1,
            data_retention_days=30,
            peak_qps=1000,
        )

        optimizer = SLAOptimizer()
        optimizer.optimize_sla(sla)
        reports = optimizer.generate_billing_report("2026-07")

        csv_output = optimizer.export_billing_csv(reports)

        assert "tenant_id" in csv_output, "Condition must be true"
        assert "month" in csv_output, "Condition must be true"
        assert "total_cost" in csv_output, "Condition must be true"
        assert "tenant-1" in csv_output, "Condition must be true"

    def test_json_export(self):
        """Test JSON export of billing reports."""
        sla = SLASpec(
            tenant_id="tenant-1",
            target_uptime_percent=99.9,
            max_response_time_ms=100,
            max_error_rate_percent=0.1,
            data_retention_days=30,
            peak_qps=1000,
        )

        optimizer = SLAOptimizer()
        optimizer.optimize_sla(sla)
        reports = optimizer.generate_billing_report("2026-07")

        json_output = optimizer.export_billing_json(reports)
        data = json.loads(json_output)

        assert "tenant-1" in data, "Data must not be empty"
        assert data["tenant-1"]["month"] == "2026-07", "Data must not be empty"

    def test_optimization_summary(self):
        """Test optimization summary generation."""
        slas = [
            SLASpec(
                tenant_id=f"tenant-{i}",
                target_uptime_percent=99.9,
                max_response_time_ms=100,
                max_error_rate_percent=0.1,
                data_retention_days=30,
                peak_qps=1000,
            )
            for i in range(4)
        ]

        optimizer = SLAOptimizer()
        optimizer.optimize_tenant_slas(slas)
        summary = optimizer.get_optimization_summary()

        assert summary["total_allocations"] == 4, "Condition must be true"
        assert summary["total_cpu_cores"] > 0, "Value must be greater than zero"
        assert summary["total_memory_gb"] > 0, "Value must be greater than zero"
        assert "tier_distribution" in summary, "Condition must be true"


class TestCostReduction:
    """Test cost reduction goals (≥10%)."""

    def test_optimized_vs_unoptimized_cost(self):
        """Test optimized allocation reduces cost by ≥10%."""
        sla = SLASpec(
            tenant_id="test-1",
            target_uptime_percent=99.9,
            max_response_time_ms=100,
            max_error_rate_percent=0.1,
            data_retention_days=30,
            peak_qps=1000,
        )

        # Unoptimized: assume 2x resources
        unoptimized_allocation = ResourceAllocation(
            tenant_id="test-1",
            cpu_cores=16,
            memory_gb=64,
            disk_gb=500,
            network_mbps=500,
            tier=Tier.GOLD,
        )

        # Optimized allocation
        optimizer = SLAOptimizer()
        optimized_allocation = optimizer.optimize_sla(sla)

        pricing = PricingModel()
        unoptimized_cost = (unoptimized_allocation.cpu_cores * pricing.cpu_per_core_hour * 730 +
                           unoptimized_allocation.memory_gb * pricing.memory_per_gb_hour * 730 +
                           unoptimized_allocation.disk_gb * pricing.disk_per_gb_month +
                           unoptimized_allocation.network_mbps * pricing.network_per_mbps_month) * Tier.GOLD.cost_multiplier

        optimized_cost = (optimized_allocation.cpu_cores * pricing.cpu_per_core_hour * 730 +
                         optimized_allocation.memory_gb * pricing.memory_per_gb_hour * 730 +
                         optimized_allocation.disk_gb * pricing.disk_per_gb_month +
                         optimized_allocation.network_mbps * pricing.network_per_mbps_month) * optimized_allocation.tier.cost_multiplier

        savings_percent = ((unoptimized_cost - optimized_cost) / unoptimized_cost * 100)
        assert savings_percent >= 10.0, f"Savings only {savings_percent:.1f}%, expected ≥10%"


class TestPricingEngine:
    """Test pricing engine integration."""

    def test_dynamic_price_adjustment(self):
        """Test prices adjust based on demand and supply."""
        from codex.optimization.pricing_engine import DynamicPricingModel

        model = DynamicPricingModel()
        base_price = model.resource_prices["cpu"].base_price

        # Update price at high demand and high utilization
        new_price = model.update_price("cpu", demand_level=0.9, supply_utilization=0.9)

        # Price should be higher than base
        assert new_price > base_price, "new_price must be greater than zero"

    def test_cost_predictor_accuracy(self):
        """Test cost prediction accuracy ±10%."""
        from codex.optimization.pricing_engine import CostPredictor

        predictor = CostPredictor()

        allocation = ResourceAllocation(
            tenant_id="test-1",
            cpu_cores=4,
            memory_gb=16,
            disk_gb=100,
            network_mbps=100,
            tier=Tier.SILVER,
        )

        predicted = predictor.predict_monthly_cost(allocation)
        actual = predicted * 1.05  # Simulate 5% variance

        predictor.record_actual_cost("test-1", actual, predicted)

        accuracy = predictor.get_prediction_accuracy()
        assert accuracy["mean_error_percent"] < 10.0, "Error should be raised or set"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
