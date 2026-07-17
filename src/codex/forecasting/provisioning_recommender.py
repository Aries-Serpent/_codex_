"""
Automated provisioning recommendations with cost analysis.

Recommends capacity increases, instance right-sizing, and cost optimizations.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class ProvisioningRecommendation:
    """Single provisioning recommendation"""
    recommendation_type: str  # 'scale_up', 'upgrade_instance', 'reserved_instance'
    resource: str
    current_capacity: str
    recommended_capacity: str
    timing: str  # e.g., "14 days"
    estimated_cost_monthly: float
    estimated_savings_monthly: float  # Negative = cost increase
    roi_months: float
    confidence: float  # 0-1


class ProvisioningRecommender:
    """
    Recommends provisioning changes to prevent bottlenecks.
    
    Provides cost analysis, timing, and right-sizing recommendations.
    """
    
    # Cost factors (example AWS pricing)
    COST_FACTORS = {
        'cpu_per_vcpu_month': 0.05,  # $/vCPU/month
        'memory_per_gb_month': 0.01,  # $/GB/month
        'disk_per_gb_month': 0.00002,  # $/GB/month
        'reserved_instance_discount': 0.30,  # 30% savings for RI
    }
    
    # Instance types (CPU, Memory, Cost/month)
    INSTANCE_TYPES = {
        't3.large': {'cpu': 2, 'memory': 8, 'cost': 28.0},
        't3.xlarge': {'cpu': 4, 'memory': 16, 'cost': 56.0},
        't3.2xlarge': {'cpu': 8, 'memory': 32, 'cost': 112.0},
        'm5.large': {'cpu': 2, 'memory': 8, 'cost': 80.0},
        'm5.xlarge': {'cpu': 4, 'memory': 16, 'cost': 160.0},
        'm5.2xlarge': {'cpu': 8, 'memory': 32, 'cost': 320.0},
    }
    
    def __init__(self):
        self.recommendations: List[ProvisioningRecommendation] = []
    
    def _calculate_capacity_increase(
        self,
        current_percent: float,
        saturation_threshold: float = 85.0,
    ) -> float:
        """Calculate required capacity increase percentage"""
        if current_percent >= saturation_threshold:
            # Already saturated, need immediate increase
            return 50.0  # Default 50% increase
        
        # Calculate days until saturation
        growth_rate_percent_per_day = (saturation_threshold - current_percent) / 30.0
        if growth_rate_percent_per_day <= 0:
            return 0.0
        
        # Recommend enough capacity for next 90 days
        projected_growth = growth_rate_percent_per_day * 90
        return max(20.0, projected_growth + 10.0)  # +10% for headroom
    
    def _calculate_monthly_cost(
        self,
        cpu_cores: int,
        memory_gb: int,
        use_reserved_instance: bool = False,
    ) -> float:
        """Calculate monthly cost for given capacity"""
        cost = (
            cpu_cores * self.COST_FACTORS['cpu_per_vcpu_month'] * 730 +
            memory_gb * self.COST_FACTORS['memory_per_gb_month'] * 730
        )
        
        if use_reserved_instance:
            cost *= (1 - self.COST_FACTORS['reserved_instance_discount'])
        
        return cost
    
    def recommend_cpu_scaling(
        self,
        current_cpu_percent: float,
        current_cpu_cores: int,
        days_to_saturation: int,
        confidence: float,
    ) -> ProvisioningRecommendation:
        """Recommend CPU scaling"""
        increase_percent = self._calculate_capacity_increase(current_cpu_percent)
        recommended_cores = int(current_cpu_cores * (1 + increase_percent / 100))
        
        current_cost = self._calculate_monthly_cost(current_cpu_cores, 0)
        recommended_cost = self._calculate_monthly_cost(recommended_cores, 0)
        
        return ProvisioningRecommendation(
            recommendation_type='scale_up',
            resource='cpu',
            current_capacity=f'{current_cpu_cores} vCPU',
            recommended_capacity=f'{recommended_cores} vCPU',
            timing=f'{max(7, days_to_saturation - 7)} days',
            estimated_cost_monthly=recommended_cost,
            estimated_savings_monthly=current_cost - recommended_cost,
            roi_months=12,
            confidence=confidence,
        )
    
    def recommend_memory_scaling(
        self,
        current_memory_percent: float,
        current_memory_gb: int,
        days_to_saturation: int,
        confidence: float,
    ) -> ProvisioningRecommendation:
        """Recommend memory scaling"""
        increase_percent = self._calculate_capacity_increase(current_memory_percent)
        recommended_memory = int(current_memory_gb * (1 + increase_percent / 100))
        
        current_cost = self._calculate_monthly_cost(0, current_memory_gb)
        recommended_cost = self._calculate_monthly_cost(0, recommended_memory)
        
        return ProvisioningRecommendation(
            recommendation_type='scale_up',
            resource='memory',
            current_capacity=f'{current_memory_gb} GB',
            recommended_capacity=f'{recommended_memory} GB',
            timing=f'{max(5, days_to_saturation - 5)} days',
            estimated_cost_monthly=recommended_cost,
            estimated_savings_monthly=current_cost - recommended_cost,
            roi_months=12,
            confidence=confidence,
        )
    
    def recommend_instance_upgrade(
        self,
        current_instance: str,
        required_cpu: int,
        required_memory: int,
    ) -> ProvisioningRecommendation:
        """Recommend instance type upgrade"""
        if current_instance not in self.INSTANCE_TYPES:
            raise ValueError(f"Unknown instance type: {current_instance}")
        
        current_spec = self.INSTANCE_TYPES[current_instance]
        current_cost = current_spec['cost']
        
        # Find suitable upgrade
        suitable_instances = [
            (name, spec) for name, spec in self.INSTANCE_TYPES.items()
            if spec['cpu'] >= required_cpu and spec['memory'] >= required_memory
            and spec['cost'] > current_cost
        ]
        
        if not suitable_instances:
            raise ValueError("No suitable upgrade available")
        
        # Pick smallest suitable upgrade
        target_instance, target_spec = min(
            suitable_instances,
            key=lambda x: x[1]['cost'],
        )
        
        target_cost = target_spec['cost']
        
        return ProvisioningRecommendation(
            recommendation_type='upgrade_instance',
            resource='instance',
            current_capacity=current_instance,
            recommended_capacity=target_instance,
            timing='14 days',
            estimated_cost_monthly=target_cost,
            estimated_savings_monthly=current_cost - target_cost,
            roi_months=24,
            confidence=0.85,
        )
    
    def recommend_reserved_instances(
        self,
        monthly_cost_on_demand: float,
    ) -> ProvisioningRecommendation:
        """Recommend switching to reserved instances"""
        reserved_cost = monthly_cost_on_demand * (
            1 - self.COST_FACTORS['reserved_instance_discount']
        )
        
        return ProvisioningRecommendation(
            recommendation_type='reserved_instance',
            resource='compute',
            current_capacity='On-Demand',
            recommended_capacity='Reserved Instance (1-year)',
            timing='Immediate',
            estimated_cost_monthly=reserved_cost,
            estimated_savings_monthly=monthly_cost_on_demand - reserved_cost,
            roi_months=12,
            confidence=1.0,
        )
    
    def get_recommendations(self) -> List[ProvisioningRecommendation]:
        """Get all recommendations sorted by ROI"""
        return sorted(
            self.recommendations,
            key=lambda r: r.estimated_savings_monthly,
            reverse=True,
        )
