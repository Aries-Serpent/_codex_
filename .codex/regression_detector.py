"""
Phase 3 Lane 3: Regression Detection System
Monitors for performance regressions and enforces thresholds
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import statistics

@dataclass
class Metric:
    """Performance metric"""
    name: str
    value: float  # in milliseconds
    timestamp: float
    unit: str = "ms"

class RegressionDetector:
    """
    Detects performance regressions using statistical analysis
    """
    
    SIGNIFICANCE_LEVEL = 0.05
    REGRESSION_THRESHOLD = 0.10  # 10% increase
    
    def __init__(self, baseline_file: Optional[str] = None):
        self.baseline_file = baseline_file or ".codex/PHASE_3_LANE_3_BASELINES.json"
        self.baselines: Dict[str, List[float]] = {}
        self.current_metrics: Dict[str, List[float]] = {}
        self.regressions: List[Dict] = []
        self.improvements: List[Dict] = []
        
        # Load baselines
        if Path(self.baseline_file).exists():
            self._load_baselines()
    
    def _load_baselines(self) -> None:
        """Load baseline metrics from file"""
        try:
            with open(self.baseline_file, 'r') as f:
                data = json.load(f)
                for op in data.get('operations', []):
                    name = op['name']
                    elapsed = op['elapsed_ms']
                    if name not in self.baselines:
                        self.baselines[name] = []
                    self.baselines[name].append(elapsed)
        except Exception as e:
            print(f"⚠️  Could not load baselines: {e}")
    
    def record_metric(self, name: str, value: float) -> None:
        """Record a current metric"""
        if name not in self.current_metrics:
            self.current_metrics[name] = []
        self.current_metrics[name].append(value)
    
    def detect_regression(self, name: str, current_value: float) -> Tuple[bool, float]:
        """
        Detect regression for a metric
        Returns: (is_regression, percent_change)
        """
        if name not in self.baselines:
            return False, 0.0
        
        baseline_values = self.baselines[name]
        baseline_mean = statistics.mean(baseline_values)
        
        percent_change = (current_value - baseline_mean) / baseline_mean
        
        is_regression = (
            percent_change > self.REGRESSION_THRESHOLD and
            current_value > baseline_mean
        )
        
        return is_regression, percent_change
    
    def analyze(self) -> Dict:
        """Analyze current metrics against baselines"""
        self.regressions.clear()
        self.improvements.clear()
        
        for name, values in self.current_metrics.items():
            current_mean = statistics.mean(values)
            is_regression, percent_change = self.detect_regression(name, current_mean)
            
            baseline_mean = statistics.mean(self.baselines.get(name, [current_mean]))
            
            if is_regression:
                self.regressions.append({
                    'name': name,
                    'baseline_ms': baseline_mean,
                    'current_ms': current_mean,
                    'change_percent': percent_change * 100,
                    'severity': self._severity_level(percent_change)
                })
            elif percent_change < -0.05:  # 5% improvement
                self.improvements.append({
                    'name': name,
                    'baseline_ms': baseline_mean,
                    'current_ms': current_mean,
                    'improvement_percent': abs(percent_change) * 100,
                })
        
        return self._generate_report()
    
    def _severity_level(self, percent_change: float) -> str:
        """Determine severity of regression"""
        percent = abs(percent_change) * 100
        if percent > 50:
            return "CRITICAL"
        elif percent > 25:
            return "HIGH"
        elif percent > 10:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _generate_report(self) -> Dict:
        """Generate analysis report"""
        return {
            'regressions_detected': len(self.regressions),
            'improvements_detected': len(self.improvements),
            'regressions': self.regressions,
            'improvements': self.improvements,
            'overall_status': 'PASS' if not self.regressions else 'FAIL'
        }
    
    def export_report(self, output_file: str) -> None:
        """Export regression report"""
        report = self.analyze()
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Regression report exported to {output_file}")

class PerformanceGate:
    """Gate that blocks on performance regressions"""
    
    def __init__(self, detector: RegressionDetector):
        self.detector = detector
        self.passed = True
    
    def check(self, name: str, value: float) -> bool:
        """Check if metric passes gate"""
        is_regression, _ = self.detector.detect_regression(name, value)
        if is_regression:
            self.passed = False
            return False
        return True
    
    def gate_status(self) -> Tuple[bool, str]:
        """Get gate status"""
        report = self.detector.analyze()
        if report['regressions_detected'] > 0:
            return False, f"Performance gate FAILED: {report['regressions_detected']} regressions detected"
        else:
            return True, "Performance gate PASSED: No regressions detected"

# Example usage and helper function
def create_regression_alert(metric_name: str, baseline: float, current: float) -> str:
    """Create a regression alert message"""
    percent_change = ((current - baseline) / baseline) * 100
    severity = "CRITICAL" if percent_change > 50 else "HIGH" if percent_change > 25 else "MEDIUM"
    
    return f"""
⚠️  PERFORMANCE REGRESSION DETECTED
Metric: {metric_name}
Baseline: {baseline:.2f}ms
Current: {current:.2f}ms
Change: +{percent_change:.1f}%
Severity: {severity}
"""
