#!/usr/bin/env python3
"""
Infrastructure Cost Estimator
Estimates infrastructure costs and provides impact analysis.
"""

import json
import logging
from dataclasses import asdict, dataclass
from typing import Dict, List

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class ResourceCost:
    """Cost for a specific resource."""
    resource_type: str
    quantity: int
    unit_cost_monthly: float
    total_monthly: float


@dataclass
class CostEstimate:
    """Complete cost estimate."""
    cluster_name: str
    environment: str
    region: str
    resources: List[ResourceCost]
    total_monthly: float
    total_yearly: float
    total_3year: float
    cost_breakdown: Dict[str, float]
    optimization_opportunities: List[str]
    monthly_projection: Dict[str, float]


class InfrastructureCostEstimator:
    """Estimate infrastructure costs."""

    def __init__(self):
        """Initialize estimator."""
        self.pricing = self._load_pricing()
        logger.info("Cost estimator initialized")

    def _load_pricing(self) -> Dict:
        """Load pricing data."""
        return {
            "aws": {
                "t3.medium": 0.0416,  # hourly * 730 hours/month
                "t3.large": 0.0832,
                "instance_storage": 0.05,  # GB/month
                "nat_gateway": 32.0,  # per month
                "data_transfer": 0.02,  # per GB
                "load_balancer": 16.0,  # per month
            },
            "gcp": {
                "e2-medium": 0.025,
                "n2-standard-2": 0.0955,
                "persistent_disk": 0.04,  # per GB
                "data_transfer": 0.12,  # inter-region per GB
                "load_balancer": 18.0,
                "ingress": 0.025,  # per GB
            },
            "azure": {
                "Standard_B2s": 0.052,
                "Standard_D4s_v3": 0.192,
                "managed_disk": 5.0,  # per disk
                "data_transfer": 0.02,  # per GB
                "load_balancer": 22.0,
                "vnet": 0.0,  # free
            }
        }

    def estimate_cost(self, pattern: Dict) -> CostEstimate:
        """Estimate infrastructure costs."""
        logger.info(f"Estimating costs for {pattern['cluster_name']}")

        provider = pattern['cloud_provider']
        environment = pattern['environment']
        sizing = pattern['resource_sizing']

        resources = []
        total_monthly = 0.0

        # Calculate node costs
        nodes = sizing['recommended_nodes']
        machine_type = sizing['node_machine_type']

        if provider == "aws":
            hourly_cost = self.pricing["aws"].get(machine_type, 0.1)
            monthly_node_cost = hourly_cost * 730
            resources.append(ResourceCost(
                resource_type="EC2 Instances",
                quantity=nodes,
                unit_cost_monthly=monthly_node_cost,
                total_monthly=monthly_node_cost * nodes
            ))
            total_monthly += monthly_node_cost * nodes

            # Add storage
            storage_gb = int(sizing['disk_per_node'].rstrip('Gi'))
            storage_cost = storage_gb * nodes * self.pricing["aws"]["instance_storage"]
            resources.append(ResourceCost(
                resource_type="Storage (EBS)",
                quantity=storage_gb * nodes,
                unit_cost_monthly=self.pricing["aws"]["instance_storage"],
                total_monthly=storage_cost
            ))
            total_monthly += storage_cost

            # Add networking
            if "prod" in environment:
                resources.append(ResourceCost(
                    resource_type="NAT Gateway",
                    quantity=2,
                    unit_cost_monthly=self.pricing["aws"]["nat_gateway"],
                    total_monthly=self.pricing["aws"]["nat_gateway"] * 2
                ))
                total_monthly += self.pricing["aws"]["nat_gateway"] * 2

            # Add load balancer
            resources.append(ResourceCost(
                resource_type="Network Load Balancer",
                quantity=1,
                unit_cost_monthly=self.pricing["aws"]["load_balancer"],
                total_monthly=self.pricing["aws"]["load_balancer"]
            ))
            total_monthly += self.pricing["aws"]["load_balancer"]

        elif provider == "gcp":
            machine_pricing = self.pricing["gcp"].get(machine_type, 0.05)
            monthly_node_cost = machine_pricing * 730
            resources.append(ResourceCost(
                resource_type="Compute Engine Instances",
                quantity=nodes,
                unit_cost_monthly=monthly_node_cost,
                total_monthly=monthly_node_cost * nodes
            ))
            total_monthly += monthly_node_cost * nodes

            # Add storage
            storage_gb = int(sizing['disk_per_node'].rstrip('Gi'))
            storage_cost = storage_gb * nodes * self.pricing["gcp"]["persistent_disk"]
            resources.append(ResourceCost(
                resource_type="Persistent Disk Storage",
                quantity=storage_gb * nodes,
                unit_cost_monthly=self.pricing["gcp"]["persistent_disk"],
                total_monthly=storage_cost
            ))
            total_monthly += storage_cost

            # Add load balancer
            resources.append(ResourceCost(
                resource_type="Cloud Load Balancer",
                quantity=1,
                unit_cost_monthly=self.pricing["gcp"]["load_balancer"],
                total_monthly=self.pricing["gcp"]["load_balancer"]
            ))
            total_monthly += self.pricing["gcp"]["load_balancer"]

        elif provider == "azure":
            machine_pricing = self.pricing["azure"].get(machine_type, 0.1)
            monthly_node_cost = machine_pricing * 730
            resources.append(ResourceCost(
                resource_type="Virtual Machines",
                quantity=nodes,
                unit_cost_monthly=monthly_node_cost,
                total_monthly=monthly_node_cost * nodes
            ))
            total_monthly += monthly_node_cost * nodes

            # Add managed disk
            disk_cost = self.pricing["azure"]["managed_disk"] * nodes
            resources.append(ResourceCost(
                resource_type="Managed Disks",
                quantity=nodes,
                unit_cost_monthly=self.pricing["azure"]["managed_disk"],
                total_monthly=disk_cost
            ))
            total_monthly += disk_cost

            # Add load balancer
            resources.append(ResourceCost(
                resource_type="Load Balancer",
                quantity=1,
                unit_cost_monthly=self.pricing["azure"]["load_balancer"],
                total_monthly=self.pricing["azure"]["load_balancer"]
            ))
            total_monthly += self.pricing["azure"]["load_balancer"]

        # Calculate projections
        total_yearly = total_monthly * 12
        total_3year = total_yearly * 3

        # Cost breakdown
        cost_breakdown = {
            resource.resource_type: resource.total_monthly
            for resource in resources
        }

        # Optimization opportunities
        optimization_opportunities = self._identify_optimizations(
            pattern, sizing, environment
        )

        # Monthly projection
        monthly_projection = {
            "month_1": total_monthly,
            "month_6": total_monthly * 6,
            "month_12": total_yearly,
            "year_3": total_3year,
        }

        estimate = CostEstimate(
            cluster_name=pattern['cluster_name'],
            environment=environment,
            region=pattern['region'],
            resources=resources,
            total_monthly=total_monthly,
            total_yearly=total_yearly,
            total_3year=total_3year,
            cost_breakdown=cost_breakdown,
            optimization_opportunities=optimization_opportunities,
            monthly_projection=monthly_projection
        )

        logger.info(f"Estimated cost: ${total_monthly:.2f}/month, ${total_yearly:.2f}/year")
        return estimate

    def _identify_optimizations(self, pattern: Dict, sizing: Dict, environment: str) -> List[str]:
        """Identify cost optimization opportunities."""
        opportunities = []

        if environment == "dev":
            if not sizing.get('use_spot_instances', False):
                opportunities.append("Use spot instances for 60-70% savings in dev")
        else:
            opportunities.append("Use reserved instances for 25-30% savings in production")

        if sizing.get('recommended_nodes', 0) > 4:
            opportunities.append("Consider vertical scaling instead of horizontal")

        if pattern.get('monitoring_enabled'):
            opportunities.append("Evaluate cloud-native monitoring (vs. third-party) for cost savings")

        opportunities.append("Implement resource quotas to prevent cost overruns")
        opportunities.append("Schedule dev clusters to stop during off-hours")

        return opportunities

    def to_dict(self, estimate: CostEstimate) -> Dict:
        """Convert estimate to dictionary."""
        return {
            "timestamp": "2026-06-20T09:46:00Z",
            "cluster_name": estimate.cluster_name,
            "environment": estimate.environment,
            "region": estimate.region,
            "cost_summary": {
                "monthly": estimate.total_monthly,
                "yearly": estimate.total_yearly,
                "3year": estimate.total_3year,
            },
            "cost_breakdown": estimate.cost_breakdown,
            "resources": [asdict(r) for r in estimate.resources],
            "optimization_opportunities": estimate.optimization_opportunities,
            "projections": estimate.monthly_projection,
        }


def main():
    """Main entry point."""
    estimator = InfrastructureCostEstimator()

    # Load patterns
    with open("k8s_patterns.json", 'r') as f:
        patterns = json.load(f)

    # Estimate costs for all patterns
    print("\n✅ Infrastructure Cost Estimates\n")

    for pattern_key, pattern in patterns.items():
        estimate = estimator.estimate_cost(pattern)
        print(f"{pattern_key}:")
        print(f"  Monthly: ${estimate.total_monthly:,.2f}")
        print(f"  Yearly: ${estimate.total_yearly:,.2f}")
        print(f"  3-Year: ${estimate.total_3year:,.2f}")
        print()

    # Save sample estimate
    first_pattern = list(patterns.values())[0]
    estimate = estimator.estimate_cost(first_pattern)

    with open("cost_estimate.json", 'w') as f:
        json.dump(estimator.to_dict(estimate), f, indent=2)

    print("✅ Cost estimates complete - Report saved to cost_estimate.json")


if __name__ == "__main__":
    main()
