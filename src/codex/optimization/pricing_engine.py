"""
Dynamic pricing engine for cloud resources with burst capacity and reservations.

Phase 4E Planset 013 - Pricing & Cost Management
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class PricingTier(Enum):
    """Pricing strategies."""
    ON_DEMAND = "on_demand"
    RESERVED = "reserved"
    BURST = "burst"
    SPOT = "spot"


@dataclass
class ResourcePrice:
    """Price for a specific resource type."""
    resource_type: str
    base_price: float  # $/unit/hour
    burst_premium: float = 0.30  # 30% surcharge for burst
    reserved_discount: float = 0.30  # 30% discount for reserved
    min_commitment_hours: int = 730  # 1 month minimum for reserved

    def calculate_on_demand_price(self, quantity: float, hours: float) -> float:
        """Calculate on-demand pricing."""
        return quantity * self.base_price * hours

    def calculate_reserved_price(self, quantity: float, hours: float) -> float:
        """Calculate reserved pricing with discount."""
        discounted_rate = self.base_price * (1 - self.reserved_discount)
        return quantity * discounted_rate * hours

    def calculate_burst_price(self, quantity: float, hours: float) -> float:
        """Calculate burst pricing with premium."""
        burst_rate = self.base_price * (1 + self.burst_premium)
        return quantity * burst_rate * hours


@dataclass
class CostForecast:
    """Cost forecast for a given period."""
    resource_type: str
    baseline_cost: float
    best_case_cost: float  # -10% variance
    worst_case_cost: float  # +10% variance
    recommended_pricing_tier: PricingTier
    confidence: float = 0.95


@dataclass
class HourlyDemandForecast:
    """Hourly demand forecast."""
    timestamp: str
    cpu_demand: float
    memory_demand: float
    disk_demand: float
    network_demand: float
    peak_probability: float  # 0-1, probability of peak demand


class DynamicPricingModel:
    """Dynamic pricing based on demand and market conditions."""

    def __init__(self):
        self.resource_prices: Dict[str, ResourcePrice] = {
            "cpu": ResourcePrice("cpu", base_price=0.05),
            "memory": ResourcePrice("memory", base_price=0.01),
            "disk": ResourcePrice("disk", base_price=0.0001),
            "network": ResourcePrice("network", base_price=0.005),
        }
        self.demand_history: Dict[str, List[float]] = {}
        self.price_history: Dict[str, List[Tuple[str, float]]] = {}

    def update_price(self, resource_type: str, demand_level: float, 
                    supply_utilization: float) -> float:
        """
        Update price dynamically based on demand and supply.
        Formula: price = base_price * (1 + demand_factor) * (1 + supply_factor)
        """
        if resource_type not in self.resource_prices:
            logger.warning(f"Unknown resource type: {resource_type}")
            return 0.0

        base_price = self.resource_prices[resource_type].base_price

        # Demand factor: scale 0-1 demand to 0.8-1.2x multiplier
        demand_factor = 0.8 + (demand_level * 0.4)

        # Supply factor: higher utilization = higher prices
        # At 50% utilization: 1.0x
        # At 80% utilization: 1.5x
        # At 100% utilization: 2.0x
        supply_factor = max(0, (supply_utilization - 0.5) * 2.0)

        new_price = base_price * demand_factor * (1 + supply_factor)

        # Record price change
        if resource_type not in self.price_history:
            self.price_history[resource_type] = []
        self.price_history[resource_type].append((datetime.now().isoformat(), new_price))

        return new_price

    def forecast_cost(self, resource_type: str, quantity: float, 
                     forecast_demand: List[float], days: int = 30) -> CostForecast:
        """
        Forecast cost based on demand patterns.
        Returns forecast with confidence interval.
        """
        # Calculate statistics from forecast
        avg_demand = np.mean(forecast_demand) if forecast_demand else 0.5
        std_demand = np.std(forecast_demand) if forecast_demand else 0.1

        # Assume 30 days at average demand
        hours = days * 24
        base_price = self.resource_prices[resource_type].base_price
        baseline_cost = quantity * base_price * hours

        # Variance ±10% based on demand std dev
        variance = min(0.10, (std_demand / max(avg_demand, 0.1)) * 0.05)
        best_case = baseline_cost * (1 - variance)
        worst_case = baseline_cost * (1 + variance)

        # Recommend tier
        if avg_demand > 0.8:
            tier = PricingTier.BURST
        elif avg_demand > 0.5:
            tier = PricingTier.ON_DEMAND
        else:
            tier = PricingTier.RESERVED

        return CostForecast(
            resource_type=resource_type,
            baseline_cost=baseline_cost,
            best_case_cost=best_case,
            worst_case_cost=worst_case,
            recommended_pricing_tier=tier,
            confidence=min(0.95, 0.5 + (avg_demand * 0.4)),
        )

    def calculate_price_for_tier(self, resource_type: str, quantity: float,
                                hours: float, tier: PricingTier) -> float:
        """Calculate price for specified pricing tier."""
        if resource_type not in self.resource_prices:
            return 0.0

        resource_price = self.resource_prices[resource_type]

        if tier == PricingTier.ON_DEMAND:
            return resource_price.calculate_on_demand_price(quantity, hours)
        elif tier == PricingTier.RESERVED:
            return resource_price.calculate_reserved_price(quantity, hours)
        elif tier == PricingTier.BURST:
            return resource_price.calculate_burst_price(quantity, hours)
        elif tier == PricingTier.SPOT:
            # Spot pricing: 70% of on-demand
            return resource_price.calculate_on_demand_price(quantity, hours) * 0.7
        else:
            return resource_price.calculate_on_demand_price(quantity, hours)

    def get_price_history(self, resource_type: str, 
                         lookback_hours: int = 168) -> List[Tuple[str, float]]:
        """Get price history for a resource type."""
        if resource_type not in self.price_history:
            return []

        history = self.price_history[resource_type]
        cutoff = datetime.now() - timedelta(hours=lookback_hours)

        return [
            (ts, price) for ts, price in history
            if datetime.fromisoformat(ts) >= cutoff
        ]


class CostPredictor:
    """Predict monthly costs with accuracy targets."""

    def __init__(self, pricing_model: Optional[DynamicPricingModel] = None):
        self.pricing_model = pricing_model or DynamicPricingModel()
        self.historical_costs: Dict[str, List[float]] = {}
        self.accuracy_errors: List[float] = []

    def predict_monthly_cost(self, resource_allocation: 'ResourceAllocation') -> float:
        """
        Predict monthly cost with ±10% accuracy target.
        Returns predicted cost in dollars.
        """
        # Assume 730 hours per month
        monthly_hours = 730

        # Calculate costs by resource type
        cpu_cost = resource_allocation.cpu_cores * self.pricing_model.resource_prices["cpu"].base_price * monthly_hours
        memory_cost = resource_allocation.memory_gb * self.pricing_model.resource_prices["memory"].base_price * monthly_hours
        disk_cost = resource_allocation.disk_gb * self.pricing_model.resource_prices["disk"].base_price * 30 * 24
        network_cost = resource_allocation.network_mbps * self.pricing_model.resource_prices["network"].base_price * monthly_hours

        # Apply tier multiplier
        subtotal = (cpu_cost + memory_cost + disk_cost + network_cost) * resource_allocation.tier.cost_multiplier

        # Apply reserved discount
        reserved_discount = subtotal * self.pricing_model.resource_prices["cpu"].reserved_discount

        predicted_cost = subtotal - reserved_discount

        # Track for accuracy measurement
        tenant_id = resource_allocation.tenant_id
        if tenant_id not in self.historical_costs:
            self.historical_costs[tenant_id] = []
        self.historical_costs[tenant_id].append(predicted_cost)

        return predicted_cost

    def record_actual_cost(self, tenant_id: str, actual_cost: float, predicted_cost: float):
        """Record actual vs predicted cost for accuracy tracking."""
        if predicted_cost == 0:
            error_percent = 0
        else:
            error_percent = abs(actual_cost - predicted_cost) / predicted_cost * 100

        self.accuracy_errors.append(error_percent)
        logger.info(f"Cost prediction for {tenant_id}: predicted ${predicted_cost:.2f}, actual ${actual_cost:.2f}, error {error_percent:.1f}%")

    def get_prediction_accuracy(self) -> Dict:
        """Get prediction accuracy statistics."""
        if not self.accuracy_errors:
            return {
                "mean_error_percent": 0,
                "std_error_percent": 0,
                "max_error_percent": 0,
                "within_target_percent": 100,
            }

        errors = np.array(self.accuracy_errors)
        return {
            "mean_error_percent": float(np.mean(errors)),
            "std_error_percent": float(np.std(errors)),
            "max_error_percent": float(np.max(errors)),
            "min_error_percent": float(np.min(errors)),
            "within_target_percent": float(np.sum(errors <= 10) / len(errors) * 100),
            "total_predictions": len(errors),
        }


class BurstCapacityManager:
    """Manage burst capacity pricing and allocation."""

    def __init__(self, base_capacity: Dict[str, float]):
        """
        Initialize with baseline capacity (reserved).
        base_capacity: dict like {"cpu": 100, "memory": 500, "disk": 5000}
        """
        self.base_capacity = base_capacity
        self.burst_usage: Dict[str, float] = {k: 0 for k in base_capacity}
        self.burst_history: List[Tuple[str, float, float]] = []  # (timestamp, resource, burst_qty)

    def allocate_burst(self, resource_type: str, quantity: float) -> bool:
        """
        Allocate burst capacity.
        Returns True if allocation succeeds, False if insufficient capacity.
        """
        if resource_type not in self.base_capacity:
            logger.warning(f"Unknown resource type: {resource_type}")
            return False

        # Check if within reasonable burst limits (5x base capacity)
        available_burst = self.base_capacity[resource_type] * 4  # 5x - 1x base
        if quantity > available_burst:
            logger.warning(f"Burst request {quantity} exceeds max {available_burst} for {resource_type}")
            return False

        self.burst_usage[resource_type] += quantity
        self.burst_history.append((datetime.now().isoformat(), resource_type, quantity))
        logger.info(f"Allocated burst: {quantity} {resource_type}")
        return True

    def release_burst(self, resource_type: str, quantity: float):
        """Release burst capacity."""
        if resource_type in self.burst_usage:
            self.burst_usage[resource_type] = max(0, self.burst_usage[resource_type] - quantity)

    def get_burst_cost(self, resource_type: str, pricing_model: DynamicPricingModel) -> float:
        """Calculate current burst cost."""
        if resource_type not in self.burst_usage:
            return 0.0

        burst_qty = self.burst_usage[resource_type]
        hourly_rate = pricing_model.resource_prices[resource_type].base_price * 1.30  # 30% premium
        return burst_qty * hourly_rate

    def get_burst_utilization(self, resource_type: str) -> float:
        """Get burst utilization as percentage of available."""
        if resource_type not in self.base_capacity:
            return 0.0

        available = self.base_capacity[resource_type] * 4
        return (self.burst_usage.get(resource_type, 0) / max(available, 1)) * 100


class ReservedCapacityPlanner:
    """Plan reserved capacity to minimize costs."""

    def __init__(self):
        self.reserved_commitments: Dict[str, float] = {}
        self.commitment_start_dates: Dict[str, str] = {}

    def calculate_optimal_reservation(self, avg_usage: Dict[str, float],
                                     peak_usage: Dict[str, float],
                                     pricing_model: DynamicPricingModel) -> Dict[str, float]:
        """
        Calculate optimal reserved capacity.
        Strategy: reserve at 70th percentile to balance cost and flexibility.
        """
        optimal_reservations = {}

        for resource_type, avg in avg_usage.items():
            peak = peak_usage.get(resource_type, avg)
            # Reserve at 70th percentile: 0.3*avg + 0.7*peak
            reserve_amount = avg * 0.3 + peak * 0.7

            # Calculate savings vs on-demand
            hours_per_month = 730
            reserved_cost = reserve_amount * pricing_model.resource_prices[resource_type].base_price * hours_per_month * 0.7
            ondemand_cost = peak * pricing_model.resource_prices[resource_type].base_price * hours_per_month

            savings_percent = ((ondemand_cost - reserved_cost) / ondemand_cost * 100) if ondemand_cost > 0 else 0
            logger.info(f"Reservation recommendation for {resource_type}: {reserve_amount:.1f} units, {savings_percent:.1f}% savings")

            optimal_reservations[resource_type] = reserve_amount

        return optimal_reservations

    def commit_reservation(self, resource_type: str, quantity: float, 
                          commitment_term_months: int = 12):
        """Commit to reserved capacity."""
        self.reserved_commitments[resource_type] = quantity
        self.commitment_start_dates[resource_type] = datetime.now().isoformat()
        logger.info(f"Reserved {quantity} {resource_type} for {commitment_term_months} months")

    def get_reservation_status(self) -> Dict:
        """Get current reservation status."""
        return {
            "active_reservations": dict(self.reserved_commitments),
            "start_dates": dict(self.commitment_start_dates),
        }
