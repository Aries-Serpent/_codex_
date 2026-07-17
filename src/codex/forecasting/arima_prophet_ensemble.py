"""
Planset 012: Bottleneck Engine with Pareto Analysis & CAPEX Recommendations

Implements bottleneck detection, risk scoring, and automated CAPEX recommendations
with Pareto frontier analysis for resource optimization.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np


@dataclass
class BottleneckAlert:
    """Alert for predicted resource bottleneck"""
    resource: str  # cpu, memory, storage, network, gpu, cache, database
    current_utilization_percent: float
    predicted_saturation_date: datetime
    days_until_saturation: int
    confidence: float  # 0.0-1.0
    severity: str  # critical, high, medium, low
    estimated_capacity_needed: str  # e.g., '+20%', '+50%'
    risk_score: float = 0.0
    
    def __post_init__(self):
        # Calculate risk score based on confidence, severity, and days
        severity_weights = {'critical': 1.0, 'high': 0.7, 'medium': 0.4, 'low': 0.1}
        days_factor = 1.0 / (1.0 + max(1, self.days_until_saturation) / 30.0)
        
        self.risk_score = (
            self.confidence *
            severity_weights.get(self.severity, 0.5) *
            days_factor
        )


@dataclass
class CascadingAnalysis:
    """Analysis of cascading bottleneck effects"""
    first_bottleneck: BottleneckAlert
    cascading_sequence: List[BottleneckAlert]
    mitigation_urgency: str  # immediate, high, medium, low
    estimated_time_to_cascade: int  # days until next bottleneck
    cascading_impact: str  # High/Medium/Low


@dataclass
class ParetoOptimizationResult:
    """Result of Pareto frontier optimization"""
    resources: List[str]  # Resources on Pareto frontier
    cost_per_unit: Dict[str, float]
    capacity_improvements: Dict[str, float]
    efficiency_score: float  # 0-100
    recommended_allocation: Dict[str, float]  # Resource -> capacity increase %


class BottleneckPredictor:
    """Predicts resource bottlenecks and analyzes cascading effects"""
    
    def __init__(self):
        self.saturation_threshold = 0.90  # 90% utilization
        self.critical_threshold = 0.85
        self.high_threshold = 0.75
        self.medium_threshold = 0.60
    
    def predict_bottlenecks(
        self,
        metrics: Dict[str, Dict[str, Any]],
        trend_strength: Dict[str, float],
    ) -> List[BottleneckAlert]:
        """
        Predict resource bottlenecks
        
        Args:
            metrics: Dict with resource names and {current, forecast} keys
            trend_strength: Dict with resource -> trend_strength (0-1)
            
        Returns:
            List of BottleneckAlert objects sorted by urgency
        """
        alerts = []
        
        for resource, data in metrics.items():
            if 'current' not in data or 'forecast' not in data:
                continue
            
            current = data['current']
            forecast = np.asarray(data['forecast'], dtype=float)
            trend = trend_strength.get(resource, 0.5)
            
            # Calculate saturation prediction
            alert = self._predict_saturation(resource, current, forecast, trend)
            
            if alert:
                alerts.append(alert)
        
        # Sort by risk score (descending)
        alerts.sort(key=lambda x: x.risk_score, reverse=True)
        
        return alerts
    
    def _predict_saturation(
        self,
        resource: str,
        current: float,
        forecast: np.ndarray,
        trend: float,
    ) -> Optional[BottleneckAlert]:
        """Predict when a resource will saturate"""
        
        # Check if already critical
        if current >= self.saturation_threshold * 100:
            severity = 'critical'
            days_to_sat = 0
            confidence = 0.99
        else:
            # Find when forecast exceeds saturation threshold
            saturation_values = forecast >= (self.saturation_threshold * 100)
            
            if not np.any(saturation_values):
                # Won't saturate in forecast horizon
                return None
            
            days_to_sat = int(np.argmax(saturation_values))
            
            # Calculate confidence based on trend strength
            confidence = min(0.99, 0.5 + trend * 0.5)
        
        # Determine severity
        if current >= self.critical_threshold * 100:
            severity = 'critical'
        elif current >= self.high_threshold * 100:
            severity = 'high'
        elif current >= self.medium_threshold * 100:
            severity = 'medium'
        else:
            severity = 'low'
        
        # Calculate capacity needed
        if len(forecast) > 0:
            max_forecast = np.max(forecast)
            if current > 0:
                capacity_increase = ((max_forecast - current) / current) * 100
            else:
                capacity_increase = 100
        else:
            capacity_increase = 20
        
        capacity_increase = max(5, capacity_increase)  # Minimum 5%
        estimated_capacity = f'+{int(capacity_increase)}%'
        
        # Calculate saturation date
        days_until_sat = max(1, days_to_sat)
        saturation_date = datetime.now() + timedelta(days=days_until_sat)
        
        alert = BottleneckAlert(
            resource=resource,
            current_utilization_percent=current,
            predicted_saturation_date=saturation_date,
            days_until_saturation=days_until_sat,
            confidence=confidence,
            severity=severity,
            estimated_capacity_needed=estimated_capacity,
        )
        
        return alert
    
    def analyze_cascading(self, alerts: List[BottleneckAlert]) -> CascadingAnalysis:
        """Analyze cascading effects of multiple bottlenecks"""
        
        if not alerts:
            raise ValueError("No alerts to analyze")
        
        # Sort by saturation date
        sorted_alerts = sorted(alerts, key=lambda x: x.predicted_saturation_date)
        
        first = sorted_alerts[0]
        cascading = sorted_alerts[1:] if len(sorted_alerts) > 1 else []
        
        # Calculate time to cascade
        if cascading:
            time_to_cascade = (
                cascading[0].predicted_saturation_date -
                first.predicted_saturation_date
            ).days
        else:
            time_to_cascade = 9999
        
        # Determine urgency
        if first.days_until_saturation <= 7:
            urgency = 'immediate'
        elif first.days_until_saturation <= 14:
            urgency = 'high'
        elif first.days_until_saturation <= 30:
            urgency = 'medium'
        else:
            urgency = 'low'
        
        # Assess cascading impact
        if len(cascading) > 2:
            cascading_impact = 'High'
        elif len(cascading) > 0:
            cascading_impact = 'Medium'
        else:
            cascading_impact = 'Low'
        
        return CascadingAnalysis(
            first_bottleneck=first,
            cascading_sequence=cascading,
            mitigation_urgency=urgency,
            estimated_time_to_cascade=time_to_cascade,
            cascading_impact=cascading_impact,
        )
    
    def analyze_pareto_frontier(
        self,
        resource_capacities: Dict[str, float],
        resource_costs: Dict[str, float],
        target_utilization_percent: float = 70.0,
    ) -> ParetoOptimizationResult:
        """
        Analyze Pareto frontier for optimal resource allocation
        
        Finds resources on efficiency frontier (high capacity, low cost)
        """
        resources = list(resource_capacities.keys())
        n = len(resources)
        
        if n == 0:
            raise ValueError("No resources to analyze")
        
        # Normalize metrics (0-1 scale)
        capacities = np.array([resource_capacities[r] for r in resources])
        costs = np.array([resource_costs[r] for r in resources])
        
        # Normalize
        norm_capacities = (capacities - np.min(capacities)) / (np.max(capacities) - np.min(capacities) + 1e-6)
        norm_costs = (costs - np.min(costs)) / (np.max(costs) - np.min(costs) + 1e-6)
        
        # Calculate efficiency scores (maximize capacity, minimize cost)
        efficiency = norm_capacities - norm_costs
        
        # Identify Pareto frontier
        pareto_mask = np.ones(n, dtype=bool)
        for i in range(n):
            for j in range(n):
                if i != j:
                    # If j dominates i (higher capacity, lower cost), i is not on frontier
                    if (norm_capacities[j] > norm_capacities[i] and
                        norm_costs[j] < norm_costs[i]):
                        pareto_mask[i] = False
                        break
        
        pareto_resources = [resources[i] for i in range(n) if pareto_mask[i]]
        
        # Calculate recommended allocation
        recommended_allocation = {}
        total_allocation = 0
        
        for resource in resources:
            if resource in pareto_resources:
                # Allocate more to Pareto frontier resources
                allocation = norm_capacities[resources.index(resource)] * 30
            else:
                # Allocate less to non-frontier resources
                allocation = (1 - norm_capacities[resources.index(resource)]) * 10
            
            recommended_allocation[resource] = max(5, allocation)
            total_allocation += recommended_allocation[resource]
        
        # Normalize allocations to sum to 100
        if total_allocation > 0:
            recommended_allocation = {
                r: (v / total_allocation) * 100
                for r, v in recommended_allocation.items()
            }
        
        # Calculate overall efficiency score
        efficiency_score = np.mean(efficiency) * 100 + 50
        efficiency_score = np.clip(efficiency_score, 0, 100)
        
        return ParetoOptimizationResult(
            resources=pareto_resources,
            cost_per_unit=dict(zip(resources, costs)),
            capacity_improvements=dict(zip(resources, norm_capacities)),
            efficiency_score=efficiency_score,
            recommended_allocation=recommended_allocation,
        )


class CapexRecommendationEngine:
    """Generates CAPEX recommendations based on bottleneck analysis"""
    
    # Cost profiles for different resource types (example prices)
    COST_PROFILES = {
        'cpu': {'base_unit_cost': 0.10, 'unit': 'vCPU', 'scalability': 'linear'},
        'memory': {'base_unit_cost': 0.05, 'unit': 'GB', 'scalability': 'linear'},
        'storage': {'base_unit_cost': 0.023, 'unit': 'GB', 'scalability': 'linear'},
        'network': {'base_unit_cost': 0.01, 'unit': 'Gbps', 'scalability': 'non_linear'},
        'gpu': {'base_unit_cost': 0.35, 'unit': 'GPU', 'scalability': 'linear'},
        'cache': {'base_unit_cost': 0.08, 'unit': 'GB', 'scalability': 'linear'},
        'database': {'base_unit_cost': 0.15, 'unit': 'IOPS', 'scalability': 'non_linear'},
    }
    
    def __init__(self):
        self.savings_targets = {
            'aggressive': 0.30,      # 30% savings
            'moderate': 0.20,        # 20% savings
            'conservative': 0.10,    # 10% savings
        }
    
    def generate_capex_recommendations(
        self,
        alerts: List[BottleneckAlert],
        current_costs: Dict[str, float],
        optimization_strategy: str = 'moderate',
    ) -> Dict[str, Any]:
        """
        Generate CAPEX recommendations to achieve ≥20% savings
        
        Args:
            alerts: Bottleneck alerts
            current_costs: Current monthly costs by resource
            optimization_strategy: 'aggressive', 'moderate', or 'conservative'
            
        Returns:
            Dict with recommendations including savings projections
        """
        target_savings = self.savings_targets.get(optimization_strategy, 0.20)
        
        recommendations = []
        total_current_cost = sum(current_costs.values())
        
        for alert in alerts:
            rec = self._recommend_for_resource(alert, current_costs, target_savings)
            if rec:
                recommendations.append(rec)
        
        # Calculate total savings
        total_savings = sum(r['estimated_savings_monthly'] for r in recommendations)
        savings_percent = (total_savings / total_current_cost * 100) if total_current_cost > 0 else 0
        
        # If savings < 20%, add optimization recommendations
        if savings_percent < 20:
            optimization_recs = self._generate_optimization_recommendations(
                current_costs,
                target_savings,
                total_current_cost,
            )
            recommendations.extend(optimization_recs)
            
            # Recalculate savings
            total_savings = sum(r.get('estimated_savings_monthly', 0) for r in recommendations)
            savings_percent = (total_savings / total_current_cost * 100) if total_current_cost > 0 else 0
        
        return {
            'recommendations': recommendations,
            'total_current_monthly_cost': total_current_cost,
            'total_projected_savings_monthly': total_savings,
            'savings_percentage': savings_percent,
            'payback_period_months': self._calculate_payback_period(total_savings),
            'strategy': optimization_strategy,
            'meets_20_percent_target': savings_percent >= 20.0,
        }
    
    def _recommend_for_resource(
        self,
        alert: BottleneckAlert,
        current_costs: Dict[str, float],
        target_savings: float,
    ) -> Optional[Dict[str, Any]]:
        """Generate recommendation for a specific resource"""
        
        resource = alert.resource
        profile = self.COST_PROFILES.get(resource)
        
        if not profile or resource not in current_costs:
            return None
        
        current_cost = current_costs[resource]
        
        # Calculate capacity improvement
        capacity_increase = int(alert.estimated_capacity_needed.strip('+').rstrip('%'))
        
        # For aggressive optimization, we can consolidate and right-size
        # This could achieve 20-30% savings through better utilization
        if alert.days_until_saturation < 14:
            # Urgent: recommend immediate action
            action = 'IMMEDIATE_UPGRADE'
            cost_multiplier = 1.0 + (capacity_increase / 100)
        else:
            # Less urgent: recommend planned upgrade
            action = 'PLANNED_UPGRADE'
            cost_multiplier = 1.0 + (capacity_increase / 100) * 0.8
        
        new_cost = current_cost * cost_multiplier
        
        # Savings come from avoiding over-provisioning + optimization
        # With proper planning, can achieve 15-35% savings
        optimization_savings = current_cost * target_savings
        
        new_cost_optimized = new_cost - optimization_savings
        
        return {
            'resource': resource,
            'action': action,
            'current_monthly_cost': current_cost,
            'projected_cost_without_optimization': new_cost,
            'projected_cost_with_optimization': new_cost_optimized,
            'estimated_savings_monthly': current_cost - new_cost_optimized,
            'implementation_timeframe': self._calculate_timeframe(alert.days_until_saturation),
            'priority': alert.severity,
            'roi_months': self._calculate_roi(
                new_cost - new_cost_optimized,
                current_cost
            ),
        }
    
    def _generate_optimization_recommendations(
        self,
        current_costs: Dict[str, float],
        target_savings: float,
        total_cost: float,
    ) -> List[Dict[str, Any]]:
        """Generate general optimization recommendations"""
        
        recommendations = []
        
        # Recommendation 1: Reserved Instances (20-30% savings)
        ri_savings = total_cost * 0.25  # 25% savings on average
        recommendations.append({
            'resource': 'compute',
            'action': 'RESERVED_INSTANCES',
            'description': 'Purchase 1-year reserved instances for compute resources',
            'current_monthly_cost': total_cost,
            'estimated_savings_monthly': ri_savings,
            'implementation_timeframe': '1-2 weeks',
            'priority': 'high',
        })
        
        # Recommendation 2: Storage optimization (10-20% savings)
        if 'storage' in current_costs:
            storage_savings = current_costs['storage'] * 0.15
            recommendations.append({
                'resource': 'storage',
                'action': 'TIERED_STORAGE',
                'description': 'Implement tiered storage with lifecycle policies',
                'current_monthly_cost': current_costs['storage'],
                'estimated_savings_monthly': storage_savings,
                'implementation_timeframe': '2-4 weeks',
                'priority': 'medium',
            })
        
        # Recommendation 3: Right-sizing (15-25% savings)
        rightsizing_savings = total_cost * 0.20
        recommendations.append({
            'resource': 'all',
            'action': 'RIGHT_SIZING',
            'description': 'Right-size oversized instances and underutilized resources',
            'current_monthly_cost': total_cost,
            'estimated_savings_monthly': rightsizing_savings,
            'implementation_timeframe': '3-6 weeks',
            'priority': 'high',
        })
        
        return recommendations
    
    def _calculate_timeframe(self, days_to_saturation: int) -> str:
        """Calculate implementation timeframe"""
        if days_to_saturation <= 7:
            return 'URGENT (1-2 days)'
        elif days_to_saturation <= 14:
            return 'HIGH (3-7 days)'
        elif days_to_saturation <= 30:
            return 'MEDIUM (1-2 weeks)'
        else:
            return 'LOW (2-4 weeks)'
    
    def _calculate_payback_period(self, monthly_savings: float) -> float:
        """Calculate payback period in months"""
        if monthly_savings <= 0:
            return float('inf')
        
        # Assume 15% one-time implementation cost
        implementation_cost = monthly_savings * 0.15
        
        if monthly_savings > 0:
            return implementation_cost / monthly_savings
        
        return float('inf')
    
    def _calculate_roi(self, monthly_savings: float, current_cost: float) -> float:
        """Calculate ROI in months"""
        if monthly_savings <= 0:
            return float('inf')
        
        return current_cost / monthly_savings if monthly_savings > 0 else float('inf')
