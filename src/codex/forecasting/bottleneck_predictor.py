"""
Bottleneck prediction with cascading analysis.

Predicts resource saturation and identifies which bottleneck hits first.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import numpy as np


@dataclass
class BottleneckAlert:
    """Alert for predicted bottleneck"""
    resource: str  # 'cpu', 'memory', 'disk', etc.
    current_utilization_percent: float
    predicted_saturation_date: datetime
    days_until_saturation: int
    confidence: float  # 0-1
    severity: str  # 'low', 'medium', 'high', 'critical'
    estimated_capacity_needed: str


@dataclass
class CascadingBottleneckAnalysis:
    """Analysis of cascading bottlenecks"""
    first_bottleneck: BottleneckAlert
    cascading_sequence: List[BottleneckAlert]
    mitigation_urgency: str  # 'immediate', 'high', 'medium', 'low'


class BottleneckPredictor:
    """
    Predicts resource bottlenecks and saturation times.
    
    Supports CPU, memory, disk, and request rate metrics.
    Implements cascading analysis to determine which bottleneck hits first.
    """
    
    # Saturation thresholds (percent)
    SATURATION_THRESHOLDS = {
        'cpu': 85.0,
        'memory': 85.0,
        'disk': 85.0,
        'request_rate': 80.0,
    }
    
    # Minimum acceptable headroom (days)
    MIN_HEADROOM_DAYS = {
        'cpu': 7,
        'memory': 5,
        'disk': 10,
        'request_rate': 7,
    }
    
    def __init__(self):
        self.predictions: Dict[str, BottleneckAlert] = {}
    
    def _calculate_saturation_time(
        self,
        current_utilization: float,
        forecast_values: np.ndarray,
        resource: str,
    ) -> Optional[int]:
        """
        Calculate days until saturation.
        
        Returns:
            Days until saturation, or None if won't saturate
        """
        threshold = self.SATURATION_THRESHOLDS.get(resource, 85.0)
        
        for i, value in enumerate(forecast_values):
            if value >= threshold:
                return i + 1  # +1 because forecast starts at day 1
        
        return None  # Won't saturate within forecast horizon
    
    def _calculate_confidence(
        self,
        trend_strength: float,
        days_to_saturation: int,
    ) -> float:
        """Calculate prediction confidence (0-1)"""
        # Higher trend strength = higher confidence
        # Shorter horizon = higher confidence
        confidence = trend_strength
        
        if days_to_saturation <= 7:
            confidence *= 1.0
        elif days_to_saturation <= 30:
            confidence *= 0.85
        else:
            confidence *= 0.70
        
        return min(1.0, max(0.0, confidence))
    
    def _calculate_severity(self, days_until_saturation: int, resource: str) -> str:
        """Calculate alert severity"""
        min_headroom = self.MIN_HEADROOM_DAYS.get(resource, 7)
        
        if days_until_saturation <= min_headroom:
            return 'critical'
        elif days_until_saturation <= min_headroom + 7:
            return 'high'
        elif days_until_saturation <= min_headroom + 14:
            return 'medium'
        else:
            return 'low'
    
    def predict_bottlenecks(
        self,
        metrics: Dict[str, Dict],  # {resource: {'current': val, 'forecast': array}}
        trend_strength: Dict[str, float],  # {resource: strength}
    ) -> List[BottleneckAlert]:
        """
        Predict all potential bottlenecks.
        
        Args:
            metrics: Dict of metrics with current and forecast values
            trend_strength: Trend strength for each metric
        
        Returns:
            List of BottleneckAlert sorted by urgency
        """
        alerts = []
        
        for resource, data in metrics.items():
            current_util = data.get('current', 0)
            forecast = data.get('forecast', [])
            
            if len(forecast) == 0:
                continue
            
            days_to_sat = self._calculate_saturation_time(
                current_util,
                forecast,
                resource,
            )
            
            if days_to_sat is None:
                continue  # Won't saturate
            
            trend = trend_strength.get(resource, 0.5)
            confidence = self._calculate_confidence(trend, days_to_sat)
            severity = self._calculate_severity(days_to_sat, resource)
            
            sat_date = datetime.now() + timedelta(days=days_to_sat)
            
            alert = BottleneckAlert(
                resource=resource,
                current_utilization_percent=current_util,
                predicted_saturation_date=sat_date,
                days_until_saturation=days_to_sat,
                confidence=confidence,
                severity=severity,
                estimated_capacity_needed=f"+{int(100 - current_util)}%",
            )
            
            alerts.append(alert)
        
        # Sort by days_until_saturation (earliest first)
        alerts.sort(key=lambda a: a.days_until_saturation)
        
        self.predictions = {a.resource: a for a in alerts}
        return alerts
    
    def analyze_cascading(
        self,
        alerts: List[BottleneckAlert],
    ) -> CascadingBottleneckAnalysis:
        """
        Analyze cascading bottlenecks.
        
        Returns:
            Analysis of which bottleneck hits first and cascading sequence
        """
        if not alerts:
            raise ValueError("No bottleneck alerts to analyze")
        
        # First bottleneck is the earliest
        first = alerts[0]
        
        # Determine mitigation urgency
        if first.days_until_saturation <= 7:
            urgency = 'immediate'
        elif first.days_until_saturation <= 14:
            urgency = 'high'
        elif first.days_until_saturation <= 30:
            urgency = 'medium'
        else:
            urgency = 'low'
        
        return CascadingBottleneckAnalysis(
            first_bottleneck=first,
            cascading_sequence=alerts,
            mitigation_urgency=urgency,
        )
